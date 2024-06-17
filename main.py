import tkinter as tk
from tkinter import font as tkfont
import sqlite3
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image, ImageTk 
import re

nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
directory = os.path.dirname(os.path.abspath(__file__))
database_file_path = os.path.join(directory, 'flashcard.db')
learn_button_file_path = os.path.join(directory, 'learn.png')
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

class FlashcardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Flashcard App")
        self.geometry("800x600")
        self.configure(bg='white')

        self.custom_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        
        self.conn = sqlite3.connect(database_file_path)
        self.create_tables()
        
        self.current_flashcard_id = None
        
        self.create_widgets()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcard (
                flashcard_id INTEGER PRIMARY KEY,
                flashcard_name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS question (
                question_id INTEGER PRIMARY KEY,
                flashcard_id INTEGER,
                question_text TEXT NOT NULL,
                FOREIGN KEY(flashcard_id) REFERENCES flashcard(flashcard_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS correct_answer (
                answer_id INTEGER PRIMARY KEY,
                question_id INTEGER,
                answer_text TEXT NOT NULL,
                FOREIGN KEY(question_id) REFERENCES question(question_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incorrect_answer (
                answer_id INTEGER PRIMARY KEY,
                question_id INTEGER,
                answer_text TEXT NOT NULL,
                FOREIGN KEY(question_id) REFERENCES question(question_id)
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        self.container = tk.Frame(self, bg="white")
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        for F in (HomePage, AddFlashcardNamePage, AddQuestionPage, StudyPage, FlashcardDetailPage):
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

        start_button = tk.Button(button_frame, text="Start Studying", font=controller.custom_font, bg="#4CAF50", fg="black", padx=20, pady=10, command=lambda: controller.show_frame("StudyPage"))
        start_button.grid(row=0, column=0, padx=10, pady=10)

        add_card_button = tk.Button(button_frame, text="Add Flashcards", font=controller.custom_font, bg="#2196F3", fg="black", padx=20, pady=10, command=lambda: controller.show_frame("AddFlashcardNamePage"))
        add_card_button.grid(row=0, column=1, padx=10, pady=10)

        tutor_button = tk.Button(button_frame, text="AI Tutor", font=controller.custom_font, bg="#FFC107", fg="black", padx=20, pady=10)
        tutor_button.grid(row=0, column=2, padx=10, pady=10)

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
    
    def back_to_study_page(self):
        global question, score
        question = 0
        score = 0
        self.controller.show_frame("StudyPage")

    def create_widgets(self):
        back_button = tk.Button(self, text="Back", font=self.controller.custom_font, bg="#FF5733", fg="black", command=self.back_to_study_page)
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

class StudyPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        back_button = tk.Button(self, text="Back", font=controller.custom_font, bg="#FF5733", fg="black", command=lambda: controller.show_frame("HomePage"))
        back_button.grid(row=0, column=0, sticky='nw', padx=10, pady=10)

        title_label = tk.Label(self, text="Select a Flashcard Set", font=controller.custom_font, bg="white", fg="#333")
        title_label.grid(row=0, column=1, pady=20, sticky='n')

        refresh_button = tk.Button(self, text="Refresh", font=controller.custom_font, bg="#4CAF50", fg="black", command=self.refresh_flashcards)
        refresh_button.grid(row=0, column=2, padx=10, pady=10)

        self.canvas = tk.Canvas(self, bg="white")
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=1, column=1, sticky='nsew')
        self.scrollbar.grid(row=1, column=2, sticky='ns')

        self.centered_frame = tk.Frame(self.scrollable_frame, bg="white")
        self.centered_frame.grid(row=0, column=0, padx=10, pady=20)

        self.load_flashcards()

    def load_flashcards(self):
        cursor = self.controller.conn.cursor()
        cursor.execute('SELECT flashcard_id, flashcard_name FROM flashcard')
        flashcards = cursor.fetchall()

        for flashcard_id, flashcard_name in flashcards:
            flashcard_button = tk.Button(self.centered_frame, text=flashcard_name, font=self.controller.custom_font, bg="#2196F3", fg="black", padx=20, pady=10, command=lambda fid=flashcard_id: self.open_flashcard_detail(fid))
            flashcard_button.pack(pady=10, fill='x', padx=20)

    def refresh_flashcards(self):
        # Clear current flashcards
        for widget in self.centered_frame.winfo_children():
            widget.destroy()
        
        # Reload flashcards
        self.load_flashcards()

    def open_flashcard_detail(self, flashcard_id):
        self.controller.current_flashcard_id = flashcard_id
        self.controller.show_frame("FlashcardDetailPage")

class FlashcardDetailPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")


        back_button = tk.Button(self, text="Back", font=controller.custom_font, bg="#FF5733", fg="black", command=lambda: controller.show_frame("StudyPage"))
        back_button.pack(anchor='nw', padx=10, pady=10)

        self.title_label = tk.Label(self, font=controller.custom_font, bg="white", fg="#333")
        self.title_label.pack(pady=20)

        self.question_label = tk.Label(self, font=controller.custom_font, bg="white", fg="#333")
        self.question_label.pack(pady=10)

        self.answer_entry = tk.Entry(self, font=controller.custom_font, width=30)
        self.answer_entry.pack(pady=10)

        image = Image.open(learn_button_file_path)  
        image = image.resize((30, 30), Image.LANCZOS)
        self.add_to_correct_img = ImageTk.PhotoImage(image)

        self.add_to_correct_button = tk.Button(self, image=self.add_to_correct_img, bg="white", bd=0, command=self.add_to_correct_answers)
        self.add_to_correct_button.pack(pady=10, padx=(10, 0), side=tk.RIGHT)

        self.feedback_label = tk.Label(self, font=controller.custom_font, bg="white", fg="#333")
        self.feedback_label.pack(pady=10)

        self.button_frame = tk.Frame(self, bg="white")
        self.button_frame.pack(pady=10)

        self.submit_button = tk.Button(self.button_frame, text="Submit Answer", font=controller.custom_font, bg="#4CAF50", fg="black", padx=20, pady=10, command=self.check_answer)
        self.submit_button.pack(side="left", padx=10)

        self.next_question_button = tk.Button(self.button_frame, text="Next Question", font=controller.custom_font, bg="#4CAF50", fg="black", padx=20, pady=10, command=self.load_next_question)
        self.next_question_button.pack(side="left", padx=10)

        self.questions = []
        self.current_question_index = -1
        self.current_question_id = None
        self.current_answer = None
        self.answered_questions = {}
        self.current_attempt = 0
    
    def load_questions(self):
        cursor = self.controller.conn.cursor()
        cursor.execute('''
        SELECT q.question_id, q.question_text, a.answer_text 
        FROM question q 
        JOIN correct_answer a ON q.question_id = a.question_id 
        WHERE q.flashcard_id = ?
        ''', (self.controller.current_flashcard_id,))
        self.questions = cursor.fetchall()
        self.current_question_index = -1
        self.load_next_question()

    def load_next_question(self):
        self.current_question_index += 1
        while self.current_question_index < len(self.questions):
            question_id, question_text, answer_text = self.questions[self.current_question_index]
            if self.answered_questions.get(question_id, 0) == 0:
                self.current_question_id = question_id
                self.current_answer = answer_text
                self.title_label.config(text=f"Flashcard Set: {self.controller.current_flashcard_id}")
                self.question_label.config(text=f"Question: {question_text}")
                self.answer_entry.delete(0, tk.END)
                self.feedback_label.config(text="")
                self.answer_entry.pack(pady=10)
                self.feedback_label.pack(pady=10)
                self.button_frame.pack(pady=10)
                self.submit_button.pack(side="left", padx=10)
                self.next_question_button.pack(side="left", padx=10)
                self.current_attempt = 0
                break
            else:
                self.current_question_index += 1
        else:
            self.question_label.config(text="No more questions.")
            self.answer_entry.pack_forget()
            self.submit_button.pack_forget()
            self.feedback_label.pack_forget()
            self.button_frame.pack_forget()

    def add_to_correct_answers(self):
        user_answer = str(self.answer_entry.get().strip())
        cursor = self.controller.conn.cursor()
        cursor.execute('DELETE FROM incorrect_answer WHERE question_id = ?', (self.current_question_id,))
        cursor.execute('INSERT INTO correct_answer (question_id, answer_text) VALUES (?, ?)', (self.current_question_id, user_answer))
        self.controller.conn.commit()
        self.answered_questions[self.current_question_id] = 1  # Mark question as answered
        self.feedback_label.config(text="Added to Correct Answers!", fg="green")

    def check_answer(self):    
        user_answer = str(self.answer_entry.get().strip())
        cursor = self.controller.conn.cursor()
        is_correct = is_correct_answer(user_answer, self.current_question_id, cursor)
        if is_correct == True:
            self.feedback_label.config(text="Correct!", fg="green")
        elif is_correct == False:
            self.feedback_label.config(text=f"Incorrect! The correct answer was: {self.current_answer}", fg="red")
            cursor.execute('INSERT INTO incorrect_answer (question_id, answer_text) VALUES (?, ?)', (self.current_question_id, user_answer))
            self.controller.conn.commit()
        else:
            self.feedback_label.config(text=f"Uncertain. The correct answer is: {self.current_answer}", fg="orange")
            cursor.execute('INSERT INTO incorrect_answer (question_id, answer_text) VALUES (?, ?)', (self.current_question_id, user_answer))
            self.controller.conn.commit()

        self.answered_questions[self.current_question_id] = 1
        self.current_attempt += 1

    def tkraise(self, aboveThis=None):
        self.load_questions()
        self.answered_questions = {}
        self.current_attempt = 0
        super().tkraise(aboveThis)

if __name__ == "__main__":
    app = FlashcardApp()
    app.mainloop()
