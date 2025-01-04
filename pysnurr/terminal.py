"""Terminal output handling with thread safety.

This module provides thread-safe terminal output operations
for command-line applications.
"""

import os
import sys
import threading

import wcwidth  # type: ignore


class TerminalWriter:
    """Handles terminal output operations with thread safety."""

    HIDE_CURSOR: str = "\033[?25l"
    SHOW_CURSOR: str = "\033[?25h"

    def __init__(self) -> None:
        self._screen_lock: threading.Lock = threading.Lock()

    def columns_width(self, text: str) -> int:
        """Calculate the display width of text in terminal columns.

        Args:
            text: The text to calculate width for.

        Returns:
            The width in columns that the text will occupy in the terminal.

        Example:
            >>> from pysnurr.terminal import TerminalWriter
            >>> writer = TerminalWriter()
            >>> writer.columns_width("hello")
            5
            >>> writer.columns_width("你好")  # wide characters
            4
        """
        return sum(wcwidth.wcwidth(char) for char in text)

    def write(self, text: str) -> None:
        """Write text to terminal with thread safety."""
        with self._screen_lock:
            sys.stdout.write(text)
            sys.stdout.flush()

    def erase_to_end(self) -> None:
        """Erase from cursor position to end of line."""
        self.write("\033[0K")

    def move_cursor_left(self, columns: int) -> None:
        """Move cursor left by specified number of columns."""
        if columns > 0:
            self.write(f"\033[{columns}D")

    def move_cursor_right(self, columns: int) -> None:
        """Move cursor right by specified number of columns."""
        if columns > 0:
            self.write(f"\033[{columns}C")

    def hide_cursor(self) -> None:
        """Hide the terminal cursor."""
        self.write(self.HIDE_CURSOR)

    def show_cursor(self) -> None:
        """Show the terminal cursor."""
        self.write(self.SHOW_CURSOR)

    def get_cursor_position(self) -> tuple[int, int]:
        """Get the current cursor position.

        Returns:
            tuple[int, int]: A tuple of (row, column), both 1-based.
        """
        import termios
        import tty

        with self._screen_lock:
            # Save terminal settings
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                # Set terminal to raw mode
                tty.setraw(sys.stdin.fileno())

                # Query cursor position
                sys.stdout.write("\x1b[6n")
                sys.stdout.flush()

                # Read response
                response = ""
                while True:
                    char = sys.stdin.read(1)
                    response += char
                    if char == "R":
                        break

                # Parse response (format is "\x1b[{row};{column}R")
                if response.startswith("\x1b[") and response.endswith("R"):
                    parts = response[2:-1].split(";")
                    if len(parts) == 2:
                        return (int(parts[0]), int(parts[1]))

                raise RuntimeError("Failed to get cursor position")

            finally:
                # Restore terminal settings
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def get_screen_width(self) -> int:
        """Get the current terminal width in columns.

        Returns:
            int: The number of columns in the terminal.

        Example:
            >>> from pysnurr.terminal import TerminalWriter
            >>> writer = TerminalWriter()
            >>> width = writer.get_screen_width()
            >>> isinstance(width, int)
            True
            >>> width > 0
            True
        """
        try:
            return os.get_terminal_size().columns
        except OSError:
            # Fallback if terminal size cannot be determined
            return 80
