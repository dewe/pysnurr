# Snurr

[![Tests](https://github.com/dewe/pysnurr/actions/workflows/tests.yml/badge.svg)](https://github.com/dewe/pysnurr/actions/workflows/tests.yml)

A lightweight terminal spinner animation for Python applications. Provides non-blocking spinner animations at the current cursor position.

## Usage

```python
from snurr import Snurr
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
spinner = Snurr(symbols=Snurr.HEARTS)   # 💛💙💜💚❤️

# Show spinner at end of line
print("Processing", end="")
spinner = Snurr(append=True)  # Adds space before spinner
spinner.start()
time.sleep(2)
spinner.stop()
print(" Done!")
```

## Features

- Non-blocking animation
- Multiple built-in spinner styles
- Cursor hiding during animation
- Thread-safe output
- No dependencies
- Flexible positioning (new line or end of text)
