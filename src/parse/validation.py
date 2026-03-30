from typing import List, Union, Tuple
from src.models.ZoneConfig import ZoneHub, ZoneConnection
ParsedData = Union[int, ZoneHub, ZoneConnection]


def validation_data(file_path: str) -> List[ParsedData]:
    """
    Parses and validates a configuration file to extract drone and map data.

    This function reads a file line-by-line, ignores comments, and converts
    the text into structured Python objects. It also ensures the file starts
    with the drone count.

    Args:
        file_path (str): The path to the input configuration file.

    Returns:
        List[ParsedData]: A list containing the number of drones (int) followed
                          by ZoneHub and ZoneConnection objects.

    Raises:
        ValueError: If the file format is incorrect, missing required elements,
                    or contains invalid data.
    """
    zone_list: List[Tuple[ParsedData, str]] = []
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
                        f"\n{line}"
                        )
                if not has_nb_drones:
                    if "nb_drones" in line_clean:
                        n_drones: int = dron_nb(line_clean)
                        zone_list.append((n_drones, line_clean))
                        has_nb_drones = True
                        continue
                    else:
                        raise ValueError(
                            "[ERROR] First line must be nb_drones"
                            )
                item: Union[ZoneHub, ZoneConnection, None] = None
                if "connection" in line_clean:
                    item = ZoneConnection.parse_line(line_clean)
                else:
                    item = ZoneHub.parse_line(line_clean)
                if item is not None:
                    zone_list.append((item, line))
            check_zone(zone_list)
            zone_clean = []
            for zone in zone_list:
                zone_clean.append(zone[0])
            return zone_clean
    except ValueError as e:
        raise ValueError(e)
    except PermissionError:
        raise ValueError("[ERROR] Permission denied")
    except FileNotFoundError:
        raise ValueError("[ERROR] File not found")
    except Exception as e:
        raise ValueError(f"[ERROR] {e}")


def check_zone(zones: List[Tuple[ParsedData, str]]) -> None:
    """
    Verifies the logical integrity of the parsed map data.

    Checks performed:
    - Exactly one 'start_hub' and one 'end_hub' exist.
    - No two hubs share the same coordinates.
    - No two hubs share the same name.
    - Connections only refer to hubs that actually exist.
    - No duplicate or self-referencing connections.
    """
    count_start = 0
    count_end = 0
    list_name = []
    name1_name2 = []
    coords_seen = set()
    for data, line in zones:
        if isinstance(data, int):
            continue
        if isinstance(data, ZoneHub):
            current_pos = (data.x, data.y)
            if current_pos in coords_seen:
                raise ValueError(
                    f"[ERROR] Collision: Multiple hubs at {current_pos}"
                    )
            coords_seen.add(current_pos)
            check_space(data.name, line)
            if data.type == "start_hub":
                list_name.append(data.name)
                count_start += 1
                if count_start > 1:
                    raise ValueError(
                        "[ERROR] There are more than 1 start_hub"
                        f"{line}"
                        )
            elif data.type == "end_hub":
                list_name.append(data.name)
                count_end += 1
                if count_end != 1:
                    raise ValueError(
                        "[ERROR] There are more than 1 end_hub"
                        f"\n{line}"
                        )
            elif data.type == "hub":
                if data.name not in list_name:
                    list_name.append(data.name)
                else:
                    raise ValueError(
                        f"[ERROR] Name is repit \n{data.name}"
                        f"\n{line}"
                        )
                continue
        elif isinstance(data, ZoneConnection):
            nam1_nam2 = data.name1, data.name2
            nam2_nam1 = data.name2, data.name1
            if nam1_nam2 in name1_name2 \
                    or data.name1 == data.name2 or nam2_nam1 in name1_name2:
                raise ValueError(
                    f"[ERROR] Connection is repit\n{line}"
                    )
            else:
                name1_name2.append(nam1_nam2)
            continue
        else:
            raise ValueError(f"[ERROR] Type is different\n{line}")
    if count_end == 0:
        raise ValueError("You need end_hub")
    if count_start == 0:
        raise ValueError("You need start_hub")
    for name1, name2 in name1_name2:
        if name1 not in list_name or name2 not in list_name:
            raise ValueError(
                "[ERROR] Names_hub not it in connections"
                f"\n{line}"
                )


def check_space(line: str, check: str) -> None:
    """
    Validates that a hub name does not contain illegal characters
    """
    if " " in line:
        raise ValueError(f"[ERROR] Name have space\n{check}")
    if "-" in line:
        raise ValueError(f"[ERROR] Name have '-'\n{check}")


def dron_nb(line: str) -> int:
    """
    Extracts the number of drones from a configuration line.
    """
    try:
        parts = line.split(":", 1)
        number = int(parts[1])
        if not number > 0:
            raise ValueError(
                "[ERROR] Need minimum 1 dron for start"
                f"\n{line}"
                )
        return number
    except ValueError as e:
        if "minimum 1 drone" in str(e):
            raise e
        raise ValueError("[ERROR] Need value for nb drons\n{line}")
