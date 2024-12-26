import time

from spinner import Snurr


def main():
    print("Starting a long process...")

    # Choose any spinner style using the class constants
    spinner = Snurr(symbols=Snurr.EARTH, delay=0.2)
    # spinner = Snurr(symbols=Snurr.CLOCK, delay=0.2)  # Try different styles
    spinner.start()

    # Simulate some work
    for _ in range(3):
        time.sleep(1)  # Simulate work being done

    spinner.stop()
    print("\nProcess completed!")


if __name__ == "__main__":
    main()
