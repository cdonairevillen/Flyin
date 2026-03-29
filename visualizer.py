import pygame
from colors import Colors
from graph import Graph
from zone import Zone
from link import Link


class VisualDrone():

    """
    Represents a drone in the visualization system.
    """

    def __init__(self, id: int, start_zone: Zone) -> None:

        """
        Initialize a VisualDrone instance.

        Args:
            id (int): Unique drone identifier.
            start_zone (Zone): Zone where the drone starts.
        """

        self.id: int = id
        self.current: Zone = start_zone
        self.target: Zone = start_zone
        self.progress: float = 1.0
        self.moving: bool = False
        self.visible: bool = False

        # Link state
        self.on_link: bool = False
        self.leaving_link: bool = False
        self.link_zone_a: Zone | None = None
        self.link_zone_b: Zone | None = None


class Visualizer():

    """
    Visualizer class for simulating and rendering drone movements in a graph.

    Manages drone states, positions, link transitions, and drawing of zones,
    links, and drones using Pygame. Supports animations turn by turn.
    """

    def __init__(self, history: dict | list,
                 graph: Graph, nb_drones: int) -> None:

        """
        Initialize the visualizer.

        Args:
            history (dict | list): Drone movement history.
            graph (Graph): Graph containing zones and links.
            nb_drones (int): Number of drones to simulate.
        """

        pygame.init()
        self.history: dict | list = history
        self.graph: Graph = graph
        self.width: int = 1920
        self.height: int = 1000

        xs: list = [z.x for z in self.graph.zones.values()]
        ys: list = [z.y for z in self.graph.zones.values()]
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-in Drone Simulator")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 28)

        self.running = True
        self.turn = 0
        self.animating = False

        start = next(z for z in graph.zones.values() if z.is_start)
        self.drones = {i: VisualDrone(i, start)
                       for i in range(1, nb_drones + 1)}
        self.zone_occupancy: dict = {}

    def scale(self, x: float, y: float) -> tuple[float, float]:

        """
        Scale zone coordinates to screen coordinates.

        Args:
            x (float): Original x-coordinate.
            y (float): Original y-coordinate.

        Returns:
            tuple[float, float]: Scaled (x, y) coordinates for rendering.
        """

        gw = max(self.max_x - self.min_x, 1)
        gh = max(self.max_y - self.min_y, 1)
        s = min((self.width - 200) / gw, (self.height - 200) / gh)
        return (x - self.min_x) * s + 100, (y - self.min_y) * s + 100

    def zone_slot(self, zone: Zone, idx: int) -> tuple[float, float]:

        """
        Calculate the slot offset for a drone in a zone to avoid overlap.

        Args:
            zone (Zone): The zone in which to place the drone.
            idx (int): Index of the drone within the zone.

        Returns:
            tuple[float, float]: Offset (x, y) relative to the zone center.
        """

        size = 50
        max_slots = min(zone.max_drones, 9)
        cols = min(3, max_slots)
        rows = (max_slots + cols - 1) // cols
        i = idx % max_slots
        r, c = i // cols, i % cols
        return (size / (cols+1) * (c+1) - size/2,
                size / (rows+1) * (r+1) - size/2)

    def link_point(self, zone_a: Zone,
                   zone_b: Zone,
                   drone_id: int,
                   capacity: int) -> tuple[float, float]:

        """
        Calculate the position of a drone along a link between two zones.

        Args:
            zone_a (Zone): Start zone of the link.
            zone_b (Zone): End zone of the link.
            drone_id (int): Drone identifier.
            capacity (int): Maximum number of drones allowed on the link.

        Returns:
            tuple[float, float]: Screen coordinates of the drone on the link.
        """
        x1, y1 = self.scale(zone_a.x, zone_a.y)
        x2, y2 = self.scale(zone_b.x, zone_b.y)
        dx, dy = x2-x1, y2-y1
        length = (dx*dx + dy*dy)**0.5 or 1
        px, py = -dy/length, dx/length
        mx, my = (x1+x2)/2, (y1+y2)/2
        n = min(capacity, 5)
        offset = (drone_id % n - (n-1)/2) * 12
        return mx + px*offset, my + py*offset

    def get_link(self, zone_a: Zone, zone_b: Zone) -> Link | None:

        """
        Retrieve the link object connecting two zones.

        Args:
            zone_a (Zone): First zone.
            zone_b (Zone): Second zone.

        Returns:
            Link | None: The link object if found, else None.
        """

        for link in zone_a.links:
            if link.zone_a == zone_b or link.zone_b == zone_b:
                return link
        return None

    def ease(self, t: float) -> float:

        """
        Smooth easing function for animation transitions.

        Args:
            t (float): Normalized progress (0.0 to 1.0).

        Returns:
            float: Adjusted progress after easing.
        """
        return t * t * (3 - 2*t)

    def zone_pos(self, zone: Zone, drone: VisualDrone) -> tuple[float, float]:

        """
        Compute screen position of a drone in a zone, including slot offsets.

        Args:
            zone (Zone): Zone where the drone is located.
            drone (VisualDrone): Drone to position.

        Returns:
            tuple[float, float]: Screen coordinates of the drone.
        """

        occ = self.zone_occupancy.get(zone.name, [])
        try:
            idx = occ.index(drone)
        except ValueError:
            idx = 0
        zx, zy = self.scale(zone.x, zone.y)
        sx, sy = self.zone_slot(zone, idx)
        return zx+sx, zy+sy

    def clear_link(self, drone: VisualDrone) -> None:

        """
        Reset a drone's link state after finishing a link traversal.

        Args:
            drone (VisualDrone): Drone whose link state will be cleared.
        """
        drone.on_link = False
        drone.leaving_link = False
        drone.link_zone_a = None
        drone.link_zone_b = None

    def draw_links(self) -> None:

        """Draw all links between zones on the screen."""
        for zone in self.graph.zones.values():
            x1, y1 = self.scale(zone.x, zone.y)
            for link in zone.links:
                other = link.zone_b if link.zone_a == zone else link.zone_a
                x2, y2 = self.scale(other.x, other.y)
                pygame.draw.line(self.screen, (80, 80, 80),
                                 (x1, y1), (x2, y2), 2)
                n = min(link.max_drones, 5)
                if n > 0:
                    dx, dy = x2-x1, y2-y1
                    ln = (dx*dx+dy*dy)**0.5 or 1
                    px, py = -dy/ln, dx/ln
                    mx, my = (x1+x2)/2, (y1+y2)/2
                    for i in range(n):
                        off = (i-(n-1)/2)*12
                        pygame.draw.circle(self.screen, (90, 90, 90),
                                           (int(mx+px*off), int(my+py*off)),
                                           3, 1)

    def draw_zones(self) -> None:

        """Draw all zones and their drone slots on the screen."""
        size = 50
        for zone in self.graph.zones.values():
            x, y = self.scale(zone.x, zone.y)
            color = (Colors.rainbow_rgb(pygame.time.get_ticks())
                     if zone.color == Colors.RAINBOW else zone.rgb)
            pygame.draw.rect(self.screen, color,
                             (x-size//2, y-size//2, size, size))
            max_slots = min(zone.max_drones, 9)
            cols = min(3, max_slots)
            rows = (max_slots+cols-1)//cols
            for i in range(max_slots):
                r, c = i//cols, i % cols
                sx = size/(cols+1)*(c+1) - size/2
                sy = size/(rows+1)*(r+1) - size/2
                pygame.draw.circle(self.screen, (70, 70, 70),
                                   (int(x+sx), int(y+sy)), 4, 1)

    def draw_drones(self) -> None:

        """Draw all visible drones on the screen."""
        for drone in self.drones.values():
            if not drone.visible:
                continue
            x, y = self.drone_position(drone)
            pygame.draw.circle(self.screen,
                               (255, 210, 0),
                               (int(x), int(y)), 8)
            pygame.draw.circle(self.screen,
                               (255, 255, 255),
                               (int(x), int(y)), 8, 2)

    def drone_position(self, drone: VisualDrone) -> tuple[float, float]:

        """
        Calculate the current screen position of a drone,
        considering movement state.

        Args:
            drone (VisualDrone): Drone to calculate position for.

        Returns:
            tuple[float, float]: Current screen coordinates of the drone.
        """

        # staying
        if not drone.moving:
            if drone.on_link:
                assert drone.link_zone_a is not None
                assert drone.link_zone_b is not None
                link = self.get_link(drone.link_zone_a, drone.link_zone_b)
                cap = link.max_drones if link else 1
                return self.link_point(drone.link_zone_a, drone.link_zone_b,
                                       drone.id, cap)
            return self.zone_pos(drone.current, drone)

        t = self.ease(drone.progress)

        # Zone to link
        if drone.on_link and not drone.leaving_link:
            assert drone.link_zone_a is not None
            assert drone.link_zone_b is not None
            link = self.get_link(drone.link_zone_a, drone.link_zone_b)
            cap = link.max_drones if link else 1
            lx, ly = self.link_point(drone.link_zone_a, drone.link_zone_b,
                                     drone.id, cap)
            x1, y1 = self.zone_pos(drone.current, drone)
            return x1 + (lx-x1)*t, y1 + (ly-y1)*t

        # Link to zone
        if drone.leaving_link:
            assert drone.link_zone_a is not None
            assert drone.link_zone_b is not None
            link = self.get_link(drone.link_zone_a, drone.link_zone_b)
            cap = link.max_drones if link else 1
            lx, ly = self.link_point(drone.link_zone_a, drone.link_zone_b,
                                     drone.id, cap)
            x2, y2 = self.zone_pos(drone.target, drone)
            return lx + (x2-lx)*t, ly + (y2-ly)*t

        # Zone to zone movement
        x1, y1 = self.zone_pos(drone.current, drone)
        x2, y2 = self.zone_pos(drone.target,  drone)

        link = self.get_link(drone.current, drone.target)
        if link:
            cap = link.max_drones
            lx, ly = self.link_point(drone.current,
                                     drone.target,
                                     drone.id, cap)
            if drone.progress < 0.5:
                t2 = self.ease(drone.progress * 2)
                return x1+(lx-x1)*t2, y1+(ly-y1)*t2
            else:
                t2 = self.ease((drone.progress-0.5)*2)
                return lx+(x2-lx)*t2, ly+(y2-ly)*t2

        return x1+(x2-x1)*t, y1+(y2-y1)*t

    def render(self) -> None:

        """
        Update the simulation, animate drones, and render the current frame.
        """

        dt = self.clock.tick(60) / 1000

        if self.animating:
            all_done = True
            for drone in self.drones.values():
                if not drone.moving:
                    continue
                drone.progress = min(1.0, drone.progress + dt * 2)
                if drone.progress < 1.0:
                    all_done = False
                else:
                    if drone.on_link and not drone.leaving_link:
                        pass
                    else:
                        drone.current = drone.target
                        self.clear_link(drone)
                    drone.moving = False

            if all_done:
                self.animating = False

        # Zone occupancy
        zone_occupancy: dict[str, list[VisualDrone]] = {}
        for drone in self.drones.values():
            if not drone.visible or drone.on_link or drone.leaving_link:
                continue
            zone = (drone.target if drone.moving and drone.progress > 0.5
                    else drone.current)
            zone_occupancy.setdefault(zone.name, []).append(drone)
        self.zone_occupancy = zone_occupancy

        self.screen.fill((30, 30, 30))
        self.draw_links()
        self.draw_zones()
        self.draw_drones()
        text = self.font.render(f"Turn: {self.turn}", True, (255, 255, 255))
        self.screen.blit(text, (20, 20))
        pygame.display.flip()

    def start_turn(self) -> None:

        """
        Initialize drone movements for the current turn based on the history.
        """

        if self.turn >= len(self.history):
            return

        for move in self.history[self.turn]:

            drone = self.drones[move["drone"]]
            drone.visible = True

            if move["on_link"]:
                # Zone to link
                zone_a = self.graph.zones[move["link_a"]]
                zone_b = self.graph.zones[move["link_b"]]

                drone.current = zone_a
                drone.target = zone_b
                drone.link_zone_a = zone_a
                drone.link_zone_b = zone_b
                drone.on_link = True
                drone.leaving_link = False
                drone.progress = 0
                drone.moving = True

            else:
                to_zone = self.graph.zones[move["to"]]

                if drone.on_link:
                    # Link to zone
                    assert drone.link_zone_a is not None
                    assert drone.link_zone_b is not None
                    drone.leaving_link = True
                    drone.on_link = False
                else:
                    # Movement zone to zone
                    self.clear_link(drone)

                drone.target = to_zone
                drone.progress = 0
                drone.moving = True

                # Spawn
                if not move.get("from") and not drone.leaving_link:
                    drone.current = to_zone
                    drone.progress = 1.0
                    drone.moving = False

        self.animating = True

    def key_input(self) -> None:

        """
        Handle Pygame events, including quit and key presses.
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.animating:
                    if self.turn >= len(self.history) - 1:
                        self.running = False
                    else:
                        self.turn += 1
                        self.start_turn()
                if event.key == pygame.K_ESCAPE:
                    self.running = False
