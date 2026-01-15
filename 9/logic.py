# logic.py
import wikipedia
import config

# Настраиваем язык Википедии при запуске модуля
wikipedia.set_lang(config.WIKI_LANGUAGE)


def clean_command(command):
    """
    Удаляет вводные слова, чтобы оставить только тему поиска.
    Пример: "Erzähl mir über Goethe" -> "Goethe"
    """
    # Список фраз, которые надо вырезать
    prefixes = [
        "erzähl mir über", "erzähl mir von", "erzähl mir etwas über",  # Расскажи о...
        "wer ist", "was ist", "wer war",  # Кто такой / Что такое...
        "suche nach", "finde",  # Найди...
        "thema", "info", "information"  # Тема...
    ]

    cleaned = command
    for prefix in prefixes:
        # Если фраза начинается с префикса, удаляем его
        if cleaned.startswith(prefix):
            cleaned = cleaned.replace(prefix, "").strip()

    return cleaned


def get_wiki_summary(term):
    """Делает запрос в Википедию"""
    try:
        # auto_suggest=False отключает автоисправление, чтобы искать точно то, что сказал пользователь
        summary = wikipedia.summary(term, sentences=config.WIKI_SENTENCES, auto_suggest=True)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        # Если найдено слишком много значений (например, "Мюллер")
        options = ", ".join(e.options[:3])  # Берем первые 3 варианта
        return f"Das Wort ist mehrdeutig. Meinten Sie: {options}?"
    except wikipedia.exceptions.PageError:
        # Если страница не найдена
        return None
    except Exception as e:
        return "Fehler bei der Verbindung zu Wikipedia."


def analyze_text(command):
    """
    Основная логика:
    1. Проверяет на выход.
    2. Выделяет тему.
    3. Ищет в Википедии.
    """

    # 1. Проверка на команду выхода
    if "ende" in command or "stop" in command or "tschüss" in command:
        return None, "Auf Wiedersehen!"

    # 2. Выделение темы поиска
    # Если пользователь сказал просто "Goethe", search_term будет "goethe"
    # Если "Was ist Faust", search_term будет "faust"
    search_term = clean_command(command)

    # Если после чистки ничего не осталось (пользователь сказал только "Erzähl mir")
    if not search_term or len(search_term) < 2:
        return "ok", "Ich habe kein Thema verstanden. Bitte nennen Sie einen Namen oder Buchtitel."

    # 3. Поиск в Википедии
    # Возвращаем промежуточный ответ, чтобы пользователь знал, что процесс идет (опционально)
    # Но так как наша архитектура синхронная, просто возвращаем результат.

    result = get_wiki_summary(search_term)

    if result:
        # Формируем красивый ответ
        response_text = f"Hier ist Information aus Wikipedia über {search_term}. {result}"
        return "ok", response_text
    else:
        return "ok", f"Entschuldigung, ich konnte auf Wikipedia nichts über {search_term} finden."