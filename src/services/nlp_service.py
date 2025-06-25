from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        logger.info("Initializing NLP service...")
        self.ner_tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        self.ner_model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
        self.ner_pipeline = self._create_ner_pipeline()
        
        logger.info('Initializing sentiment service...')
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained("siebert/sentiment-roberta-large-english")
        self.sentiment_model = AutoModelForTokenClassification.from_pretrained("siebert/sentiment-roberta-large-english")
        self.sentiment_pipeline = self._create_sentiment_pipeline()


    def _create_ner_pipeline(self):

        return pipeline(
            'ner',
            model=self.ner_model,
            tokenizer=self.ner_tokenizer,
            aggregation_strategy="simple"
        )
    
    def create_sentiment_pipeline(self):
        return pipeline(
            'sentiment-analysis',
            model = self.sentiment_model,
            tokenizer=self.sentiment_tokenizer,
            
        )
 

    def process_articles_ner(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not articles:
            logger.warning("No articles provided for processing")
            return []

        results_ner = []
        for art in articles:
            try:
                title = art.get('title', '')
                content = art.get('content', '')
                
                if not title and not content:
                    logger.warning("Skipping article due to missing content")
                    continue
                    
                logger.info(f"Processing article: {title[:50]}...")
                text_to_analyze = f"{title}. {content}"
                ner_result = self.ner_pipeline(text_to_analyze)
                results_ner.append(ner_result)
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                continue
            
        return results_ner

    def process_articles_sentiment(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not articles:
            logger.warning("No articles provided for processing")
            return []
            
        results_sentiment = []
        for art in articles:
            try:
                title = art.get('title', '')
                content = art.get('content', '')
            
                if not title and not content:
                    logger.warning("Skipping article due to missing content")
                    continue
                    
                logger.info(f"Processing article: {title[:50]}...")
                text_to_analyze = f"{title}. {content}"
                sentiment_result = self.sentiment_pipeline(text_to_analyze)
                art_dict = {"title": title, "sentiment": sentiment_result[0].get('label'), "score": float(sentiment_result[0].get('score'))}
                results_sentiment.append(art_dict)
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                continue
        
        return results_sentiment
   