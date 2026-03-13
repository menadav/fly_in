import sys

try:
    from pydantic import ValidationError
except ImportError:
    sys.stderr.write("[ERROR] Install Dependencies")
    sys.exit(1)

from src.parse.validation import validation_data
from src.models.Zones import ManagerZone
mng = ManagerZone()


def main() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write("[ERROR] You need config.txt \n")
        sys.exit(1)
    try:
        data = validation_data(sys.argv[1])
        mng._append_zones_drons_connections(data)
        for es in mng.zones:
            print(es.name)
    except ValueError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)
    except ValidationError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
