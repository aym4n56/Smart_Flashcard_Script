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

        self.question_text_input = TextField(label='Question', width=300)
        self.answer_text_input = TextField(label='Answer', width=300)
        
        def handle_submit_and_next(e):
            self.submit_content(e)
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
                    ElevatedButton(text='Done', on_click=handle_submit_and_next),
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
        print(variables.current_flashcard_name)
        variables.flashcards[self.question_text_input.value.strip()] = self.answer_text_input.value.strip()
        print(variables.flashcards)

    def view(self):
        return self.container
