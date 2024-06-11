#python3 /Users/ayman/Desktop/FlashcardApp/flaschard.py
import os
import json
import random
import time
import sys
import math
import sqlite3
import nltk
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
stemmer = PorterStemmer()

flashcards = {} #define dictionary list
directory = os.path.dirname(os.path.abspath(__file__))
correct_similarity_threshold = 0.7
incorrect_similarity_threshold = 0.7
decay_rate = 0.01
minimum_threshold = 0.4
valid_size_input = False
size = 0

database_file_path = os.path.join(directory, 'answer_learning.db')

current_file = ""
json_file_id_result = ""
question_id_result = ""
question_id = ""

conn = sqlite3.connect(database_file_path)
cursor = conn.cursor()

def stem_text(text):
    words = nltk.word_tokenize(text)
    stemmed_words = [stemmer.stem(word) for word in words]
    return ' '.join(stemmed_words)

def clear_screen():
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For macOS and Linux (os.name is 'posix')
    else:
        os.system('clear')

def save_to_file(flashcards, correct_similarity_threshold, incorrect_similarity_threshold, filename, directory=directory):
    filepath = os.path.join(directory, filename)
    data = {
        'flashcards': flashcards,
        'correct_similarity_threshold': correct_similarity_threshold,
        'incorrect_similarity_threshold': incorrect_similarity_threshold
    }
    with open(filepath, 'w') as file:
        json.dump(data, file)

