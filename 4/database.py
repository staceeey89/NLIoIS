import sqlite3


class DatabaseHandler:
    def __init__(self, db_name="dictionary_en_de.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        # Удаляем старую таблицу для пересоздания с новой структурой (для лабы проще всего)
        # В реальном проекте нужна миграция
        try:
            self.cursor.execute("SELECT gender FROM words LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("DROP TABLE IF EXISTS words")

        self._create_table()
        self._seed_data()

    def _create_table(self):
        # Добавили поле gender: 'm' (masc), 'f' (fem), 'n' (neut), или NULL
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                en_word TEXT UNIQUE,
                de_word TEXT,
                gender TEXT 
            )
        """)
        self.conn.commit()

    def _seed_data(self):
        # Формат: (English, German, Gender)
        initial_data = [
            ("the", "der/die/das", None), ("a", "ein", None), ("is", "ist", None),
            # Медицина (m=der, f=die, n=das)
            ("doctor", "Arzt", "m"),
            ("surgeon", "Chirurg", "m"),
            ("patient", "Patient", "m"),
            ("nurse", "Krankenschwester", "f"),
            ("treats", "behandelt", None),
            ("examines", "untersucht", None),
            ("hospital", "Krankenhaus", "n"),
            ("medicine", "Medizin", "f"),
            # Искусство
            ("artist", "Künstler", "m"),
            ("paints", "malt", None),
            ("canvas", "Leinwand", "f"),
            ("portrait", "Porträt", "n"),
            ("beautiful", "schön", None),
            ("colors", "Farben", "f"),
            ("effective", "wirksam", None)
        ]

        for item in initial_data:
            en, de, gender = item
            try:
                self.cursor.execute(
                    "INSERT INTO words (en_word, de_word, gender) VALUES (?, ?, ?)",
                    (en, de, gender)
                )
            except sqlite3.IntegrityError:
                pass
        self.conn.commit()

    def get_word_data(self, word: str):
        """Возвращает кортеж (translation, gender)"""
        self.cursor.execute("SELECT de_word, gender FROM words WHERE en_word=?", (word.lower(),))
        return self.cursor.fetchone()

    def add_word(self, en_word: str, de_word: str, gender: str = None) -> bool:
        try:
            self.cursor.execute(
                "INSERT INTO words (en_word, de_word, gender) VALUES (?, ?, ?)",
                (en_word.lower(), de_word, gender)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def close(self):
        self.conn.close()