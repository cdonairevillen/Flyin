from parser import Parser
from graph import Graph
from dijkstra import Dijkstra
from path import Path
from simulation import Simulation
from visualizer import Visualizer
import pygame
import sys


class Fly_in():

    def __init__(self):

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