def load_flashcards_from_json(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
            flashcards = data.get('flashcards', {})
            correct_similarity_threshold = data.get('correct_similarity_threshold', 0.7)
            incorrect_similarity_threshold = data.get('incorrect_similarity_threshold', 0.7)
            return flashcards, correct_similarity_threshold, incorrect_similarity_threshold
    except FileNotFoundError:
        print("File not found.\n")
        return {}, 0.7, 0.7
        
def preprocess_data(flashcards):
    questions = list(flashcards.keys())
    answer = list(flashcards.values())
    return questions, answer
    
def is_correct_answer(users_answer, question_id, cursor, correct_similarity_threshold, incorrect_similarity_threshold):
    # Retrieve all answers (both correct and incorrect) for the given question_id
    cursor.execute("SELECT answer_text FROM correct_answers WHERE question_id = ?", (question_id,))
    correct_answers = cursor.fetchall()
    cursor.execute("SELECT answer_text FROM incorrect_answers WHERE question_id = ?", (question_id,))
    incorrect_answers = cursor.fetchall()
    
    # Stem user's answer
    stemmed_users_answer = stem_text(users_answer)
    
    # Stem correct answers
    stemmed_correct_answers = [stem_text(answer[0]) for answer in correct_answers]
    
    # Stem incorrect answers
    stemmed_incorrect_answers = [stem_text(answer[0]) for answer in incorrect_answers]
    
    # Prepare a list of all answers (user's, correct, and incorrect)
    all_answers = [stemmed_users_answer] + stemmed_correct_answers + stemmed_incorrect_answers
    
    # Vectorize all answers
    vectorizer = TfidfVectorizer().fit_transform(all_answers)
    vectors = vectorizer.toarray()
    
    # Calculate cosine similarity between the user's answer and all answers
    similarity_scores = cosine_similarity(vectors[0:1], vectors[1:])
    
    # Calculate average similarity scores for correct and incorrect answers separately
    num_correct = len(correct_answers)
    num_incorrect = len(incorrect_answers)
    total_correct_similarity = sum(similarity_scores[0][0:num_correct])
    total_incorrect_similarity = sum(similarity_scores[0][num_correct:])
    avg_correct_similarity = total_correct_similarity / num_correct if num_correct > 0 else 0
    avg_incorrect_similarity = total_incorrect_similarity / num_incorrect if num_incorrect > 0 else 0
    
    # Compare average similarity scores to determine correctness
    if avg_correct_similarity > avg_incorrect_similarity and avg_correct_similarity > correct_similarity_threshold:
        return True  # User's answer has a higher average similarity to correct answers
    elif avg_incorrect_similarity > avg_correct_similarity and avg_incorrect_similarity > incorrect_similarity_threshold:
        return False  # User's answer has a higher average similarity to incorrect answers
    else:
        return None  # Unable to determine based on average similarities
    
def get_json_file_id(cursor, current_file):
    cursor.execute("SELECT id FROM JSON_files WHERE file_name = ?", (current_file,))
    json_file_id_result = cursor.fetchone()
    return json_file_id_result

def get_question_id(cursor, json_file_id, question_text):
    cursor.execute("SELECT question_id FROM questions WHERE json_file_id = ? AND question_text = ?", (json_file_id, question_text))
    question_id_result = cursor.fetchone()
    return question_id_result

def insert_question(cursor, json_file_id, question_text):
    cursor.execute("INSERT OR IGNORE INTO questions (json_file_id, question_text) VALUES (?, ?)", (json_file_id, question_text))
    conn.commit()
    cursor.execute("SELECT question_id FROM questions WHERE json_file_id = ? AND question_text = ?", (json_file_id, question_text))
    question_id_result = cursor.fetchone()
    if question_id_result:
        return question_id_result[0]
    return None

def insert_correct_answer(cursor, question_id, answer_text):
    cursor.execute("INSERT OR IGNORE INTO correct_answers (question_id, answer_text) VALUES (?, ?)", (question_id, answer_text))
    conn.commit()

def insert_incorrect_answer(cursor, question_id, answer_text):
    cursor.execute("INSERT OR IGNORE INTO incorrect_answers (question_id, answer_text) VALUES (?, ?)", (question_id, answer_text))
    conn.commit()

clear_screen()

#initialsing variables
new_or_old = ""
new = "new"
old = "old"

#while loop so that the user has to answer old or new
while new_or_old.strip().lower() not in [new.strip().lower(), old.strip().lower()]:
    print("Do you want to access a flashcard file or do you want to make a new flashcard?\n")
    new_or_old = input("Type old or new\n")

if new_or_old.strip().lower() == old.strip().lower():
    old_file_name = input("What is the file called?\n")
    old_flashcards_file = os.path.join(directory, old_file_name)
    flashcards = load_flashcards_from_json(old_flashcards_file)

    flashcards_data = load_flashcards_from_json(old_flashcards_file)
    flashcards = flashcards_data[0]
    correct_similarity_threshold = flashcards_data[1]
    incorrect_similarity_threshold = flashcards_data[2]

    cursor.execute("INSERT OR IGNORE INTO JSON_files(file_name) VALUES (?)", (old_file_name,))
    conn.commit()

    current_file = (old_file_name)
    print("current file: "+ current_file)

elif new_or_old.strip().lower() == new.strip().lower():
    while not valid_size_input:
        size_input = input("How many flashcards do you have?\n")
        if size_input.isdigit():  # Checking if the input is a digit
            size = int(size_input)  # Converting the input to an integer
            valid_size_input = True  # Set the flag to True to exit the loop
        else:
            print("Please enter a valid integer.")

    # question will repeat until the list has been filled
    for i in range(size):
        question = input("Enter the Question:\n")
        answer = input("Enter the answer for this question:\n")
        flashcards[question] = answer
        # Finished entering flashcards

    print("You have entered all your flashcards\n")
    
    # Initialise variables now
    yes_or_no = ""
    yes = "Y"

    while yes_or_no.strip().lower() not in [yes.strip().lower()]:
        yes_or_no = input("Type Y to save file\n")
    
    if yes_or_no.strip().lower() == yes.strip().lower():
        set_file_name = input("Enter your filename:\n")
        save_to_file(flashcards, correct_similarity_threshold, incorrect_similarity_threshold, set_file_name + ".json",directory)
        cursor.execute("INSERT OR IGNORE INTO JSON_files(file_name) VALUES (?)", (set_file_name+".json",))
        conn.commit()

        current_file = (set_file_name + ".json")
        print("current file: "+ current_file)
    
#makes program wait before clearing screen
time.sleep(1)

questions, answer = preprocess_data(flashcards)

#converts flashcards to a random order so that questions are asked randomly.
random_questions = list(flashcards.items())
random.shuffle(random_questions)

clear_screen()

#Psudo code: Ask all questions check if answer is equal to answer

#score is being tracked starts at zero
score = 0

#number of questions
number_of_questions = 0

for question, answer in random_questions:
     
    json_file_id_result = get_json_file_id(cursor, current_file)
    if json_file_id_result:
        json_file_id = json_file_id_result[0]
    
    question_id = insert_question(cursor, json_file_id, question)
    insert_correct_answer(cursor, question_id, answer)
    insert_incorrect_answer(cursor, question_id, "The wrong answer is " + answer)

    users_answer = input(question + "\n") #initialised this variable to compare to real answer
    number_of_questions = number_of_questions + 1 #keeps count of questions asked    

    if is_correct_answer(users_answer, question_id, cursor, correct_similarity_threshold, incorrect_similarity_threshold) :
        print("Nice!\n")
        score = score+1
        my_answer_was_wrong = input(f"Was your answer along the lines of {answer} (yes/no) ")
        if my_answer_was_wrong.lower() == "no":
            incorrect_similarity_threshold = incorrect_similarity_threshold * math.exp(-decay_rate)
            if incorrect_similarity_threshold < minimum_threshold:
                incorrect_similarity_threshold = minimum_threshold
            score = score - 1
            insert_incorrect_answer(cursor, question_id, users_answer)

        else:
            insert_correct_answer(cursor, question_id, users_answer)
    else:
        print(f"Wrong, the answer is {answer}\n")
        supervised_learning_feedback = input("Was your answer correct? (yes/no) ")
        
        if supervised_learning_feedback.lower() == "yes":
            correct_similarity_threshold = correct_similarity_threshold * math.exp(-decay_rate)
            if correct_similarity_threshold < minimum_threshold:
                correct_similarity_threshold = minimum_threshold
            score = score + 1
            insert_correct_answer(cursor, question_id, users_answer)
            print("Thank you for the feeback, the program will learn from this")
        
        elif supervised_learning_feedback.lower() == "no":
            insert_incorrect_answer(cursor, question_id, users_answer)
        

try:
    save_to_file(flashcards, correct_similarity_threshold, incorrect_similarity_threshold, set_file_name+".json", directory)
except Exception as e:
    save_to_file(flashcards, correct_similarity_threshold, incorrect_similarity_threshold, old_file_name, directory)

print(f"You got {score}/{number_of_questions}")

time.sleep(1)

run_again = input("Would you like to run the program again?\n")
run_again_yes = "yes"
run_again_no = "no"
if run_again.strip().lower() == run_again_yes.strip().lower():
     os.execv(sys.executable, [sys.executable] + sys.argv)
else:
    sys.exit()
