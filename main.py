import tkinter as tk
from tkinter import font as tkfont
import sqlite3
import os

directory = os.path.dirname(os.path.abspath(__file__))
database_file_path = os.path.join(directory, 'flashcard.db')

class FlashcardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Flashcard App")
        self.geometry("800x600")
        self.configure(bg='white')

        self.custom_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        
        self.conn = sqlite3.connect(database_file_path)
        
        self.current_flashcard_id = None
        
        self.create_widgets()

    def create_widgets(self):
        self.container = tk.Frame(self, bg="white")
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        for F in (HomePage, AddFlashcardNamePage, AddQuestionPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")

        title_label = tk.Label(self, text="Flashcard App", font=controller.custom_font, bg="white", fg="#333")
        title_label.pack(pady=20)

        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(pady=20)

        start_button = tk.Button(button_frame, text="Start Studying", font=controller.custom_font, bg="#4CAF50", fg="black", padx=20, pady=10, command=self.start_studying)
        start_button.grid(row=0, column=0, padx=10, pady=10)

        add_card_button = tk.Button(button_frame, text="Add Flashcards", font=controller.custom_font, bg="#2196F3", fg="black", padx=20, pady=10, command=lambda: controller.show_frame("AddFlashcardNamePage"))
        add_card_button.grid(row=0, column=1, padx=10, pady=10)

        settings_button = tk.Button(button_frame, text="Settings", font=controller.custom_font, bg="#FFC107", fg="black", padx=20, pady=10, command=self.open_settings)
        settings_button.grid(row=0, column=2, padx=10, pady=10)

    def start_studying(self):
        print("Start Studying clicked")

    def open_settings(self):
        print("Settings clicked")

class AddFlashcardNamePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")

        back_button = tk.Button(self, text="Back", font=controller.custom_font, bg="#FF5733", fg="black", command=lambda: controller.show_frame("HomePage"))
        back_button.pack(anchor='nw', padx=10, pady=10)

        title_label = tk.Label(self, text="Add Flashcard Name", font=controller.custom_font, bg="white", fg="#333")
        title_label.pack(pady=20)

        self.flashcard_name_entry = tk.Entry(self, font=controller.custom_font, width=30)
        self.flashcard_name_entry.pack(pady=10)

        next_button = tk.Button(self, text="Next", font=controller.custom_font, bg="#4CAF50", fg="black", padx=20, pady=10, command=self.save_flashcard_name)
        next_button.pack(pady=20)

    def save_flashcard_name(self):
        flashcard_name = self.flashcard_name_entry.get()
        cursor = self.controller.conn.cursor()
        cursor.execute('INSERT INTO flashcard (flashcard_name) VALUES (?)', (flashcard_name,))
        self.controller.conn.commit()
        self.controller.current_flashcard_id = cursor.lastrowid
        self.controller.show_frame("AddQuestionPage")

class AddQuestionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")

        self.question_text_entry = tk.Entry(self, font=controller.custom_font, width=30)
        self.answer_text_entry = tk.Entry(self, font=controller.custom_font, width=30)

        self.create_widgets()

    def create_widgets(self):
        back_button = tk.Button(self, text="Back", font=self.controller.custom_font, bg="#FF5733", fg="black", command=lambda: self.controller.show_frame("HomePage"))
        back_button.pack(anchor='nw', padx=10, pady=10)

        title_label = tk.Label(self, text="Add Question and Answer", font=self.controller.custom_font, bg="white", fg="#333")
        title_label.pack(pady=20)

        question_text_label = tk.Label(self, text="Question Text:", font=self.controller.custom_font, bg="white", fg="#333")
        question_text_label.pack(pady=10)
        self.question_text_entry.pack(pady=10)

        answer_text_label = tk.Label(self, text="Answer Text:", font=self.controller.custom_font, bg="white", fg="#333")
        answer_text_label.pack(pady=10)
        self.answer_text_entry.pack(pady=10)

        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(pady=20)

        next_button = tk.Button(button_frame, text="Next", font=self.controller.custom_font, bg="#4CAF50", fg="black", padx=20, pady=10, command=self.save_question_and_answer)
        next_button.grid(row=0, column=0, padx=10, pady=10)

        done_button = tk.Button(button_frame, text="Done", font=self.controller.custom_font, bg="#2196F3", fg="black", padx=20, pady=10, command=self.finish_adding)
        done_button.grid(row=0, column=1, padx=10, pady=10)

    def save_question_and_answer(self):
        question_text = self.question_text_entry.get()
        answer_text = self.answer_text_entry.get()

        cursor = self.controller.conn.cursor()
        cursor.execute('INSERT INTO question (flashcard_id, question_text) VALUES (?, ?)', (self.controller.current_flashcard_id, question_text))
        question_id = cursor.lastrowid
        cursor.execute('INSERT INTO correct_answer (question_id, answer_text) VALUES (?, ?)', (question_id, answer_text))
        self.controller.conn.commit()

        self.question_text_entry.delete(0, tk.END)
        self.answer_text_entry.delete(0, tk.END)

    def finish_adding(self):
        self.save_question_and_answer()
        self.controller.show_frame("HomePage")

if __name__ == "__main__":
    app = FlashcardApp()
    app.mainloop()
