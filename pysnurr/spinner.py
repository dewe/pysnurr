import itertools
import sys
import threading
import time


class SpinnerStyles:
    """Collection of spinner animation styles."""

    DOTS = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"  # Default braille dots
    CLASSIC = "/-\\|"  # Classic ASCII spinner
    BAR = "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁"  # ASCII loading bar
    EARTH = "🌍🌎🌏"  # Earth rotation
    MOON = "🌑🌒🌓🌔🌕🌖🌗🌘"  # Moon phases
    CLOCK = "🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛"  # Clock rotation
    ARROWS = "←↖↑↗→↘↓↙"  # Arrow rotation
    DOTS_BOUNCE = ".oO°Oo."  # Bouncing dots
    TRIANGLES = "◢◣◤◥"  # Rotating triangles
    HEARTS = "💛💙💜💚"  # Colorful hearts


class TerminalWriter:
    """Handles terminal output operations with thread safety."""

    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"

    def __init__(self):
        self._screen_lock = threading.Lock()

    def write(self, text):
        """Write text to terminal with thread safety."""
        with self._screen_lock:
            sys.stdout.write(text)
            sys.stdout.flush()

    def erase(self, width):
        """Erase 'width' characters using backspace sequence."""
        self.write("\b" * width + " " * width + "\b" * width)

    def hide_cursor(self):
        """Hide the terminal cursor."""
        self.write(self.HIDE_CURSOR)

    def show_cursor(self):
        """Show the terminal cursor."""
        self.write(self.SHOW_CURSOR)


class Snurr:
    """A non-blocking terminal spinner animation."""

    # Make spinner styles available as class attributes for backward
    # compatibility
    DOTS = SpinnerStyles.DOTS
    CLASSIC = SpinnerStyles.CLASSIC
    BAR = SpinnerStyles.BAR
    EARTH = SpinnerStyles.EARTH
    MOON = SpinnerStyles.MOON
    CLOCK = SpinnerStyles.CLOCK
    ARROWS = SpinnerStyles.ARROWS
    DOTS_BOUNCE = SpinnerStyles.DOTS_BOUNCE
    TRIANGLES = SpinnerStyles.TRIANGLES
    HEARTS = SpinnerStyles.HEARTS

    def __init__(self, delay=0.1, symbols=SpinnerStyles.CLASSIC, append=False):
        """Initialize the spinner.

        Args:
            delay (float): Time between spinner updates in seconds
            symbols (str): String containing spinner animation frames
            append (bool): If True, adds space and shows spinner at line end
        """
        self.symbols = symbols
        self.delay = delay
        self.append = append
        self.busy = False
        self._spinner_thread = None
        self._current_symbol = None
        self._terminal = TerminalWriter()

    def _get_symbol_width(self, symbol):
        """Calculate display width of a symbol."""
        width = len(symbol.encode("utf-16-le")) // 2
        return width + 1 if self.append else width

    def _spin(self):
        """Internal method that handles the spinning animation."""
        for symbol in itertools.cycle(self.symbols):
            if not self.busy:
                break
            self._update_symbol(symbol)
            time.sleep(self.delay)

    def _update_symbol(self, new_symbol):
        """Update the displayed spinner symbol."""
        if self._current_symbol:
            width = self._get_symbol_width(self._current_symbol)
            self._terminal.erase(width)

        text = f" {new_symbol}" if self.append else new_symbol
        self._terminal.write(text)
        self._current_symbol = new_symbol

    def start(self):
        """Start the spinner animation in a non-blocking way."""
        self.busy = True
        self._terminal.hide_cursor()
        self._spinner_thread = threading.Thread(target=self._spin)
        self._spinner_thread.daemon = True
        self._spinner_thread.start()

    def stop(self):
        """Stop the spinner animation."""
        self.busy = False
        if self._spinner_thread:
            self._spinner_thread.join()
            if self._current_symbol:
                width = self._get_symbol_width(self._current_symbol)
                self._terminal.erase(width)
            self._terminal.show_cursor()
            self._current_symbol = None

    def write(self, text, end="\n"):
        """Write text to stdout safely.

        Thread-safe write that won't interfere with the spinner animation.

        Args:
            text (str): The text to write
            end (str): String appended after the text, defaults to newline
        """
        if self._current_symbol:
            width = self._get_symbol_width(self._current_symbol)
            self._terminal.erase(width)
        self._terminal.write(str(text) + end)
