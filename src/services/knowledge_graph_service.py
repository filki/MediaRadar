from pyvis.network import Network
import logging
from itertools import combinations
import networkx as nx
logger = logging.getLogger(__name__)

class KnowledgeGraphService:
    def __init__(self):
        pass
        
    def create_knowledge_graph(self, ner_data):
        """Tworzy graf wiedzy na podstawie listy encji."""
        nodes_data = ner_data['all_canonical_entities']
        edges_data = ner_data['co_occurrences']
        entity_colors = {'PER': 'red', 'LOC': 'green', 'ORG': 'blue'}
        
      
        computational_graph = nx.Graph()
        
    
        for names_list in edges_data:
            for i, j in combinations(names_list, 2):
                if computational_graph.has_edge(i, j):
                    
                    computational_graph.edges[i, j]['weight'] += 1
                else:
                  
                    computational_graph.add_edge(i, j, weight=1)
        
     
        net = Network(
            height="750px",
            width="100%",
            notebook=True,
            cdn_resources="remote"
        )
        
        print(computational_graph.edges(data=True))
        net.from_nx(computational_graph)
        
       
        for node in net.nodes:
            entity_name = node['id']
            for entity_type, names_list in nodes_data.items():
                if entity_name in names_list:
                    node['color'] = entity_colors.get(entity_type)
                    break

        html_content = net.generate_html()
        
        return html_content, computational_graph