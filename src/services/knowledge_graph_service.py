from pyvis.network import Network
import logging
from itertools import combinations

logger = logging.getLogger(__name__)

class KnowledgeGraphService:
    def __init__(self):
        pass

    def create_knowledge_graph(self, ner_data):
        """Tworzy graf wiedzy na podstawie listy encji."""
        nodes_data = ner_data['all_canonical_entities']
        edges_data = ner_data['co_occurrences']
        entity_colors = {'PER': 'red', 'LOC': 'green', 'ORG': 'blue'}
        net = Network(
            height="750px",
            width="100%",
            notebook=True,
            cdn_resources="remote"
        )
       
        for entity_type, names_list in nodes_data.items():
            for name in names_list:
                net.add_node(name, color = entity_colors.get(entity_type))
        
        for names_list in edges_data:
            for i, j in combinations(names_list, 2):
                net.add_edge(i, j)
        
        net = net.generate_html()
        
        return net