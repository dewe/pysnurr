import itertools
import sys
import threading
import time


class Snurr:
    # Spinner style constants
    DOTS = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"  # Default braille dots
    CLASSIC = "/-\\|"  # Classic ASCII spinner
    BAR = "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁"  # ASCII loading bar
    EARTH = "🌍🌎🌏"  # Earth rotation
    MOON = "🌑🌒🌓🌔🌕🌖🌗🌘"  # Moon phases
    CLOCK = "🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛"  # Clock rotation
    ARROWS = "←↖↑↗→↘↓↙"  # Arrow rotation
    DOTS_BOUNCE = ".oO°Oo."  # Bouncing dots
    TRIANGLES = "◢◣◤◥"  # Rotating triangles
    # HEARTS = "💛💙💜💚❤️"  # Colorful hearts
    HEARTS = "💛💙💜💚"  # Colorful hearts

    def __init__(self, delay=0.1, symbols=CLASSIC, append=False):
        """
        Initialize the spinner.

        Args:
            delay (float): Time between spinner updates in seconds
            symbols (str): String containing spinner animation frames
            append (bool): If True, adds space and shows spinner at line end
        """
        self.symbols = symbols
        self.delay = delay
        self.busy = False
        self.append = append
        self.spinner_thread = None
        self._screen_lock = threading.Lock()
        self._current_symbol = None  # Track current symbol
        # ANSI escape codes for cursor visibility
        self.hide_cursor = "\033[?25l"
        self.show_cursor = "\033[?25h"

    def _get_display_width(self, text):
        """Calculate the display width of a string.

        Args:
            text (str): The text to calculate width for

        Returns:
            int: The display width of the text
        """
        return len(text.encode("utf-16-le")) // 2

    def _erase_current(self, width):
        """Erase the current spinner using three-step sequence.

        Args:
            width (int): The width of text to erase
        """
        if self.append:
            width += 1  # Account for the space
        sys.stdout.write("\b" * width)  # Move back
        sys.stdout.write(" " * width)  # Clear
        sys.stdout.write("\b" * width)  # Move back

    def _spin(self):
        """Internal method that handles the spinning animation."""
        spinner_cycle = itertools.cycle(self.symbols)
        while self.busy:
            with self._screen_lock:
                next_symbol = next(spinner_cycle)

                # First erase the previous symbol if it exists
                if self._current_symbol:
                    width = self._get_display_width(self._current_symbol)
                    self._erase_current(width)

                # Write the new symbol
                if self.append:
                    sys.stdout.write(" " + next_symbol)
                else:
                    sys.stdout.write(next_symbol)
                sys.stdout.flush()

                self._current_symbol = next_symbol
            time.sleep(self.delay)

    def start(self):
        """Start the spinner animation in a non-blocking way."""
        self.busy = True
        sys.stdout.write(self.hide_cursor)  # Hide cursor when starting
        sys.stdout.flush()
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()

    def stop(self):
        """Stop the spinner animation."""
        self.busy = False
        if self.spinner_thread is not None:
            self.spinner_thread.join()
        with self._screen_lock:
            # Use three-step erasing for the last symbol
            if self._current_symbol:
                width = self._get_display_width(self._current_symbol)
                self._erase_current(width)
            sys.stdout.write(self.show_cursor)  # Show cursor
            sys.stdout.flush()
            self._current_symbol = None

    def write(self, text, end="\n"):
        """Write text to stdout safely.

        Thread-safe write that won't interfere with the spinner animation.

        Args:
            text (str): The text to write
            end (str): String appended after the text, defaults to newline
        """
        with self._screen_lock:
            # Clear current spinner using three-step erasing
            if self._current_symbol:
                width = self._get_display_width(self._current_symbol)
                self._erase_current(width)

            # Write the text
            sys.stdout.write(str(text) + end)
            sys.stdout.flush()
