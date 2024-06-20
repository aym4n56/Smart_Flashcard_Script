import sqlite3
import os
from flet import *

directory = os.path.dirname(os.path.abspath(__file__))
database_file_path = os.path.join(directory, 'flashcard.db')

class Home:
    def __init__(self, page: Page):
        self.page = page
        self.conn = sqlite3.connect(database_file_path)
        self.cursor = self.conn.cursor()

        BG = '#041995'
        FG = '#3450a1'

        # Define buttons for home screen
        buttons = Column(
            height=400,
            scroll='auto',
            controls=[
                Container(
                    height=70,
                    width=400,
                    bgcolor=BG,
                    border_radius=25,
                    on_click=lambda _: page.go("/name_flashcard"),
                    content=Row(
                        alignment='center',
                        controls=[
                            Text(value="Create Flashcard", color='white'),
                        ],
                    ),
                ),
                Container(
                    height=70,
                    width=400,
                    bgcolor=BG,
                    border_radius=25,
                    on_click=lambda _: page.go("/pick_flashcard"),
                    content=Row(
                        alignment='center',
                        controls=[
                            Text(value="Test yourself", color='white'),
                        ],
                    )
                ),
                Container(
                    height=70,
                    width=400,
                    bgcolor=BG,
                    border_radius=25,
                    content=Row(
                        alignment='center',
                        controls=[
                            Text(value="Average Marks", color='white'),
                        ],
                    )
                ),
                Container(
                    height=70,
                    width=400,
                    bgcolor=BG,
                    border_radius=25,
                    content=Row(
                        alignment='center',
                        controls=[
                            Text(value="AI Tutor", color='white'),
                        ],
                    )
                ),
            ]
        )

        home_screen = Container(
            content=Column(
                controls=[
                    Container(height=20),
                    Text(value='Welcome to the Flashcard App!', size=31, weight='bold'),
                    Text(value='Choose an option from below:'),
                    Container(height=20),
                    Stack(
                        controls=[
                            buttons,
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
            content=home_screen,
        )

    def view(self):
        return self.container
