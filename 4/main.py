import tkinter as tk
from tkinter import messagebox
from database import DatabaseHandler
from nlp import NLPProcessor
from logic import Translator
from gui import MainWindow

if __name__ == "__main__":
    root = tk.Tk()

    # Внедрение зависимостей (Dependency Injection)
    # Мы создаем объекты здесь и передаем их внутрь других объектов
    try:
        db = DatabaseHandler()  # Слой данных
        nlp = NLPProcessor()  # Слой NLP
        logic = Translator(db, nlp)  # Слой логики связывает данные и NLP

        # Слой представления получает готовые инструменты
        app = MainWindow(root, logic, db)

        root.mainloop()

        # Закрываем соединение при выходе
        db.close()

    except Exception as e:
        messagebox.showerror("Critical Error", str(e))