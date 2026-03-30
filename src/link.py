from dataclasses import dataclass
from typing import Any


@dataclass
class Link():
    """
    Represents a connection between two zones.

    Links act as transit buffers when a drone cannot directly
    enter the next zone. They also enforce capacity limits to
    simulate congestion between hubs.
    """

    zone_a: Any
    zone_b: Any

    max_drones: int = 1
    current_drones: int = 0

    def __hash__(self) -> int:
        """
        Allow link usage in sets and dictionaries.

        Returns:
            Hash based on connected zones.
        """

        return hash((self.zone_a, self.zone_b))

    def has_capacity(self) -> bool:
        """
        Check if link can accept another drone.

        Returns:
            True if link is not full.
        """

        return self.current_drones < self.max_drones

    def enter(self) -> None:
        """
        Register a drone entering the link.
        """

        self.current_drones += 1

    def leave(self) -> None:
        """
        Register a drone leaving the link.
        """

        self.current_drones -= 1
