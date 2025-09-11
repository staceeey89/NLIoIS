import os


class Config:
    SERPER_API_KEY = os.environ.get('SERPER_API_KEY', '')
    SERPER_SEARCH_URL = 'https://google.serper.dev/search'

    # Data/cache
    DATA_DIR = os.environ.get('DATA_DIR', 'data')
    SQLITE_PATH = os.path.join(DATA_DIR, 'search.db')

    # Search defaults
    NUM_SEARCH_RESULTS = int(os.environ.get('NUM_SEARCH_RESULTS', '15'))
    USER_AGENT = os.environ.get('USER_AGENT', 'GrungeSearchBot/1.0 (+https://example.local)')




