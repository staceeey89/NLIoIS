# app.py

from flask import Flask, request, render_template, jsonify, send_file, send_from_directory
import io
import os
import time
import json
import glob
from datetime import datetime
from typing import Dict, Any, List
import logging
from dotenv import load_dotenv

load_dotenv()

from preprocessor import process_uploaded_pdf
from lang_model import recognize_language_classic
from nn_api_client import recognize_language_nn
from config import CLASSIFIED_LANGUAGES, IMPLEMENTED_METHODS, INPUT_FORMAT, DATA_FOLDER

app = Flask(__name__)

# Настройка логирования для Flask
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

test_collection_results: List[Dict[str, Any]] = []


@app.route('/', methods=['GET'])
def index():
    context = {
        "classified_languages": ', '.join(CLASSIFIED_LANGUAGES),
        "input_format": INPUT_FORMAT,
        "implemented_methods": ', '.join(IMPLEMENTED_METHODS),
        "data_folder": DATA_FOLDER,
        "total_documents_processed": len(test_collection_results),
        "results": test_collection_results
    }
    return render_template('index.html', **context)


@app.route('/data/<path:filename>')
def serve_file(filename):
    return send_from_directory(DATA_FOLDER, filename)


@app.route('/process_collection', methods=['POST'])
def process_collection_route():
    global test_collection_results
    test_collection_results = []

    pdf_files = glob.glob(os.path.join(DATA_FOLDER, "*.pdf"))

    if not pdf_files:
        return jsonify({"error": f"В папке '{DATA_FOLDER}' не найдено PDF-файлов."}), 404

    for file_path in pdf_files:
        filename = os.path.basename(file_path)

        try:
            with open(file_path, 'rb') as f:
                file_stream = io.BytesIO(f.read())
        except Exception as e:
            app.logger.error(f"Ошибка чтения файла {filename}: {e}")
            continue

        extracted_text, preprocessed_text = process_uploaded_pdf(file_stream)
        if not preprocessed_text:
            continue

        classic_results = recognize_language_classic(preprocessed_text)
        nn_result = recognize_language_nn(extracted_text)

        result = {
            "file_info": {"filename": filename},
            "results_by_method": {
                "Short_Words": classic_results.get("Short_Words"),
                "Alphabetical": classic_results.get("Alphabetical"),
                "Neural_Network_API": nn_result,
            }
        }
        test_collection_results.append(result)

    return jsonify(test_collection_results)


@app.route('/results/json', methods=['GET'])
def download_stats():
    data_to_save = {
        "report_date": datetime.now().isoformat(),
        "total_documents_processed": len(test_collection_results),
        "results": test_collection_results
    }
    json_string = json.dumps(data_to_save, indent=4, ensure_ascii=False)
    buffer = io.BytesIO(json_string.encode('utf-8'))
    buffer.seek(0)
    filename = f"lab31_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    return send_file(
        buffer,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )


if __name__ == '__main__':
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    if not os.path.exists("training_data"):
        os.makedirs("training_data")
    app.run(debug=True)