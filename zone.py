from dataclasses import dataclass, field
from colors import Colors


@dataclass
class Zone():
    """
    Represents a node (hub) in the simulation graph.

    A zone can:
    - Connect to other zones through links
    - Hold drones depending on its capacity
    - Affect pathfinding through zone_cost
    - Have special types (restricted, blocked, priority)

    Used both by pathfinding and simulation movement logic.
    """

    from link import Link
    name: str
    x: int
    y: int

    zone_type: str = "normal"

    color: Colors | None = None

    max_drones: int = 1
    current_drones: int = 0
    is_start: bool = False
    is_end: bool = False
    links: list["Link"] = field(default_factory=list)
    adjacent: list["Zone"] = field(default_factory=list)

    def __hash__(self) -> int:
        """
        Allow zone usage in sets and dicts.

        Returns:
            Hash based on unique zone name.
        """
        return hash(self.name)

    @property
    def zone_cost(self) -> float:
        """
        Cost used for pathfinding algorithms.

        Returns:
            float cost modifier:
            - blocked → infinite cost
            - restricted → penalty cost
            - priority → reduced cost
            - normal → base cost
        """
        if self.zone_type == "blocked":
            return float('inf')
        if self.zone_type == "restricted":
            return 2
        if self.zone_type == "priority":
            return 0.9
        else:
            return 1

    @property
    def rgb(self) -> tuple[int, int, int]:
        """
        Returns RGB color for visualization.

        Returns:
            RGB tuple or default gray.
        """

        if self.color and self.color.rgb:

            return self.color.rgb

        return (200, 200, 200)

    def is_blocked(self) -> bool:
        """
        Check if zone is blocked.

        Returns:
            True if zone cannot be traversed.
        """

        return self.zone_type == "blocked"

    def has_capacity(self) -> bool:
        """
        Check if zone can accept a drone.

        Start and end zones have unlimited capacity.

        Returns:
            True if drone can enter.
        """

        if self.is_start or self.is_end:
            return True

        return self.current_drones < self.max_drones

    def enter(self) -> None:
        """
        Register a drone entering the zone.

        Start and end zones do not track occupancy.
        """

        if not self.is_start and not self.is_end:
            self.current_drones += 1

    def leave(self) -> None:
        """
        Register a drone leaving the zone.

        Start and end zones do not track occupancy.
        """

        if not self.is_start and not self.is_end:
            self.current_drones -= 1