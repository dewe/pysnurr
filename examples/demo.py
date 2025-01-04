from time import sleep

from pysnurr import SPINNERS, Snurr


def demo_basic() -> None:
    """Demo basic spinner usage"""
    print("\n=== Basic Usage ===")

    print("\nContext manager (recommended):")
    with Snurr() as spinner:
        spinner.status = "Working..."
        sleep(2)  # Simulate work

    # TODO: Add a demo for busy=False and busy=True

    print("\nTraditional usage:")
    spinner = Snurr()
    spinner.start()
    spinner.status = "Processing..."
    sleep(2)  # Simulate work
    spinner.stop()


def demo_styles() -> None:
    """Demo all available spinner styles"""
    print("\n=== Spinner Styles ===")

    for name, style in SPINNERS.items():
        style_name = f"{name} (default)" if name == "CLASSIC" else name
        print(f"\nStyle: {style_name}")
        with Snurr(frames=style):
            sleep(2)


def demo_status_updates() -> None:
    """Demo dynamic status updates"""
    print("\n=== Status Updates ===")

    print("\nUpdating status while spinning:")
    with Snurr(frames=SPINNERS["EARTH"]) as spinner:
        spinner.status = "Starting up..."
        sleep(1)
        spinner.status = "Processing files..."
        sleep(1.5)
        spinner.status = "Analyzing data..."
        sleep(1.5)
        spinner.status = "Finishing up..."
        sleep(2)

    print("\nStatus text with emojis:")
    with Snurr(frames=SPINNERS["SPARKLES"]) as spinner:
        sleep(2)
        spinner.status = "🚀 Launching..."
        sleep(2)


def demo_custom() -> None:
    """Demo custom spinner configuration"""
    print("\n=== Custom Spinner ===")

    print("\nCustom frames and slower speed:")
    with Snurr(frames="◉◎", delay=0.5):
        sleep(3)

    print("\nSpinner at end of text: ", end="")
    with Snurr(frames=SPINNERS["HEARTS"]) as spinner:
        sleep(2)
        spinner.status = "Here -->"
        sleep(2)
    print()


if __name__ == "__main__":
    print("=== Snurr Spinner Demo ===")
    print("Press Ctrl+C to exit at any time")

    try:
        demo_basic()
        demo_styles()
        demo_status_updates()
        demo_custom()

        print("\nDemo completed! 🎉")
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
