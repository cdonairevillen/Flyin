from zone import Zone
from link import Link


class Graph():
    """
    Represents a network of zones and the links connecting them.

    Handles construction of adjacency lists and links between zones
    based on given connection specifications.
    """

    def __init__(self,
                 zones: dict[str, Zone],
                 connections: list[tuple[str, str, int]]
                 ) -> None:
        """
        Initialize the graph with zones and connections.

        Args:
            zones: Dictionary mapping zone names to Zone objects.
            connections: List of tuples (zone_name_a, zone_name_b, capacity)
                defining the links between zones.
        """

        self.zones: dict[str, Zone] = zones
        self.links: dict[tuple[Zone, Zone], Link] = {}
        self.build_graph(connections)

    def build_graph(self, connections: list[tuple[str, str, int]]
                    ) -> None:
        """
        Build adjacency lists and links for all zones.

        Populates:
        - Each zone's `links` list with Link objects
        - Each zone's `adjacent` list with neighboring zones

        Args:
            connections: List of tuples (zone_name_a, zone_name_b, capacity)
                representing bidirectional links.
        """
        for a, b, capacity in connections:
            zone_a: Zone = self.zones[a]
            zone_b: Zone = self.zones[b]

            link: Link = Link(zone_a, zone_b, capacity)

            if zone_b.zone_type == "blocked":
                continue

            if zone_a.zone_type == "blocked":
                continue

            zone_a.links.append(link)
            zone_a.adjacent.append(zone_b)
            zone_b.links.append(link)
            zone_b.adjacent.append(zone_a)
