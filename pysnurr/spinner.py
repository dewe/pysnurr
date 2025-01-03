"""Terminal spinner animation for Python applications.

This module provides a non-blocking terminal spinner animation that can be used
to indicate progress or ongoing operations in command-line applications.
"""

import itertools
import threading
import time

import regex
import wcwidth  # type: ignore

from .terminal import TerminalWriter

# Spinner animation styles
SPINNERS = {
    "CLASSIC": "/-\\|",  # Classic ASCII spinner (default)
    "ARROWS": "←↖↑↗→↘↓↙",  # Arrow rotation
    "BAR": "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁",  # ASCII loading bar
    "BLOCKS": "▌▀▐▄",  # Minimal blocks
    "DOTS_BOUNCE": ".oOᐤ°ᐤOo.",  # Bouncing dots
    "EARTH": "🌍🌎🌏",  # Earth rotation
    "HEARTS": "💛💙💜💚",  # Colorful hearts
    "MOON": "🌑🌒🌓🌔🌕🌖🌗🌘",  # Moon phases
    "SPARKLES": "✨⭐️💫",  # Sparkling animation
    "TRIANGLES": "◢◣◤◥",  # Rotating triangles
    "WAVE": "⎺⎻⎼⎽⎼⎻",  # Wave pattern
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
    ) -> None:
        """Initialize the spinner.

        Args:
            delay: Time between spinner updates in seconds
            symbols: String containing spinner animation frames

        Raises:
            ValueError: If delay is negative or symbols is empty/too long
        """
        if delay < 0:
            raise ValueError("delay must be non-negative")

        if not symbols:
            raise ValueError("symbols cannot be empty")
        if len(symbols) > 100:
            raise ValueError("symbols string too long (max 100 characters)")

        self.symbols: list[str] = self._split_graphemes(symbols)
        self.delay: float = delay
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
            self._current_symbol = None
            self._terminal.show_cursor()

    def write(self, text: str, end: str = "\n") -> None:
        """Write text to stdout while spinner is active.

        Thread-safe method to write text while the spinner is running.
        The spinner will be temporarily cleared before writing.
        """
        self._erase_current_symbol()
        self._terminal.write(text + end)
        if not end.endswith("\n"):
            self._current_symbol = None  # Resets spinner position

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
    def _split_graphemes(self, text: str) -> list[str]:
        """Split a string into an array of grapheme clusters using regex."""
        return regex.findall(r"\X", text)

    def _get_symbol_width(self, symbol: str) -> int:
        """Calculate the display width of a symbol in terminal columns."""
        return sum(wcwidth.wcwidth(char) for char in symbol)

    def _spin(self) -> None:
        """Main spinner animation loop."""
        symbols = itertools.cycle(self.symbols)
        while self.busy:
            self._update_symbol(next(symbols))
            time.sleep(self.delay)

    def _update_symbol(self, new_symbol: str) -> None:
        """Update the displayed spinner symbol."""
        self._move_left_current_symbol()
        self._current_symbol = new_symbol
        self._terminal.write(new_symbol)

    def _erase_current_symbol(self) -> None:
        """Erase the current spinner symbol from the terminal."""
        if self._current_symbol:
            width = self._get_symbol_width(self._current_symbol)
            self._terminal.erase(width)

    def _move_left_current_symbol(self) -> None:
        """Move the cursor to the left of current spinner symbol."""
        if self._current_symbol:
            width = self._get_symbol_width(self._current_symbol)
            self._terminal.write(f"\033[{width}D")
