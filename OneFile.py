import flet as ft
import sqlite3
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import re
import openai
from ucimlrepo import fetch_ucirepo 
import pandas as pd

nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

database_file_path = 'flashcard.db'

# Global variables
current_flashcard_name = ""
flashcards = {}
selected_flashcard = ""
current_flashcard_id = ""
question_text = ""
current_question_id = ""
new_incorrect_answers = {}
learnt_answers = {}
score = 0
total = 0

openai.api_key = 'use ur api key'

class Home:
    def __init__(self, page):
        self.page = page
        BG = '#041995'
        FG = '#3450a1'

        buttons = ft.Column(
            height=400,
            scroll='auto',
            controls=[
                ft.Container(
                    height=70,
                    width=400,
                    bgcolor=BG,
                    border_radius=25,
                    on_click=lambda _: page.go("/name_flashcard"),
                    content=ft.Row(
                        alignment='center',
                        controls=[
                            ft.Text(value="Create Flashcard", color='white'),
                        ],
                    ),
                ),
                ft.Container(
                    height=70,
                    width=400,
                    bgcolor=BG,
                    border_radius=25,
                    on_click=lambda _: page.go("/pick_flashcard"),
                    content=ft.Row(
                        alignment='center',
                        controls=[
                            ft.Text(value="Test yourself", color='white'),
                        ],
                    )
                ),
                ft.Container(
                    height=70,
                    width=400,
                    bgcolor=BG,
                    border_radius=25,
                    on_click=lambda _: page.go("/grade_predictor"),
                    content=ft.Row(
                        alignment='center',
                        controls=[
                            ft.Text(value="Grade Predictor", color='white'),
                        ],
                    )
                ),
                ft.Container(
                    height=70,
                    width=400,
                    bgcolor=BG,
                    border_radius=25,
                    on_click=lambda _: page.go("/ai_tutor"),
                    content=ft.Row(
                        alignment='center',
                        controls=[
                            ft.Text(value="AI Tutor", color='white'),
                        ],
                    )
                ),
            ]
        )

        home_screen = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=20),
                    ft.Text(value='Welcome to the Flashcard App!', size=31, weight='bold'),
                    ft.Text(value='Choose an option from below:'),
                    ft.Container(height=20),
                    ft.Stack(
                        controls=[
                            buttons,
                        ]
                    )
                ],
            ),
        )

        self.container = ft.Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=ft.padding.only(top=50, left=20, right=20, bottom=5),
            content=home_screen,
        )

    def view(self):
        return self.container

class NameFlashcard:
    def __init__(self, page):
        self.page = page

        BG = '#041995'
        FG = '#3450a1'

        def handle_submit_and_next(e):
            global current_flashcard_name
            current_flashcard_name = self.flashcard_name_input.value
            print(current_flashcard_name)
            self.page.go("/flashcard_content")

        self.flashcard_name_input = ft.TextField(label='Flashcard Name', width=400)

        name_flashcard = ft.Container(
            content=ft.Column(
                controls=[
                    ft.ElevatedButton(text='Back', on_click=lambda _: self.page.go("/")),
                    ft.Container(height=20),
                    ft.Text(value='What is your flashcard called?', size=31, weight='bold'),
                    ft.Container(height=20),
                    self.flashcard_name_input,
                    ft.ElevatedButton(text='Next', on_click=handle_submit_and_next),
                ],
            ),
        )

        self.container = ft.Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=ft.padding.only(top=50, left=20, right=20, bottom=5),
            content=name_flashcard,
        )

    def view(self):
        return self.container

