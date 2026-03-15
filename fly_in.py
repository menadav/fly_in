import sys

try:
    from pydantic import ValidationError
except ImportError:
    sys.stderr.write("[ERROR] Install Dependencies")
    sys.exit(1)

from src.parse.validation import validation_data
from src.models.FlyinData import FlyinData


def main() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write("[ERROR] You need config.txt \n")
        sys.exit(1)
    try:
        data = validation_data(sys.argv[1])
    except ValueError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)
    except ValidationError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)
    fly_data = FlyinData()
    fly_data._append_zones_drons_connections(data)



if __name__ == "__main__":
    main()
