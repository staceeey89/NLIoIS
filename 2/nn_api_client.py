# nn_api_client.py

import os
import json
import re
import logging
from typing import Dict

import google.generativeai as genai
from config import GEMINI_MODEL_NAME


def recognize_language_nn(extracted_text: str) -> Dict[str, any]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("Переменная окружения GEMINI_API_KEY не установлена.")
        return {"result": "Error", "score": 0.0, "all_scores": {"Error": "GEMINI_API_KEY not set"}}

    if not extracted_text or not extracted_text.strip():
        return {"result": "Unknown", "score": 0.0, "all_scores": {}}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        text_snippet = extracted_text[:2000]

        prompt = f"""
        Проанализируй текст и определи его язык.
        Возможные языки: "Russian", "German", "Unknown".
        Твой ответ ДОЛЖЕН БЫТЬ ТОЛЬКО валидным JSON-объектом и ничем больше. Не добавляй никакого пояснительного текста или markdown.
        Структура JSON: {{ "language": "определенный_язык", "confidence": число_от_0.0_до_1.0 }}
        Текст: "{text_snippet}"
        """

        logging.debug(f"Отправка запроса в Gemini с моделью {GEMINI_MODEL_NAME}.")
        response = model.generate_content(prompt)
        raw_response_text = response.text
        logging.debug(f"ПОЛУЧЕН СЫРОЙ ОТВЕТ ОТ GEMINI: ->>>{raw_response_text}<<<--")

        try:
            json_match = re.search(r'\{.*\}', raw_response_text, re.DOTALL)
            if not json_match:
                raise json.JSONDecodeError("JSON объект не найден в ответе модели", raw_response_text, 0)

            json_string = json_match.group(0)
            data = json.loads(json_string)

            language = data.get("language", "Unknown")
            confidence = float(data.get("confidence", 0.5))

            all_scores = {}
            if language == "Russian":
                all_scores = {"Russian": confidence, "German": 1.0 - confidence}
            elif language == "German":
                all_scores = {"German": confidence, "Russian": 1.0 - confidence}
            else:
                all_scores = {"Russian": 0.5, "German": 0.5}

            logging.info(f"Gemini успешно определил язык: {language} с уверенностью {confidence}")
            return {"result": language, "score": confidence, "all_scores": all_scores}

        except (json.JSONDecodeError, TypeError) as e:
            logging.warning(f"Не удалось распарсить JSON от Gemini. Ошибка: {e}. Применяем аварийную логику.")
            answer = raw_response_text
            if "Russian" in answer:
                return {"result": "Russian", "score": 0.90, "all_scores": {"Russian": 0.90, "German": 0.10}}
            elif "German" in answer:
                return {"result": "German", "score": 0.90, "all_scores": {"German": 0.90, "Russian": 0.10}}
            else:
                return {"result": "Unknown", "score": 0.5, "all_scores": {"Russian": 0.5, "German": 0.5}}

    except Exception as e:
        logging.error(f"Критическая ошибка при вызове Gemini API: {e}")
        return {"result": "Error", "score": 0.0, "all_scores": {"Error": str(e)}}