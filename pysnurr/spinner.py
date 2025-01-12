"""Terminal spinner animation for Python applications.

This module provides a non-blocking terminal spinner animation that can be used
to indicate progress or ongoing operations in command-line applications.
"""

import itertools
import threading
import time
from typing import Iterator, Optional

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

        self.frames = split_graphemes(frames)
        self.delay = delay
        self._status = status
        self._frame = self.frames[0]
        self._terminal = TerminalWriter()
        self._stop_event = threading.Event()
        self._stop_event.set()  # Start in stopped state
        self._spinner_thread: Optional[threading.Thread] = None

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

    def start(self) -> None:
        """Start the spinner animation in a non-blocking way."""
        if not self._stop_event.is_set():  # Already running
            return

        self._stop_event.clear()
        self._terminal.hide_cursor()
        self._spinner_thread = threading.Thread(target=self._spin)
        self._spinner_thread.daemon = True
        self._spinner_thread.start()

    def stop(self) -> None:
        """Stop the spinner animation and restore cursor."""
        if self._stop_event.is_set():  # Already stopped
            return

        self._stop_event.set()
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
        if not self._stop_event.is_set():  # Only update if running
            self._update_display()

    def _spin(self) -> None:
        """Main spinner animation loop."""
        frames = self._frame_iterator()
        while not self._stop_event.is_set():
            try:
                self._frame = next(frames)
                self._update_display()
                time.sleep(self.delay)
            except Exception:
                break

    def _frame_iterator(self) -> Iterator[str]:
        """Generate frames indefinitely."""
        return itertools.cycle(self.frames)

    def _update_display(self) -> None:
        """Update the display with current frame and status."""
        content = self._format()
        width = self._terminal.columns_width(content)
        max_width = self._get_max_width()

        # Truncate if needed
        if width > max_width:
            content = self._truncate(content, max_width)
            width = self._terminal.columns_width(content)

        buffer = content + self._terminal.get_cursor_left_sequence(width)
        self._terminal.write(buffer)

    def _format(self) -> str:
        """Format message and frame."""
        return f"{self._status} {self._frame}" if self._status else self._frame

    def _truncate(self, content: str, max_width: int) -> str:
        """Truncate content to fit available width while preserving the spinner frame.

        Ensures the spinner frame is always visible at the end of the line, even when
        content needs to be truncated.
        """
        frame_width = self._terminal.columns_width(self._frame)

        # If we can't even fit the frame, just return it
        if frame_width >= max_width:
            return self._frame

        # Reserve space for frame and one space
        available_width = max_width - frame_width - 1

        # If we have a status, truncate it to fit
        if self._status:
            status_graphemes = split_graphemes(self._status)
            result = []
            width = 0

            for g in status_graphemes:
                g_width = self._terminal.columns_width(g)
                if width + g_width > available_width:
                    break
                result.append(g)
                width += g_width

            return "".join(result) + " " + self._frame

        return self._frame

    def _clear(self) -> None:
        """Clear from current position to end of line."""
        self._terminal.erase_to_end()

    def _get_max_width(self) -> int:
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