class FlashcardContent:
    def __init__(self, page):
        self.page = page

        BG = '#041995'
        FG = '#3450a1'

        self.question_text_input = ft.TextField(label='Question', width=400)
        self.answer_text_input = ft.TextField(label='Answer', width=400)

        def handle_done(e):
            global current_flashcard_name, flashcards

            conn = sqlite3.connect(database_file_path)
            cursor = conn.cursor()

            cursor.execute("INSERT INTO flashcard (flashcard_name) VALUES (?)", (current_flashcard_name,))
            cursor.execute("SELECT flashcard_id FROM flashcard WHERE flashcard_name = ?", (current_flashcard_name,))
            flashcard_id = cursor.fetchone()[0]

            for question, answer in flashcards.items():
                cursor.execute("INSERT INTO question (flashcard_id, question_text) VALUES (?, ?)", (flashcard_id, question))
                question_id = cursor.lastrowid

                cursor.execute("INSERT INTO correct_answer (question_id, answer_text) VALUES (?, ?)", (question_id, answer))
            conn.commit()
            cursor.close()
            conn.close()

            page.go("/")

        flashcard_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.ElevatedButton(text='Back', on_click=lambda _: page.go("/")),
                    ft.Container(height=20),
                    ft.Text(value='Enter your question and answer:', size=31, weight='bold'),
                    ft.Container(height=20),
                    self.question_text_input,
                    self.answer_text_input,
                    ft.ElevatedButton(text='Submit', on_click=self.submit_content),
                    ft.ElevatedButton(text='Done', on_click=handle_done),
                ],
            ),
        )

        self.container = ft.Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=ft.padding.only(top=50, left=20, right=20, bottom=5),
            content=flashcard_content,
        )

    def submit_content(self, e):
        global flashcards, current_flashcard_name
        question = self.question_text_input.value
        answer = self.answer_text_input.value
        if question and answer:
            flashcards[question] = answer
        else:
            print("Empty fields")
        self.question_text_input.value = ""
        self.answer_text_input.value = ""
        self.page.update()

    def view(self):
        return self.container

