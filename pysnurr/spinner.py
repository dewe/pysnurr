"""Terminal spinner animation for Python applications.

This module provides a non-blocking terminal spinner animation that can be used
to indicate progress or ongoing operations in command-line applications.
"""

import itertools
import threading
import time
from dataclasses import dataclass, replace
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


@dataclass(frozen=True)
class SpinnerState:
    """Immutable state of a spinner.

    This class represents the complete state of a spinner at any point in time.
    Being frozen (immutable), any state change requires creating a new instance.
    """

    frame: str = ""
    max_available_width: int = 80
    status: str = ""


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
        self._terminal: TerminalWriter = TerminalWriter()
        self._state = SpinnerState(status=status)
        self._stop_event = threading.Event()
        self._stop_event.set()  # Start in stopped state
        self._spinner_thread: Optional[threading.Thread] = None

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
        if not self._stop_event.is_set():  # Already running
            return

        self._state = replace(
            self._state,
            max_available_width=self._calculate_max_width(),
            frame=self.frames[0],  # Set initial frame when starting
        )

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
        return self._state.status

    @status.setter
    def status(self, message: str) -> None:
        """Set a new status message."""
        self._clear()
        self._state = replace(self._state, status=message)
        if not self._stop_event.is_set():  # Only update if running
            self._update_display(self._state)

    # Private helper methods - Spinner animation
    def _spin(self) -> None:
        """Main spinner animation loop."""
        frames = self._frame_iterator()
        while not self._stop_event.is_set():
            try:
                frame = next(frames)
                self._state = replace(self._state, frame=frame)
                self._update_display(self._state)
                time.sleep(self.delay)
            except Exception:
                break

    def _frame_iterator(self) -> Iterator[str]:
        """Generate frames indefinitely."""
        return itertools.cycle(self.frames)

    def _update_display(self, state: SpinnerState) -> None:
        """Update the display with current state."""
        content = self._truncate(state)
        width = self._terminal.columns_width(content)
        buffer = content + self._terminal.get_cursor_left_sequence(width)
        self._terminal.write(buffer)

    def _truncate(self, state: SpinnerState) -> str:
        """Truncate message if it would exceed available width."""
        buffer = self._format(state)
        new_width = self._terminal.columns_width(buffer)

        if new_width <= state.max_available_width:
            return buffer

        msg_graphemes = split_graphemes(state.status)
        # Try progressively shorter messages until we find one that fits
        for i in range(len(msg_graphemes) - 1, -1, -1):
            truncated_msg = "".join(msg_graphemes[:i])
            state = replace(state, status=truncated_msg)
            buffer = self._format(state)
            new_width = self._terminal.columns_width(buffer)
            if new_width <= state.max_available_width:
                return buffer

        return state.frame  # Return just the frame if even empty message is too long

    @staticmethod
    def _format(state: SpinnerState) -> str:
        """Format message and frame."""
        if state.status:
            return f"{state.status} {state.frame}"
        return state.frame

    def _clear(self) -> None:
        """Clear from current position to end of line."""
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
