from typing import List, Tuple, Dict

from .serper import search_serper
from .scraper import fetch_clean_text
from .indexer import build_tfidf_index, rank_documents, extract_present_query_terms


def perform_search(query: str, top_n: int = 10) -> Tuple[List[Dict], List[str]]:
    # 1) Find candidate URLs
    candidates = search_serper(query, num_results=top_n * 2)
    if not candidates:
        return [], []

    # 2) Scrape and collect texts
    texts: List[str] = []
    kept: List[Dict] = []
    for item in candidates:
        text = fetch_clean_text(item['url'])
        if not text:
            continue
        texts.append(text)
        kept.append(item)

    if not texts:
        return [], []

    # 3) Build TF-IDF and rank
    vectorizer, tfidf_matrix = build_tfidf_index(texts)
    sims = rank_documents(query, vectorizer, tfidf_matrix)

    # 4) Sort and prepare results
    sorted_indices = sims.argsort()[::-1][:top_n]
    results: List[Dict] = []
    for rank, idx in enumerate(sorted_indices, start=1):
        meta = kept[idx]
        present_terms = extract_present_query_terms(query, vectorizer, idx)
        results.append({
            'rank': rank,
            'url': meta['url'],
            'title': meta.get('title') or meta['url'],
            'score': float(sims[idx]),
            'present_terms': present_terms,
        })

    # 5) Suggestions (simple): top tokens from query back (placeholder for AI UI)
    did_you_mean = []
    return results, did_you_mean


def suggest_terms(prefix: str) -> List[str]:
    # Placeholder autocomplete: echo back prefix variations
    prefix = (prefix or '').strip()
    if not prefix:
        return []
    return [prefix, prefix + ' news', prefix + ' tutorial', prefix + ' wiki']




