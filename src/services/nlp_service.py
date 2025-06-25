from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        logger.info("Initializing NLP service...")
        self.tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        self.model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
        self.ner_pipeline = self._create_ner_pipeline()
    
    def _create_ner_pipeline(self):

        return pipeline(
            'ner',
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple"
        )
    
    def process_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not articles:
            logger.warning("No articles provided for processing")
            return []

        results = []

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
                results.append(ner_result)
                
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                continue
                
        return results