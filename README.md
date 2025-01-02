# pysnurr

[![Tests](https://github.com/dewe/pysnurr/actions/workflows/tests.yml/badge.svg)](https://github.com/dewe/pysnurr/actions/workflows/tests.yml)

A beautiful terminal spinner library for Python. Provides non-blocking spinner animations at the current cursor position.

## Installation

```bash
pip install pysnurr
```

## Usage

```python
from pysnurr import Snurr, SPINNERS
import time

# Basic usage with context manager (recommended)
with Snurr() as spinner:
    time.sleep(2)  # Do some work

# Traditional usage
spinner = Snurr()
spinner.start()
time.sleep(2)  # Do some work
spinner.stop()

# Choose from various spinner styles
spinner = Snurr(symbols=SPINNERS["CLASSIC"])  # /-\|
spinner = Snurr(symbols=SPINNERS["EARTH"])    # 🌍🌎🌏
spinner = Snurr(symbols=SPINNERS["HEARTS"])   # 💛💙💜💚
spinner = Snurr(symbols=SPINNERS["MOON"])     # 🌑🌒🌓🌔🌕🌖🌗🌘
...

# Show spinner at end of line
print("Processing", end="")
with Snurr() as spinner:
    time.sleep(2)
print(" Done!")

# Thread-safe output during spinning
with Snurr(symbols=SPINNERS["EARTH"]) as spinner:
    spinner.write("Starting a long process...")
    time.sleep(1)
    spinner.write("Step 1: Data processing")
    time.sleep(1)
    spinner.write("Step 2: Analysis complete")
```

## Features

- Non-blocking animation
- Multiple built-in spinner styles:
  - `CLASSIC`: Classic ASCII spinner (/-\|)
  - `ARROWS`: Arrow rotation (←↖↑↗→↘↓↙)
  - `BAR`: ASCII loading bar (▁▂▃▄▅▆▇█▇▆▅▄▃▂▁)
  - `BLOCKS`: Minimal blocks (▌▀▐▄)
  - `DOTS_BOUNCE`: Bouncing dots (.oOᐤ°ᐤOo.)
  - `EARTH`: Earth rotation (🌍🌎🌏)
  - `HEARTS`: Colorful hearts (💛💙💜💚)
  - `MOON`: Moon phases (🌑🌒🌓🌔🌕🌖🌗🌘)
  - `SPARKLES`: Sparkling animation (✨⭐️💫)
  - `TRIANGLES`: Rotating triangles (◢◣◤◥)
  - `WAVE`: Wave pattern (⎺⎻⎼⎽⎼⎻)
- Cursor hiding during animation
- Thread-safe output
- Flexible positioning at current cursor position
- Python 3.10+ support

## Development

Clone the repository and install in development mode with all development dependencies:

```bash
git clone https://github.com/dewe/pysnurr.git
cd pysnurr
make dev-install  # Installs package and test dependencies
```

Run tests and checks:

```bash
make test        # Run type checking and tests
make lint        # Run code style checks (black & ruff)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
