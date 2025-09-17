# services/text_processor.py
import nltk
from nltk.corpus import stopwords
import pymorphy2
import re

# Загрузка необходимых данных NLTK (выполнить один раз)
# Этот блок теперь будет работать корректно
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading NLTK stopwords data...")
    nltk.download('stopwords')

morph = pymorphy2.MorphAnalyzer()
russian_stopwords = stopwords.words('russian')
# Добавим английские стоп-слова, на случай если попадутся англ. тексты
english_stopwords = stopwords.words('english')
# Объединим их для простоты
all_stopwords = set(russian_stopwords).union(set(english_stopwords))


def preprocess_text(text, lang='ru'): # lang больше не используется, но оставим для совместимости
    """
    Очищает и лемматизирует текст.
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r'[^а-яa-z\s]', '', text)

    tokens = text.split()
    processed_tokens = []

    for token in tokens:
        if token and token not in all_stopwords:
            # Для русского языка используем pymorphy2 для лемматизации
            lemma = morph.parse(token)[0].normal_form
            processed_tokens.append(lemma)

    return " ".join(processed_tokens)