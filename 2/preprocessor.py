# preprocessor.py

import io
from pypdf import PdfReader
import re
from typing import Optional, Tuple


def extract_text_from_pdf(pdf_file: io.BytesIO) -> Optional[str]:
    """
    Извлекает текст из объекта-файла PDF.
    """
    try:
        reader = PdfReader(pdf_file)
        full_text = []
        for page in reader.pages:
            full_text.append(page.extract_text() or "")

        return "\n".join(full_text)
    except Exception as e:
        print(f"Ошибка при извлечении текста из PDF: {e}")
        return None


def preprocess_text(text: str) -> str:
    """
    Выполняет базовую предобработку текста.
    """
    text = text.lower()
    text = re.sub(r'[^a-zа-яäöüß\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def process_uploaded_pdf(pdf_file: io.BytesIO) -> Tuple[Optional[str], Optional[str]]:
    """
    Полный цикл обработки загруженного PDF.
    """
    extracted_text = extract_text_from_pdf(pdf_file)
    if extracted_text:
        preprocessed_text = preprocess_text(extracted_text)
        return extracted_text, preprocessed_text
    return None, None