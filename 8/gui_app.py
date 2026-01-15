import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tts_logic import TTSManager


class GermanTTSApp:
    """Класс графического интерфейса (View/Controller)"""

    def __init__(self, root):
        self.root = root
        self.root.title("Синтезатор речи (Вариант 7: Немецкий язык)")
        self.root.geometry("650x550")

        self.logic = TTSManager()

        # Переменные состояния
        self.rate_var = tk.IntVar(value=150)
        self.volume_var = tk.DoubleVar(value=1.0)
        self.selected_voice_id = tk.StringVar()
        self.is_speaking = False

        self._init_ui()
        self._load_voices()

    def _init_ui(self):
        # 1. Заголовок и ввод текста
        tk.Label(self.root, text="Текст сочинения (Немецкий язык):", font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))

        self.text_area = scrolledtext.ScrolledText(self.root, width=70, height=15, font=("Segoe UI", 11))
        self.text_area.pack(padx=10, pady=5)
        self.text_area.insert(tk.END,
                              "Die Leiden des jungen Werther ist ein Briefroman von Johann Wolfgang von Goethe.")

        # 2. Группировка настроек
        settings_frame = tk.LabelFrame(self.root, text="Параметры голоса")
        settings_frame.pack(fill="x", padx=15, pady=10)

        # Выбор голоса
        tk.Label(settings_frame, text="Диктор:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.voice_combo = ttk.Combobox(settings_frame, state="readonly", width=50)
        self.voice_combo.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        self.voice_combo.bind("<<ComboboxSelected>>", self._on_voice_change)

        # Скорость
        tk.Label(settings_frame, text="Темп:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Scale(settings_frame, from_=50, to=300, orient=tk.HORIZONTAL, variable=self.rate_var).grid(row=1, column=1,
                                                                                                      sticky="we",
                                                                                                      padx=5)

        # Громкость
        tk.Label(settings_frame, text="Громкость:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.Scale(settings_frame, from_=0.0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL,
                 variable=self.volume_var).grid(row=2, column=1, sticky="we", padx=5)

        # 3. Кнопки
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.btn_speak = tk.Button(btn_frame, text="🔊 Читать текст", bg="#4CAF50", fg="white", font=("Segoe UI", 11),
                                   command=self._start_reading)
        self.btn_speak.pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="Очистить", command=lambda: self.text_area.delete('1.0', tk.END)).pack(side=tk.LEFT,
                                                                                                         padx=10)

    def _load_voices(self):
        self.voices_data = self.logic.get_available_voices()
        display_values = [v["display"] for v in self.voices_data]
        self.voice_combo['values'] = display_values

        # Автовыбор немецкого
        for i, v in enumerate(self.voices_data):
            if "[DE]" in v["display"]:
                self.voice_combo.current(i)
                self.selected_voice_id.set(v["id"])
                return

        if display_values:
            self.voice_combo.current(0)
            self.selected_voice_id.set(self.voices_data[0]["id"])

    def _on_voice_change(self, event):
        idx = self.voice_combo.current()
        if idx >= 0:
            self.selected_voice_id.set(self.voices_data[idx]["id"])

    def _start_reading(self):
        if self.is_speaking:
            return  # Защита от двойного клика

        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Внимание", "Текстовое поле пустое.")
            return

        self.is_speaking = True
        self.btn_speak.config(state="disabled", text="⏳ Чтение...")

        # Вызов логики
        self.logic.speak_async(
            text=text,
            voice_id=self.selected_voice_id.get(),
            rate=self.rate_var.get(),
            volume=self.volume_var.get(),
            on_complete=self._on_reading_finished
        )

    def _on_reading_finished(self):
        """Callback, вызываемый по завершении речи (нужно вернуть в main thread)"""
        self.root.after(0, self._reset_button)

    def _reset_button(self):
        self.is_speaking = False
        self.btn_speak.config(state="normal", text="🔊 Читать текст")