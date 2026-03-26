*This project has been created as part of the 42 curriculum by dmena-li*
# **Fly-in**

### Description
Fly-in is a strategic simulation designed to solve a complex logistical challenge:
navigating a fleet of autonomous drones througha network of interconnected zones.
The goal is to move all drones from a starting hub to a final destination in the fewest number
of turns possible, acting as a high-level "traffic controller" for aerial logistics.

The project simulates a dynamic environment where drones must compete for space and time.
It isn't just about finding the shortest path; it’s about smart scheduling.
The system must decide when a drone should fly full speed, when it should take a longer "priority"
route to avoid traffic, or when it’s safer to stay in place to let others pass.
## Instructions

#### Installation
This project requires Python 3.10 or later. It uses uv for dependency management. To install the necessary packages (pydantic, pygame, flake8 and mypy):

```
make install
```
You can run the default pipeline using the Makefile:
```
make run
```
For use other map write:
```
make run MAP=<file>
```
or
```
python3 -m fly_in <file>
```

### Technical Choices
1. Architecture:

	In compliance with the mandatory project constraints, the system is built on a robust Object-Oriented foundation. We have implemented a centralized data structure that manages the following core entities as specialized objects:

	Zones (Hubs): Each zone is an instance of a class hierarchy (e.g., NormalZone, RestrictedZone, PriorityZone). These objects encapsulate their own specific logic, such as unique coordinates , movement costs , and real-time occupancy tracking based on max_drones capacity.

	Connections: These are treated as first-class objects that link two zones. They store metadata such as max_link_capacity , ensuring that the simulation respects the maximum number of drones allowed to traverse a specific path simultaneously.

	Drones: Each drone is an independent object with its own unique identifier (e.g., D1, D2). Drones maintain their current state, including their position in the graph, their active path, and their transit progress when moving through restricted zones.


2. Pathfinding Algorithm:

	To achieve optimal performance and minimize total simulation turns, the routing engine implements a dynamic pathfinding system based on Dijkstra's Algorithm:

	Initial Path Caching: At the start of the simulation, an initial Dijkstra pass calculates the optimal route from the start_hub to the end_hub for all drones. These paths are stored in a cache to reduce computational overhead during the simulation.

	Predictive Zone Reservation: To ensure fluid traffic flow and prevent the formation of queues, the algorithm implements a reservation system. This system tracks zone and connection occupancy turn-by-turn to respect all capacity constraints (max_drones and max_link_capacity).

	Dynamic Traffic Cost Scaling: To prevent drones from crowding a single "shortest" path, the cost of a route increases dynamically based on its current traffic density. This forces subsequent drones to evaluate alternative "cheaper" paths that might be geographically longer but faster in terms of simulation turns.
	Real-time Collision Avoidance: If a drone encounters an occupied zone that was not previously cleared , the algorithm triggers a real-time Dijkstra recalculation.

	Path Optimization Logic: A drone will only switch to a newly calculated path if it is more efficient than the remaining portion of its current route (i.e., len(new_path) < len(current_remaining_path))


3. Visualization Engine:

	The choice of [Pygame / Terminal Colors] was made to provide an intuitive understanding of the drone fleet’s behavior.
	Real-time Feedback: It allows peers to verify that drones correctly occupy connections toward restricted zones for exactly 2 turns.
	State Monitoring: Visual cues make it easy to see when a zone is at maximum capacity or when a drone is waiting.


### Resources
	- https://es.wikibooks.org/wiki/Algoritmia/Algoritmo_de_Dijkstra
	- https://www.youtube.com/watch?v=UFZN0NmY1jQ
	- IA
