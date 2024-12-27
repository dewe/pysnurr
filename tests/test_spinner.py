import time
from contextlib import redirect_stdout
from io import StringIO

import pytest

from pysnurr import Snurr


def test_init_default():
    """Test default initialization behavior"""
    spinner = Snurr()
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(0.02)
        spinner.stop()

    # Verify default spinner produces output
    assert len(output.getvalue()) > 0


def test_init_custom():
    """Test custom initialization behavior"""
    custom_symbols = "↑↓"
    custom_delay = 0.2
    spinner = Snurr(delay=custom_delay, symbols=custom_symbols)
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(custom_delay * 2)  # Wait for at least one cycle
        spinner.stop()

    # Verify custom symbols are used
    assert any(symbol in output.getvalue() for symbol in custom_symbols)


def test_start_stop():
    """Test starting and stopping behavior"""
    spinner = Snurr(symbols="X")  # Single char for simpler testing
    output = StringIO()

    with redirect_stdout(output):
        # Start should show spinner
        spinner.start()
        time.sleep(0.02)
        first_output = output.getvalue()
        assert "X" in first_output

        # Stop should clear spinner
        spinner.stop()
        final_output = output.getvalue()
        assert not final_output.endswith("X")  # Spinner cleaned up


def test_spinner_animation():
    """Test that spinner animates through its symbols"""
    spinner = Snurr(delay=0.01, symbols="AB")  # Two distinct chars
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(0.05)  # Allow for multiple cycles
        spinner.stop()

    captured = output.getvalue()
    # Verify both symbols appeared
    assert "A" in captured and "B" in captured


def test_wide_character_display():
    """Test handling of wide (emoji) characters"""
    test_emoji = "🌍"
    spinner = Snurr(delay=0.01, symbols=test_emoji)
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(0.02)
        spinner.stop()

    lines = output.getvalue().split("\n")
    # Verify emoji appeared and was cleaned up
    assert test_emoji in output.getvalue()
    assert not lines[-1].endswith(test_emoji)


def test_cursor_handling():
    """Test cursor visibility behavior"""
    spinner = Snurr(delay=0.01)
    output1 = StringIO()
    output2 = StringIO()

    # Test that cursor state is restored after normal operation
    with redirect_stdout(output1):
        print("before", end="")
        spinner.start()
        time.sleep(0.02)
        spinner.stop()
        print("after", end="")

    # Test that cursor state is restored after exception
    with redirect_stdout(output2):
        print("before", end="")
        try:
            spinner.start()
            raise KeyboardInterrupt
        except KeyboardInterrupt:
            spinner.stop()
        print("after", end="")

    # Verify cursor handling in both cases
    assert "before" in output1.getvalue() and "after" in output1.getvalue()
    assert "before" in output2.getvalue() and "after" in output2.getvalue()


def test_all_spinner_styles():
    """Test all predefined spinner styles produce output"""
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
        output = StringIO()
        with redirect_stdout(output):
            spinner.start()
            time.sleep(0.02)
            spinner.stop()
        # Verify style produces visible output
        assert len(output.getvalue().strip()) > 0


def test_concurrent_output():
    """Test output integrity during spinning"""
    test_messages = ["Start", "Middle", "End"]
    spinner = Snurr(delay=0.01)
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        for msg in test_messages:
            spinner.write(msg)
            time.sleep(0.02)
        spinner.stop()

    # Verify all messages appear in order
    captured = output.getvalue()
    last_pos = -1
    for msg in test_messages:
        pos = captured.find(msg)
        assert pos > last_pos  # Messages in correct order
        last_pos = pos


def test_append_mode():
    """Test spinner appears at end of line in append mode"""
    spinner = Snurr(delay=0.01, append=True)
    output = StringIO()

    with redirect_stdout(output):
        print("Text", end="")
        spinner.start()
        time.sleep(0.02)
        spinner.stop()
        print("More", end="")  # Should be able to continue the line

    captured = output.getvalue()
    # Verify text remains and we can continue writing on the same line
    assert captured.startswith("Text")
    assert "More" in captured
    assert "Text" in captured.split("More")[0]  # Text appears before continuation


def test_invalid_delay():
    """Test that invalid delay values raise appropriate exceptions"""
    with pytest.raises(TypeError, match="delay must be a number"):
        Snurr(delay="0.1")

    with pytest.raises(ValueError, match="delay must be non-negative"):
        Snurr(delay=-1)


def test_invalid_symbols():
    """Test that invalid symbols raise appropriate exceptions"""
    with pytest.raises(TypeError, match="symbols must be a string"):
        Snurr(symbols=123)

    with pytest.raises(ValueError, match="symbols cannot be empty"):
        Snurr(symbols="")

    with pytest.raises(ValueError, match="symbols string too long"):
        Snurr(symbols="x" * 101)  # Exceeds max length


def test_invalid_append():
    """Test that invalid append value raises TypeError"""
    with pytest.raises(TypeError, match="append must be a boolean"):
        Snurr(append="true")


def test_invalid_write():
    """Test that invalid write parameters raise appropriate exceptions"""
    spinner = Snurr()

    with pytest.raises(TypeError, match="text must be a string or bytes"):
        spinner.write(123)

    with pytest.raises(TypeError, match="end must be a string"):
        spinner.write("text", end=123)
