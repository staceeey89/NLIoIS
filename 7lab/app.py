import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
load_dotenv()
from services.search_engine import SearchEngine
from services.live_search_service import perform_live_search
from config import Config


def create_app() -> Flask:

    app = Flask(__name__)
    app.config.from_object(Config)

    print("Инициализация сервиса подсказок...")
    suggestion_engine = SearchEngine()

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/search', methods=['POST'])
    def search():
        query = request.form.get('query', '').strip()
        if not query:
            return redirect(url_for('index'))

        top_n = request.form.get('top_n', type=int, default=15)

        # --- ИЗМЕНЕНИЕ 1: Получаем только 2 значения, suggestions убраны ---
        results, _ = perform_live_search(query=query, top_n=top_n)

        # --- ИЗМЕНЕНИЕ 2: ВЫЗОВ ДЛЯ "DID YOU MEAN" ПОЛНОСТЬЮ УДАЛЕН ---

        # --- ИЗМЕНЕНИЕ 3: did_you_mean убран из вызова render_template ---
        return render_template(
            'results.html',
            query=query,
            results=results
        )

    @app.route('/suggest', methods=['GET'])
    def suggest():
        q = request.args.get('q', '').strip()
        suggestions = suggestion_engine.suggest_terms(q)
        return jsonify(suggestions)

    @app.route('/health', methods=['GET'])
    def health():
        status = 'ok' if suggestion_engine.vectorizer is not None else 'degraded'
        return jsonify({'status': status, 'suggestion_index_loaded': status == 'ok'})

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))