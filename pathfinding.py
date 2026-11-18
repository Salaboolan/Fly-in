"""Find shortest paths to the end zone."""

import heapq

from models import Connection, Graph


class PathFinder:
    """Find the best path to the end zone."""

    def __init__(self, graph: Graph) -> None:
        """Store graph and calculate distances."""
        self.graph = graph
        self.distance: dict[str, float] = self._dijkstra()

    def choices(self, current: str) -> list[tuple[Connection, str]]:
        """Return useful next zones."""
        result: list[tuple[Connection, str]] = []

        for connection in self.graph.neighbors[current]:
            target = connection.other(current)
            zone = self.graph.zones[target]
            if zone.kind == "blocked":
                continue
            if self.distance[target] < self.distance[current]:
                result.append((connection, target))
        result.sort(
            key=lambda item: (
                self.distance[item[1]],
                self.graph.zones[item[1]].kind != "priority",
            )
        )
        return result

    def _dijkstra(self) -> dict[str, float]:
        """Calculate distance from every zone to the end zone."""
        distance = {
            name: float("inf")
            for name in self.graph.zones
        }
        distance[self.graph.end] = 0
        pending: list[tuple[float, str]] = [
            (0, self.graph.end)
        ]

        while pending:
            current_cost, current = heapq.heappop(pending)
            if current_cost != distance[current]:
                continue
            for connection in self.graph.neighbors[current]:
                previous = connection.other(current)
                if self.graph.zones[previous].kind == "blocked":
                    continue
                cost = (
                    current_cost
                    + self.graph.zones[current].move_cost
                )
                if cost < distance[previous]:
                    distance[previous] = cost
                    heapq.heappush(
                        pending,
                        (cost, previous),
                    )
        return distance
