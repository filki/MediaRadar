from pyvis.network import Network
import logging
from itertools import combinations

logger = logging.getLogger(__name__)

class KnowledgeGraphService:
    def __init__(self):
        pass
    
    def create_knowledge_graph_lists(self, ner_result):
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

    def create_knowledge(self, knowledge_graph_list: list):
        """Tworzy graf wiedzy na podstawie listy encji."""
        net = Network(
            height="750px",
            width="100%",
            notebook=False,
            cdn_resources="remote"
        )
        
        # Zbierz wszystkie encje (z duplikatami)
        wszystkie_encje = []
        for ent_list in knowledge_graph_list:
            for ent in ent_list:
                wszystkie_encje.append(ent['word'])
        
        # Utwórz węzły dla unikalnych encji
        for ent in set(wszystkie_encje):
            net.add_node(ent, title=ent)
        
        # Dodaj krawędzie między encjami występującymi w tym samym artykule
        for ent_list in knowledge_graph_list:
            entities = [ent['word'] for ent in ent_list]
            for i, j in combinations(entities, 2):
                net.add_edge(i, j)
        
        # Wygeneruj i zwróć HTML
        return net.generate_html(name='graph.html', local=True, notebook=False)