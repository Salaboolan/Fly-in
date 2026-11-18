"""Run the drone simulation."""

from collections import Counter

from models import Connection, Drone, Graph
from pathfinding import PathFinder


class SimulationError(RuntimeError):
    """Represent a simulation error."""


class Simulation:
    """Move all drones from start to end."""

    def __init__(self, graph: Graph) -> None:
        """Prepare the simulation."""
        self.graph = graph
        self.finder = PathFinder(graph)
        self.drones = [
            Drone(number, graph.start)
            for number in range(1, graph.drone_count + 1)
        ]
        self.reserved: Counter[str] = Counter()

    def run(self) -> list[list[str]]:
        """Run the simulation until all drones arrive"""
        turns: list[list[str]] = []
        idle = 0

        while any(
            drone.zone != self.graph.end
            for drone in self.drones
        ):
            moves = self._turn()

            if moves:
                turns.append(moves)
                idle = 0
            else:
                idle += 1
            if idle > len(self.graph.zones):
                raise SimulationError("simulation deadlocked")
        return turns

    def _turn(self) -> list[str]:
        """Run one simulation turn."""
        moves: list[str] = []
        arrived: set[int] = set()

        occupancy: Counter[str] = Counter(
            drone.zone
            for drone in self.drones
            if drone.zone != self.graph.end
            and drone.transit_to is None
        )

        for drone in self.drones:
            if drone.transit_to is not None:
                target = drone.transit_to
                drone.zone = target
                drone.transit_to = None

                self.reserved[target] -= 1
                occupancy[target] += 1
                arrived.add(drone.identifier)
                moves.append(
                    f"D{drone.identifier}-{target}"
                )
        link_use: Counter[frozenset[str]] = Counter()
        active = [
            drone for drone in self.drones
            if drone.zone != self.graph.end
            and drone.identifier not in arrived
        ]
        active.sort(
            key=lambda drone: (
                self.finder.distance[drone.zone],
                drone.identifier,
            )
        )

        for drone in active:
            choice = self._choose(
                drone, occupancy, link_use,
            )
            if choice is None:
                continue
            connection, target = choice
            occupancy[drone.zone] -= 1
            link_use[connection.key] += 1

            if self.graph.zones[target].move_cost == 2:
                drone.transit_to = target
                self.reserved[target] += 1
                moves.append(
                    f"D{drone.identifier}-{connection.name}"
                )
            else:
                drone.zone = target
                if target != self.graph.end:
                    occupancy[target] += 1
                moves.append(
                    f"D{drone.identifier}-{target}"
                )
        moves.sort(
            key=lambda move: int(
                move.split("-", 1)[0][1:]
            )
        )
        return moves

    def _choose(
        self,
        drone: Drone,
        occupancy: Counter[str],
        link_use: Counter[frozenset[str]],
    ) -> tuple[Connection, str] | None:
        """Choose the first available path."""
        for connection, target in self.finder.choices(drone.zone):
            if link_use[connection.key] >= connection.capacity:
                continue

            if self.graph.zones[target].move_cost == 2:
                used = self.reserved[target]
            else:
                used = occupancy[target] + self.reserved[target]

            if used >= self.graph.capacity(target):
                continue

            return connection, target

        return None
