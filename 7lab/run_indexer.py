# run_indexer.py
import os
import sqlite3
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from config import Config
from services.url_sourcing import search_urls
from services.scraper import scrape_urls
from services.text_processor import preprocess_text


def init_db():
    """Инициализирует базу данных SQLite."""
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE,
            title TEXT,
            raw_text TEXT,
            processed_text TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_document_to_db(url, title, raw_text, processed_text):
    """Сохраняет документ в базу данных."""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO documents (url, title, raw_text, processed_text)
            VALUES (?, ?, ?, ?)
        ''', (url, title, raw_text, processed_text))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Документ с URL '{url}' уже существует.")
    finally:
        conn.close()


def get_all_processed_texts():
    """Извлекает все обработанные тексты и их ID из базы данных."""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, processed_text FROM documents WHERE processed_text IS NOT NULL ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [(row[0], row[1]) for row in rows]


def main():
    """Главная функция для запуска индексации."""
    init_db()

    initial_queries = [
        "обработка естественного языка python",
        "как работает tf-idf",
        "векторное представление слов",
        "библиотека scikit-learn",
        "создание поисковой системы"
    ]

    print("--- Этап 1: Сбор URL ---")
    all_urls = []
    for query in initial_queries:
        print(f"Поиск по запросу: '{query}'")
        urls = search_urls(query, num_results=Config.NUM_URLS_TO_SCRAPE)
        all_urls.extend(urls)

    unique_urls = list(dict.fromkeys(all_urls))
    print(f"\nНайдено {len(unique_urls)} уникальных URL для скрапинга.")

    print("\n--- Этап 2: Скрапинг и обработка ---")
    scraped_data = scrape_urls(unique_urls)
    for doc in scraped_data:
        if doc['text']:
            processed_text = preprocess_text(doc['text'], lang='ru')
            save_document_to_db(doc['url'], doc['title'], doc['text'], processed_text)

    print("\n--- Этап 3: Построение TF-IDF индекса ---")
    docs_from_db = get_all_processed_texts()
    if not docs_from_db:
        print("Нет документов для индексации.")
        return

    doc_ids = [doc[0] for doc in docs_from_db]
    processed_texts = [doc[1] for doc in docs_from_db]

    print(f"Индексируем {len(processed_texts)} документов...")
    vectorizer = TfidfVectorizer(max_features=5000)  # Ограничим словарь для эффективности
    tfidf_matrix = vectorizer.fit_transform(processed_texts)

    joblib.dump(vectorizer, Config.VECTORIZER_PATH)
    joblib.dump(tfidf_matrix, Config.TFIDF_MATRIX_PATH)
    joblib.dump(doc_ids, Config.DOC_IDS_PATH)

    print(f"\nИндексация завершена. Модель сохранена в папку '{Config.DATA_DIR}'.")


if __name__ == '__main__':
    main()