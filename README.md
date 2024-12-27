# pysnurr

[![Tests](https://github.com/dewe/pysnurr/actions/workflows/tests.yml/badge.svg)](https://github.com/dewe/pysnurr/actions/workflows/tests.yml)

A beautiful terminal spinner library for Python. Provides non-blocking spinner animations at the current cursor position.

## Installation

```bash
pip install pysnurr
```

## Usage

```python
from pysnurr import Snurr
import time

# Basic usage with default spinner (/-\|)
spinner = Snurr()
spinner.start()
time.sleep(2)  # Do some work
spinner.stop()

# Choose from various spinner styles
spinner = Snurr(symbols=Snurr.DOTS)     # ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏
spinner = Snurr(symbols=Snurr.EARTH)    # 🌍🌎🌏
spinner = Snurr(symbols=Snurr.CLOCK)    # 🕐🕑🕒...
spinner = Snurr(symbols=Snurr.HEARTS)   # 💛💙💜💚

# Show spinner at end of line
print("Processing", end="")
spinner = Snurr(append=True)  # Adds space before spinner
spinner.start()
time.sleep(2)
spinner.stop()
print(" Done!")

# Thread-safe output during spinning
spinner = Snurr(symbols=Snurr.EARTH)
spinner.start()
spinner.write("Starting a long process...")
time.sleep(1)
spinner.write("Step 1: Data processing")
time.sleep(1)
spinner.write("Step 2: Analysis complete")
spinner.stop()
```

## Features

- Non-blocking animation
- Multiple built-in spinner styles:
  - `CLASSIC`: Classic ASCII spinner (/-\|)
  - `DOTS`: Braille dots animation
  - `BAR`: ASCII loading bar
  - `EARTH`: Earth rotation (🌍🌎🌏)
  - `MOON`: Moon phases
  - `CLOCK`: Clock rotation
  - `ARROWS`: Arrow rotation
  - `DOTS_BOUNCE`: Bouncing dots
  - `TRIANGLES`: Rotating triangles
  - `HEARTS`: Colorful hearts
- Cursor hiding during animation
- Thread-safe output
- No external dependencies
- Flexible positioning (new line or end of text)
- Python 3.7+ support

## Development

Clone the repository and install in development mode:

```bash
git clone https://github.com/dewe/pysnurr.git
cd pysnurr
pip install -e .
```

Run tests:

```bash
pip install pytest
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
