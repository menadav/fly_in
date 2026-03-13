from typing import List
from src.parse.zone import check_zone, ZoneHub, ZoneConnection, dron_nb


def validation_data(file_path: str) -> List:
    zone_list = []
    has_nb_drones = False
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            for line in f:
                line_clean = line.strip()
                if not line_clean or line_clean[0] == '#':
                    continue
                if ':' not in line_clean:
                    raise ValueError(
                        "[ERROR] Invalid line format (missing ':')"
                        )
                if "nb_drones" in line_clean:
                    if not has_nb_drones:
                        n_drones = dron_nb(line_clean)
                        zone_list.append(n_drones)
                        has_nb_drones = True
                        continue
                    else:
                        raise ValueError(
                            "[ERROR] First line must be nb_drones"
                                         )
                if "connection" in line_clean:
                    new_zone = ZoneConnection.parse_line(line_clean)
                else:
                    new_zone = ZoneHub.parse_line(line_clean)
                zone_list.append(new_zone)
            check_zone(zone_list)
            return zone_list
    except ValueError as e:
        raise ValueError(e)
    except PermissionError:
        raise ValueError("[ERROR] Permission denied")
    except FileNotFoundError:
        raise ValueError("[ERROR] File not found")
    except Exception as e:
        raise ValueError(f"[ERROR] {e}")
