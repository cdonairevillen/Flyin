from zone import Zone
from path import Path
from link import Link
from typing import Optional, Any


class Drone():
    """
    Represents a drone moving along a predefined path of zones.

    A drone can be:
    - Inside a zone
    - In transit through a link
    - Finished (reached end zone)

    Movement rules:
    - Links have limited capacity.
    - Zones have limited capacity.
    - Restricted zones apply a movement delay after entry.
    - A drone that just landed from a link cannot move again
      in the same simulation phase.
    """

    def __init__(self, id: int, path: Path) -> None:
        """
        Initialize a drone.

        Args:
            id: Unique drone identifier.
            path: Path the drone will follow.
        """

        self.id: int = id
        self.path: Path = path
        self.position: int = 0
        self.finished: bool = False
        self.in_transit: bool = False
        self.next_zone: Optional[Zone] = None
        self.current_link: Optional[Link] = None
        self.restricted_penalty: bool = False
        self._landed_this_phase: bool = False
        self.transit_time: int = 0

    def try_move(self) -> bool:
        """
        Attempt to move the drone forward.

        Movement priority:
        1. Finish link traversal if in transit.
        2. Apply restricted zone penalty if active.
        3. Perform normal movement.

        Returns:
            True if the drone moved.
            False otherwise.
        """

        if self.finished:
            return False

        # --- Link transit phase ---
        if self.in_transit:

            self.transit_time -= 1

            if self.transit_time > 0:
                return False

            assert self.next_zone is not None
            if not self.next_zone.has_capacity():
                self.transit_time += 1
                return False

            assert self.current_link is not None
            self.current_link.leave()
            self.current_link = None

            self.next_zone.enter()
            self.position += 1
            self.in_transit = False

            # Prevent second movement in same phase
            self._landed_this_phase = True

            if self.next_zone.zone_type == "restricted":
                self.restricted_penalty = True

            if self.next_zone.is_end:
                self.finished = True

            return True

        # --- Restricted zone penalty phase ---
        if self.restricted_penalty:

            next_pos: int = self.position + 1
            if next_pos >= len(self.path.zones):
                return False

            current: Zone = self.path.zones[self.position]
            next_zone: Zone = self.path.zones[next_pos]
            link: Optional[Link] = self.path.get_link(current, next_zone)

            assert link is not None
            if not link.has_capacity():
                return False

            self.restricted_penalty = False

            current.leave()
            link.enter()

            self.current_link = link
            self.in_transit = True
            self.next_zone = next_zone
            self.transit_time = 1

            return True

        # Prevent movement after landing this phase
        if self._landed_this_phase:
            return False

        # --- Normal movement phase ---
        next_pos = self.position + 1
        if next_pos >= len(self.path.zones):
            return False

        current = self.path.zones[self.position]
        next_zone = self.path.zones[next_pos]
        link = self.path.get_link(current, next_zone)

        assert link is not None
        if not link.has_capacity():
            return False

        self.transit_time = 1

        if next_zone.zone_type == "restricted":

            current.leave()
            link.enter()

            self.current_link = link
            self.in_transit = True
            self.next_zone = next_zone
            self.transit_time = 2

            return True

        current.leave()
        link.enter()

        self.current_link = link
        self.in_transit = True
        self.next_zone = next_zone

        return True

    def reset_phase_flags(self) -> None:
        """
        Reset per-turn movement protection flags.

        Allows the drone to move again in the next simulation turn.
        """

        self._landed_this_phase = False

    def current_zone(self) -> Any:
        """
        Return the current zone occupied by the drone.

        Returns:
            Zone object where the drone is located.
        """

        return self.path.zones[self.position]
