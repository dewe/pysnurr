from time import sleep

from pysnurr import Snurr


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

    # Using synchronized write method
    print("\nUsing synchronized write method:")
    spinner = Snurr(symbols=Snurr.EARTH)
    spinner.start()
    spinner.write("Starting a long process...")
    sleep(1)
    spinner.write("Step 1: Data processing")
    sleep(1)
    spinner.write("Step 2: Analysis complete")
    sleep(1)
    spinner.stop()

    # Spinner at end of line with synchronized writes
    print("\nSpinner at end of line:")
    spinner = Snurr(symbols=Snurr.HEARTS, append=True)
    spinner.start()

    for i in range(3):
        spinner.write(f"\rLine {i+1} while spinning", end="")
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
        demo_basic()
        demo_styles()
        demo_with_output()
        demo_custom()

        print("\nDemo completed! 🎉")
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
