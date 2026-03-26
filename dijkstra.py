import heapq
from zone import Zone


class Dijkstra():
    """
    Modified Dijkstra implementation supporting multi-path discovery.

    Instead of returning only one shortest path, this version tracks
    all predecessors with equal cost to reconstruct every optimal path
    between start and end zones.

    Used for drone path assignment optimisation.
    """

    def __init__(self, graph) -> None:
        """
        Initialize pathfinder.

        Args:
            graph: Graph containing zones and connections.
        """

        self.graph = graph
        self.counter = 0

    def find_paths(self, start: Zone, end: Zone) -> list[list[Zone]]:
        """
        Compute all shortest paths between start and end.

        Uses modified Dijkstra storing multiple parents when
        equal-cost paths are found.

        Args:
            start: starting zone
            end: destination zone

        Returns:
            List of optimal paths (each path is a list of zones).
            Returns empty list if no path exists.
        """

        distances = {
            zone: float('inf') for zone in self.graph.zones.values()
        }

        previous = {
            zone: [] for zone in self.graph.zones.values()
        }

        distances[start] = 0

        pq = [(0, self.counter, start)]
        self.counter += 1
        best_end_distance = float('inf')

        while pq:
            cost, _, current = heapq.heappop(pq)

            if cost > distances[current]:
                continue

            if cost > best_end_distance:
                break

            if current == end and cost < best_end_distance:
                best_end_distance = cost

            for n in current.adjacent:
                new_cost = cost + n.zone_cost

                if new_cost < distances[n]:
                    distances[n] = new_cost
                    previous[n] = [current]
                    heapq.heappush(pq, (new_cost, self.counter,  n))
                    self.counter += 1

                elif new_cost == distances[n]:
                    previous[n].append(current)

        if not previous[end]:
            return []

        return self.build_paths(previous, start, end)

    def build_paths(self,
                    previous: dict[Zone, list[Zone]],
                    start: Zone,
                    node: Zone) -> list[list[Zone]]:
        """
        Reconstruct all optimal paths recursively.

        Walks the predecessor graph built during Dijkstra
        to generate every valid shortest path.

        Args:
            previous: predecessor mapping
            start: starting zone
            node: current reconstruction node

        Returns:
            List of paths from start to node.
        """

        if node == start:
            return [[start]]

        paths = []

        for parent in previous[node]:

            parent_paths = self.build_paths(previous, start, parent)

            for path in parent_paths:
                paths.append(path + [node])

        return paths
