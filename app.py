import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
load_dotenv()
from services.search_engine import SearchEngine
from services.live_search_service import perform_live_search
from config import Config
from services.query_store import (
    init_query_db,
    get_cached_results,
    save_results,
    increment_usage,
    get_popular_queries,
    find_similar_queries,
)


def create_app() -> Flask:

    app = Flask(__name__)
    app.config.from_object(Config)

    print("Инициализация сервиса подсказок...")
    suggestion_engine = SearchEngine()
    init_query_db()

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/search', methods=['POST'])
    def search():
        query = request.form.get('query', '').strip()
        if not query:
            return redirect(url_for('index'))

        top_n = request.form.get('top_n', type=int, default=15)
        page = request.form.get('page', type=int, default=1)
        prev_query = request.form.get('prev_query', type=str, default=None)

        # Сброс пагинации при новом запросе
        if prev_query is not None and prev_query != query:
            page = 1
        if not page or page < 1:
            page = 1

        cached = get_cached_results(query, page=page)
        if cached is not None:
            increment_usage(query, page=page)
            results = cached
        else:
            results, _ = perform_live_search(query=query, top_n=top_n, page=page)
            save_results(query, results, page=page)
        return render_template(
            'results.html',
            query=query,
            results=results,
            page=page
        )

    @app.route('/suggest', methods=['GET'])
    def suggest():
        q = request.args.get('q', '').strip()
        # Если пустая строка — вернуть популярные запросы из БД
        if not q:
            popular = get_popular_queries(limit=15)
            return jsonify({"popular": popular})

        # Если есть префикс — искать похожие запросы в БД
        similar = find_similar_queries(prefix=q, limit=15)
        if similar:
            return jsonify({"completions": similar})

        # Фолбэк на TF-IDF inline подсказку
        inline = suggestion_engine.suggest_terms(q)
        return jsonify(inline)

    @app.route('/health', methods=['GET'])
    def health():
        status = 'ok' if suggestion_engine.vectorizer is not None else 'degraded'
        return jsonify({'status': status, 'suggestion_index_loaded': status == 'ok'})

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))