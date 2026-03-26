class Drone():

    def __init__(self, id, path):

        self.id = id
        self.path = path
        self.position = 0
        self.finished = False
        self.in_transit = False
        self.next_zone = None
        self.current_link = None
        self.restricted_penalty = False
        self._landed_this_phase = False  # bloquea movimiento en fase 2 tras aterrizar desde link

    def try_move(self):

        if self.finished:
            return False

        # --- En transito en link ---
        if self.in_transit:

            if not self.next_zone.has_capacity():
                return False

            self.current_link.leave()
            self.current_link = None
            self.next_zone.enter()
            self.position += 1
            self.in_transit = False
            # Bloquear fase 2 siempre que se aterriza desde un link
            self._landed_this_phase = True

            if self.next_zone.zone_type == "restricted":
                self.restricted_penalty = True

            if self.next_zone.is_end:
                self.finished = True

            return True

        # Bloquear si acabo de aterrizar desde link en esta misma fase
        if self._landed_this_phase:
            return False

        # --- Penalizacion restricted ---
        if self.restricted_penalty:

            next_pos = self.position + 1
            if next_pos >= len(self.path.zones):
                return False

            current   = self.path.zones[self.position]
            next_zone = self.path.zones[next_pos]
            link      = self.path.get_link(current, next_zone)

            if not link.has_capacity():
                return False

            self.restricted_penalty = False
            current.leave()
            link.enter()
            self.current_link = link
            self.in_transit   = True
            self.next_zone    = next_zone
            return True

        # --- Movimiento normal ---
        next_pos = self.position + 1
        if next_pos >= len(self.path.zones):
            return False

        current   = self.path.zones[self.position]
        next_zone = self.path.zones[next_pos]
        link      = self.path.get_link(current, next_zone)

        if not link.has_capacity():
            return False

        if next_zone.zone_type == "restricted":
            current.leave()
            link.enter()
            self.current_link = link
            self.in_transit   = True
            self.next_zone    = next_zone
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

    def reset_phase_flags(self):
        self._landed_this_phase = False

    def current_zone(self):
        return self.path.zones[self.position]