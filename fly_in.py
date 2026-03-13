import sys

try:
    from pydantic import ValidationError
except ImportError:
    sys.stderr.write("[ERROR] Install Dependencies")
    sys.exit(1)

from src.parse.validation import validation_data


def main() -> None:
    try:
        data = validation_data(sys.argv[1])
        print(data)
    except ValueError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)
    except ValidationError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
