"""Display simulation turns in the terminal."""

import os
import sys

from models import Graph


class Display:
    """Print drone movements with colors."""

    COLORS = {
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "purple": 35,
        "magenta": 35,
        "cyan": 36,
        "gray": 37,
        "orange": 33,
        "brown": 33,
        "lime": 92,
        "gold": 93,
    }

    def __init__(self, graph: Graph) -> None:
        """Store graph and check terminal color support."""
        self.graph = graph
        self.color = (
            sys.stdout.isatty()
            and os.getenv("NO_COLOR") is None
        )

    def show(self, turns: list[list[str]]) -> None:
        """Print one simulation turn per line."""
        for turn in turns:
            print(" ".join(
                self._color(move)
                for move in turn
            ))

    def _color(self, move: str) -> str:
        """Add destination color to a movement."""
        if not self.color:
            return move

        target = move.rsplit("-", 1)[-1]
        zone = self.graph.zones.get(target)

        if zone is None or zone.color is None:
            return move

        code = self.COLORS.get(zone.color.lower(), 37)
        return f"\033[{code}m{move}\033[0m"
