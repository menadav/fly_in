from src.models.ClassZone import Zone

def check_bfs(map_zone: dict[str, Zone]) -> bool:
    start_zone = next((z for z in map_zone.values() if z.role == "START"), None)
    end_zone = next((z for z in map_zone.values() if z.role == "END"), None)
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
                role = getattr(neighbor, 'role', 'NORMAL')
                if neighbor not in visited and role != "BLOCKED":
                    visited.add(neighbor)
                    queue.append(neighbor)
    return False
