import pyttsx3


class Speaker:
    def __init__(self):
        # Мы не сохраняем engine в self, чтобы создавать его "свежим" каждый раз
        pass

    def speak(self, text):
        """Озвучить текст"""
        if not text:
            return

        print(f"System: {text}")  # Печатаем в консоль

        try:
            # Инициализируем движок прямо перед речью
            engine = pyttsx3.init()

            # Настройки
            engine.setProperty('rate', 150)

            # Поиск немецкого голоса
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'de' in voice.id.lower() or 'german' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break

            # ОЗВУЧИВАНИЕ
            engine.say(text)
            engine.runAndWait()

            # Важно: останавливаем движок, чтобы освободить ресурсы
            engine.stop()

        except Exception as e:
            print(f"[ОШИБКА ЗВУКА]: {e}")