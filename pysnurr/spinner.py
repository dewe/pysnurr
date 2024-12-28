import itertools
import sys
import threading
import time
from typing import Optional, TypeAlias, Union

SpinnerSymbols: TypeAlias = str
Delay: TypeAlias = float
TextContent: TypeAlias = Union[str, bytes]


class SpinnerStyles:
    """Collection of spinner animation styles."""

    DOTS: SpinnerSymbols = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"  # Default braille dots
    CLASSIC: SpinnerSymbols = "/-\\|"  # Classic ASCII spinner
    BAR: SpinnerSymbols = "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁"  # ASCII loading bar
    EARTH: SpinnerSymbols = "🌍🌎🌏"  # Earth rotation
    MOON: SpinnerSymbols = "🌑🌒🌓🌔🌕🌖🌗🌘"  # Moon phases
    CLOCK: SpinnerSymbols = "🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛"  # Clock rotation
    ARROWS: SpinnerSymbols = "←↖↑↗→↘↓↙"  # Arrow rotation
    DOTS_BOUNCE: SpinnerSymbols = ".oO°Oo."  # Bouncing dots
    TRIANGLES: SpinnerSymbols = "◢◣◤◥"  # Rotating triangles
    HEARTS: SpinnerSymbols = "💛💙💜💚"  # Colorful hearts


class TerminalWriter:
    """Handles terminal output operations with thread safety."""

    HIDE_CURSOR: str = "\033[?25l"
    SHOW_CURSOR: str = "\033[?25h"

    def __init__(self) -> None:
        self._screen_lock: threading.Lock = threading.Lock()

    def write(self, text: TextContent) -> None:
        """Write text to terminal with thread safety."""
        with self._screen_lock:
            sys.stdout.write(str(text))
            sys.stdout.flush()

    def erase(self, width: int) -> None:
        """Erase 'width' characters using backspace sequence."""
        self.write("\b" * width + " " * width + "\b" * width)

    def hide_cursor(self) -> None:
        """Hide the terminal cursor."""
        self.write(self.HIDE_CURSOR)

    def show_cursor(self) -> None:
        """Show the terminal cursor."""
        self.write(self.SHOW_CURSOR)


class Snurr:
    """A non-blocking terminal spinner animation."""

    # Make spinner styles available as class attributes for backward
    # compatibility
    DOTS: SpinnerSymbols = SpinnerStyles.DOTS
    CLASSIC: SpinnerSymbols = SpinnerStyles.CLASSIC
    BAR: SpinnerSymbols = SpinnerStyles.BAR
    EARTH: SpinnerSymbols = SpinnerStyles.EARTH
    MOON: SpinnerSymbols = SpinnerStyles.MOON
    CLOCK: SpinnerSymbols = SpinnerStyles.CLOCK
    ARROWS: SpinnerSymbols = SpinnerStyles.ARROWS
    DOTS_BOUNCE: SpinnerSymbols = SpinnerStyles.DOTS_BOUNCE
    TRIANGLES: SpinnerSymbols = SpinnerStyles.TRIANGLES
    HEARTS: SpinnerSymbols = SpinnerStyles.HEARTS

    def __init__(
        self,
        delay: Delay = 0.1,
        symbols: SpinnerSymbols = SpinnerStyles.CLASSIC,
        append: bool = False,
    ) -> None:
        """Initialize the spinner.

        Args:
            delay: Time between spinner updates in seconds
            symbols: String containing spinner animation frames
                    (max 100 chars)
            append: If True, adds space and shows spinner at line end

        Raises:
            ValueError: If delay is negative or symbols is empty/too long
            TypeError: If symbols is not a string or delay is not a number
        """
        if not isinstance(delay, (int, float)):
            raise TypeError("delay must be a number")
        if delay < 0:
            raise ValueError("delay must be non-negative")

        if not isinstance(symbols, str):
            raise TypeError("symbols must be a string")
        if not symbols:
            raise ValueError("symbols cannot be empty")
        if len(symbols) > 100:  # Reasonable limit for animation frames
            raise ValueError("symbols string too long (max 100 characters)")

        if not isinstance(append, bool):
            raise TypeError("append must be a boolean")

        self.symbols: SpinnerSymbols = symbols
        self.delay: Delay = delay
        self.append: bool = append
        self.busy: bool = False
        self._spinner_thread: Optional[threading.Thread] = None
        self._current_symbol: Optional[SpinnerSymbols] = None
        self._terminal: TerminalWriter = TerminalWriter()

    def _get_symbol_width(self, symbol: SpinnerSymbols) -> int:
        """Calculate display width of a symbol."""
        width = len(symbol.encode("utf-16-le")) // 2
        return width + 1 if self.append else width

    def _spin(self) -> None:
        """Internal method that handles the spinning animation."""
        for symbol in itertools.cycle(self.symbols):
            if not self.busy:
                break
            self._update_symbol(symbol)
            time.sleep(self.delay)

    def _update_symbol(self, new_symbol: SpinnerSymbols) -> None:
        """Update the displayed spinner symbol."""
        if self._current_symbol:
            width = self._get_symbol_width(self._current_symbol)
            self._terminal.erase(width)

        text = f" {new_symbol}" if self.append else new_symbol
        self._terminal.write(text)
        self._current_symbol = new_symbol

    def start(self) -> None:
        """Start the spinner animation in a non-blocking way."""
        self.busy = True
        self._terminal.hide_cursor()
        self._spinner_thread = threading.Thread(target=self._spin)
        self._spinner_thread.daemon = True
        self._spinner_thread.start()

    def stop(self) -> None:
        """Stop the spinner animation."""
        self.busy = False
        if self._spinner_thread:
            self._spinner_thread.join()
            if self._current_symbol:
                width = self._get_symbol_width(self._current_symbol)
                self._terminal.erase(width)
            self._terminal.show_cursor()
            self._current_symbol = None

    def write(self, text: TextContent, end: str = "\n") -> None:
        """Write text to stdout safely.

        Thread-safe write that won't interfere with the spinner animation.

        Args:
            text: The text to write
            end: String appended after the text, defaults to newline

        Raises:
            TypeError: If text or end is not a string
        """
        if not isinstance(text, (str, bytes)):
            raise TypeError("text must be a string or bytes")
        if not isinstance(end, str):
            raise TypeError("end must be a string")

        if self._current_symbol:
            width = self._get_symbol_width(self._current_symbol)
            self._terminal.erase(width)

        self._terminal.write(str(text) + end)

        # Reset spinner position if writing without newline
        if not end.endswith("\n"):
            # Force redraw of spinner at new position
            self._current_symbol = None

    def __enter__(self) -> "Snurr":
        """Enter the context manager, starting the spinner.

        Returns:
            Snurr: The spinner instance for use in the context.
        """
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Exit the context manager, stopping the spinner.

        Args:
            exc_type: The type of the exception that occurred, if any
            exc_val: The instance of the exception that occurred, if any
            exc_tb: The traceback of the exception that occurred, if any
        """
        self.stop()
