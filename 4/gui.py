import tkinter as tk
from tkinter import ttk, messagebox, Menu, filedialog
from collections import Counter
from logic import Translator
from database import DatabaseHandler


class MainWindow:
    def __init__(self, root, translator: Translator, db_handler: DatabaseHandler):
        self.root = root
        self.translator = translator
        self.db_handler = db_handler

        self.root.title("OOP Translator: English -> German (Lab 10)")
        self.root.geometry("1100x750")

        self._setup_ui()
        self._setup_context_menu()

    def _setup_ui(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Блок ввода/вывода
        split_frame = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        split_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.input_area = self._create_text_area(split_frame, "Input (English)")
        self.output_area = self._create_text_area(split_frame, "Output (German)")

        # 2. Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="ПЕРЕВЕСТИ", command=self.on_translate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сохранить отчет", command=self.on_save).pack(side=tk.LEFT, padx=5)
        self.stats_label = ttk.Label(btn_frame, text="Готов к работе")
        self.stats_label.pack(side=tk.RIGHT, padx=10)

        # 3. Вкладки
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tree_view = self._create_stats_tab(self.notebook)
        self.syntax_text = self._create_syntax_tab(self.notebook)

        # 4. Блок добавления слов (ИСПРАВЛЕНО: Добавлен выбор рода)
        self._create_admin_panel(main_frame)

    def _create_text_area(self, parent, title):
        frame = ttk.Labelframe(parent, text=title)
        parent.add(frame)
        text_widget = tk.Text(frame, height=10, width=40, undo=True)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        return text_widget

    def _create_stats_tab(self, parent):
        frame = ttk.Frame(parent)
        parent.add(frame, text="Словарь и Грамматика")
        cols = ("Word", "Translation", "Freq", "POS", "Description")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill=tk.BOTH, expand=True)
        return tree

    def _create_syntax_tab(self, parent):
        frame = ttk.Frame(parent)
        parent.add(frame, text="Синтаксическое дерево")
        text_w = tk.Text(frame)
        text_w.pack(fill=tk.BOTH, expand=True)
        return text_w

    def _create_admin_panel(self, parent):
        # ИСПРАВЛЕННЫЙ МЕТОД
        frame = ttk.Labelframe(parent, text="Пополнение словаря (Add Word)", padding=5)
        frame.pack(fill=tk.X, pady=10)

        # English
        ttk.Label(frame, text="English:").pack(side=tk.LEFT)
        self.entry_en = ttk.Entry(frame, width=15)
        self.entry_en.pack(side=tk.LEFT, padx=5)

        # German
        ttk.Label(frame, text="German:").pack(side=tk.LEFT)
        self.entry_de = ttk.Entry(frame, width=15)
        self.entry_de.pack(side=tk.LEFT, padx=5)

        # Gender (Combobox)
        ttk.Label(frame, text="Gender:").pack(side=tk.LEFT)
        self.combo_gender = ttk.Combobox(frame, values=["", "m", "f", "n"], width=5, state="readonly")
        self.combo_gender.set("")  # По умолчанию пусто
        self.combo_gender.pack(side=tk.LEFT, padx=5)

        # Подсказка
        ttk.Label(frame, text="(m=der, f=die, n=das)", font=("Arial", 8), foreground="gray").pack(side=tk.LEFT, padx=2)

        # Кнопка
        ttk.Button(frame, text="Добавить", command=self.on_add_word).pack(side=tk.LEFT, padx=10)

    def _setup_context_menu(self):
        """Меню ПКМ для Copy/Paste"""
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Cut", command=lambda: self.root.focus_get().event_generate('<<Cut>>'))
        self.context_menu.add_command(label="Copy", command=lambda: self.root.focus_get().event_generate('<<Copy>>'))
        self.context_menu.add_command(label="Paste", command=lambda: self.root.focus_get().event_generate('<<Paste>>'))

        def show_menu(event):
            widget = event.widget
            # Добавляем Combobox в разрешенные виджеты
            if isinstance(widget, (tk.Text, ttk.Entry, tk.Entry, ttk.Combobox)):
                self.context_menu.tk_popup(event.x_root, event.y_root)

        # Привязываем ко всем нужным элементам, включая новый комбобокс
        widgets = [self.input_area, self.output_area, self.entry_en, self.entry_de, self.syntax_text, self.combo_gender]
        for widget in widgets:
            widget.bind("<Button-3>", show_menu)

    def on_translate(self):
        input_text = self.input_area.get("1.0", tk.END).strip()
        if not input_text:
            return

        translation, stats, doc = self.translator.process_text(input_text)

        self.output_area.delete("1.0", tk.END)
        self.output_area.insert("1.0", translation)

        self._update_stats_table(stats)
        self._update_syntax_tree(doc)

        self.stats_label.config(text=f"Обработано слов: {len(stats)}")

    def on_add_word(self):
        # ИСПРАВЛЕННЫЙ МЕТОД
        en = self.entry_en.get().strip()
        de = self.entry_de.get().strip()
        gender = self.combo_gender.get().strip()

        # Если Gender пустой, превращаем в None (для базы данных)
        if gender == "":
            gender = None

        if en and de:
            # Передаем 3 аргумента
            success = self.db_handler.add_word(en, de, gender)
            if success:
                msg = f"Added: {en} -> {de}"
                if gender:
                    msg += f" ({gender})"
                messagebox.showinfo("OK", msg)

                # Очистка полей
                self.entry_en.delete(0, tk.END)
                self.entry_de.delete(0, tk.END)
                self.combo_gender.set("")
            else:
                messagebox.showerror("Error", "Word already exists!")
        else:
            messagebox.showwarning("Warning", "Fields 'English' and 'German' are required.")

    def on_save(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("=== INPUT (ENGLISH) ===\n")
                f.write(self.input_area.get("1.0", tk.END).strip() + "\n\n")

                f.write("=== OUTPUT (GERMAN) ===\n")
                f.write(self.output_area.get("1.0", tk.END).strip() + "\n\n")

                f.write("=== STATISTICS ===\n")
                f.write(f"{'Word':<15} {'Trans':<15} {'Freq':<5} {'POS':<6} {'Desc'}\n")
                f.write("-" * 70 + "\n")

                for child in self.tree_view.get_children():
                    vals = self.tree_view.item(child)["values"]
                    f.write(
                        f"{str(vals[0]):<15} {str(vals[1]):<15} {str(vals[2]):<5} {str(vals[3]):<6} {str(vals[4])}\n")

            messagebox.showinfo("Success", "Файл успешно сохранен!")
        except Exception as e:
            messagebox.showerror("Error", f"Ошибка при сохранении: {e}")

    def _update_stats_table(self, data):
        for i in self.tree_view.get_children():
            self.tree_view.delete(i)

        counts = Counter([item['en'] for item in data])
        unique_processed = set()

        sorted_data = sorted(data, key=lambda x: counts[x['en']], reverse=True)

        for item in sorted_data:
            if item['en'] not in unique_processed:
                self.tree_view.insert("", tk.END, values=(
                    item['en'],
                    item['de'],
                    counts[item['en']],
                    item['pos'],
                    item['desc']
                ))
                unique_processed.add(item['en'])

    def _update_syntax_tree(self, doc):
        self.syntax_text.delete("1.0", tk.END)
        tree_str = ""
        for sent in doc.sents:
            tree_str += f"=== Sentence: {sent.text} ===\n"
            for token in sent:
                tree_str += f"{token.text:<12} --({token.dep_})--> {token.head.text}\n"
            tree_str += "\n"
        self.syntax_text.insert("1.0", tree_str)