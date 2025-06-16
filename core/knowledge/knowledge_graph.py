import networkx as nx
from typing import Dict, List, Any, Optional, Union, Tuple

class KnowledgeGraph:
    """
    Graph representation of database schema relationships.
    Uses NetworkX for graph operations.
    """
    
    def __init__(self):
        """Initialize empty knowledge graph"""
        self.graph = nx.DiGraph()
        
    def add_table(
        self, 
        table_name: str, 
        attributes: Dict[str, Any] = {}
    ):
        """Add a table node to the graph"""
        node_id = f"table:{table_name}"
        self.graph.add_node(
            node_id,
            type="table",
            name=table_name,
            **attributes
        )
        return node_id
        
    def add_column(
        self, 
        table_name: str, 
        column_name: str,
        attributes: Dict[str, Any] = {}
    ):
        """Add a column node and connect to its table"""
        table_node_id = f"table:{table_name}"
        column_node_id = f"column:{table_name}.{column_name}"
        
        # Add column node
        self.graph.add_node(
            column_node_id,
            type="column",
            name=column_name,
            table=table_name,
            **attributes
        )
        
        # Add edge from table to column
        self.graph.add_edge(
            table_node_id,
            column_node_id,
            type="has_column"
        )
        
        return column_node_id
    
    def add_relationship(
        self,
        source_table: str,
        source_column: str,
        target_table: str,
        target_column: str,
        relationship_type: str = "foreign_key",
        attributes: Dict[str, Any] = {}
    ):
        """Add a relationship between columns"""
        source_node_id = f"column:{source_table}.{source_column}"
        target_node_id = f"column:{target_table}.{target_column}"
        
        # Add edge between columns
        self.graph.add_edge(
            source_node_id,
            target_node_id,
            type=relationship_type,
            **attributes
        )
    
    def get_related_tables(self, table_name: str, max_distance: int = 2) -> List[Dict[str, Any]]:
        """Get tables related to the specified table within max_distance"""
        source_node_id = f"table:{table_name}"
        
        # Check if node exists
        if source_node_id not in self.graph:
            return []
            
        # Get subgraph of nodes within max_distance
        node_gen = nx.ego_graph(
            self.graph, 
            source_node_id,
            radius=max_distance
        )
        
        # Filter to just table nodes
        related_tables = []
        for node in node_gen.nodes():
            node_data = self.graph.nodes[node]
            if node_data.get("type") == "table" and node != source_node_id:
                # Find shortest path
                path = nx.shortest_path(self.graph, source_node_id, node)
                path_edges = list(zip(path[:-1], path[1:]))
                
                # Extract edge attributes
                edge_types = []
                for u, v in path_edges:
                    edge_attrs = self.graph.edges[u, v]
                    edge_types.append(edge_attrs.get("type", "unknown"))
                
                # Add to results
                related_tables.append({
                    "table_name": node_data.get("name"),
                    "node_id": node,
                    "distance": len(path) - 1,
                    "path": path,
                    "relationship_types": edge_types,
                    "attributes": {k: v for k, v in node_data.items() if k not in ["type", "name"]}
                })
                
        # Sort by distance
        related_tables.sort(key=lambda x: x["distance"])
        
        return related_tables
    
    def get_path_between_tables(self, source_table: str, target_table: str) -> Optional[List[Dict[str, Any]]]:
        """Find the shortest path between two tables"""
        source_node_id = f"table:{source_table}"
        target_node_id = f"table:{target_table}"
        
        # Check if nodes exist
        if source_node_id not in self.graph or target_node_id not in self.graph:
            return None
            
        try:
            # Find shortest path
            path = nx.shortest_path(self.graph, source_node_id, target_node_id)
            
            # Format result
            result = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_attrs = self.graph.edges[u, v]
                u_attrs = self.graph.nodes[u]
                v_attrs = self.graph.nodes[v]
                
                result.append({
                    "source": {
                        "id": u,
                        "type": u_attrs.get("type"),
                        "name": u_attrs.get("name"),
                    },
                    "target": {
                        "id": v,
                        "type": v_attrs.get("type"),
                        "name": v_attrs.get("name"),
                    },
                    "relationship": {
                        "type": edge_attrs.get("type"),
                        **{k: v for k, v in edge_attrs.items() if k != "type"}
                    }
                })
                
            return result
            
        except nx.NetworkXNoPath:
            return None
    
    def export_subgraph(self, table_names: List[str], include_columns: bool = True) -> Dict[str, Any]:
        """Export a subgraph containing specified tables and their relationships"""
        nodes = []
        
        # Add table nodes
        for table in table_names:
            table_node_id = f"table:{table}"
            if table_node_id in self.graph:
                nodes.append(table_node_id)
                
                # Add column nodes if requested
                if include_columns:
                    for _, column, _ in self.graph.out_edges(table_node_id, data=True):
                        nodes.append(column)
        
        # Create subgraph
        subgraph = self.graph.subgraph(nodes)
        
        # Format for export
        export_data = {
            "nodes": [],
            "edges": []
        }
        
        # Add nodes
        for node in subgraph.nodes():
            node_attrs = subgraph.nodes[node]
            export_data["nodes"].append({
                "id": node,
                **node_attrs
            })
            
        # Add edges
        for u, v, attrs in subgraph.edges(data=True):
            export_data["edges"].append({
                "source": u,
                "target": v,
                **attrs
            })
            
        return export_data