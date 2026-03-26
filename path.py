from zone import Zone
from typing import Any


class Path():
    """
    Represents a route from start to end composed of zones and links.

    Path objects store:
    - Physical structure (zones + links)
    - Traversal cost
    - Flow capacity
    - Assignment statistics for load balancing

    Used by the simulation to distribute drones efficiently.
    """

    def __init__(self, zones: list) -> None:

        """
        Build path from ordered zones.

        Args:
            zones: ordered list of zones forming the path
        """

        self.zones: list = zones
        self.links: dict = {}
        self.inner_zones = [zone for zone in zones
                            if not zone.is_start and not zone.is_end]
        self.length: int = len(zones)
        self.cost: float = sum(zone.zone_cost for zone in zones)
        self.capacity: float = self.compute_capacity()
        self.score: float = self.compute_score()
        self.assigned: int = 0

        self.build_links()

    def assign(self) -> bool:
        """
        Register drone assignment to this path.

        Returns:
            Always True (used for compatibility with selection logic).
        """

        self.assigned += 1

        return True

    def get_link(self, a: 'Zone', b: 'Zone') -> Any | None:
        """
        Retrieve link connecting two zones.

        Args:
            a: first zone
            b: second zone

        Returns:
            Link object or None.
        """

        return self.links.get((a, b)) or self.links.get((b, a))

    def build_links(self) -> None:
        """
        Build internal link mapping for fast lookup.

        Associates each consecutive zone pair with its link.
        """

        for i in range(len(self.zones) - 1):
            a = self.zones[i]
            b = self.zones[i + 1]

            for link in a.links:
                if (link.zone_a == a and link.zone_b == b) or \
                   (link.zone_a == b and link.zone_b == a):
                    self.links[(a, b)] = link

    def total_time(self) -> float:
        """
        Estimate total traversal time considering congestion.

        Combines static path cost with load balancing penalty.

        Returns:
            Estimated traversal time.
        """

        return self.cost + (self.assigned / self.capacity)

    def compute_capacity(self) -> Any:
        """
        Compute bottleneck capacity of the path.

        Capacity is limited by the smallest capacity among:
        - Inner zones
        - Links

        Returns:
            Minimum capacity or infinite if unconstrained.
        """

        zone_caps = [zone.max_drones for zone in self.inner_zones]
        linked_caps = [link.max_drones for link in self.links.values()]

        caps = zone_caps + linked_caps

        if not caps:
            return float("inf")

        return min(caps)

    def compute_score(self) -> float:
        """
        Compute path efficiency score.

        Used to compare paths for selection.

        Returns:
            Score based on length and capacity.
        """

        if self.capacity == 0:
            return float("inf")

        return self.length / self.capacity

    def __lt__(self, other: 'Path') -> Any:
        """
        Comparison operator for path sorting.

        Args:
            other: another Path

        Returns:
            True if this path has lower score.
        """

        return self.score < other.score
