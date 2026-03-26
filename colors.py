import colorsys
import sys
import time
from enum import Enum
from typing import Any


class Colors(Enum):
    """
    Enumeration of colors used in simulation visualization.

    Each color contains:
    - RGB tuple (for graphical rendering)
    - ANSI escape code (for terminal output)

    RAINBOW is a special dynamic color.
    """

    # Format: ((R, G, B), "ANSI")
    DEFAULT = ((200, 200, 200), "\033[0m")
    GREEN = ((80, 200, 120), "\033[32m")
    RED = ((220, 80, 80), "\033[31m")
    BLUE = ((80, 140, 255), "\033[34m")
    YELLOW = ((240, 220, 90), "\033[33m")
    PURPLE = ((180, 120, 255), "\033[35m")
    CRIMSON = ((220, 20, 60), "\033[38;5;197m")
    BLACK = ((0, 0, 0), "\033[30m")
    BROWN = ((165, 42, 42), "\033[33m")
    ORANGE = ((255, 165, 0), "\033[38;5;208m")
    MAROON = ((128, 0, 0), "\033[31m")
    GOLD = ((255, 215, 0), "\033[38;5;220m")
    DARKRED = ((139, 0, 0), "\033[31m")
    VIOLET = ((143, 0, 255), "\033[35m")
    RAINBOW = (None, "DYNAMIC_RAINBOW")

    @property
    def rgb(self) -> Any:
        """
        Returns RGB tuple of the color.

        Returns None for dynamic colors like RAINBOW.
        """
        return self.value[0]

    @property
    def ansi(self) -> Any:
        """
        Returns ANSI escape code for terminal coloring.
        """
        return self.value[1]

    @staticmethod
    def rainbow_rgb(t: float) -> tuple[int, int, int]:
        """
        Generate a rainbow RGB color based on a time/offset value.

        Args:
            t: time or animation offset value

        Returns:
            RGB tuple (0-255 range)
        """

        import colorsys

        hue = (t * 0.002) % 1

        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)

        return (int(r * 255),
                int(g * 255),
                int(b * 255))

    @staticmethod
    def rainbow_text(text: str, offset: float) -> str:
        """
        Apply animated rainbow coloring to text.

        Args:
            text: text to color
            offset: animation phase offset

        Returns:
            ANSI colored string
        """

        out = ""

        for i, c in enumerate(text):

            hue = (i * 0.08 + offset) % 1

            r, g, b = Colors.rainbow_rgb(hue)

            r = int(r * 255)
            g = int(g * 255)
            b = int(b * 255)

            out += f"\033[38;2;{r};{g};{b}m{c}"

        return out + "\033[0m"

    @staticmethod
    def get_rainbow_text(text: str) -> str:
        """
        Apply static rainbow coloring to text.

        Args:
            text: text to color

        Returns:
            ANSI colored string
        """

        rainbow_str = ""
        n = len(text)
        for i, char in enumerate(text):
            hue = i / n
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            r, g, b = [int(x * 255) for x in rgb]

            rainbow_str += f"\033[38;2;{r};{g};{b}m{char}"

        return rainbow_str + "\033[0m"

    @staticmethod
    def animate_rainbow(text: str) -> None:
        """
        Continuously changes text render in terminal.

        Stops when user interrupts execution.
        """

        offset = 0
        try:
            while True:
                output = ""
                for i, char in enumerate(text):
                    hue = (i / 20 + offset) % 1.0
                    r, g, b = [int(x * 255)
                               for x in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
                    output += f"\033[38;2;{r};{g};{b}m{char}"

                sys.stdout.write("\r" + output + "\033[0m")
                sys.stdout.flush()
                offset += 0.05
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("\nAnimation stopped.")
