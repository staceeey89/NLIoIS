import os
import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from text_processor import preprocess_text
from scraper import scrape_urls
from search_api_client import search_urls  # Если хотите индексировать с нуля
import sqlite3

# Пути для сохранения/загрузки данных
DATA_DIR = 'data'
DB_PATH = os.path.join(DATA_DIR, 'documents.db')
VECTORIZER_PATH = os.path.join(DATA_DIR, 'tfidf_vectorizer.joblib')
TFIDF_MATRIX_PATH = os.path.join(DATA_DIR, 'tfidf_matrix.joblib')

os.makedirs(DATA_DIR, exist_ok=True)


def init_db():
    """Инициализирует базу данных SQLite."""
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO documents (url, title, raw_text, processed_text)
            VALUES (?, ?, ?, ?)
        ''', (url, title, raw_text, processed_text))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"Документ с URL '{url}' уже существует.")
        return None
    finally:
        conn.close()


def get_all_processed_texts():
    """Извлекает все обработанные тексты и их ID из базы данных."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, processed_text FROM documents ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [(row[0], row[1]) for row in rows]  # (doc_id, processed_text)


def build_index(initial_queries=None, num_urls_per_query=5):
    """
    Строит TF-IDF индекс из собранных и обработанных документов.
    """
    init_db()
    print("Индексация запущена...")

    # 1. Сбор и обработка данных
    if initial_queries:
        all_urls = []
        for query in initial_queries:
            print(f"Поиск URL для '{query}'...")
            urls = search_urls(query, num_results=num_urls_per_query)
            all_urls.extend(urls)

        # Удаляем дубликаты, сохраняя порядок
        unique_urls = list(dict.fromkeys(all_urls))
        print(f"Найдено {len(unique_urls)} уникальных URL для скрапинга.")

        scraped_data = scrape_urls(unique_urls)

        for doc in scraped_data:
            if doc['text']:
                processed_text = preprocess_text(doc['text'], lang='ru')  # Предполагаем русский язык
                save_document_to_db(doc['url'], doc['title'], doc['text'], processed_text)

    # 2. Получение всех обработанных текстов из БД
    docs_from_db = get_all_processed_texts()
    doc_ids = [doc[0] for doc in docs_from_db]
    processed_texts = [doc[1] for doc in docs_from_db]

    if not processed_texts:
        print("Нет документов для индексации. Выполните сбор данных.")
        return

    # 3. Построение TF-IDF модели
    print(f"Построение TF-IDF векторайзера для {len(processed_texts)} документов...")
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(processed_texts)

    # 4. Сохранение модели
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(tfidf_matrix, TFIDF_MATRIX_PATH)
    # Дополнительно сохраним соответствие ID документов и строк в матрице
    joblib.dump(doc_ids, os.path.join(DATA_DIR, 'doc_ids.joblib'))

    print(f"Индексация завершена. Модель сохранена в {DATA_DIR}")


if __name__ == '__main__':
    # Пример использования:
    # Запустите этот скрипт, чтобы проиндексировать данные.
    # Он будет искать URL по этим запросам, скрапить их и строить индекс.
    initial_queries_to_index = [
        "индексация текстов",
        "tf-idf как работает",
        "лемматизация python"
    ]

    # Для первого запуска (или если хотите обновить индекс), передайте запросы
    build_index(initial_queries=initial_queries_to_index, num_urls_per_query=5)

    # Если индекс уже построен и вы хотите просто перестроить TF-IDF по существующим данным в БД
    # build_index()