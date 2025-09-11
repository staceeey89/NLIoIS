from typing import List, Tuple, Dict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_tfidf_index(documents: List[str]) -> Tuple[TfidfVectorizer, np.ndarray]:
    vectorizer = TfidfVectorizer(stop_words='english', max_df=0.9, min_df=1)
    tfidf_matrix = vectorizer.fit_transform(documents)
    return vectorizer, tfidf_matrix


def rank_documents(query: str, vectorizer: TfidfVectorizer, tfidf_matrix: np.ndarray) -> np.ndarray:
    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, tfidf_matrix).flatten()
    return sims


def extract_present_query_terms(query: str, vectorizer: TfidfVectorizer, doc_index: int, top_k: int = 25) -> List[str]:
    """Return list of query terms that appear in the given document, per TF-IDF vocab."""
    analyzer = vectorizer.build_analyzer()
    query_terms = list(dict.fromkeys(analyzer(query)))
    vocab: Dict[str, int] = vectorizer.vocabulary_  # type: ignore[attr-defined]
    present: List[str] = []
    for term in query_terms:
        idx = vocab.get(term)
        if idx is None:
            continue
        # if document has non-zero weight for this term
        if tfidf_has_term(tfidf_matrix, doc_index, idx):
            present.append(term)
    return present[:top_k]


def tfidf_has_term(tfidf_matrix, doc_index: int, term_index: int) -> bool:
    row = tfidf_matrix[doc_index]
    if hasattr(row, 'tocoo'):
        row = row.tocoo()
    if row.nnz == 0:
        return False
    # Check if the term index exists in the row indices
    return term_index in set(row.indices)




