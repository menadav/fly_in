try:
    from pydantic import BaseModel, Field
except ImportError:
    raise ValueError("[ERROR] Import dependencies")

from abc import ABC, abstractmethod
import re
from typing import Optional, Any
from enum import Enum


class HubColor(Enum):
    NONE = "none"
    RED = "red"
    BLUE = "blue"
    GRAY = "gray"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    CYAN = "cyan"
    PURPLE = "purple"
    BROWN = "brown"
    LIME = "lime"
    MAGENTA = "magenta"
    GOLD = "gold"
    BLACK = "black"
    MAROON = "maroon"
    DARKRED = "darkred"
    VIOLET = "violet"
    CRIMSON = "crimson"
    RAINBOW = "rainbow"


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class DronData(ABC, BaseModel):
    type: str

    @classmethod
    @abstractmethod
    def parse_line(cls, line: str) -> Optional["DronData"]:
        pass


class ZoneHub(DronData):
    name: str
    x: int
    y: int
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: HubColor = Field(default=HubColor.NONE)
    max_drones: int = Field(default=1, gt=0)

    @classmethod
    def parse_line(cls, line: str) -> Optional["ZoneHub"]:
        try:
            parts = line.split(':', 1)
            z_type = parts[0].strip()
            rest = parts[1].strip()
            metadata = re.findall(r"\[(.*)\]", rest)
            if len(metadata) > 1:
                raise ValueError(
                    f"[ERROR] There are 2 or more Metadatas {line}"
                    )
            clean_rest = re.sub(r"\[(.*)]", "", rest).strip()
            name_x_y = clean_rest.split()
            if len(name_x_y) != 3:
                raise ValueError(f"[ERROR] Arguments are missing. {line}")
            data: dict[str, Any] = {
                "type": z_type,
                "name": name_x_y[0],
                "x": int(name_x_y[1]),
                "y": int(name_x_y[2]),
                "zone": ZoneType.NORMAL,
                "color": HubColor.NONE,
                "max_drones": 1
            }
            if metadata:
                metadata_str = metadata[0].strip("[] ").strip()
                metadata_str = re.sub(r'\s*=\s*', '=', metadata_str)
                pairs = re.split(r"[,\s]+", metadata_str)
                check_zone = False
                check_color = False
                check_drones = False
                for pair in pairs:
                    pair = pair.strip()
                    if '=' not in pair:
                        raise ValueError(f"[ERROR] Incorrect Metadata {line}")
                    key, value = [p.strip() for p in pair.split("=", 1)]
                    if key == "zone":
                        if check_zone:
                            raise ValueError(f"[ERROR] Color is repit {line}")
                        data["zone"] = ZoneType(value.lower())
                        check_zone = True
                    elif key == "color":
                        if check_color:
                            raise ValueError(f"[ERROR] Color is repit {line}")
                        data["color"] = HubColor(value.lower())
                        check_color = True
                    elif key == "max_drones":
                        if check_drones:
                            raise ValueError(
                                f"[ERROR] Max_drones is repit {line}"
                                )
                        data["max_drones"] = int(value)
                        check_drones = True
                    else:
                        raise ValueError(f"[ERROR] Unknowed metadata {line}")
            return cls(
                type=str(data["type"]),
                name=str(data["name"]),
                x=int(data["x"]),
                y=int(data["y"]),
                zone=data["zone"],
                color=data["color"],
                max_drones=int(data["max_drones"])
            )
        except Exception as e:
            error_msg = str(e)
            if "Zone" in error_msg:
                raise ValueError(f"[ERROR] Invalid zone type: {line}")
            elif "Color" in error_msg:
                raise ValueError(f"[ERROR] Unrecognized color: {line}")
            raise ValueError(f"[CRITICAL] ERROR DATA ZoneHub {e}")


class ZoneConnection(DronData):
    name1: str
    name2: str
    max_link_capacity: int = Field(default=1, gt=0)

    @classmethod
    def parse_line(cls, line: str) -> Optional["ZoneConnection"]:
        try:
            parts = line.split(':', 1)
            z_type = parts[0].strip()
            rest = parts[1].strip()
            metadata = re.findall(r"\[(.*)\]", rest)
            if len(metadata) > 1:
                raise ValueError(
                    f"[ERROR] There are 2 or more Metadatas {line}"
                    )
            clean_rest = re.sub(r"\[(.*)]", "", rest).strip()
            names = clean_rest.split('-')
            if len(names) != 2:
                raise ValueError(f"[ERROR] Incorrect number names {line}")
            conn_data: dict[str, Any] = {
                "type": z_type,
                "name1": names[0].strip(),
                "name2": names[1].strip(),
                "max_link_capacity": 1

            }
            if metadata:
                metadata_str = metadata[0].strip("[] ").strip()
                if '=' in metadata_str:
                    key_raw, value_raw = metadata_str.split('=', 1)
                    key = key_raw.strip()
                    value = value_raw.strip()
                    if key == "max_link_capacity":
                        conn_data["max_link_capacity"] = int(value.strip())
                    else:
                        raise ValueError(
                                f"[ERROR] Diferent Key: {line}"
                                )
                else:
                    raise ValueError(
                        "[ERROR] Diferrent Metadata"
                        f" 'max_link_capacity': {line}"
                        )
            return cls(
                type=str(conn_data["type"]),
                name1=str(conn_data["name1"]),
                name2=str(conn_data["name2"]),
                max_link_capacity=int(conn_data["max_link_capacity"])
            )
        except Exception as e:
            raise ValueError(f"{e}")
