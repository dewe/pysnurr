import itertools
import sys
import threading
import time


class Styles:
    """Collection of spinner animation styles."""

    DOTS: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"  # Default braille dots
    CLASSIC: str = "/-\\|"  # Classic ASCII spinner
    BAR: str = "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁"  # ASCII loading bar
    EARTH: str = "🌍🌎🌏"  # Earth rotation
    MOON: str = "🌑🌒🌓🌔🌕🌖🌗🌘"  # Moon phases
    CLOCK: str = "🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛"  # Clock rotation
    ARROWS: str = "←↖↑↗→↘↓↙"  # Arrow rotation
    DOTS_BOUNCE: str = ".oO°Oo."  # Bouncing dots
    TRIANGLES: str = "◢◣◤◥"  # Rotating triangles
    HEARTS: str = "💛💙💜💚"  # Colorful hearts


class TerminalWriter:
    """Handles terminal output operations with thread safety."""

    HIDE_CURSOR: str = "\033[?25l"
    SHOW_CURSOR: str = "\033[?25h"

    def __init__(self) -> None:
        self._screen_lock: threading.Lock = threading.Lock()

    def write(self, text: str | bytes) -> None:
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

    def __init__(
        self,
        delay: float = 0.1,
        symbols: str = Styles.CLASSIC,
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
        if delay < 0:
            raise ValueError("delay must be non-negative")

        if not symbols:
            raise ValueError("symbols cannot be empty")
        if len(symbols) > 100:  # Reasonable limit for animation frames
            raise ValueError("symbols string too long (max 100 characters)")

        self.symbols: str = symbols
        self.delay: float = delay
        self.append: bool = append
        self.busy: bool = False
        self._spinner_thread: threading.Thread | None = None
        self._current_symbol: str | None = None
        self._terminal: TerminalWriter = TerminalWriter()

    def _get_symbol_width(self, symbol: str) -> int:
        width = len(symbol.encode("utf-16-le")) // 2
        return width + 1 if self.append else width

    def _spin(self) -> None:
        for symbol in itertools.cycle(self.symbols):
            if not self.busy:
                break
            self._update_symbol(symbol)
            time.sleep(self.delay)

    def _update_symbol(self, new_symbol: str) -> None:
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

    def write(self, text: str | bytes, end: str = "\n") -> None:
        """Thread-safe write text to stdout while spinner is active."""
        if self._current_symbol:
            width = self._get_symbol_width(self._current_symbol)
            self._terminal.erase(width)

        self._terminal.write(str(text) + end)

        # Reset spinner position if writing without newline
        if not end.endswith("\n"):
            self._current_symbol = None

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
        self.stop()
