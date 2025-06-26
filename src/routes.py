from flask import Blueprint, render_template, request
import os

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template('index.html')
    
    # Initialize services only when needed
    from services.news_service import NewsService
    from services.nlp_service import NLPService
    from services.knowledge_graph_service import KnowledgeGraphService
    
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        return "Missing API key", 500
        
    try:
        # Initialize services
        news_service = NewsService(api_key)
        nlp_service = NLPService()
        kg_service = KnowledgeGraphService()
        
        # Process only on form submission
        articles = news_service.fetch_articles()
        if not articles:
            return "No articles found", 400
            
        ner_results = nlp_service.process_articles_ner(articles)
        sentiment_results = nlp_service.process_articles_sentiment(articles)
        sentiment_summary = nlp_service.create_sentiment_summary(sentiment_results)
        graph_html, _ = kg_service.create_knowledge_graph(ner_results)
        
        return render_template('index.html', graph_html=graph_html, sentiment_summary=sentiment_summary)
        
    except Exception as e:
        return f"An error occurred: {str(e)}", 500