try:
    from pydantic import BaseModel, Field
except ImportError:
    raise ValueError("[ERROR] Import dependencies")

from abc import ABC, abstractmethod
import re
from typing import Optional
from enum import Enum


class HubColor(Enum):
    NONE = "none"
    RED = "red"
    BLUE = "blue"
    GRAY = "gray"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"

class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class DronData(ABC, BaseModel):
    type: str

    @classmethod
    @abstractmethod
    def parse_line(cls, line: str):
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
                raise ValueError("[ERROR] There are 2 or more Metadatas")
            clean_rest = re.sub(r"\[(.*)]", "", rest).strip()
            name_x_y = clean_rest.split()
            if len(name_x_y) != 3:
                raise ValueError("[ERROR] Arguments are missing.")
            data = {
                "type": z_type,
                "name": name_x_y[0],
                "x": name_x_y[1],
                "y": name_x_y[2]
            }
            if metadata:
                metadata_str = metadata[0]
                pairs = re.split(r"[,\s]+", metadata_str)
                check_zone = False
                check_color = False
                check_drones = False
                for pair in pairs:
                    if '=' not in pair:
                        raise ValueError("[ERROR] Incorrect Metadata")
                    key, value = pair.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key == "zone":
                        if check_zone:
                            raise ValueError("[ERROR] Color is repit")
                        data["zone"] = value
                        check_zone = True
                    elif key == "color":
                        if check_color:
                            raise ValueError("[ERROR] Color is repit")
                        data["color"] = value
                        check_color = True
                    elif key == "max_drones":
                        if check_drones:
                            raise ValueError("[ERROR] Max_drones is repit")
                        data["max_drones"] = value
                        check_drones = True
                    else:
                        raise ValueError("[ERROR] Unknowed metadata")
            return cls(**data)
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
                raise ValueError("[ERROR] There are 2 or more Metadatas")
            clean_rest = re.sub(r"\[(.*)]", "", rest).strip()
            names = clean_rest.split('-')
            if len(names) != 2:
                raise ValueError("[ERROR] Incorrect number names.")
            data = {
                "type": z_type,
                "name1": names[0],
                "name2": names[1],
            }
            if metadata:
                metadata_str = metadata[0]
                key, value = metadata_str.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key == "max_link_capacity":
                    data["max_link_capacity"] = value
                else:
                    raise ValueError(
                        "[ERROR] Diferrent Metadata 'max_link_capacity'"
                        )
            return cls(**data)
        except Exception as e:
            raise ValueError(f"{e}")
