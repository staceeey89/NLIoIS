import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv

from services.search import perform_search
from services.search import suggest_terms


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object('config.Config')

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/search', methods=['POST'])
    def search():
        query = request.form.get('query', '').strip()
        if not query:
            return redirect(url_for('index'))

        top_n = request.form.get('top_n', type=int, default=10)
        results, did_you_mean = perform_search(query=query, top_n=top_n)
        return render_template('results.html', query=query, results=results, did_you_mean=did_you_mean)

    @app.route('/suggest', methods=['GET'])
    def suggest():
        q = request.args.get('q', '').strip()
        suggestions = suggest_terms(q)
        return jsonify({
            'suggestions': suggestions[:10]
        })

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)




