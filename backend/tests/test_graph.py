import pytest
from app.core.graph import Graph

def test_add_node():
    g = Graph()
    g.add_node("A")
    assert "A" in g.nodes
    assert g.nodes["A"] == {}

def test_add_edge_bidirectional():
    g = Graph()
    # Add a two-way road between A and B with a distance of 5.0
    g.add_edge("A", "B", 5.0)
    
    assert "A" in g.nodes
    assert "B" in g.nodes
    assert g.nodes["A"]["B"] == 5.0
    assert g.nodes["B"]["A"] == 5.0

def test_add_edge_unidirectional():
    g = Graph()
    # Add a one-way road from A to B
    g.add_edge("A", "B", 3.0, bidirectional=False)
    
    assert g.nodes["A"]["B"] == 3.0
    assert "A" not in g.nodes["B"]

def test_get_neighbors():
    g = Graph()
    g.add_edge("A", "B", 5.0)
    g.add_edge("A", "C", 2.0)
    
    # A should be connected to B and C
    neighbors = g.get_neighbors("A")
    assert neighbors == {"B": 5.0, "C": 2.0}
    
    # C should only be connected to A (since we made bidirectional edges)
    assert g.get_neighbors("C") == {"A": 2.0}
