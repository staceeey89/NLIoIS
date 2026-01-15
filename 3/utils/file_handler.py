# utils/file_handler.py

import docx


def read_document(filepath):
    """
    Читает текст из файла в зависимости от его расширения.
    Поддерживает .txt и .docx.

    :param filepath: Путь к файлу.
    :return: Строка с текстом документа.
    """
    # Извлекаем расширение файла, приводя его к нижнему регистру
    extension = filepath.rsplit('.', 1)[-1].lower()

    if extension == "txt":
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Пробуем другую кодировку, если utf-8 не сработала
            with open(filepath, 'r', encoding='cp1251') as file:
                return file.read()

    elif extension == "docx":
        try:
            # Открываем .docx файл
            doc = docx.Document(filepath)
            # Собираем текст из всех параграфов документа
            full_text = [para.text for para in doc.paragraphs]
            return '\n'.join(full_text)
        except Exception as e:
            print(f"Ошибка при чтении .docx файла: {e}")
            return ""

    else:
        # Если формат не поддерживается, возвращаем пустую строку
        return ""