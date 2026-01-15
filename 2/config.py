# config.py

import os

# --- Основные настройки ---
CLASSIFIED_LANGUAGES = ["Russian", "German"]
INPUT_FORMAT = "Pdf"
IMPLEMENTED_METHODS = ["Short_Words", "Alphabetical", "Neural_Network"]

# --- Настройки для метода "Коротких слов" ---
# Максимальная длина слова, которое считается "коротким"
SHORT_WORD_MAX_LENGTH = 5
# Минимальная частота для включения лексемы в профиль (используется только при построении профиля)
MIN_WORD_FREQUENCY_THRESHOLD = 3
# "Температура" для сглаживания логарифмических вероятностей.
# Предотвращает получение абсолютных 1.0 и 0.0.
LOG_PROB_TEMPERATURE = 1000

# --- Настройки для Алфавитного метода ---
# Символы, характерные для русского языка
RUSSIAN_UNIQUE_CHARS = set('ёжцчшщъыьэюя')
# Символы, характерные для немецкого языка
GERMAN_UNIQUE_CHARS = set('äöüß')

# --- Настройки для Gemini API ---
# Используем стабильную модель. Можно поменять на 'gemini-1.5-flash-latest', если она доступна вам.
GEMINI_MODEL_NAME = 'gemini-2.0-flash'

DATA_FOLDER = "data"