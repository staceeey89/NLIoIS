import os

class Config:
    # API
    SERPER_API_KEY = os.environ.get('SERPER_API_KEY', '')
    SERPER_SEARCH_URL = 'https://google.serper.dev/search'

    # Data/cache
    DATA_DIR = os.environ.get('DATA_DIR', 'data')
    DB_PATH = os.path.join(DATA_DIR, 'documents.db')
    VECTORIZER_PATH = os.path.join(DATA_DIR, 'tfidf_vectorizer.joblib')
    TFIDF_MATRIX_PATH = os.path.join(DATA_DIR, 'tfidf_matrix.joblib')
    DOC_IDS_PATH = os.path.join(DATA_DIR, 'doc_ids.joblib')

    # Search defaults
    NUM_URLS_TO_SCRAPE = int(os.environ.get('NUM_URLS_TO_SCRAPE', '15'))
    USER_AGENT = os.environ.get('USER_AGENT', 'MySearchEngine/1.0')