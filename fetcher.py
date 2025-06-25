import os
import requests
import json
from dotenv import load_dotenv
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from itertools import combinations
from pyvis.network import Network

# Initialize the NER model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")


def setup():
    """Wczytuje konfigurację i tworzy pipeline NLP."""
    load_dotenv()
    api_key = os.getenv("GNEWS_API_KEY")
    
    if not api_key:
        raise ValueError("Nie znaleziono klucza GNEWS_API_KEY.")
    
    print("Inicjalizuję pipeline NER... (to może chwilę potrwać)")
    ner_pipeline = pipeline(
        'ner',
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple"
    )
    return api_key, ner_pipeline


def fetch_articles(api_key, lang='en', country='gb', max_articles=10):
    """Pobiera artykuły z GNews API."""
    url = (f"https://gnews.io/api/v4/top-headlines?"
           f"category=general&lang={lang}&country={country}&max={max_articles}&apikey={api_key}")
    
    try:
        response = requests.get(url=url)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            print("Nie znaleziono żadnych artykułów.")
            return None
            
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Wystąpił błąd podczas komunikacji z API: {e}")
        return None


def process_articles(articles, ner_pipeline):
    """
    Przetwarza listę artykułów, wyciągając encje za pomocą modelu NER.
    Jest odporna na brakujące klucze 'title' lub 'content' w artykułach.
    """
    if not articles:
        return []

    results = []

    for art in articles:
        try:
            title = art.get('title', '')
            content = art.get('content', '')
            
            if not title and not content:
                print("\n[OSTRZEŻENIE] Pomijam artykuł z powodu braku treści.")
                continue
                
            print(f"\nAnalizuję artykuł: {title[:50]}...")
            text_to_analyze = f"{title}. {content}"
            ner_result = ner_pipeline(text_to_analyze)
            results.append(ner_result)
            
        except Exception as e:
            print(f"\n[OSTRZEŻENIE] Błąd podczas przetwarzania artykułu: {e}")
            continue
            
    return results


def create_knowledge_graph_lists(ner_result):
    """Sortuje encje z wyniku NER do osobnych list."""
    if not ner_result:
        return {"osoby": [], "miejsca": [], "organizacje": []}

    osoby = []
    miejsca = []
    organizacje = []

    for entity in ner_result:
        # Przywracamy logikę dopasowania do wyników z modelu BERT
        match entity:
            case {'entity_group': 'PER', 'word': word}:
                osoby.append(word)
            case {'entity_group': 'LOC', 'word': word}:
                miejsca.append(word)
            case {'entity_group': 'ORG', 'word': word}:
                organizacje.append(word)

    return {"osoby": osoby, "miejsca": miejsca, "organizacje": organizacje}


def create_knowledge(knowledge_graph_list: list):
    """Tworzy graf wiedzy na podstawie listy encji."""
    net = Network(
        height="750px",
        width="100%",
        notebook=True,
        cdn_resources="remote"
    )
    
    # Zbierz wszystkie encje (z duplikatami)
    wszystkie_encje_z_duplikatami = []
    for ent_list in knowledge_graph_list:
        for ent in ent_list:
            wszystkie_encje_z_duplikatami.append(ent['word'])
    
    # Utwórz węzły dla unikalnych encji
    unikalne_encje = set(wszystkie_encje_z_duplikatami)
    for ent in unikalne_encje:
        net.add_node(ent)
    
    # Dodaj krawędzie między encjami występującymi w tym samym artykule
    for ent_list in knowledge_graph_list:
        nazwy_w_artykule = [ent['word'] for ent in ent_list]
        for i, j in combinations(nazwy_w_artykule, 2):
            net.add_edge(i, j)
    
    return net