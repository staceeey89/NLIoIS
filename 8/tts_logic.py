import pyttsx3
import threading


class TTSManager:
    """Класс, отвечающий за взаимодействие с движком синтеза речи (Model)"""

    @staticmethod
    def get_available_voices():
        """Получает список голосов. Создает временный движок, чтобы не блокировать основной поток."""
        try:
            temp_engine = pyttsx3.init()
            voices = temp_engine.getProperty('voices')
            voice_data = []
            for v in voices:
                # Определяем метку языка для удобства
                lang_tag = "[?]"
                if "DE" in v.id.upper() or "GERMAN" in v.name.upper():
                    lang_tag = "[DE]"
                elif "EN" in v.id.upper() or "ENGLISH" in v.name.upper():
                    lang_tag = "[EN]"
                elif "RU" in v.id.upper() or "RUSSIAN" in v.name.upper():
                    lang_tag = "[RU]"

                voice_data.append({
                    "id": v.id,
                    "name": v.name,
                    "display": f"{lang_tag} {v.name}"
                })
            del temp_engine
            return voice_data
        except Exception as e:
            print(f"Error loading voices: {e}")
            return []

    def speak_async(self, text, voice_id, rate, volume, on_complete=None):
        """Запускает синтез речи в отдельном потоке"""
        thread = threading.Thread(
            target=self._speak_worker,
            args=(text, voice_id, rate, volume, on_complete)
        )
        thread.start()

    def _speak_worker(self, text, voice_id, rate, volume, on_complete):
        """Рабочая функция потока. Инициализирует движок локально."""
        try:
            # Инициализация внутри потока критична для стабильности в Windows (COM-объекты)
            engine = pyttsx3.init()

            # Установка параметров
            if voice_id:
                engine.setProperty('voice', voice_id)
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)

            # Синтез
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
        finally:
            if on_complete:
                on_complete()