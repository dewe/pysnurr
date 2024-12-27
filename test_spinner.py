import threading
import time
from contextlib import redirect_stdout
from io import StringIO

from spinner import Snurr


def test_init_default():
    """Test default initialization of Snurr"""
    spinner = Snurr()
    assert spinner.delay == 0.1
    assert spinner.symbols == Snurr.CLASSIC
    assert not spinner.busy
    assert spinner.spinner_thread is None


def test_init_custom():
    """Test custom initialization of Snurr"""
    spinner = Snurr(delay=0.2, symbols=Snurr.DOTS)
    assert spinner.delay == 0.2
    assert spinner.symbols == Snurr.DOTS
    assert not spinner.busy
    assert spinner.spinner_thread is None


def test_start_stop():
    """Test starting and stopping the spinner"""
    spinner = Snurr(delay=0.01)

    # Test start
    spinner.start()
    assert spinner.busy
    assert isinstance(spinner.spinner_thread, threading.Thread)
    assert spinner.spinner_thread.daemon
    assert spinner.spinner_thread.is_alive()

    # Test stop
    spinner.stop()
    assert not spinner.busy
    assert not spinner.spinner_thread.is_alive()


def test_spinner_output_simple():
    """Test spinner output with simple ASCII characters"""
    spinner = Snurr(delay=0.01, symbols="ab")
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(0.05)  # Allow for a few cycles
        spinner.stop()

    captured = output.getvalue()

    # Check that output contains our spinner characters
    assert "a" in captured
    assert "b" in captured

    # Check for backspace characters for animation
    assert "\b" in captured
    assert captured.count("\b") >= captured.count("a") + captured.count("b")


def test_spinner_output_wide_chars():
    """Test spinner output with emoji/wide characters"""
    spinner = Snurr(delay=0.01, symbols="🌍🌎")
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(0.05)
        spinner.stop()

    captured = output.getvalue()

    # Check that wide characters are present
    assert "🌍" in captured
    assert "🌎" in captured

    # Check for the pattern of our erasing sequence
    backspace_count = captured.count("\b")
    space_count = captured.count(" ")

    # We should have backspaces for erasing and spaces for clearing
    assert backspace_count > 0
    assert space_count > 0

    # The ratio of backspaces to spaces should be about 2:1
    # (we use \b twice for each space: once before, once after)
    assert abs(backspace_count - (space_count * 2)) <= 2


def test_cursor_visibility():
    """Test that cursor is properly hidden/shown during spinner operation"""
    spinner = Snurr(delay=0.01)
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(0.02)
        spinner.stop()

    captured = output.getvalue()

    # Verify cursor control sequences
    assert captured.startswith("\033[?25l")  # Should hide cursor first
    assert captured.endswith("\033[?25h")  # Should show cursor last
    assert captured.count("\033[?25l") == 1  # Should only hide once
    assert captured.count("\033[?25h") == 1  # Should only show once


def test_all_spinner_styles():
    """Test that all predefined spinner styles can be used"""
    styles = [
        Snurr.DOTS,
        Snurr.CLASSIC,
        Snurr.BAR,
        Snurr.EARTH,
        Snurr.MOON,
        Snurr.CLOCK,
        Snurr.ARROWS,
        Snurr.DOTS_BOUNCE,
        Snurr.TRIANGLES,
        Snurr.HEARTS,
    ]

    for style in styles:
        spinner = Snurr(delay=0.01, symbols=style)
        spinner.start()
        time.sleep(0.02)
        spinner.stop()


def test_concurrent_output():
    """Test that spinner works correctly with concurrent stdout writes"""
    spinner = Snurr(delay=0.01, symbols="ab")
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        # Simulate other work that writes to stdout
        print("Starting work...")
        time.sleep(0.02)
        print("More output")
        time.sleep(0.02)
        print("Done!")
        spinner.stop()

    captured = output.getvalue()

    # Check that our printed messages are present
    assert "Starting work..." in captured
    assert "More output" in captured
    assert "Done!" in captured

    # Check that spinner characters are also present
    assert "a" in captured
    assert "b" in captured

    # Verify newlines don't break the spinner animation
    lines = captured.split("\n")
    # Last line should contain backspaces from spinner cleanup
    assert "\b" in lines[-1]


def test_append_mode():
    """Test spinner in append mode (at end of line)"""
    spinner = Snurr(delay=0.01, symbols="ab", append=True)
    output = StringIO()

    with redirect_stdout(output):
        print("Processing", end="")  # No newline
        spinner.start()
        time.sleep(0.05)
        spinner.stop()

    captured = output.getvalue()

    # Check that output starts with our text
    assert captured.startswith("Processing")

    # Check that spinner appears after a space
    assert " a" in captured or " b" in captured

    # Check backspaces account for space
    backspace_count = captured.count("\b")
    assert backspace_count >= 2  # At least one for char + one for space
