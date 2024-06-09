#python3 /Users/ayman/Desktop/FlashcardApp/flaschard.py
import os
import json
import random
import time
import sys

import sqlite3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

flashcards = {} #define dictionary list
directory = os.path.dirname(os.path.abspath(__file__))
similarity_threshold = 0.5
valid_size_input = False
size = 0

database_file_path = os.path.join(directory, 'answer_learning.db')

conn = sqlite3.connect(database_file_path)
cursor = conn.cursor()

def clear_screen():
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For macOS and Linux (os.name is 'posix')
    else:
        os.system('clear')

def save_to_file(flashcards, similarity_threshold, filename, directory=directory):
    filepath = os.path.join(directory, filename)
    data = {
        'flashcards': flashcards,
        'similarity_threshold': similarity_threshold
    }
    with open(filepath, 'w') as file:
        json.dump(data, file)


def load_flashcards_from_json(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
            flashcards = data.get('flashcards', {})
            similarity_threshold = data.get('similarity_threshold', 0.5)
            return flashcards, similarity_threshold
    except FileNotFoundError:
        print("File not found.\n")
        return {}, 0.5
        
def preprocess_data(flashcards):
    questions = list(flashcards.keys())
    answer = list(flashcards.values())
    return questions, answer
    
def is_correct_answer(users_answer, answer):
    # Try to handle numeric answers
    try:
        users_answer = float(users_answer)
        answer = float(answer)
        return users_answer == answer
    except ValueError:
        # Handle non-numeric answers
        vectorizer = TfidfVectorizer().fit_transform([users_answer, answer])
        vectors = vectorizer.toarray()
        similarity = cosine_similarity(vectors[0:2])
        return similarity[0][1] > similarity_threshold

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
    similarity_threshold = flashcards_data[1]

    cursor.execute("INSERT OR IGNORE INTO JSON_files(file_name) VALUES (?)", (old_file_name,))
    conn.commit()

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
    no = "N"

    while yes_or_no.strip().lower() not in [yes.strip().lower(), no.strip().lower()]:
        print("Do you want to save these to a file so you dont need to type then out again?\n")
        yes_or_no = input("Type Y or N\n")
    
    if yes_or_no.strip().lower() == yes.strip().lower():
        set_file_name = input("Enter your filename:\n")
        save_to_file(flashcards, similarity_threshold, set_file_name + ".json",directory)
        cursor.execute("INSERT OR IGNORE INTO JSON_files(file_name) VALUES (?)", (set_file_name+".json",))
        conn.commit()
    elif yes_or_no.strip().lower() == no.strip().lower():
        print("You have chosen not to save these quesions you may now continue")
    
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
    users_answer = input(question + "\n") #initialised this variable to compare to real answer
    number_of_questions = number_of_questions + 1 #keeps count of questions asked
    
    if is_correct_answer(users_answer, answer) :
        print("Nice!\n")
        score = score+1
    else:
        print(f"Wrong, the answer is {answer}\n")
        supervised_learning_feedback = input("Was your answer correct? (yes/no) ")
        
        if supervised_learning_feedback.lower() == "yes":
            similarity_threshold = similarity_threshold - 0.05
            score = score + 1
            print("Thank you for the feeback, the program will learn from this")
        

try:
    save_to_file(flashcards, similarity_threshold, set_file_name+".json", directory)
except Exception as e:
    save_to_file(flashcards, similarity_threshold, old_file_name, directory)

print(f"You got {score}/{number_of_questions}")

time.sleep(1)

run_again = input("Would you like to run the program again?\n")
run_again_yes = "yes"
run_again_no = "no"
if run_again.strip().lower() == run_again_yes.strip().lower():
     os.execv(sys.executable, [sys.executable] + sys.argv)
else:
    sys.exit()
