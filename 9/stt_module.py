# stt_module.py
import speech_recognition as sr
import config


def listen_command():
    # 1. Создаем объект распознавания
    recognizer = sr.Recognizer()

    # === НАСТРОЙКИ ЧУВСТВИТЕЛЬНОСТИ (ЗДЕСЬ РЕШЕНИЕ ВАШЕЙ ПРОБЛЕМЫ) ===

    # Сколько секунд тишины считать концом фразы.
    # Было 0.8, ставим 1.5. Теперь можно делать паузы между словами.
    recognizer.pause_threshold = 1.5

    # Минимальная длина звука, чтобы считать его речью (отсекает короткие щелчки)
    recognizer.phrase_threshold = 0.3

    # ===================================================================

    with sr.Microphone() as source:
        print("\n[...] Kalibrierung (Пожалуйста, помолчите 1 сек)...")
        # Увеличим время калибровки шума до 1 секунды для точности
        recognizer.adjust_for_ambient_noise(source, duration=1.0)

        print(f"[O] Zuhören... (Я слушаю до 15 секунд...)")

        try:
            # phrase_time_limit=15: Теперь у вас есть 15 секунд на фразу (было 5)
            # timeout=5: Если вы молчите 5 секунд после запуска, система переспросит
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)

            # Распознавание
            command = recognizer.recognize_google(audio, language=config.LANGUAGE_CODE)
            print(f"User: {command}")
            return command.lower()

        except sr.WaitTimeoutError:
            # Если вы молчали в самом начале
            return None
        except sr.UnknownValueError:
            return "error_unknown"
        except sr.RequestError:
            return "error_net"