import os
import logging
from typing import List, Dict
import requests

from flask import current_app


def search_serper(query: str, num_results: int) -> List[Dict]:
    """Query Serper API and return a list of {url, title} dicts."""
    api_key = current_app.config.get('SERPER_API_KEY') or os.environ.get('SERPER_API_KEY', '')
    if not api_key:
        logging.warning('SERPER_API_KEY not set; returning empty results.')
        return []

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json',
    }
    payload = {
        'q': query,
        'num': num_results,
        'page': 1,
        'autocorrect': True,
    }
    url = current_app.config.get('SERPER_SEARCH_URL', 'https://google.serper.dev/search')

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logging.exception('Serper API error: %s', exc)
        return []

    results: List[Dict] = []
    for item in data.get('organic', [])[:num_results]:
        link = item.get('link') or item.get('url')
        title = item.get('title') or ''
        if link:
            results.append({'url': link, 'title': title})
    return results




