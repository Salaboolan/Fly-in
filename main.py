"""Run the Fly-in program."""

import sys

from display import Display
from parser import ParseError, Parser
from simulation import Simulation, SimulationError


class FlyInApp:
    """Run the Fly-in application."""

    def run(self) -> int:
        """Parse, simulate, and display the map."""
        if len(sys.argv) != 2:
            print("Usage: python3 main.py <map_file>")
            return 1

        try:
            graph = Parser(sys.argv[1]).parse()
            turns = Simulation(graph).run()
            Display(graph).show(turns)
        except (ParseError, SimulationError) as error:
            print(f"Error: {error}")
            return 1

        return 0


if __name__ == "__main__":
    raise SystemExit(FlyInApp().run())
