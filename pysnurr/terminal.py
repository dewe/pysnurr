"""Terminal output handling with thread safety.

This module provides thread-safe terminal output operations
for command-line applications.
"""

import sys
import threading


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
