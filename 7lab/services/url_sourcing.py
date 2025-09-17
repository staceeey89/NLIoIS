# services/url_sourcing.py
import requests
from config import Config

def search_urls(query, num_results=10):
    """Выполняет поиск в Google через Serper API и возвращает список URL."""
    if not Config.SERPER_API_KEY:
        raise ValueError("Serper API Key не установлен. Проверьте .env файл и config.py.")

    headers = {'X-API-KEY': Config.SERPER_API_KEY, 'Content-Type': 'application/json'}
    payload = {"q": query, "num": num_results}

    try:
        response = requests.post(Config.SERPER_SEARCH_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        urls = [item.get('link') for item in data.get('organic', []) if item.get('link')]
        return urls
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к Serper API: {e}")
        return []