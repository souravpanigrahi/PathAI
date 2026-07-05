import heapq
from typing import List, Tuple, Optional
from app.core.graph import Graph

def find_shortest_path(graph: Graph, start_node: str, end_node: str) -> Tuple[Optional[List[str]], float, Optional[dict]]:
    """
    Finds the shortest path using Dijkstra's algorithm.
    Returns a tuple of (path_as_list_of_nodes, base_distance, traffic_context).
    If no path exists, returns (None, float('inf'), None).
    """
    if start_node not in graph.nodes or end_node not in graph.nodes:
        return None, float('inf'), None

    # Min-Heap Priority Queue: stores tuples of (current_distance, current_node)
    # heapq will automatically sort this list so the lowest distance is ALWAYS first.
    pq = [(0.0, start_node)]
    
    # Dictionary to track the shortest known distance from start to each node
    distances = {node: float('inf') for node in graph.nodes}
    distances[start_node] = 0.0
    
    # Dictionary to reconstruct the path backwards (where did we come from?)
    previous_nodes = {node: None for node in graph.nodes}

    from app.core.traffic import get_effective_weight

    used_hour = None

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
        for neighbor, edge_data in graph.get_neighbors(current_node).items():
            # edge_data is now a dict: {"weight": float, "road_type": str}
            base_weight = edge_data["weight"]
            road_type = edge_data["road_type"]
            
            # Apply dynamic traffic multipliers based on current time/day
            effective_weight, h = get_effective_weight(base_weight, road_type)
            used_hour = h

            # Calculate the total distance from start to this neighbor
            distance = current_distance + effective_weight

            # 5. If we found a *better* (shorter) path to the neighbor...
            if distance < distances[neighbor]:
                # Update our records!
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                
                # Push the new improved distance onto the priority queue so we can explore it later
                heapq.heappush(pq, (distance, neighbor))

    # If the end_node's distance is still infinity, no path exists
    if distances[end_node] == float('inf'):
        return None, float('inf'), None

    # Reconstruct the path by walking backwards from the end
    path = []
    current = end_node
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    
    path.reverse()  # Reverse it to get Start -> End
    
    # Calculate base distance (raw road length) along the final path
    base_dist = 0.0
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        base_dist += graph.nodes[u][v]["weight"]
        
    eff_dist = distances[end_node]
    avg_traffic_factor = eff_dist / base_dist if base_dist > 0 else 1.0
    
    from datetime import datetime
    current_hour = used_hour if used_hour is not None else datetime.now().hour
    
    if avg_traffic_factor < 1.2:
        traffic_level = "light"
    elif avg_traffic_factor <= 1.8:
        traffic_level = "moderate"
    else:
        traffic_level = "heavy"
        
    traffic_context = {
        "current_hour": current_hour,
        "avg_traffic_factor": round(avg_traffic_factor, 2),
        "traffic_level": traffic_level,
        "effective_distance_meters": round(eff_dist, 2),
        "base_distance_meters": round(base_dist, 2)
    }
    
    return path, eff_dist, traffic_context