class PickFlashcard:
    def __init__(self, page):
        self.page = page

        BG = '#041995'
        FG = '#3450a1'

        flashcard_rectangles = ft.Column(
            height=400,
            scroll='auto',
            controls=[]
        )

        self.update_flashcards(flashcard_rectangles)

        pick_flashcard = ft.Container(
            content=ft.Column(
                controls=[
                    ft.ElevatedButton(text='Back', on_click=lambda _: self.page.go("/")),
                    ft.Container(height=20),
                    ft.Text(value='What would you like to revise?', size=31, weight='bold'),
                    ft.Container(height=20),
                    ft.Stack(
                        controls=[
                            flashcard_rectangles,
                        ]
                    )
                ],
            ),
        )

        self.container = ft.Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=ft.padding.only(top=50, left=20, right=20, bottom=5),
            content=pick_flashcard,
        )

    def update_flashcards(self, flashcard_rectangles):
        conn = sqlite3.connect(database_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT flashcard_name FROM flashcard")
        flashcards = cursor.fetchall()
        cursor.close()
        conn.close()

        flashcard_rectangles.controls = [
            ft.Container(
                height=70,
                width=400,
                bgcolor='#041995',
                border_radius=25,
                on_click=lambda _, name=flashcard[0]: self.select_flashcard(name),
                content=ft.Row(
                    alignment='center',
                    controls=[
                        ft.Text(value=flashcard[0], color='white'),
                    ],
                )
            ) for flashcard in flashcards
        ]
        self.page.update()

    def select_flashcard(self, name):
        global current_flashcard_id, question_text
        selected_flashcard = name
        print(selected_flashcard)
        
        conn = sqlite3.connect(database_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT flashcard_id FROM flashcard WHERE flashcard_name = ?", (selected_flashcard,))
        result = cursor.fetchone()
        if result:
            current_flashcard_id = result[0]
            print(f"Flashcard ID: {current_flashcard_id}")
            cursor.execute("SELECT question_text FROM question WHERE flashcard_id = ? LIMIT 1", (current_flashcard_id,))
            question_result = cursor.fetchone()
            if question_result:
                question_text = question_result[0]
                print(question_text)
            else:
                print("No question")
        else:
            print("Flashcard not found or result is empty")
        cursor.close()
        conn.close()
        self.page.update()
        self.page.go("/view_flashcard")

    def view(self):
        return self.container

class ViewFlashcard:
    def __init__(self, page: ft.Page):
        self.page = page
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.similarity_threshold = 0.9
        global score, total
        score = int(0)
        total = int(0)

        BG = '#041995'
        FG = '#3450a1'

        self.user_answer_input = ft.TextField(label='Answer', width=400)
        self.question_text = ft.Text(value=question_text, size=20, weight='bold')
        
        view_flashcard = ft.Container(
            content=ft.Column(
                controls=[
                    ft.ElevatedButton(text='Back', on_click=lambda _: self.page.go("/pick_flashcard")),
                    ft.Container(height=20),
                    self.question_text,
                    ft.Container(height=20),
                    self.user_answer_input,
                    ft.ElevatedButton(text='Check', on_click=self.submit_answer),
                    ft.Container(height=20),
                    ft.ElevatedButton(text='LEARN', on_click=self.learn_answer),
                ],
            ),
        )

        self.container = ft.Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=ft.padding.only(top=50, left=20, right=20, bottom=5),
            content=view_flashcard,
        )

    def preprocess_text(self, text):
        words = nltk.word_tokenize(text)
        filtered_words = [word for word in words if word.isalnum() and word.lower() not in self.stop_words]
        lemmatized_words = [self.lemmatizer.lemmatize(word) for word in filtered_words]
        return ' '.join(lemmatized_words)

    def extract_numbers(self, text):
        return [int(num) for num in re.findall(r'\d+', text)]

    def is_correct_answer(self, users_answer, question_id):
        conn = sqlite3.connect(database_file_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT answer_text FROM correct_answer WHERE question_id = ?", (question_id,))
        correct_answers = cursor.fetchall()
        cursor.execute("SELECT answer_text FROM incorrect_answer WHERE question_id = ?", (question_id,))
        incorrect_answers = cursor.fetchall()

        user_numbers = self.extract_numbers(users_answer)
        if user_numbers:
            for answer in correct_answers:
                if self.extract_numbers(answer[0]) == user_numbers:
                    return True
            for answer in incorrect_answers:
                if self.extract_numbers(answer[0]) == user_numbers:
                    return False

        preprocessed_users_answer = self.preprocess_text(users_answer)
        preprocessed_correct_answers = [self.preprocess_text(answer[0]) for answer in correct_answers]
        preprocessed_incorrect_answers = [self.preprocess_text(answer[0]) for answer in incorrect_answers]

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

        cursor.close()
        conn.close()

        if avg_correct_similarity > avg_incorrect_similarity:
            return True
        elif avg_incorrect_similarity > avg_correct_similarity:
            return False
        else:
            return None

    def next_question(self, e):
        global question_text
        conn = sqlite3.connect(database_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT question_id, question_text FROM question WHERE flashcard_id = ? ORDER BY question_id ASC", (current_flashcard_id,))
        questions = cursor.fetchall()
        cursor.close()
        conn.close()

        current_question_index = next((index for index, question in enumerate(questions) if question[1] == question_text), -1)

        if current_question_index == len(questions) - 1:
            next_question_index = 0
            self.page.go("/score")
        else:
            next_question_index = ((current_question_index + 1) % len(questions))
            question_text = questions[next_question_index][1]
            self.question_text.value = question_text
            self.user_answer_input.value = ""
            self.page.update()

    def submit_answer(self, e):
        global score, total
        users_answer = self.user_answer_input.value
        conn = sqlite3.connect(database_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT question_id FROM question WHERE question_text = ?", (self.question_text.value,))
        question_id = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        if self.is_correct_answer(users_answer, question_id):
            feedback = "Correct!"
            score = score + 1
            total = total + 1
            self.next_question(e)
        else:
            feedback = "Incorrect. Try again."
            total + 1
            score = score - 1
            new_incorrect_answers[question_id] = users_answer
            print(new_incorrect_answers)
        
        self.page.snack_bar = ft.SnackBar(content=ft.Text(feedback))
        self.page.snack_bar.open = True
        self.page.update()
    
    def learn_answer(self, e):
        conn = sqlite3.connect(database_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT question_id FROM question WHERE question_text = ?", (self.question_text.value,))
        question_id = cursor.fetchone()[0]
        
        if question_id in new_incorrect_answers:
            learnt_answers[question_id] = new_incorrect_answers.pop(question_id)
        
        cursor.close()
        conn.close()

        score = score + 1
        
        self.page.snack_bar = ft.SnackBar(content=ft.Text("Answer learned!"))
        self.page.snack_bar.open = True
        self.page.update()

    def view(self):
        return self.container

class Score:
    def __init__(self, page: ft.Page):
        self.page = page

        global score, total

        BG = '#041995'
        FG = '#3450a1'
        
        score = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=70),
                    ft.Text(value=f"You have achieved {score} out of {total}", size=35, weight='bold'),
                    ft.ElevatedButton(text='Home', on_click = self.go_home),
                    ft.Container(height=70),

                ],
            ),
        )

        self.container = ft.Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=ft.padding.only(top=50, left=20, right=20, bottom=5),
            content=score,
        )

    def go_home(self, e):
        self.conn = sqlite3.connect(database_file_path)
        self.cursor = self.conn.cursor()
        
        for question_id, users_answer in learnt_answers.items():
            self.cursor.execute('''INSERT INTO correct_answer (question_id, answer_text) VALUES (?, ?)''', (question_id, users_answer))
            self.conn.commit()

        for question_id, users_answer in new_incorrect_answers.items():
            self.cursor.execute('''INSERT INTO incorrect_answer (question_id, answer_text) VALUES (?, ?)''', (question_id, users_answer))
            self.conn.commit()
        self.conn.close()
        self.page.go("/")

    def view(self):
        return self.container
    
