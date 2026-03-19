from src.models.ClassZone import Zone, EndZone, StartZone, BlockedZone

def check_bfs(map_zone: dict[str, Zone]) -> bool:
    end_zone = next((z for z in map_zone.values() if isinstance(z, EndZone)), None)
    start_zone = next((z for z in map_zone.values() if isinstance(z, StartZone)), None)
    if not end_zone or not start_zone:
        return False
    queue = [start_zone]
    visited = {start_zone.name}
    while queue:
        current_zone = queue.pop(0)
        if current_zone == end_zone:
            return True
        for conn in current_zone.connection:
            x , y = conn.nodes
            if not current_zone.name == x:
                conn = x
            else:
                conn = y
            if conn in map_zone:
                neighbor = map_zone[conn]
                is_blocked = isinstance(neighbor, BlockedZone) or neighbor.typ == "blocked"
                if neighbor not in visited and not is_blocked:
                    visited.add(neighbor)
                    queue.append(neighbor)
    return False
