*This project has been created as part of the 42 curriculum by salabool.*

# Fly-in

## Description

Fly-in is a Python-based simulation the shows the movement of multiple autonomous drones through a network of interconnected zones. The objective is to guide every drone from a designated starting hub to its final destination while minimizing the total number of simulation turns.

The network is represented as a graph consisting of zones and connections, each with its own properties and limitations. The simulation takes into account zone occupancy, connection capacities, restricted areas, and inaccessible zones to coordinate drone movements efficiently.

By combining shortest-path calculations with turn-based movement scheduling, the program aims to reduce congestion, prevent collisions, and ensure that all drones reach their destination.

## Instructions

Use the provided `Makefile` to manage the project's setup and execution.

**Installation**
Install the required dependencies (such as `mypy` and `flake8`) before running the program:
```bash
make install
```

**Execution**
Run the simulation by providing a map file:
```bash
make run MAP=map.txt
```
*(You can also execute it directly via Python: `python3 main.py map.txt`)*

**Debugging**
Launch the program using Python's built-in `pdb` debugger for step-by-step inspection:
```bash
make debug MAP=map.txt
```

**Linting & Type Checking**
Verify code quality and strict type hints:
```bash
make lint
```

**Cleanup**
Remove cache directories and temporary Python files:
```bash
make clean
```

## Algorithm

The project implements a **Reverse Dijkstra's Algorithm** to handle pathfinding. Rather than calculating paths forward from the starting point, it maps the shortest weighted distances from the `end_hub` backwards to every node in the graph.

**Traversal Rules:**
- **Normal & Priority Zones:** Require 1 turn to cross. The algorithm actively favors priority zones when distances are equal.
- **Restricted Zones:** Require 2 turns. A drone spends the first turn traveling on the connection and arrives at the zone on the second turn.
- **Blocked Zones:** Completely ignored and avoided by the pathfinder.

**Traffic Control:**
To prevent deadlocks, the engine evaluates movements on a turn-by-turn basis. Drones are sorted by their proximity to the end goal. Drones closest to the destination move first, dynamically freeing up capacity in their previous zones to allow trailing drones to advance within the exact same turn.

## Visual Representation

To enhance the user experience, the simulation features a color-coded terminal output. Each printed line corresponds to a single turn. If a zone is assigned a `color` attribute in the map file, the program uses ANSI escape codes to highlight that destination in the terminal, providing clear and real-time visual tracking of the drone swarm.

## Example Input

```text
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

## Example Output

```text
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

## Resources

* Python `dataclasses` documentation
* Python `heapq` documentation
* Dijkstra's shortest path algorithm
* Fly-in project subject
* Used AI solely to better understand the project requirements and concepts.