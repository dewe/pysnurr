import time
from contextlib import redirect_stdout
from io import StringIO

import pytest
import regex

from pysnurr import Snurr


def test_init_default():
    """Test default initialization behavior"""
    spinner = Snurr()
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(0.002)
        spinner.stop()

    # Verify default spinner produces output
    assert len(output.getvalue()) > 0


def test_init_custom():
    """Test custom initialization behavior"""
    custom_symbols = "↑↓"
    custom_delay = 0.002
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
        time.sleep(0.002)
        first_output = output.getvalue()
        assert "X" in first_output

        # Stop should clear spinner
        spinner.stop()
        final_output = output.getvalue()
        assert not final_output.endswith("X")  # Spinner cleaned up


def test_spinner_animation():
    """Test that spinner animates through its symbols"""
    spinner = Snurr(delay=0.001, symbols="AB")  # Two distinct chars
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(0.005)  # Allow for multiple cycles
        spinner.stop()

    captured = output.getvalue()
    # Verify both symbols appeared
    assert "A" in captured and "B" in captured


def test_wide_character_display():
    """Test handling of wide (emoji) characters"""
    test_emoji = "🌍"
    spinner = Snurr(delay=0.001, symbols=test_emoji)
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(0.002)
        spinner.stop()

    lines = output.getvalue().split("\n")
    # Verify emoji appeared and was cleaned up
    assert test_emoji in output.getvalue()
    assert not lines[-1].endswith(test_emoji)


def test_concurrent_output():
    """Test output integrity during spinning"""
    test_messages = ["Start", "Middle", "End"]
    spinner = Snurr(delay=0.001)
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        for msg in test_messages:
            spinner.write(msg)
            time.sleep(0.002)
        spinner.stop()

    # Verify all messages appear in order
    captured = output.getvalue()
    last_pos = -1
    for msg in test_messages:
        pos = captured.find(msg)
        assert pos > last_pos  # Messages in correct order
        last_pos = pos


def test_spinner_at_end_of_line():
    """Test spinner appears at end of line"""
    spinner = Snurr(delay=0.001, symbols="_")
    output = StringIO()

    with redirect_stdout(output):
        print("Text", end="")
        spinner.start()
        time.sleep(0.002)
        spinner.stop()
        print("More", end="")  # Should be able to continue the line

    cleaned = simulate_backspaces(clean_escape_sequences(output.getvalue()))
    assert regex.match(r"Text(_*)More", cleaned)


def test_spinner_at_end_of_line_wide_chars():
    """Test spinner appears at end of line with emoji symbols"""
    spinner = Snurr(delay=0.001, symbols="⭐️")
    output = StringIO()

    with redirect_stdout(output):
        print("Text", end="")
        spinner.start()
        time.sleep(0.003)
        spinner.stop()
        print("More", end="")  # Should be able to continue the line

    cleaned = simulate_backspaces(clean_escape_sequences(output.getvalue()))
    assert regex.match(r"Text(\X*)More", cleaned)


def test_invalid_delay():
    """Test that invalid delay values raise appropriate exceptions"""
    with pytest.raises(ValueError, match="delay must be non-negative"):
        Snurr(delay=-1)


def test_invalid_symbols():
    """Test that invalid symbols raise appropriate exceptions"""
    with pytest.raises(ValueError, match="symbols cannot be empty"):
        Snurr(symbols="")

    with pytest.raises(ValueError, match="symbols string too long"):
        Snurr(symbols="x" * 101)  # Exceeds max length


def test_write_during_spinning():
    """Test that write works correctly while spinner is running"""
    spinner = Snurr(delay=0.001, symbols="_")
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(0.002)  # Let spinner run a bit
        spinner.write("Hello", end="")
        time.sleep(0.002)
        spinner.write("There")
        time.sleep(0.002)  # Let spinner continue after write
        spinner.stop()

    cleaned = simulate_backspaces(clean_escape_sequences(output.getvalue()))
    assert regex.match(r"(_*)Hello(_*)There", cleaned)


def test_keyboard_interrupt_handling():
    """Test that KeyboardInterrupt is handled gracefully in context manager"""
    spinner = Snurr(symbols="_", delay=0.001)
    stdout = StringIO()

    with redirect_stdout(stdout):
        try:
            print("Text")
            with spinner:
                time.sleep(0.002)  # Let spinner run briefly
                simulate_ctrl_c()
        except KeyboardInterrupt:
            pass  # Expected

    # Verify cleanup
    assert not spinner.busy
    # Verify thread is not running
    thread_alive = (
        spinner._spinner_thread is not None
        and spinner._spinner_thread.is_alive()  # noqa: E501
    )
    assert not thread_alive
    # Verify current symbol is cleared
    assert spinner._current_symbol is None

    # Verify final output ends with ^C
    cleaned = simulate_backspaces(clean_escape_sequences(stdout.getvalue()))
    assert regex.fullmatch(r"Text\n(_*)\^C", cleaned)


def test_write_bytes():
    """Test that write works correctly with bytes input"""
    spinner = Snurr(delay=0.001, symbols="_")
    output = StringIO()

    with redirect_stdout(output):
        spinner.start()
        time.sleep(0.002)  # Let spinner run a bit
        spinner.write(b"Hello", end="")
        time.sleep(0.002)
        spinner.write(b"There")
        time.sleep(0.002)  # Let spinner continue after write
        spinner.stop()

    cleaned = simulate_backspaces(clean_escape_sequences(output.getvalue()))
    assert regex.match(r"(_*)Hello(_*)There", cleaned)


def simulate_backspaces(str):
    result = ""
    i = 0
    while i < len(str):
        if str[i] == "\b":
            if result:  # Only remove last char if there is one
                result = result[:-1]
            i += 1
        else:
            result += str[i]
            i += 1
    return result


def clean_escape_sequences(str):
    result = ""
    i = 0
    while i < len(str):
        if str[i] == "\033":  # ESC character
            # Skip until end of ANSI sequence
            while i < len(str) and not str[i].isalpha():
                i += 1
            i += 1  # Skip the final letter
        else:
            result += str[i]
            i += 1
    return result


def simulate_ctrl_c():
    print("^C", end="")
    raise KeyboardInterrupt
