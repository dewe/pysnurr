from time import sleep

from spinner import Snurr


def demo_basic():
    """Demo basic spinner usage"""
    print("\n=== Basic Usage ===")
    spinner = Snurr()
    spinner.start()
    sleep(2)  # Simulate work
    spinner.stop()


def demo_styles():
    """Demo all available spinner styles"""
    print("\n=== Spinner Styles ===")
    styles = {
        "CLASSIC (default)": Snurr.CLASSIC,
        "DOTS": Snurr.DOTS,
        "BAR": Snurr.BAR,
        "EARTH": Snurr.EARTH,
        "MOON": Snurr.MOON,
        "CLOCK": Snurr.CLOCK,
        "ARROWS": Snurr.ARROWS,
        "DOTS_BOUNCE": Snurr.DOTS_BOUNCE,
        "TRIANGLES": Snurr.TRIANGLES,
        "HEARTS": Snurr.HEARTS,
    }

    for name, style in styles.items():
        print(f"\nStyle: {name}")
        spinner = Snurr(symbols=style)
        spinner.start()
        sleep(2)
        spinner.stop()


def demo_with_output():
    """Demo spinner with concurrent stdout writes"""
    print("\n=== Spinner with Output ===")

    # Normal output with spinner on new line
    spinner = Snurr(symbols=Snurr.EARTH)
    spinner.start()
    print("Starting a long process...")
    sleep(1)
    print("Step 1: Data processing")
    sleep(1)
    spinner.stop()

    # Spinner at end of line
    print("\nSpinner at end of line:")
    spinner = Snurr(symbols=Snurr.CLASSIC, append=True)
    spinner.start()

    for i in range(3):
        print(f"\r{' ' * 40}", end="")
        print(f"\rLine {i} printed after spinner started", end="", flush=True)
        sleep(1)

    spinner.stop()
    print("\nDone!")


def demo_custom():
    """Demo custom spinner configuration"""
    print("\n=== Custom Spinner ===")
    print("Custom symbols and slower speed:")
    spinner = Snurr(symbols="◉◎", delay=0.5)
    spinner.start()
    sleep(2)
    spinner.stop()


if __name__ == "__main__":
    print("=== Snurr Spinner Demo ===")
    print("Press Ctrl+C to exit at any time")

    try:
        # demo_basic()
        # demo_styles()
        demo_with_output()
        # demo_custom()

        print("\nDemo completed! 🎉")
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
