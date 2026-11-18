"""Data classes for Fly-in Hubs, Connections, Drones, and Graphs."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Zone:
    """Represents a zone in the graph."""
    name: str
    x: int
    y: int
    kind: str = "normal"
    color: str | None = None
    capacity: int = 1
    is_start: bool = False
    is_end: bool = False

    @property
    def move_cost(self) -> int:
        """Return the movement cost."""
        return 2 if self.kind == "restricted" else 1


@dataclass(frozen=True)
class Connection:
    """Represents a connection between two zones."""
    first: str
    second: str
    capacity: int = 1

    @property
    def name(self) -> str:
        """Return the connection name."""
        return f"{self.first}-{self.second}"

    @property
    def key(self) -> frozenset[str]:
        """Return a unique key for the connection."""
        return frozenset((self.first, self.second))

    def other(self, zone: str) -> str:
        """Return the zone on the other end of the connection."""
        if zone == self.first:
            return self.second
        if zone == self.second:
            return self.first
        raise ValueError("Zone is not part of the connection.")


@dataclass
class Drone:
    """Represents a drone."""
    identifier: int
    zone: str
    transit_to: str | None = None


@dataclass
class Graph:
    """Store the complete map."""
    drone_count: int
    zones: dict[str, Zone]
    connections: dict[frozenset[str], Connection]
    start: str
    end: str
    neighbors: dict[str, list[Connection]] = field(init=False)

    def __post_init__(self) -> None:
        """Build the neighbor list."""
        self.neighbors = {name: [] for name in self.zones}

        for connection in self.connections.values():
            self.neighbors[connection.first].append(connection)
            self.neighbors[connection.second].append(connection)

    def capacity(self, name: str) -> float:
        """Return the capacity of a zone."""
        zone = self.zones[name]

        if zone.is_start or zone.is_end:
            return float("inf")
        return float(zone.capacity)
