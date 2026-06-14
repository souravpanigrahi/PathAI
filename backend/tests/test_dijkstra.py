import pytest
from app.core.graph import Graph
from app.core.dijkstra import find_shortest_path

def setup_test_graph():
    g = Graph()
    # A -- 1.0 -- B -- 2.0 -- C
    # |                       |
    # 4.0                    1.0
    # |                       |
    # D -------- 5.0 ---------+
    
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 2.0)
    g.add_edge("A", "D", 4.0)
    g.add_edge("D", "C", 5.0)
    
    return g

def test_dijkstra_shortest_path():
    g = setup_test_graph()
    
    # The shortest path from A to C is A -> B -> C (distance 1 + 2 = 3)
    # The alternate path A -> D -> C would be 4 + 5 = 9
    path, distance = find_shortest_path(g, "A", "C")
    
    assert distance == 3.0
    assert path == ["A", "B", "C"]

def test_dijkstra_no_path():
    g = setup_test_graph()
    g.add_node("Isolated_Island")
    
    path, distance = find_shortest_path(g, "A", "Isolated_Island")
    assert path is None
    assert distance == float('inf')

def test_dijkstra_same_node():
    g = setup_test_graph()
    path, distance = find_shortest_path(g, "A", "A")
    
    assert distance == 0.0
    assert path == ["A"]
