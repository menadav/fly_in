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
from src.render.render_zones import Visualizer


def main() -> None:
    """
    Execute the main simulation pipeline for the Fly-in Drones project.
    This function handles the lifecycle of the simulation:
    1. Parses and validates input data from a JSON/file source.
    2. Initializes the data models and drone maps.
    3. Performs a BFS check to ensure a valid path exists between
        start and end.
    4. Runs the pathfinding algorithm (Dijkstra-based) to schedule
        drone movements.
    5. Launches the visualizer to display the simulation results.

    Args:
        None (Reads from sys.argv).

    Raises:
        ValueError: If the input file format is incorrect.
        ValidationError: If the data does not match the Pydantic schema.
    """
    if len(sys.argv) != 2:
        print("[ERROR] Need a file \n", file=sys.stderr)
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
    visual = Visualizer(algo)
    visual.main_loop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] The simulation has stopped.")
        sys.exit(0)
