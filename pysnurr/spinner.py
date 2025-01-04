"""Terminal spinner animation for Python applications.

This module provides a non-blocking terminal spinner animation that can be used
to indicate progress or ongoing operations in command-line applications.
"""

import itertools
import threading
import time

import regex

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
        frames: str = SPINNERS["CLASSIC"],
        status: str = "",
    ) -> None:
        """Initialize the spinner.

        Args:
            delay: Time between spinner updates in seconds
            frames: String containing spinner animation frames
            status: Initial status message to display

        Raises:
            ValueError: If delay is negative or frames is empty/too long
        """
        if delay < 0:
            raise ValueError("delay must be non-negative")

        if not frames:
            raise ValueError("frames cannot be empty")
        if len(frames) > 100:
            raise ValueError("frames string too long (max 100 characters)")

        self.frames: list[str] = split_graphemes(frames)
        self.delay: float = delay
        self._busy: bool = False
        self._spinner_thread: threading.Thread | None = None
        self._buffer: str = ""
        self._status: str = status
        self._terminal: TerminalWriter = TerminalWriter()

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
        self.stop()

    # Public interface methods
    def start(self) -> None:
        """Start the spinner animation in a non-blocking way."""
        self._busy = True
        self._terminal.hide_cursor()
        self._spinner_thread = threading.Thread(target=self._spin)
        self._spinner_thread.daemon = True
        self._spinner_thread.start()

    def stop(self) -> None:
        """Stop the spinner animation and restore cursor."""
        self._busy = False
        if self._spinner_thread:
            self._spinner_thread.join()
            self._clear()
            self._terminal.show_cursor()

    @property
    def status(self) -> str:
        """Get the current status message."""
        return self._status

    @status.setter
    def status(self, message: str) -> None:
        """Set a new status message."""
        self._clear()
        self._status = message
        if self._busy:  # Only update if spinner is running
            self._update(self.frames[0])  # Use first frame as placeholder

    # Private helper methods - Spinner animation
    def _spin(self) -> None:
        """Main spinner animation loop."""
        frames = itertools.cycle(self.frames)
        while self._busy:
            self._update(next(frames))
            time.sleep(self.delay)

    def _update(self, new_frame: str) -> None:
        """Update the buffer with new frame and status."""
        message = f"{self._status} " if self._status else ""

        self._buffer = f"{message}{new_frame}"
        self._render()

    def _render(self) -> None:
        """Render the current buffer to the terminal."""
        width = self._terminal.get_columns(self._buffer)

        self._terminal.write(self._buffer)
        self._terminal.move_cursor_left(width)

    def _clear(self) -> None:
        """Clear from current location to end of line."""
        self._buffer = ""
        self._terminal.erase_to_end()


def split_graphemes(text: str) -> list[str]:
    """Split Unicode text into grapheme clusters.

    A grapheme cluster represents what a user would consider a single
    character, which may consist of multiple Unicode code points (e.g. emojis,
    combining marks).

    Args:
        text: The input string to split into grapheme clusters.

    Returns:
        A list of strings, where each string is a single grapheme cluster.

    Example:
        >>> split_graphemes("👨‍👩‍👧")
        ['👨‍👩‍👧']  # Family emoji is a single grapheme
        >>> split_graphemes("é")
        ['é']  # Accented e is a single grapheme
    """
    return regex.findall(r"\X", text)
