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
    HEARTS = "💛💙💜💚❤️"  # Colorful hearts

    def __init__(self, delay=0.1, symbols=CLASSIC):
        """
        Initialize the spinner.

        Args:
            delay (float): Time between spinner updates in seconds
            symbols (str): String containing spinner animation frames
        """
        self.symbols = symbols
        self.delay = delay
        self.busy = False
        self.spinner_thread = None
        self._screen_lock = threading.Lock()
        # ANSI escape codes for cursor visibility
        self.hide_cursor = "\033[?25l"
        self.show_cursor = "\033[?25h"

    def _spin(self):
        """Internal method that handles the spinning animation."""
        spinner_cycle = itertools.cycle(self.symbols)
        while self.busy:
            with self._screen_lock:
                current_symbol = next(spinner_cycle)
                sys.stdout.write(current_symbol)
                sys.stdout.flush()
                # Calculate backspace count for wide characters
                backspace_count = len(current_symbol.encode("utf-16-le")) // 2
                sys.stdout.write("\b" * backspace_count)
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
            # Calculate space count for wide characters
            space_count = len(self.symbols[0].encode("utf-16-le")) // 2
            sys.stdout.write(" " * space_count)
            sys.stdout.write("\b" * space_count)
            sys.stdout.write(self.show_cursor)  # Show cursor when stopping
            sys.stdout.flush()
