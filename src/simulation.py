from .colors import Colors
from typing import Any, List, Dict


class Simulation():
    """
    Handles the simulation of drones moving along paths.
    """

    def __init__(self, paths: list, nb_drones: int) -> None:
        """
        Initialize the simulation with paths and number of drones.

        Args:
            paths (list): List of Path objects representing available paths.
            nb_drones (int): Number of drones to simulate.
        """
        self.paths: list = paths
        self.nb_drones: int = nb_drones
        self.drones: list = []
        self.turn: int = 0
        self.history: list = []

    def colored(self, text: str, color: Any) -> str:
        """
        Return a colored string for console output.

        Args:
            text (str): Text to color.
            color (Colors or None): Color object or RAINBOW.

        Returns:
            str: ANSI colored text.
        """
        if color == Colors.RAINBOW:
            r, g, b = Colors.rainbow_rgb(self.turn * 120)
            return f"\033[38;2;{r};{g};{b}m{text}\033[0m"
        if color:
            return f"{color.ansi}{text}\033[0m"
        return text

    def build_drones(self) -> None:
        """
        Initialize all drones at the start and assign them to paths.
        """
        from .drone import Drone
        for i in range(self.nb_drones):
            best = min(self.paths, key=lambda p: p.total_time())
            best.assign()
            self.drones.append(Drone(i + 1, best))

    def finished(self) -> bool:
        """
        Check if all drones have finished their paths.

        Returns:
            bool: True if all drones are finished, False otherwise.
        """
        return all(d.finished for d in self.drones)

    def link_label(self, drone: Any) -> str:
        """
        Generate a label for a drone currently on a link.

        Args:
            drone (Drone): Drone object.

        Returns:
            str: Link label in the format "L-zoneA-zoneB".
        """
        return (f"L-{drone.current_link.zone_a.name}-"
                f"{drone.current_link.zone_b.name}")

    def simulate_turn(self) -> None:
        """
        Simulate one turn of the simulation, updating drone positions
        and printing the output for this turn.
        """
        print(f"Turn: {self.turn}")
        self.turn += 1

        # Reset phase flags for all drones
        for drone in self.drones:
            drone.reset_phase_flags()

        drones_sorted = sorted(self.drones,
                               key=lambda d: d.position,
                               reverse=True)

        before_pos: Dict[int, int] = {d.id: d.position for d in self.drones}

        for drone in drones_sorted:
            if not drone.finished:
                drone.try_move()

        # Phase 3: build output and history
        output_tokens: List[str] = []
        turn_moves: List[Dict[str, Any]] = []

        for drone in drones_sorted:
            if drone.in_transit:
                conn = self.link_label(drone)
                color = drone.next_zone.color
                output_tokens.append(
                    f"D{drone.id}-{self.colored(conn, color)}"
                )
                turn_moves.append({
                    "drone": drone.id,
                    "on_link": True,
                    "link_a": drone.current_link.zone_a.name,
                    "link_b": drone.current_link.zone_b.name,
                    "to": drone.next_zone.name,
                })
            elif drone.position > before_pos[drone.id]:
                zone = drone.current_zone()
                output_tokens.append(
                    f"D{drone.id}-{self.colored(zone.name, zone.color)}"
                )
                turn_moves.append({
                    "drone": drone.id,
                    "on_link": False,
                    "from": drone.path.zones[before_pos[drone.id]].name,
                    "to": zone.name,
                })

        if output_tokens:
            print(" ".join(output_tokens))
        print()

        self.history.append(turn_moves)

    def run(self) -> None:
        """
        Run the full simulation until all drones finish,
        printing output per turn.
        """
        self.build_drones()

        # Turn 0: show all drones at start
        start_zone = self.drones[0].path.zones[0]
        print(f"Turn: {self.turn}")
        tokens = [f"D{d.id}-{self.colored(start_zone.name, start_zone.color)}"
                  for d in self.drones]
        print(" ".join(tokens))
        print()
        self.history.append([{
            "drone": d.id,
            "on_link": False,
            "from": None,
            "to": start_zone.name,
        } for d in self.drones])
        self.turn += 1

        while not self.finished():
            self.simulate_turn()
