import sqlite3
import os
from flet import *

directory = os.path.dirname(os.path.abspath(__file__))
database_file_path = os.path.join(directory, 'flashcard.db')

def main(page: Page):
    conn = sqlite3.connect(database_file_path)
    cursor = conn.cursor()

    BG = '#041995'
    FWG = '#97b4ff'
    FG = '#3450a1'
    PINK = '#eb06ff'

    current_flashcard_id = None

    def go_to_create_flashcard(e):
        container.content = create_flashcard_elements
        page.update()

# Function to navigate back to the home screen
    def go_back(e):
        container.content = home_screen_elements
        page.update()

    def handle_create_flashcard(e):
        flashcard_name = flashcard_name_input.value
        if flashcard_name:
            cursor.execute('INSERT INTO flashcard (flashcard_name) VALUES (?)', (flashcard_name,))
            conn.commit()
            cursor.execute('SELECT last_insert_rowid()')
            nonlocal current_flashcard_id
            current_flashcard_id = cursor.fetchone()[0]
            flashcard_name_input.value = ""
            container.content = define_question_answer
            page.update()

    def handle_create_question_answer(e):
        question_text = question_text_input.value
        answer_text = answer_text_input.value
        if question_text and answer_text and current_flashcard_id is not None:
            cursor.execute('INSERT INTO question (flashcard_id, question_text) VALUES (?, ?)', (current_flashcard_id, question_text))
            conn.commit()
            cursor.execute('SELECT last_insert_rowid()')
            question_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO correct_answer (question_id, answer_text) VALUES (?, ?)', (question_id, answer_text))
            conn.commit()
            question_text_input.value = ""
            answer_text_input.value = ""
            page.update()


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
                on_click=go_to_create_flashcard,
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

    home_screen_elements = Container(
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

    flashcard_name_input = TextField(label='Flashcard Name', width=300)
    create_flashcard_elements = Container(
        content=Column(
            controls=[
                ElevatedButton(text='Back', on_click=go_back),
                Container(height=20),
                Text(value ='What is your flashcard called?', size=31, weight='bold'),
                Container(height=20),
                flashcard_name_input,
                ElevatedButton(text='Submit', on_click=handle_create_flashcard),
            ],
        ),
    )

    question_text_input = TextField(label='Question', width=300)
    answer_text_input = TextField(label='Answer', width=300)
    define_question_answer = Container(
        content=Column(
            controls=[
                ElevatedButton(text='Back', on_click=go_back),
                Container(height=20),
                Text(value='Enter your question and answer:', size=31, weight='bold'),
                Container(height=20),
                question_text_input,
                answer_text_input,
                ElevatedButton(text='Submit', on_click=handle_create_question_answer),
            ],
        ),
    )

    container = Container(
        width=400,
        height=850,
        bgcolor=FG,
        border_radius=35,
        padding=padding.only(top=50, left=20, right=20, bottom=5),
        content=home_screen_elements,
    )

    page.add(container)

    # Close the database connection when the page is closed
    def on_close(e):
        conn.close()

    page.on_close = on_close
app(target=main)
