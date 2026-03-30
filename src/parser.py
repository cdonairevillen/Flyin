from typing import List
from .zone import Zone
from .colors import Colors


class Parser():

    """
    Parser for a fly-in configuration file.

    Handles loading the file, parsing zones, connections,
    metadata, and number of drones.
    """

    def __init__(self, filepath: str) -> None:

        """
        Parser for a fly-in configuration file.

        Handles loading the file, parsing zones, connections, metadata,
        and number of drones.
        """

        self.filepath = filepath
        self.nb_drones = 0

        self.lines: List[str] = []
        self.zones: dict[str, Zone] = {}
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None
        self.connections: list[tuple[str, str, int]] = []
        self.VALID_ZONE_TYPES = {
            "normal",
            "priority",
            "restricted",
            "blocked"
            }

        self.check_start: int = 0
        self.check_end: int = 0
        self.nb_drones_defined: bool = False
        self.valid: bool = False

    def load_file(self) -> None:

        """Load the file content into `self.lines`,
        ignoring empty lines and comments."""

        with open(self.filepath, "r") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                self.lines.append(line)

    def parse_metadata(self, meta: str) -> dict:

        """
        Parse a metadata string into a dictionary.

        Args:
            meta: Metadata string (e.g., 'zone=priority color=red')

        Returns:
            Dictionary of metadata key-value pairs.
        """

        result = {}

        for item in meta.split():
            if "=" not in item:
                raise ValueError(f"Invalid metadata: {item}")

            key, value = item.split("=", 1)

            if key in result:
                raise ValueError(f"Duplicated metadata key:{key}")
            result[key] = value
        return result

    def apply_metadata(self, zone: Zone, metadata: dict) -> None:

        """
        Parse a metadata string into a dictionary.

        Args:
            meta: Metadata string (e.g., 'zone=priority color=red')

        Returns:
            Dictionary of metadata key-value pairs.
        """

        if "zone" in metadata:
            ztype = metadata['zone']

            if ztype not in self.VALID_ZONE_TYPES:

                raise ValueError("Invalid zone type", ztype)

            zone.zone_type = ztype

        if "color" in metadata:
            try:

                zone.color = Colors[metadata["color"].upper()]

            except KeyError:

                zone.color = Colors['DEFAULT']
                print(f"Invalid color: {metadata['color']}"
                      " Setted to the DEFAULT color")
        if "max_drones" in metadata:
            try:
                value = int(metadata["max_drones"])

                if value <= 0:
                    raise ValueError

                zone.max_drones = value

            except ValueError:
                raise ValueError(
                    f"Invalid max_drones value: {metadata['max_drones']}")

    def parse_zone(self, line: str, zone_type: str) -> None:

        """
        Parse a line defining a zone and create a Zone object.

        Args:
            line: The line from the file.
            zone_type: Type of zone ('start', 'end', or 'hub').
        """

        content = line.split(":", 1)[1].strip()
        metadata = {}

        if "[" in content:
            main, meta = content.split("[", 1)
            meta = meta.replace("]", "")
            metadata = self.parse_metadata(meta)

        else:
            main = content

        parts = main.split()

        if len(parts) != 3:
            raise ValueError(f"Invalid zone format: {line}")

        name = parts[0].strip()
        x = int(parts[1])
        y = int(parts[2])

        if name in self.zones:
            raise ValueError(f"Duplicated zone:{name}")

        zone = Zone(name, x, y)
        self.apply_metadata(zone, metadata)

        if zone_type == "start":
            zone.is_start = True
            if zone.max_drones == 1:
                zone.max_drones = self.nb_drones
            self.start_zone = zone

        if zone_type == "end":
            zone.is_end = True
            if zone.max_drones == 1:
                zone.max_drones = self.nb_drones
            self.end_zone = zone

        self.zones[name] = zone

    def parse_connection(self, line: str) -> None:

        """
        Parse a line defining a zone and create a Zone object.

        Args:
            line: The line from the file.
            zone_type: Type of zone ('start', 'end', or 'hub').
        """

        content = line.split(":", 1)[1].strip()
        metadata = {}
        if "[" in content:

            main, meta = content.split("[")

            meta = meta.replace("]", "")
            metadata = self.parse_metadata(meta)

        else:
            main = content

        a, b = main.split("-")
        a = a.strip()
        b = b.strip()

        if a not in self.zones or b not in self.zones:
            raise ValueError(f"Connection uses unknown zone: {a}-{b}")

        if a == b:
            raise ValueError(f"Self connection not allowed: {a}-{b}")

        capacity = int(metadata.get("max_link_capacity", 1))

        if capacity <= 0:
            raise ValueError(f"Invalid max_link_capacity between {a}-{b}")

        key = tuple(sorted((a, b)))

        if any((key[0], key[1]) == (x, y) for x, y, _ in self.connections):
            raise ValueError(f"Duplicated connection detected: {a}-{b}")

        self.connections.append((a, b, capacity))

    def get_line_type(self, line: str) -> str:

        """
        Determine the type of a line.

        Args:
            line: The line from the file.

        Returns:
            A string indicating the line type:
            'drones', 'start', 'hub', 'end', 'connection'.
        """

        if line.startswith("nb_drones:"):
            return "drones"
        if line.startswith("start_hub:"):
            self.check_start += 1
            return "start"
        if line.startswith("hub:"):
            return "hub"
        if line.startswith("end_hub:"):
            self.check_end += 1
            return "end"
        if line.startswith("connection:"):
            return "connection"

        raise ValueError(f"Invalid line format: {line}")

    def parse_drones(self, line: str) -> None:

        """
        Parse a line defining the number of drones.

        Args:
            line: The line from the file.
        """

        try:
            self.nb_drones = int(line.split(":")[1].strip())
            if self.nb_drones <= 0:
                raise ValueError

        except ValueError:
            raise ValueError(f"Invalid number of drones: {line}")

    def parse(self) -> None:

        """
        Execute the full parsing process over all loaded lines.

        Raises:
            ValueError: If any parsing rule is violated
            (e.g., missing start/end zone, duplicates, invalid formats).
        """

        for line in self.lines:
            line_type = self.get_line_type(line)

            if not self.nb_drones_defined:

                if line_type != "drones":
                    raise ValueError(
                        "nb_drones must be the first config entry")

                self.parse_drones(line)
                self.nb_drones_defined = True
                continue

            if self.check_start > 1:
                raise ValueError("Multiples entries detected")

            if self.check_end > 1:
                raise ValueError("Multiples exits detected")

            if line_type == "drones":
                raise ValueError("Multiple nb_drones entries detected")

            elif line_type in ("start", "hub", "end"):
                self.parse_zone(line, line_type)

            elif line_type == "connection":
                self.parse_connection(line)

        if self.start_zone is None:
            raise ValueError("Missing start zone")

        if self.end_zone is None:
            raise ValueError("Missing end zone")

        if self.nb_drones > 0:
            if self.start_zone.max_drones < self.nb_drones:
                raise ValueError(
                    f"start_hub '{self.start_zone.name}' max_drones="
                    f"{self.start_zone.max_drones} is less than "
                    f"nb_drones={self.nb_drones}"
                )
            if self.end_zone.max_drones < self.nb_drones:
                raise ValueError(
                    f"end_hub '{self.end_zone.name}' max_drones="
                    f"{self.end_zone.max_drones} is less than "
                    f"nb_drones={self.nb_drones}"
                )
