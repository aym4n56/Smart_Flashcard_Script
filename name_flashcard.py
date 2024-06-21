import sqlite3
import os
from flet import *
from views import variables  # Import variables from the views folder

class NameFlashcard:
    def __init__(self, page: Page):
        self.page = page

        BG = '#041995'
        FG = '#3450a1'

        def handle_submit_and_next(e):
            current_flashcard_name = self.flashcard_name_input.value 
            print(current_flashcard_name) 
            variables.current_flashcard_name = current_flashcard_name  
            self.page.go("/flashcard_content") 

        self.flashcard_name_input = TextField(label='Flashcard Name', width=400)
        
        name_flashcard = Container(
            content=Column(
                controls=[
                    ElevatedButton(text='Back', on_click=lambda _: self.page.go("/")),
                    Container(height=20),
                    Text(value='What is your flashcard called?', size=31, weight='bold'),
                    Container(height=20),
                    self.flashcard_name_input,
                    ElevatedButton(text='Next', on_click=handle_submit_and_next),
                ],
            ),
        )

        self.container = Container(
            width=400,
            height=850,
            bgcolor=FG,
            border_radius=35,
            padding=padding.only(top=50, left=20, right=20, bottom=5),
            content=name_flashcard,
        )

    def view(self):
        return self.container
