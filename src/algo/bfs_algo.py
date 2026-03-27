from typing import List, Set, Any
from src.models.ClassZone import Zone, EndZone, StartZone, BlockedZone


def check_bfs(map_zone: dict[Any, Zone]) -> bool:
    """
    Performs a Breadth-First Search to verify if the destination is reachable.

    This acts as a sanity check for the simulation. It ignores movement
    costs and capacities, focusing solely on whether a physical path exists
    from the start hub to the end hub while avoiding blocked zones.

    Args:
        map_zone (dict[Any, Zone]): A dictionary mapping zone names/IDs
                                     to their respective Zone objects.

    Returns:
        bool: True if at least one valid path exists between Start and End,
              False otherwise.
    """
    end_zone = next(
        (z for z in map_zone.values() if isinstance(z, EndZone)), None
        )
    start_zone = next(
        (z for z in map_zone.values() if isinstance(z, StartZone)), None
        )
    if not end_zone or not start_zone:
        return False
    queue: List[Zone] = [start_zone]
    visited: Set[str] = {start_zone.name}
    while queue:
        current_zone = queue.pop(0)
        if current_zone == end_zone:
            return True
        for conn in current_zone.connection:
            x, y = conn.nodes
            name_x: str = x.name if isinstance(x, Zone) else str(x)
            name_y: str = y.name if isinstance(y, Zone) else str(y)
            target_name: str = name_x if current_zone.name != name_x\
                else name_y
            if target_name in map_zone:
                neighbor = map_zone[target_name]
                is_blocked = isinstance(neighbor, BlockedZone)\
                    or getattr(neighbor, 'typ', '') == "blocked"
                if neighbor.name not in visited and not is_blocked:
                    visited.add(neighbor.name)
                    queue.append(neighbor)
    return False
