from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification,AutoModelForSequenceClassification
from typing import List, Dict, Any
import logging
from thefuzz import fuzz
logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        logger.info("Initializing NLP service...")
        self.ner_tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        self.ner_model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
        self.ner_pipeline = self._create_ner_pipeline()
        
        logger.info('Initializing sentiment service...')
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained("siebert/sentiment-roberta-large-english")
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained("siebert/sentiment-roberta-large-english")
        self.sentiment_pipeline = self._create_sentiment_pipeline()


    def _create_ner_pipeline(self):

        return pipeline(
            'ner',
            model=self.ner_model,
            tokenizer=self.ner_tokenizer,
            aggregation_strategy="simple"
        )
    
    def _create_sentiment_pipeline(self):
        return pipeline(
            'sentiment-analysis',
            model = self.sentiment_model,
            tokenizer=self.sentiment_tokenizer,
            
        )
 

    def process_articles_ner(self, articles):
        if not articles:
            logger.warning("No articles provided for processing")
            return {}

        # 1. Przetwarzaj każdy artykuł i przechowuj jego wyniki NER
        article_ner_results = []
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
                article_ner_results.append(ner_result)
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                continue

        # 2. Spłaszcz wszystkie encje i zbuduj mapę nazw kanonicznych
        all_entities_flat = [entity for article_res in article_ner_results for entity in article_res]
        all_raw_names = [entity['word'] for entity in all_entities_flat]
        canonical_map = self._build_canonical_mapping(all_raw_names)

        # 3. Utwórz listę współwystępujących encji kanonicznych dla każdego artykułu
        co_occurrences = []
        for article_res in article_ner_results:
            # Użyj seta, aby uzyskać unikalne nazwy kanoniczne na artykuł
            canonical_names_in_article = {canonical_map.get(entity['word']) for entity in article_res if canonical_map.get(entity['word']) is not None and entity.get('entity_group') in ['PER', 'LOC', 'ORG']}
            if len(canonical_names_in_article) > 1:
                co_occurrences.append(list(canonical_names_in_article))

        # 4. Utwórz ostateczny słownik wszystkich unikalnych encji kanonicznych, pogrupowanych według typu
        all_canonical_entities = {'PER': set(), 'LOC': set(), 'ORG': set()}
        for entity in all_entities_flat:
            canonical_name = canonical_map.get(entity['word'])
            entity_type = entity.get('entity_group')
            if canonical_name and entity_type in all_canonical_entities:
                all_canonical_entities[entity_type].add(canonical_name)
        
        final_entities_by_type = {k: list(v) for k, v in all_canonical_entities.items()}

        # 5. Zwróć ostateczną strukturę
        return {
            'all_canonical_entities': final_entities_by_type,
            'co_occurrences': co_occurrences
        }
       
    def _build_canonical_mapping(self, all_raw_unique_names):
        canonical_mapping = {}
        canonical_names = self._deduplicate_names(all_raw_unique_names)
        for raw_name in all_raw_unique_names:
            for foo in canonical_names:
               if fuzz.ratio(raw_name, foo) > 95:
                    canonical_mapping[raw_name] = foo
        for raw_name in all_raw_unique_names:
            for foo in canonical_names:
               if fuzz.ratio(raw_name, foo) > 95:
                    canonical_mapping[raw_name] = foo
                    break
        return canonical_mapping

    def _extract_raw_entities_by_type(self, ner_results):
        ent_dict = {'PER':[], 'LOC':[], 'ORG':[]}
        for ent in ner_results:
            for grouped_entities in ent:
                if grouped_entities['entity_group'] == 'PER':
                    ent_dict['PER'].append(grouped_entities['word'])
                elif grouped_entities['entity_group'] == 'LOC':
                    ent_dict['LOC'].append(grouped_entities['word'])
                else:
                    ent_dict['ORG'].append(grouped_entities['word'])
        return ent_dict

    def _deduplicate_names(self, names):
        final_dedup = []
        naive_dedup = list(set(names))
        for ent in naive_dedup:
            found_match = False
            for i in final_dedup:
                if fuzz.ratio(ent, i) > 95:
                    found_match = True
                    break
            if not found_match:
                final_dedup.append(ent)
        return final_dedup
        
            
    def process_articles_sentiment(self, articles) :
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
    
    
    def create_sentiment_summary(self, results_sentiment:list):
        total_articles = len(results_sentiment)
        pos_art = sum(1 for art in results_sentiment if art['sentiment'] == 'POSITIVE')
        neg_art = sum(1 for art in results_sentiment if art['sentiment'] == 'NEGATIVE')
        perct_pos = pos_art/total_articles
        perct_neg = neg_art/total_articles
        summary = {"Positive %" : perct_pos, "Negative %" : perct_neg}
        return summary
