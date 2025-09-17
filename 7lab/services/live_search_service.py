# services/live_search_service.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time
import re

from .url_sourcing import search_urls
from .scraper import scrape_urls
from .text_processor import preprocess_text
from config import Config


def perform_live_search(query, top_n=15):
    """
    Выполняет полный цикл поиска "на лету".
    """
    start_time = time.time()
    print(f"--- НАЧАТ ПОИСК 'НА ЛЕТУ' ДЛЯ ЗАПРОСА: '{query}' ---")

    print(f"[1] Поиск URL через Serper API...")
    found_urls = search_urls(query, num_results=Config.NUM_URLS_TO_SCRAPE)
    if not found_urls:
        return [], None
    print(f"   > Найдено URL: {len(found_urls)}")

    print(f"[2] Скрапинг {len(found_urls)} страниц...")
    scraped_data = scrape_urls(found_urls)
    documents = [doc for doc in scraped_data if doc.get('text')]
    if not documents:
        return [], None
    print(f"   > Успешно получено: {len(documents)} документов")

    print(f"[3] Предобработка текстов...")
    raw_texts = [doc['text'] for doc in documents]
    processed_texts = [preprocess_text(text) for text in raw_texts]
    print(f"   > Тексты обработаны.")

    print(f"[4] Построение временной TF-IDF матрицы...")
    processed_query = preprocess_text(query)

    vectorizer = TfidfVectorizer(max_features=2000)
    tfidf_matrix = vectorizer.fit_transform(processed_texts + [processed_query])

    doc_matrix = tfidf_matrix[:-1]
    query_vector = tfidf_matrix[-1]
    print(f"   > Матрица создана.")

    print(f"[5] Ранжирование результатов...")
    similarities = cosine_similarity(query_vector, doc_matrix).flatten()
    ranked_indices = similarities.argsort()[::-1]

    results = []
    original_query_words = set(query.lower().split())

    for i in ranked_indices:
        if similarities[i] == 0:
            continue

        doc = documents[i]
        found_words = [word for word in original_query_words if word in doc['text'].lower()]

        results.append({
            'score': similarities[i],
            'url': doc['url'],
            'title': doc['title'],
            'present_terms': list(set(found_words)),
            'rank': len(results) + 1
        })

        if len(results) >= top_n:
            break

    end_time = time.time()
    print(f"--- ПОИСК 'НА ЛЕТУ' ЗАВЕРШЕН ЗА {end_time - start_time:.2f} СЕКУНД ---")

    # Возвращаем только результаты и None для совместимости
    return results, None