import os
import requests
import json
import logging

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        

    def fetch_articles(self, lang = 'en', country = 'gb', max_articles = 10):
        """Pobiera artykuły z GNews API."""
        url = (f"https://gnews.io/api/v4/top-headlines?"
               f"category=general&lang={lang}&country={country}&max={max_articles}&apikey={self.api_key}")

        try:
            response = requests.get(url=url)
            response.raise_for_status()
            data = response.json()
            articles = data.get('articles', [])
            
            if not articles:
                logger.warning("Nie znaleziono żadnych artykułów.")

                return None
                
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed with status {response.status_code}: {response.text}")
            return None
        