from zone import Zone
from path import Path
from link import Link
from typing import Any


class Drone():

    def __init__(self, id: int, path: Path) -> None:

        """
        Initialize a drone.

        Args:
            id: Unique identifier for the drone.
            path: Path object representing the sequence of zones
                  the drone will traverse.

        Attributes:
            position: Current index in the path's zone list.
            finished: True if the drone has reached its end zone.
            in_transit: True if the drone is currently on a link.
            next_zone: Next zone the drone is moving to, if in transit.
            current_link: Current link the drone is traversing, if any.
            restricted_penalty: True if drone is blocked due to entering a
                restricted zone.
            _landed_this_phase: Internal flag to prevent multiple moves in
                the same phase.
        """

        self.id: int = id
        self.path: Path = path
        self.position: int = 0
        self.finished: bool = False
        self.in_transit: bool = False
        self.next_zone: Zone | None = None
        self.current_link: Link | None = None
        self.restricted_penalty: bool = False
        self._landed_this_phase: bool = False

    def try_move(self) -> bool:

        """
        Attempt to move the drone along its path.

        Handles:
            - Moving from zone to link.
            - Moving from link to zone.
            - Restricted zone penalties.
            - Normal movement between zones.

        Returns:
            True if the drone successfully moved this phase, False otherwise.
        """

        if self.finished:
            return False

        # On link
        if self.in_transit:

            assert self.next_zone is not None
            if not self.next_zone.has_capacity():
                return False

            assert self.current_link is not None
            self.current_link.leave()
            self.current_link = None
            self.next_zone.enter()
            self.position += 1
            self.in_transit = False
            self._landed_this_phase = True

            if self.next_zone.zone_type == "restricted":
                self.restricted_penalty = True

            if self.next_zone.is_end:
                self.finished = True

            return True

        # Block if landed from link this phase
        if self._landed_this_phase:
            return False

        # Restricted penalty
        if self.restricted_penalty:

            next_pos = self.position + 1
            if next_pos >= len(self.path.zones):
                return False

            current = self.path.zones[self.position]
            next_zone = self.path.zones[next_pos]
            link = self.path.get_link(current, next_zone)

            assert link is not None
            if not link.has_capacity():
                return False

            self.restricted_penalty = False
            current.leave()
            link.enter()
            self.current_link = link
            self.in_transit = True
            self.next_zone = next_zone
            return True

        # Normal movement
        next_pos = self.position + 1
        if next_pos >= len(self.path.zones):
            return False

        current = self.path.zones[self.position]
        next_zone = self.path.zones[next_pos]
        link = self.path.get_link(current, next_zone)

        assert link is not None
        if not link.has_capacity():
            return False

        if next_zone.zone_type == "restricted":
            current.leave()
            link.enter()
            self.current_link = link
            self.in_transit = True
            self.next_zone = next_zone
            return True

        assert next_zone is not None
        if not next_zone.has_capacity():
            return False

        current.leave()
        link.enter()
        link.leave()
        next_zone.enter()
        self.position += 1

        if next_zone.is_end:
            self.finished = True

        return True

    def reset_phase_flags(self) -> None:

        """
        Reset internal phase flags at the start of each simulation phase.

        Clears the _landed_this_phase flag to allow movement in the next phase.
        """
        self._landed_this_phase = False

    def current_zone(self) -> Any:

        """
        Get the current zone the drone occupies.

        Returns:
            The Zone object corresponding to the drone's current position.
        """
        return self.path.zones[self.position]
