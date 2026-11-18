"""Parse Fly-in map files."""

from models import Connection, Graph, Zone


class ParseError(ValueError):
    """Represent an input file error."""


class Parser:
    """Parse and validate a Fly-in map."""

    def __init__(self, filename: str) -> None:
        """Initialize a Parser instance."""
        self.filename = filename
        self.drones = 0
        self.zones: dict[str, Zone] = {}
        self.connections: dict[frozenset[str], Connection] = {}
        self.start: str | None = None
        self.end: str | None = None

    def parse(self) -> Graph:
        """Read the file and return a Graph."""
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except OSError as error:
            raise ParseError(str(error)) from error

        first = True

        for number, raw in enumerate(lines, 1):
            line = raw.split("#", 1)[0].strip()

            if not line:
                continue
            if first:
                self._drones(line, number)
                first = False
            elif line.startswith("connection:"):
                self._connection(line, number)
            elif line.startswith(("hub:", "start_hub:", "end_hub:")):
                self._zone(line, number)
            else:
                self._error(number, "Invalid line")

        if first:
            raise ParseError("empty file")
        if self.start is None:
            raise ParseError("missing start_hub")
        if self.end is None:
            raise ParseError("missing end_hub")

        return Graph(
            self.drones,
            self.zones,
            self.connections,
            self.start,
            self.end
        )

    def _drones(self, line: str, number: int) -> None:
        """Parse drone count."""
        if not line.startswith("nb_drones:"):
            self._error(number, "First line must be nb_drones: <number>")
        value = line.split(":", 1)[1].strip()
        try:
            self.drones = int(value)
        except ValueError:
            self._error(number, "Invalid drone count")
        if self.drones <= 0:
            self._error(number, "Drone count must be positive")

    def _zone(self, line: str, number: int) -> None:
        """Parse one zone."""
        prefix, text = line.split(":", 1)
        main, data = self._metadata(text.strip(), number)
        parts = main.split()

        if len(parts) != 3:
            self._error(number, "Invalid zone")
        name = parts[0]
        if "-" in name:
            self._error(number, "Dash not allowed in zone name")
        if name in self.zones:
            self._error(number, "Duplicate zone")

        try:
            x, y = int(parts[1]), int(parts[2])
        except ValueError:
            self._error(number, "Invalid coordinates")
        kind = data.get("zone", "normal")
        if kind not in {"normal", "blocked", "restricted", "priority"}:
            self._error(number, "Invalid zone type")
        capacity = 1
        if prefix == "hub":
            capacity = self._capacity(
                data.get("max_drones", "1"), number
            )
        if prefix == "start_hub":
            if self.start is not None:
                self._error(number, "Duplicate start_hub")
            self.start = name
        if prefix == "end_hub":
            if self.end is not None:
                self._error(number, "Duplicate end_hub")
            self.end = name

        self.zones[name] = Zone(
            name,
            x,
            y,
            kind,
            data.get("color"),
            capacity,
            prefix == "start_hub",
            prefix == "end_hub",
        )

    def _connection(self, line: str, number: int) -> None:
        """Parse one connection."""
        text = line.split(":", 1)[1].strip()
        main, data = self._metadata(text, number)
        parts = main.split("-")

        if len(parts) != 2:
            self._error(number, "Invalid connection")
        first, second = parts
        if first not in self.zones or second not in self.zones:
            self._error(number, "Unknown zone in connection")
        key = frozenset((first, second))
        if key in self.connections:
            self._error(number, "Duplicate connection")
        capacity = self._capacity(
            data.get("max_link_capacity", "1"),
            number,
        )
        self.connections[key] = Connection(first, second, capacity)

    def _metadata(self, text: str, number: int) -> tuple[str, dict[str, str]]:
        """Extract optional metadata."""
        if "[" not in text:
            if "]" in text:
                self._error(number, "Invalid metadata")
            return text, {}
        if not text.endswith("]") or text.count("[") != 1:
            self._error(number, "Invalid metadata")

        main, raw = text[:-1].split("[", 1)
        data: dict[str, str] = {}
        for item in raw.split():
            if item.count("=") != 1:
                self._error(number, "Invalid metadata")
            key, value = item.split("=", 1)
            if not key or not value or key in data:
                self._error(number, "Invalid metadata")
            data[key] = value
        return main.strip(), data

    def _capacity(self, value: str, number: int) -> int:
        """Return a positive capacity."""
        try:
            capacity = int(value)
        except ValueError:
            self._error(number, "Invalid capacity")
        if capacity <= 0:
            self._error(number, "capacity must be positive")
        return capacity

    def _error(self, number: int, msg: str) -> None:
        """Raise an error containing the line number and issue."""
        raise ParseError(f"line {number}: {msg}")
