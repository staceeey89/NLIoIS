import logging
from typing import Optional

import requests
import trafilatura
from flask import current_app


def fetch_clean_text(url: str) -> Optional[str]:
    """Fetch a URL and extract clean main content text using trafilatura."""
    try:
        headers = {'User-Agent': current_app.config.get('USER_AGENT', 'GrungeSearchBot/1.0')}
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as exc:
        logging.warning('Fetch failed for %s: %s', url, exc)
        return None

    try:
        downloaded = trafilatura.extract(resp.text, url=url, include_comments=False, include_tables=False)
        if not downloaded:
            return None
        return downloaded
    except Exception as exc:
        logging.warning('Trafilatura extract failed for %s: %s', url, exc)
        return None




