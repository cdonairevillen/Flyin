from zone import Zone
from path import Path
from link import Link


class Drone():

    def __init__(self, id: int, path: Path) -> None:

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

        if self.finished:
            return False

        # On link
        if self.in_transit:

            if not self.next_zone.has_capacity():
                return False

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

        if not link.has_capacity():
            return False

        if next_zone.zone_type == "restricted":
            current.leave()
            link.enter()
            self.current_link = link
            self.in_transit = True
            self.next_zone = next_zone
            return True

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
        self._landed_this_phase = False

    def current_zone(self) -> Zone:
        return self.path.zones[self.position]
