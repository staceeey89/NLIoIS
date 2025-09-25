import joblib
import os

from config import Config


class SearchEngine:
    def __init__(self):
        self.vectorizer = None
        self.vocabulary = None
        self._load_index()

    def _load_index(self):
        """Загружает TF-IDF векторизатор для подсказок."""
        print("Попытка загрузки индекса для подсказок...")
        if not os.path.exists(Config.VECTORIZER_PATH):
            print("ВНИМАНИЕ: Векторизатор не найден. Подсказки не будут работать.")
            print(f"Ожидаемый файл: {Config.VECTORIZER_PATH}")
            print("Пожалуйста, запустите 'python run_indexer.py' для создания индекса.")
            return

        self.vectorizer = joblib.load(Config.VECTORIZER_PATH)
        self.vocabulary = self.vectorizer.get_feature_names_out()

        print("Индекс для подсказок успешно загружен.")

    def perform_search(self, query, top_n=10):
        """
        В этой архитектуре этот метод не используется.
        Возвращает пустые значения для совместимости.
        """
        return [], None

    def suggest_terms(self, query_text):
        """
        Предлагает inline-дополнение для последнего слова в запросе.
        """
        if self.vocabulary is None or self.vocabulary.size == 0 or not query_text:
            return {}

        query_text = query_text.lower()
        words = query_text.split()
        last_word = words[-1]

        if not last_word:
            return {}

        for term in self.vocabulary:
            if term.startswith(last_word) and term != last_word:
                base = " ".join(words[:-1])
                full_suggestion = (base + " " + term).strip()
                return {"base": query_text, "suggestion": full_suggestion}

        return {}