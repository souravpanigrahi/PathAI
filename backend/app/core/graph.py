class Graph:
    def __init__(self):
        # We use an adjacency list to represent the graph.
        # It's a dictionary where the key is a node_id, and the value is another dictionary
        # containing its neighbors and the distance (weight) to them.
        # Example: {'Intersection_A': {'Intersection_B': 5.0, 'Intersection_C': 2.5}}
        self.nodes = {}

    def add_node(self, node_id: str):
        """Adds a single node to the graph if it doesn't already exist."""
        if node_id not in self.nodes:
            self.nodes[node_id] = {}

    def add_edge(self, from_node: str, to_node: str, weight: float, bidirectional: bool = True):
        """Adds an edge (road) between two nodes with a specific weight (distance/time)."""
        # Ensure both nodes exist in the graph
        self.add_node(from_node)
        self.add_node(to_node)
        
        # Add the connection
        self.nodes[from_node][to_node] = weight
        
        # For city routing, roads are often two-way, but sometimes one-way.
        if bidirectional:
            self.nodes[to_node][from_node] = weight

    def get_neighbors(self, node_id: str) -> dict:
        """Returns all connected nodes and their weights for a given node."""
        return self.nodes.get(node_id, {})
