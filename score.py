import sqlite3
import os
from flet import *
from views import variables


directory = os.path.dirname(os.path.abspath(__file__))
database_file_path = os.path.join(directory, 'flashcard.db')

class Score:
    def __init__(self, page: Page):
        self.page = page
        self.conn = sqlite3.connect(database_file_path)
        self.cursor = self.conn.cursor()

        BG = '#041995'
        FG = '#3450a1'
        
        score = Container(
            content=Column(
                controls=[
                    Container(height=70),
                    Text(value="You have achieved 10/10", size=35, weight='bold'),
                    ElevatedButton(text='Home', on_click = self.go_home),
                    Container(height=70),

                ],
            ),
        )

        self.container = Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=padding.only(top=50, left=20, right=20, bottom=5),
            content=score,
        )

    def go_home(self, e):
        for question_id, users_answer in variables.new_incorrect_answers.items():
            self.cursor.execute('''INSERT INTO correct_answer (question_id, answer_text) VALUES (?, ?)''', (question_id, users_answer))
            self.conn.commit()
        self.page.go("/")

    def view(self):
        return self.container
