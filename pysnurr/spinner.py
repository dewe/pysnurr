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
        >>> with Snurr() as spinner:  # doctest: +SKIP
        ...     # Do some work
        ...     spinner.status = "Processing..."
        ...     time.sleep(0.1)  # Spinner will be visible here
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
        self._max_available_width = self._calculate_max_width()
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
        new_buffer = self._truncate(self._status, new_frame)
        self._buffer = new_buffer
        self._render()

    def _truncate(self, message: str, frame: str) -> str:
        """Truncate message if it would exceed available width."""
        new_buffer = self._format(message, frame)
        new_width = self._terminal.columns_width(new_buffer)

        if new_width <= self._max_available_width:
            return new_buffer

        msg_graphemes = split_graphemes(message)
        # Try progressively shorter messages until we find one that fits
        for i in range(len(msg_graphemes) - 1, -1, -1):
            truncated_msg = "".join(msg_graphemes[:i])
            new_buffer = self._format(truncated_msg, frame)
            new_width = self._terminal.columns_width(new_buffer)
            if new_width <= self._max_available_width:
                return new_buffer

        return frame  # Return just the frame if even empty message is too long

    def _format(self, message: str, frame: str) -> str:
        """Format message and frame."""
        if message:
            return f"{message} {frame}"
        return frame

    def _render(self) -> None:
        """Render the current buffer to the terminal."""
        width = self._terminal.columns_width(self._buffer)

        self._terminal.write(self._buffer)

        # TODO: jump back to start position instead of moving cursor left
        self._terminal.move_cursor_left(width)

    def _clear(self) -> None:
        """Clear from current position to end of line."""
        self._buffer = ""
        self._terminal.erase_to_end()

    def _calculate_max_width(self) -> int:
        """Calculate maximum available width from current position to end of line."""
        _, col = self._terminal.get_cursor_position()
        screen_width = self._terminal.get_screen_width()
        return max(0, screen_width - col)


def split_graphemes(text: str) -> list[str]:
    """Split text into grapheme clusters.

    Args:
        text: The text to split into grapheme clusters.

    Returns:
        A list of grapheme clusters.

    Example:
        >>> split_graphemes("é⭐️🇸🇪")
        ['é', '⭐️', '🇸🇪']
    """
    return regex.findall(r"\X", text)
