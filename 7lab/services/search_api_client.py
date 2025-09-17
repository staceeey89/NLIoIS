import requests
import os

# Получите ваш Serper API Key и установите его как переменную окружения
# export SERPER_API_KEY="ВАШ_КЛЮЧ"
SERPER_API_KEY = os.getenv("76777b45b76d6961c15dcaa7f13804450c90e91b")

if not SERPER_API_KEY:
    raise ValueError("Serper API Key не установлен. Установите переменную окружения SERPER_API_KEY.")

def search_urls(query, num_results=10):
    """
    Выполняет поиск в Google через Serper API и возвращает список URL-адресов.
    """
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        "q": query,
        "num": num_results
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Вызовет исключение для ошибок HTTP
        data = response.json()

        urls = []
        if 'organic' in data:
            for item in data['organic']:
                urls.append(item.get('link'))
        return [url for url in urls if url] # Фильтруем пустые ссылки
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к Serper API: {e}")
        return []

if __name__ == '__main__':
    # Пример использования
    search_query = "Scrapy tutorial"
    found_urls = search_urls(search_query, num_results=5)
    print(f"Найденные URL по запросу '{search_query}':")
    for url in found_urls:
        print(url)