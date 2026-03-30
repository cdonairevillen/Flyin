from .parser import Parser
from .graph import Graph
from .dijkstra import Dijkstra
from .path import Path
from .simulation import Simulation
from .visualizer import Visualizer
import pygame
import sys


class Fly_in():

    """
    Main class to run the Fly-in drone simulation.

    Handles command-line arguments, file parsing, graph construction,
    pathfinding, simulation execution, and visualization.

    Attributes:
        None (all functionality is executed on initialization).
    """

    def __init__(self) -> None:

        """
        Initialize and run the Fly-in simulation.

        Steps performed:
            1. Check command-line arguments to determine input file.
            2. Load and parse the input file using Parser.
            3. Construct a Graph with zones and connections.
            4. Find all shortest paths between start and end zones using
                Dijkstra.
            5. Create Path objects for each shortest path.
            6. Run the Simulation with the specified number of drones.
            7. Initialize Visualizer to display the simulation.
            8. Enter main loop to handle events and render frames.
            9. Quit Pygame when the simulation ends.

        Raises:
            ValueError: If too many arguments are provided, no paths found,
                        or any critical assertion fails.
            Exception: Catches and prints any other errors occurring during
                       setup or execution.
        """

        try:
            if len(sys.argv) > 2:
                raise ValueError("Too many args detected")

            elif len(sys.argv) == 2:
                entry = sys.argv[1]

            else:
                entry = "input.txt"

            parser = Parser(entry)

            parser.load_file()
            parser.parse()

            graph = Graph(parser.zones, parser.connections)
            dijkstra = Dijkstra(graph)
            assert parser.start_zone is not None
            assert parser.end_zone is not None
            r_paths = dijkstra.find_paths(parser.start_zone, parser.end_zone)
            paths = [Path(p) for p in r_paths]

            if paths == []:
                raise ValueError("Not path found")

            sim = Simulation(paths, parser.nb_drones)
            sim.run()

            vis = Visualizer(sim.history, graph, parser.nb_drones)

            while vis.running:
                vis.key_input()
                vis.render()

            pygame.quit()

        except Exception as e:
            print(f"ERROR: {e}, simulation aborted.")
