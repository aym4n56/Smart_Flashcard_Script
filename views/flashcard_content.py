import sqlite3
import os
from flet import *
from views import variables  # Import variables from the views folder

directory = os.path.dirname(os.path.abspath(__file__))
database_file_path = os.path.join(directory, 'flashcard.db')

class FlashcardContent:
    def __init__(self, page: Page):
        self.page = page
        

        self.conn = sqlite3.connect(database_file_path)
        self.cursor = self.conn.cursor()

        BG = '#041995'
        FG = '#3450a1'

        self.question_text_input = TextField(label='Question', width=400)
        self.answer_text_input = TextField(label='Answer', width=400)

        
        
        def handle_done(e):

            self.cursor.execute("INSERT INTO flashcard (flashcard_name) VALUES (?)", (variables.current_flashcard_name,))
            self.cursor.execute("SELECT flashcard_id FROM flashcard WHERE flashcard_name = ?", (variables.current_flashcard_name,))
            flashcard_id = self.cursor.fetchone()[0]
            self.conn.commit()

            for question, answer in variables.flashcards.items():
                self.cursor.execute("INSERT INTO question (flashcard_id, question_text) VALUES (?, ?)", (flashcard_id, question))
                question_id = self.cursor.lastrowid
                
                self.cursor.execute("INSERT INTO correct_answer (question_id, answer_text) VALUES (?, ?)", (question_id, answer))
            self.conn.commit()

            page.go("/")  # Assuming this navigates back to the previous page

        flashcard_content = Container(
            content=Column(
                controls=[
                    ElevatedButton(text='Back', on_click=lambda _: page.go("/")),
                    Container(height=20),
                    Text(value='Enter your question and answer:', size=31, weight='bold'),
                    Container(height=20),
                    self.question_text_input,
                    self.answer_text_input,
                    ElevatedButton(text='Submit', on_click=self.submit_content),
                    ElevatedButton(text='Done', on_click=handle_done),
                ],
            ),
        )

        self.container = Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=padding.only(top=50, left=20, right=20, bottom=5),
            content=flashcard_content,
        )

    def submit_content(self, e):
        question = self.question_text_input.value
        answer = self.answer_text_input.value
        if question and answer:
            print(variables.current_flashcard_name)
            variables.flashcards[question] = answer
            print(variables.flashcards)
        else:
            print("empty fields")
        self.question_text_input.value = ""
        self.answer_text_input.value = ""
        self.page.update()

    def view(self):
        return self.container
