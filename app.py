from flask import Flask, render_template, request
from fetcher import setup, fetch_articles, process_articles, create_knowledge

app = Flask(__name__)
API_KEY, ner_pipeline = setup()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template('index.html')
    else:
        articles = fetch_articles(API_KEY)
        print(f"Pobrano artykułów: {len(articles) if articles else 0}")
        if articles:
            wynik_ner = process_articles(articles, ner_pipeline)
            graph = create_knowledge(wynik_ner)
            html_str = graph.generate_html('knowledge_graph.html')
            return render_template('index.html', graf_html=html_str)
        return render_template('index.html', error="Nie udało się pobrać artykułów")

if __name__ == '__main__':
    app.run(debug=True)