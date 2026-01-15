from database import DatabaseHandler
from nlp import NLPProcessor


class Translator:
    def __init__(self, db_handler: DatabaseHandler, nlp_processor: NLPProcessor):
        self.db = db_handler
        self.nlp = nlp_processor

    def process_text(self, text):
        doc = self.nlp.analyze(text)

        # Словарь для хранения "умных" переводов, которые мы вычислим правилами
        # Ключ: индекс токена, Значение: готовое немецкое слово
        overrides = {}

        # --- ЭТАП 1: Грамматический анализ и применение правил ---
        for token in doc:
            # 1. Получаем данные о текущем слове из БД
            db_data = self.db.get_word_data(token.text)
            de_word = db_data[0] if db_data else token.text
            gender = db_data[1] if db_data else None  # 'm', 'f', 'n'

            # Если это Существительное и мы знаем его род
            if token.pos_ == "NOUN" and gender:

                # Определяем Падеж (Case) по роли в предложении
                case = "nom"  # По умолчанию именительный
                if token.dep_ == "dobj":  # Прямое дополнение -> Винительный (Akkusativ)
                    case = "acc"

                # Ищем зависимые слова (артикли и прилагательные)
                for child in token.children:

                    # --- ПРАВИЛО 1: Артикли (The / A) ---
                    if child.text.lower() in ["the", "a"]:
                        article_trans = self._resolve_article(child.text.lower(), gender, case)
                        overrides[child.i] = article_trans

                    # --- ПРАВИЛО 2: Прилагательные (amod) ---
                    # Согласование окончания: beautiful portrait -> schönes Porträt
                    if child.dep_ == "amod":
                        # Получаем перевод самого прилагательного
                        adj_data = self.db.get_word_data(child.text)
                        adj_root = adj_data[0] if adj_data else child.text

                        # Вычисляем окончание
                        ending = self._resolve_adj_ending(gender, case, child.head)
                        overrides[child.i] = adj_root + ending

        # --- ЭТАП 2: Сборка финального текста ---
        translated_parts = []
        analysis_data = []

        for token in doc:
            # Если для токена есть вычисленный "умный" перевод, берем его
            if token.i in overrides:
                final_word = overrides[token.i]
                is_rule_based = True
            else:
                # Иначе обычный поиск в словаре
                res = self.db.get_word_data(token.text)
                final_word = res[0] if res else token.text
                is_rule_based = False

            translated_parts.append(final_word + token.whitespace_)

            # Статистика
            if not token.is_punct and not token.is_space:
                desc = self.nlp.get_explanation(token.pos_)
                if is_rule_based:
                    desc += " [Grammar Rule Applied]"

                analysis_data.append({
                    "en": token.text.lower(),
                    "de": final_word,
                    "pos": token.pos_,
                    "desc": desc
                })

        return "".join(translated_parts), analysis_data, doc

    def _resolve_article(self, eng_article, gender, case):
        """Выбирает правильный немецкий артикль"""
        # Таблица для "THE" (Definite)
        if eng_article == "the":
            if gender == 'm':
                return "den" if case == "acc" else "der"
            elif gender == 'f':
                return "die"
            elif gender == 'n':
                return "das"

        # Таблица для "A" (Indefinite)
        elif eng_article == "a":
            if gender == 'm':
                return "einen" if case == "acc" else "ein"
            elif gender == 'f':
                return "eine"
            elif gender == 'n':
                return "ein"

        return eng_article

    def _resolve_adj_ending(self, gender, case, noun_token):
        """
        Упрощенная логика окончаний прилагательных (смешанное склонение после 'a'/'ein').
        Для лабораторной реализуем самые частые случаи.
        """
        # Проверяем, есть ли перед существительным неопределенный артикль "a"
        has_indefinite = any(c.text.lower() == 'a' for c in noun_token.children)

        # Если есть "a" (ein/eine), используем Mixed Declension
        if has_indefinite:
            if gender == 'n' and case == 'nom': return "es"  # ein schönes (Bild)
            if gender == 'n' and case == 'acc': return "es"  # ein schönes (Bild)
            if gender == 'm' and case == 'nom': return "er"  # ein guter (Mann)
            if gender == 'm' and case == 'acc': return "en"  # einen guten (Mann)
            if gender == 'f': return "e"  # eine gute (Frau)

        # Если "the", то Weak Declension (чаще всего -e или -en)
        # Для простоты лабы, если нет "a", добавим дефолтные окончания
        else:
            if gender == 'm' and case == 'acc': return "en"  # den guten
            return "e"  # der gute, das gute

        return ""