# lang_model.py

from collections import Counter
import re
from typing import Dict, Any
import math
import logging
from flask import current_app

# Импорты из модулей проекта
from config import (
    CLASSIFIED_LANGUAGES, SHORT_WORD_MAX_LENGTH, MIN_WORD_FREQUENCY_THRESHOLD,
    RUSSIAN_UNIQUE_CHARS, GERMAN_UNIQUE_CHARS, LOG_PROB_TEMPERATURE
)
from preprocessor import preprocess_text


def build_short_words_profile(filepath: str) -> Dict[str, float]:
    """
    Читает текстовый файл, анализирует его и строит профиль коротких слов.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        logging.error(f"Тренировочный файл не найден: {filepath}")
        return {}

    clean_text = preprocess_text(text)
    words = clean_text.split()
    short_words = [word for word in words if len(word) <= SHORT_WORD_MAX_LENGTH]

    if not short_words:
        logging.warning(f"В тренировочном файле {filepath} не найдено коротких слов.")
        return {}

    word_counts = Counter(short_words)
    total_short_words = len(short_words)
    profile = {word: count / total_short_words for word, count in word_counts.items()}
    return profile


# --- ОСНОВНАЯ ЛОГИКА: Строим профили при запуске модуля ---
logging.info("Построение языковых профилей на основе тренировочных данных...")
SHORT_WORDS_MODEL_PROFILES = {
    "Russian": build_short_words_profile('training_data/russian.txt'),
    "German": build_short_words_profile('training_data/german.txt')
}
if not SHORT_WORDS_MODEL_PROFILES["Russian"] or not SHORT_WORDS_MODEL_PROFILES["German"]:
    logging.critical(
        "Не удалось построить языковые профили. Проверьте наличие и содержимое файлов в папке training_data.")
else:
    logging.info("Языковые профили успешно построены.")

MIN_PROBABILITY = 1e-10


def get_word_frequencies(text: str) -> Counter:
    words = text.split()
    return Counter(words)


# --- Метод Коротких Слов (с температурным сглаживанием) ---
def calculate_short_word_probability(text: str) -> Dict[str, Any]:
    word_counts = get_word_frequencies(text)
    short_words = {w: c for w, c in word_counts.items() if len(w) <= SHORT_WORD_MAX_LENGTH}

    current_app.logger.debug(f"Метод коротких слов: Найдено {len(short_words)} уникальных коротких слов для анализа.")

    if not short_words:
        current_app.logger.warning("Метод коротких слов: в тексте не найдено коротких слов. Возвращаем 0.5.")
        return {"result": "Unknown", "score": 0.5, "all_scores": {"Russian": 0.5, "German": 0.5}}

    log_probs = {}
    for lang in CLASSIFIED_LANGUAGES:
        lang_profile = SHORT_WORDS_MODEL_PROFILES.get(lang, {})
        if not lang_profile:
            log_probs[lang] = -float('inf')
            continue

        lang_log_prob = 0.0
        for word, count in short_words.items():
            prob_word_in_lang = lang_profile.get(word, MIN_PROBABILITY)
            lang_log_prob += count * math.log(prob_word_in_lang)
        log_probs[lang] = lang_log_prob

    current_app.logger.debug(f"Метод коротких слов: Рассчитанные лог. вероятности: {log_probs}")

    log_ru = log_probs.get("Russian", -float('inf'))
    log_de = log_probs.get("German", -float('inf'))

    if log_ru == -float('inf') and log_de == -float('inf'):
        return {"result": "Unknown", "score": 0.5, "all_scores": {"Russian": 0.5, "German": 0.5}}

    # --- Применяем "температуру" для смягчения резких различий ---
    log_ru /= LOG_PROB_TEMPERATURE
    log_de /= LOG_PROB_TEMPERATURE

    max_log = max(log_ru, log_de)
    shifted_log_ru = log_ru - max_log
    shifted_log_de = log_de - max_log

    prob_ru = math.exp(shifted_log_ru)
    prob_de = math.exp(shifted_log_de)

    total_prob = prob_ru + prob_de

    if total_prob == 0:
        return {"result": "Unknown", "score": 0.5, "all_scores": {"Russian": 0.5, "German": 0.5}}

    confidence_ru = prob_ru / total_prob
    confidence_de = prob_de / total_prob

    all_scores = {"Russian": confidence_ru, "German": confidence_de}

    current_app.logger.debug(f"Итоговая уверенность (RU/DE): {confidence_ru:.4f} / {confidence_de:.4f}")

    if confidence_ru >= confidence_de:
        return {"result": "Russian", "score": confidence_ru, "all_scores": all_scores}
    else:
        return {"result": "German", "score": confidence_de, "all_scores": all_scores}


# --- Алфавитный Метод ---
def calculate_alphabetical_score(text: str) -> Dict[str, Any]:
    char_counts = Counter(c for c in text if c != ' ')

    score_ru = sum(char_counts.get(char, 0) for char in RUSSIAN_UNIQUE_CHARS)
    score_de = sum(char_counts.get(char, 0) for char in GERMAN_UNIQUE_CHARS)

    smoothing_alpha = 1
    score_ru += smoothing_alpha
    score_de += smoothing_alpha

    total_score = score_ru + score_de

    confidence_ru = score_ru / total_score
    confidence_de = score_de / total_score

    all_scores = {"Russian": confidence_ru, "German": confidence_de}

    if abs(confidence_ru - confidence_de) < 0.1:
        winner = "Unknown"
        winner_score = max(confidence_ru, confidence_de)
    elif confidence_ru > confidence_de:
        winner = "Russian"
        winner_score = confidence_ru
    else:
        winner = "German"
        winner_score = confidence_de

    return {"result": winner, "score": winner_score, "all_scores": all_scores}


def recognize_language_classic(preprocessed_text: str) -> Dict[str, Dict]:
    if not preprocessed_text:
        return {
            "Short_Words": {"result": "Error", "score": 0.0, "all_scores": {}},
            "Alphabetical": {"result": "Error", "score": 0.0, "all_scores": {}}
        }

    results = {
        "Short_Words": calculate_short_word_probability(preprocessed_text),
        "Alphabetical": calculate_alphabetical_score(preprocessed_text),
    }

    return results