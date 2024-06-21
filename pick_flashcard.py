import sqlite3
import os
from flet import *
from views import variables

directory = os.path.dirname(os.path.abspath(__file__))
database_file_path = os.path.join(directory, 'flashcard.db')

class PickFlashcard:
    def __init__(self, page: Page):
        self.page = page
        self.conn = sqlite3.connect(database_file_path)
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT flashcard_name FROM flashcard")
        flashcards = self.cursor.fetchall()

        BG = '#041995'
        FG = '#3450a1'

        # Define buttons for home screen
        flashcard_rectangles = Column(
            height=400,
            scroll='auto',
            controls=[
                Container(
                    height=70,
                    width=400,
                    bgcolor=BG,
                    border_radius=25,
                    on_click=lambda _, name=flashcard[0]: self.select_flashcard(name),
                    content=Row(
                        alignment='center',
                        controls=[
                            Text(value=flashcard[0], color='white'),
                        ],
                    )
                ) for flashcard in flashcards
            ]
        )

        pick_flashcard = Container(
            content=Column(
                controls=[
                    ElevatedButton(text='Back', on_click=lambda _: self.page.go("/")),
                    Container(height=20),
                    Text(value='What would you like to revise?', size=31, weight='bold'),
                    Container(height=20),
                    Stack(
                        controls=[
                            flashcard_rectangles,
                        ]
                    )
                ],
            ),
        )

        self.container = Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=padding.only(top=50, left=20, right=20, bottom=5),
            content=pick_flashcard,
        )
    
    def select_flashcard(self, name):
        variables.selected_flashcard = name
        print(variables.selected_flashcard)
        self.cursor.execute("SELECT flashcard_id FROM flashcard WHERE flashcard_name = ?", (variables.selected_flashcard,))
        result = self.cursor.fetchone()
        if result:
            variables.current_flashcard_id = result[0]
            print(f"Flashcard ID: {variables.current_flashcard_id}")
            
            self.cursor.execute("SELECT question_text FROM question WHERE flashcard_id = ?", (variables.current_flashcard_id,))
            question_result = self.cursor.fetchone()
            
            if result:
                variables.question_text = question_result[0]
                print(variables.question_text)
            else:
                print("no question")
        
        else:
            print("Flashcard not found or result is empty")
        self.page.update()
        self.page.go("/view_flashcard")


    def view(self):
        return self.container
