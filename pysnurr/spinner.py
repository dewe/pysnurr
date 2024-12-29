"""Terminal spinner animation for Python applications.

This module provides a non-blocking terminal spinner animation that can be used
to indicate progress or ongoing operations in command-line applications.
"""

import itertools
import threading
import time

from .terminal import TerminalWriter

# Spinner animation styles
SPINNERS = {
    "CLASSIC": "/-\\|",  # Classic ASCII spinner
    "DOTS": "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏",  # Default braille dots
    "BAR": "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁",  # ASCII loading bar
    "EARTH": "🌍🌎🌏",  # Earth rotation
    "MOON": "🌑🌒🌓🌔🌕🌖🌗🌘",  # Moon phases
    "CLOCK": "🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛",  # Clock rotation
    "ARROWS": "←↖↑↗→↘↓↙",  # Arrow rotation
    "DOTS_BOUNCE": ".oO°Oo.",  # Bouncing dots
    "TRIANGLES": "◢◣◤◥",  # Rotating triangles
    "HEARTS": "💛💙💜💚",  # Colorful hearts
}


class Snurr:
    """A non-blocking terminal spinner animation.

    This class provides a spinner animation that can be used to indicate
    progress or ongoing operations in command-line applications. It can be
    used either as a context manager or manually started and stopped.

    Example:
        >>> with Snurr() as spinner:
        ...     # Do some work
        ...     spinner.write("Processing...")
        ...     time.sleep(2)
    """

    def __init__(
        self,
        delay: float = 0.1,
        symbols: str = SPINNERS["CLASSIC"],
        append: bool = False,
    ) -> None:
        """Initialize the spinner.

        Args:
            delay: Time between spinner updates in seconds
            symbols: String containing spinner animation frames
            append: If True, adds space and shows spinner at line end

        Raises:
            ValueError: If delay is negative or symbols is empty/too long
        """
        if delay < 0:
            raise ValueError("delay must be non-negative")

        if not symbols:
            raise ValueError("symbols cannot be empty")
        if len(symbols) > 100:
            raise ValueError("symbols string too long (max 100 characters)")

        self.symbols: str = symbols
        self.delay: float = delay
        self.append: bool = append
        self.busy: bool = False
        self._spinner_thread: threading.Thread | None = None
        self._current_symbol: str | None = None
        self._terminal: TerminalWriter = TerminalWriter()

    # Public interface methods
    def start(self) -> None:
        """Start the spinner animation in a non-blocking way."""
        self.busy = True
        self._terminal.hide_cursor()
        self._spinner_thread = threading.Thread(target=self._spin)
        self._spinner_thread.daemon = True
        self._spinner_thread.start()

    def stop(self) -> None:
        """Stop the spinner animation and restore cursor."""
        self.busy = False
        if self._spinner_thread:
            self._spinner_thread.join()
            self._erase_current_symbol()
            self._terminal.show_cursor()
            self._current_symbol = None

    def write(self, text: str | bytes, end: str = "\n") -> None:
        """Write text to stdout while spinner is active.

        Thread-safe method to write text while the spinner is running.
        The spinner will be temporarily cleared before writing.

        Args:
            text: The text to write
            end: String to append after the text (default: newline)
        """
        self._erase_current_symbol()
        self._terminal.write(str(text) + end)
        if not end.endswith("\n"):
            self._current_symbol = None  # Reset spinner position

    # Context manager methods
    def __enter__(self) -> "Snurr":
        """Enter the context manager, starting the spinner."""
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit the context manager, stopping the spinner."""
        if exc_type is KeyboardInterrupt:
            self._terminal.erase(2)  # remove ^C
            self.stop()
            print("^C", end="")  # print ^C again
        else:
            self.stop()

    # Private helper methods
    def _get_symbol_width(self, symbol: str) -> int:
        """Calculate the display width of a symbol in terminal columns."""
        width = len(symbol.encode("utf-16-le")) // 2
        return width + 1 if self.append else width

    def _spin(self) -> None:
        """Main spinner animation loop."""
        for symbol in itertools.cycle(self.symbols):
            if not self.busy:
                break
            self._update_symbol(symbol)
            time.sleep(self.delay)

    def _update_symbol(self, new_symbol: str) -> None:
        """Update the displayed spinner symbol."""
        self._erase_current_symbol()
        text = self._format_symbol(new_symbol)
        self._terminal.write(text)
        self._current_symbol = new_symbol

    def _erase_current_symbol(self) -> None:
        """Erase the current spinner symbol from the terminal."""
        if self._current_symbol:
            width = self._get_symbol_width(self._current_symbol)
            self._terminal.erase(width)

    def _format_symbol(self, new_symbol: str) -> str:
        """Format a symbol for display, adding space if append is True."""
        if self.append:
            return f" {new_symbol}"
        return new_symbol
