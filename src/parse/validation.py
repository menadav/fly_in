from typing import List
from src.models.ZoneConfig import ZoneHub, ZoneConnection, DronData


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


def check_zone(zones: List[int | DronData]) -> None:
    count_start = 0
    count_end = 0
    list_name = []
    name1_name2 = []
    coords_seen = set()
    data_zone = ["start_hub", "end_hub", "hub"]
    for data in zones:
        if isinstance(data, int):
            continue
        if data.type in data_zone:
            current_pos = (data.x, data.y)
            if current_pos in coords_seen:
                raise ValueError(
                    f"[ERROR] Collision: Multiple hubs at {current_pos}"
                    )
            coords_seen.add(current_pos)
        if data.type == "start_hub":
            check_space(data.name)
            list_name.append(data.name)
            count_start += 1
            if count_start != 1:
                raise ValueError("[ERROR] start_hub")
        elif data.type == "end_hub":
            check_space(data.name)
            list_name.append(data.name)
            count_end += 1
            if count_end != 1:
                raise ValueError("[ERROR] end_hub")
        elif data.type == "hub":
            if data.name not in list_name:
                check_space(data.name)
                list_name.append(data.name)
            else:
                raise ValueError("[ERROR] Name is repit")
            continue
        elif data.type == "connection":
            nam1_nam2 = data.name1, data.name2
            nam2_nam1 = data.name2, data.name1
            if nam1_nam2 in name1_name2 \
                    or data.name1 == data.name2 or nam2_nam1 in name1_name2:
                raise ValueError("[ERROR] Connection is repit")
            else:
                name1_name2.append(nam1_nam2)
            continue
        else:
            raise ValueError("[ERROR] Type is different")
    if count_start != 1:
        raise ValueError("[ERROR] Need start_hub")
    elif count_end != 1:
        raise ValueError("[ERROR] Need end_hub")
    for name1, name2 in name1_name2:
        if name1 not in list_name or name2 not in list_name:
            raise ValueError("[ERROR] Names_hub not it in connections")


def check_space(line: str) -> None:
    if " " in line:
        raise ValueError("[ERROR] Name have space {line}")
    if "-" in line:
        raise ValueError("[ERROR] Name have '-' {line}")


def dron_nb(line: str) -> int:
    try: 
        parts = line.split(":", 1)
        number = int(parts[1])
        if number <= 0:
            raise ValueError("[ERROR] Need positiv Drons {line}")
        return number
    except ValueError:
        raise ValueError("[ERROR] Need value for nb drons {line}")
