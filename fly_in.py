import sys

try:
    from pydantic import ValidationError
except ImportError:
    print("[ERROR] Install Dependencies \n", file=sys.stderr)
    sys.exit(1)
from src.parse.validation import validation_data
from src.models.FlyinData import FlyinData
from src.algo.bfs_algo import check_bfs
from src.algo.dijks_algo import Algorithm

def main() -> None:
    if len(sys.argv) != 2:
        print("[ERROR] You need config.txt \n", file=sys.stderr)
        sys.exit(1)
    try:
        data = validation_data(sys.argv[1])
    except ValueError as e:
        print(f"{e}\n", file=sys.stderr)
        sys.exit(1)
    except ValidationError as e:
        print(f"{e}\n", file=sys.stderr)
        sys.exit(1)
    fly_data = FlyinData()
    fly_data._append_zones_drons_connections(data)
    if check_bfs(fly_data.map_zones) is False:
        print("[ERROR] No path found \n", file=sys.stderr)
        sys.exit(1)
    algo = Algorithm(fly_data)
    algo.simulation_fly()

if __name__ == "__main__":
    main()