class AITutor:
    def __init__(self, page):
        self.page = page

        BG = '#041995'
        FG = '#3450a1'

        self.question_text_input = ft.TextField(label='Question', width=400)
        self.ai_answer_output = ft.Text(value='', size=15)

        ai_tutor_screen = ft.Column(
            controls=[
                ft.ElevatedButton(text='Back', on_click=lambda _: page.go("/")),
                ft.Container(height=20),
                ft.Text(value='Ask me anything!', size=31, weight='bold'),
                ft.Container(height=20),
                self.question_text_input,
                ft.ElevatedButton(text='Ask AI', on_click=self.ask_ai),
                ft.Container(height=20),
                ft.Container(
                    width=400,
                    height=400,
                    padding=10,
                    bgcolor=FG,
                    border_radius=0,
                    content=ft.Column(
                        controls=[self.ai_answer_output],
                        scroll='auto',
                    )
                ),
            ]
        )

        self.container = ft.Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=ft.padding.only(top=50, left=20, right=20, bottom=5),
            content=ai_tutor_screen
        )

    def ask_ai(self, e):
        question = self.question_text_input.value.strip()

        if question:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": question}],
                    stream=True
                )

                answer = ""
                for message in response:
                    delta = message['choices'][0]['delta']
                    content = delta.get('content', '')
                    answer += content
                    self.ai_answer_output.value = answer
                    self.page.update()

            except Exception as ex:
                print(f"Error asking AI: {ex}")
                self.ai_answer_output.value = "Error: AI could not provide an answer."
        else:
            self.ai_answer_output.value = "Please enter a question."

        self.page.update()

    def view(self):
        return self.container

    
class Router:
    def __init__(self, page):
        self.page = page
        self.routes = {
            "/": Home(page).view(),
            "/name_flashcard": NameFlashcard(page).view(),
            "/flashcard_content": FlashcardContent(page).view(),
            "/pick_flashcard": PickFlashcard(page).view(),
            "/view_flashcard": None, 
            "/score": None,
             "/ai_tutor": AITutor(page).view(),
        }

    def route_change(self, route):
        self.page.views.clear()
        if route.route == '/view_flashcard':
            view_flashcard = ViewFlashcard(self.page)
            self.routes["/view_flashcard"] = view_flashcard.view()
        if route.route == '/score':
            scorePage = Score(self.page)
            self.routes["/score"] = scorePage.view()
        self.page.views.append(self.routes.get(route.route, self.routes["/"]))
        self.page.update()

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    router = Router(page)
    page.on_route_change = router.route_change
    page.title = "Flashcard App"
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)
