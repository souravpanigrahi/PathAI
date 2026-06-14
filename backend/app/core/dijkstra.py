import heapq
from typing import List, Tuple, Optional
from app.core.graph import Graph

def find_shortest_path(graph: Graph, start_node: str, end_node: str) -> Tuple[Optional[List[str]], float]:
    """
    Finds the shortest path using Dijkstra's algorithm.
    Returns a tuple of (path_as_list_of_nodes, total_distance).
    If no path exists, returns (None, float('inf')).
    """
    if start_node not in graph.nodes or end_node not in graph.nodes:
        return None, float('inf')

    # Min-Heap Priority Queue: stores tuples of (current_distance, current_node)
    # heapq will automatically sort this list so the lowest distance is ALWAYS first.
    pq = [(0.0, start_node)]
    
    # Dictionary to track the shortest known distance from start to each node
    distances = {node: float('inf') for node in graph.nodes}
    distances[start_node] = 0.0
    
    # Dictionary to reconstruct the path backwards (where did we come from?)
    previous_nodes = {node: None for node in graph.nodes}

    while pq:
        # 1. Grab the node with the absolute lowest distance from our queue
        current_distance, current_node = heapq.heappop(pq)

        # 2. If we reached our destination, we can stop early!
        if current_node == end_node:
            break
            
        # 3. If we found a shorter path previously and just popped an old, worse entry, skip it
        if current_distance > distances[current_node]:
            continue

        # 4. Explore all neighbors of the current node
        for neighbor, weight in graph.get_neighbors(current_node).items():
            # Calculate the total distance from start to this neighbor
            distance = current_distance + weight

            # 5. If we found a *better* (shorter) path to the neighbor...
            if distance < distances[neighbor]:
                # Update our records!
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                
                # Push the new improved distance onto the priority queue so we can explore it later
                heapq.heappush(pq, (distance, neighbor))

    # If the end_node's distance is still infinity, no path exists
    if distances[end_node] == float('inf'):
        return None, float('inf')

    # Reconstruct the path by walking backwards from the end
    path = []
    current = end_node
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    
    path.reverse()  # Reverse it to get Start -> End
    
    return path, distances[end_node]
