"""
Utility to download and load the Chennai road network from OpenStreetMap
into our in-memory Graph class using the osmnx library.
"""

import os
from typing import Dict, Tuple, Optional

import numpy as np
import osmnx as ox
from scipy.spatial import KDTree

from app.core.graph import Graph

# Path to the cached graphml file so we don't re-download every time
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
GRAPHML_PATH = os.path.join(DATA_DIR, "chennai.graphml")

# ---------------------------------------------------------------------------
# Node coordinate store (populated by load_chennai_graph)
# ---------------------------------------------------------------------------

# node_id (str) → (lat, lng)
node_coords: Dict[str, Tuple[float, float]] = {}

# KDTree over graph nodes for fast nearest-node lookups
_graph_node_tree: Optional[KDTree] = None
_graph_node_ids: list = []          # index → node_id, maps tree indices back


def find_nearest_graph_node(lat: float, lng: float) -> str:
    """
    Snap a (lat, lng) coordinate to the nearest node in the road graph.
    Returns the node_id (str).
    """
    if _graph_node_tree is None:
        raise RuntimeError("Graph node tree not built yet — call load_chennai_graph() first.")

    _, index = _graph_node_tree.query([lat, lng], k=1)
    return _graph_node_ids[index]


# ---------------------------------------------------------------------------
# Download / Load
# ---------------------------------------------------------------------------

def download_chennai_graph() -> None:
    """
    Downloads the drivable road network for Chennai from OSM and saves it
    as a GraphML file. Skips the download if the file already exists.
    """
    if os.path.exists(GRAPHML_PATH):
        print(f"[OSM] GraphML file already exists at {GRAPHML_PATH}, skipping download.")
        return

    os.makedirs(DATA_DIR, exist_ok=True)

    print("[OSM] Downloading drivable road network for Chennai, Tamil Nadu, India ...")
    osm_graph = ox.graph_from_place("Chennai, Tamil Nadu, India", network_type="drive")
    ox.save_graphml(osm_graph, filepath=GRAPHML_PATH)
    print(f"[OSM] Saved raw graph to {GRAPHML_PATH}")


def load_chennai_graph() -> Graph:
    """
    Reads the saved GraphML file, loops through its nodes and edges,
    and populates an instance of our Graph class using add_node / add_edge.

    Also populates node_coords and builds a KDTree over all graph nodes
    so that any (lat, lng) can be snapped to the nearest road intersection.

    Node IDs are the OSM node IDs (converted to str to match Graph.add_node signature).
    Edge weight is the road length in metres (the 'length' attribute in OSM data).
    """
    global _graph_node_tree, _graph_node_ids

    # Make sure the graphml file exists first
    download_chennai_graph()

    print("[OSM] Loading Chennai graph from GraphML ...")
    osm_graph = ox.load_graphml(GRAPHML_PATH)

    graph = Graph()
    node_count = 0
    edge_count = 0

    # --- Add nodes + store coordinates ---
    # OSM node attributes: 'y' = latitude, 'x' = longitude
    for osm_node_id, data in osm_graph.nodes(data=True):
        nid = str(osm_node_id)
        graph.add_node(nid)
        node_coords[nid] = (float(data["y"]), float(data["x"]))
        node_count += 1

    # --- Build KDTree over graph node coordinates ---
    _graph_node_ids = list(node_coords.keys())
    coords_array = np.array([node_coords[nid] for nid in _graph_node_ids])
    _graph_node_tree = KDTree(coords_array)
    print(f"[OSM] Built graph-node KDTree over {len(_graph_node_ids)} nodes.")

    # --- Add edges ---
    # osm_graph.edges(data=True) yields (u, v, attr_dict)
    # OSM road networks are MultiDiGraphs, so edges are directed.
    # We add each directed edge individually (bidirectional=False) to
    # preserve the original one-way / two-way semantics from OSM.
    for u, v, data in osm_graph.edges(data=True):
        weight = data.get("length", 0.0)
        graph.add_edge(str(u), str(v), weight=float(weight), bidirectional=False)
        edge_count += 1

    print(f"[OSM] Loaded {node_count} nodes and {edge_count} edges into Graph.")
    return graph

