#!/usr/bin/env python3
"""Demo showing how Snurr handles long status messages."""

import time

from pysnurr import Snurr


def main() -> None:
    # Create a spinner with a fun style
    with Snurr(frames="🌍🌎🌏", delay=0.2) as spinner:
        # Start with a short message
        spinner.status = "Starting up..."
        time.sleep(2)

        # Show a medium length message
        spinner.status = "Processing data and performing calculations..."
        time.sleep(2)

        # Show a very long message that will likely be truncated
        spinner.status = (
            "This is a very long status message that will be automatically truncated "
            "if it exceeds the available width of your terminal window..."
        )
        time.sleep(2)

        # Show another long message with emojis and special characters
        spinner.status = (
            "🚀 Launching rockets to Mars while analyzing quantum fluctuations "
            "in the space-time continuum... 🌌 ✨"
        )
        time.sleep(2)

        # Back to a short message
        spinner.status = "Done! 🎉"
        time.sleep(1)


if __name__ == "__main__":
    main()
