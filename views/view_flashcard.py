import sqlite3
import os
from flet import *
from views import variables
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

directory = os.path.dirname(os.path.abspath(__file__))
database_file_path = os.path.join(directory, 'flashcard.db')

similarity_threshold = 0.7

def preprocess_text(text):
    words = nltk.word_tokenize(text)
    filtered_words = [word for word in words if word.isalnum() and word.lower() not in stop_words]
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]
    return ' '.join(lemmatized_words)

def extract_numbers(text):
    return [int(num) for num in re.findall(r'\d+', text)]

def is_correct_answer(users_answer, question_id, cursor):
    cursor.execute("SELECT answer_text FROM correct_answer WHERE question_id = ?", (question_id,))
    correct_answers = cursor.fetchall()
    cursor.execute("SELECT answer_text FROM incorrect_answer WHERE question_id = ?", (question_id,))
    incorrect_answers = cursor.fetchall()

    user_numbers = extract_numbers(users_answer)
    if user_numbers:
        for answer in correct_answers:
            if extract_numbers(answer[0]) == user_numbers:
                return True
        for answer in incorrect_answers:
            if extract_numbers(answer[0]) == user_numbers:
                return False

    preprocessed_users_answer = preprocess_text(users_answer)
    preprocessed_correct_answers = [preprocess_text(answer[0]) for answer in correct_answers]
    preprocessed_incorrect_answers = [preprocess_text(answer[0]) for answer in incorrect_answers]

    all_answers = [preprocessed_users_answer] + preprocessed_correct_answers + preprocessed_incorrect_answers

    try:
        vectorizer = TfidfVectorizer().fit_transform(all_answers)
        vectors = vectorizer.toarray()
    except ValueError:
        return None

    similarity_scores = cosine_similarity(vectors[0:1], vectors[1:])

    num_correct = len(preprocessed_correct_answers)
    num_incorrect = len(preprocessed_incorrect_answers)
    total_correct_similarity = sum(similarity_scores[0][:num_correct])
    total_incorrect_similarity = sum(similarity_scores[0][num_correct:])
    avg_correct_similarity = total_correct_similarity / num_correct if num_correct > 0 else 0
    avg_incorrect_similarity = total_incorrect_similarity / num_incorrect if num_incorrect > 0 else 0

    if avg_correct_similarity > avg_incorrect_similarity:
        return True
    elif avg_incorrect_similarity > avg_correct_similarity:
        return False
    else:
        return None

class ViewFlashcard:
    def __init__(self, page: Page):
        self.page = page
        self.conn = sqlite3.connect(database_file_path)
        self.cursor = self.conn.cursor()

        BG = '#041995'
        FG = '#3450a1'

        self.user_answer_input = TextField(label='Answer', width=400)

        self.question_text = Text(value=variables.question_text, size=20, weight='bold')
        
        view_flashcard = Container(
            content=Column(
                controls=[
                    ElevatedButton(text='Back', on_click=lambda _: self.page.go("/pick_flashcard")),
                    Container(height=20),
                    self.question_text,
                    Container(height=20),
                    self.user_answer_input,
                    ElevatedButton(text='Submit Answer', on_click=self.submit_answer),
                    ElevatedButton(text='Next', on_click=self.next_question),
                    Container(height=20),

                ],
            ),
        )

        self.container = Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=padding.only(top=50, left=20, right=20, bottom=5),
            content=view_flashcard,
        )

    def next_question(self, e):
        self.cursor.execute("SELECT question_id, question_text FROM question WHERE flashcard_id = ? ORDER BY question_id ASC", (variables.current_flashcard_id,))
        questions = self.cursor.fetchall()
        current_question_index = next((index for index, question in enumerate(questions) if question[1] == variables.question_text), -1)
        next_question_index = ((current_question_index + 1) % len(questions))
        variables.question_text = questions[next_question_index][1]
        self.question_text.value = variables.question_text
        print(variables.question_text)
        self.user_answer_input.value = ""
        self.page.update()
        

    def submit_answer(self, e):
        users_answer = self.user_answer_input.value
        self.cursor.execute("SELECT question_id FROM question WHERE question_text = ?", (variables.question_text,))
        question_id = self.cursor.fetchone()[0]

        if is_correct_answer(users_answer, question_id, self.cursor):
            feedback = "Correct!"
        else:
            feedback = "Incorrect. Try again."
            variables.new_incorrect_answers[question_id] = users_answer
            print(variables.new_incorrect_answers)
        
        self.page.snack_bar = SnackBar(content=Text(feedback))
        self.page.snack_bar.open = True
        self.page.update()

    def view(self):
        return self.container
