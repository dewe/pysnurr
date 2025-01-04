#!/usr/bin/env python3

import time

from pysnurr.terminal import TerminalWriter


def main() -> None:
    writer = TerminalWriter()

    # Clear screen and move to top
    print("\033[2J\033[H", end="", flush=True)

    try:
        # Show terminal width
        width = writer.get_screen_width()
        writer.write(f"Terminal width: {width} columns\n")
        writer.write("=" * width + "\n")
        time.sleep(1)

        writer.write("Testing cursor position...\n")
        time.sleep(1)

        pos1 = writer.get_cursor_position()
        writer.write(f"Current position: row={pos1[0]}, col={pos1[1]}\n")
        time.sleep(1)

        writer.write("Moving cursor right by 10 columns...")
        writer.move_cursor_right(10)
        pos2 = writer.get_cursor_position()
        writer.write(f" Now at: row={pos2[0]}, col={pos2[1]}\n")
        time.sleep(1)

        writer.write("Moving cursor left by 5 columns...")
        writer.move_cursor_left(5)
        pos3 = writer.get_cursor_position()
        writer.write(f" Now at: row={pos3[0]}, col={pos3[1]}\n")

    except KeyboardInterrupt:
        print("\nDemo interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Ensure cursor is visible when script ends
        writer.show_cursor()


if __name__ == "__main__":
    main()
