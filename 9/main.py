# main.py
import sys
from tts_module import Speaker
from stt_module import listen_command
from logic import analyze_text

def main():
    # Инициализация голоса
    bot = Speaker()
    bot.speak("Willkommen! Das System ist bereit.")

    while True:
        try:
            # 1. Слушаем
            user_text = listen_command()

            # 2. Обработка ошибок слуха
            if user_text is None:
                continue
            if user_text == "error_unknown":
                bot.speak("Wie bitte? Ich habe das nicht verstanden.")
                continue
            if user_text == "error_net":
                bot.speak("Fehler mit der Internetverbindung.")
                continue

            # 3. Логика (получаем текст для озвучки)
            status, response_text = analyze_text(user_text)

            # 4. Озвучиваем ответ
            # Здесь бот скажет то, что вернула logic.py
            # (например: "Thema goethe. Johann Wolfgang...")
            bot.speak(response_text)

            # 5. Если статус выхода
            if status is None:
                break

        except KeyboardInterrupt:
            print("\nПрограмма остановлена вручную.")
            sys.exit()

if __name__ == "__main__":
    main()