# services/scraper.py
import requests
from trafilatura import extract
import time
from config import Config # Добавим импорт конфига для User-Agent

def fetch_and_extract(url):
    """
    Загружает веб-страницу и извлекает основной текст с помощью trafilatura.
    Возвращает кортеж (URL, заголовок, текст) или (URL, None, None) в случае ошибки.
    """
    try:
        headers = {'User-Agent': Config.USER_AGENT} # Используем User-Agent из конфига
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        downloaded = response.text
        # Используем json-вывод, он более надежный для извлечения заголовков
        import json
        json_output = extract(downloaded, output_format='json', include_links=False, include_comments=False)

        if json_output:
            data = json.loads(json_output)
            return url, data.get('title'), data.get('text')
        else:
            print(f"Не удалось извлечь контент с {url}")
            return url, None, None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке или извлечении контента с {url}: {e}")
        return url, None, None
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON для {url}: {e}")
        return url, None, None


def scrape_urls(urls):
    """
    Скрапит список URL-адресов и возвращает список словарей.
    """
    scraped_data = []
    for url in urls:
        print(f"Скрапинг: {url}")
        url, title, text = fetch_and_extract(url)
        if text and title: # Добавляем только если есть и текст, и заголовок
            scraped_data.append({'url': url, 'title': title, 'text': text})
        time.sleep(1) # Задержка, чтобы не нагружать сайты
    return scraped_data