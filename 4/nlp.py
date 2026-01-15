import spacy


class NLPProcessor:
    def __init__(self, model="en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            raise RuntimeError(f"Модель {model} не найдена. Запустите: python -m spacy download {model}")

    def analyze(self, text):
        return self.nlp(text)

    @staticmethod
    def get_explanation(pos_tag):
        """Возвращает расшифровку тега части речи"""
        return spacy.explain(pos_tag)