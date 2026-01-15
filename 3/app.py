import os
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename

from utils.file_handler import read_document

from core.summarizer import create_summary

# --- Конфигурация приложения ---
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'txt', 'docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.secret_key = 'super_secret_key'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Роуты ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не был отправлен', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('Файл не выбран', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                text = read_document(filepath)
                if not text:
                    flash('Файл пуст или не читается', 'error')
                    return redirect(request.url)

                lang = 'german' if any(c in 'äöüß' for c in text.lower()) else 'russian'

                # --- ВЫЗОВ ОСНОВНОЙ ЛОГИКИ ---
                # Теперь мы вызываем всего одну простую функцию
                summary_results = create_summary(text, language=lang)

                # --- Подготовка файла для скачивания ---
                summary_filename = f"summary_{filename}.txt"
                output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], summary_filename)
                with open(output_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"РЕЗУЛЬТАТЫ АНАЛИЗА ДЛЯ ФАЙЛА: {filename}\n\n")
                    f.write("--- КЛАССИЧЕСКИЙ РЕФЕРАТ ---\n\n")
                    f.write("\n".join(summary_results['classic_summary']))
                    f.write("\n\n--- КЛЮЧЕВЫЕ СЛОВА ---\n\n")
                    f.write(", ".join(summary_results['keywords']))

                results_to_render = {
                    'filename': filename,
                    'classic_summary': summary_results['classic_summary'],
                    'keywords': summary_results['keywords'],
                    'summary_filename': summary_filename
                }

                return render_template('index.html', results=results_to_render)

            except Exception as e:
                flash(f'Произошла ошибка при обработке: {e}', 'error')
                return redirect(request.url)

    return render_template('index.html')


@app.route('/download/<filename>')
def download_summary(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)


# --- Запуск ---
if __name__ == '__main__':
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    app.run(debug=True)