import time
from contextlib import redirect_stdout
from io import StringIO

import pytest
import regex

from pysnurr import Snurr


class TestUtils:
    @staticmethod
    def simulate_backspaces(text: str) -> str:
        """Simulate the effect of backspace characters in a terminal."""
        visible_chars = []

        for char in text:
            if char == "\b":
                if visible_chars:
                    visible_chars.pop()
            else:
                visible_chars.append(char)

        return "".join(visible_chars)

    @staticmethod
    def clean_escape_sequences(text: str) -> str:
        """Remove ANSI escape sequences from text."""
        result = []
        skip_until_letter = False

        for char in text:
            if char == "\033":  # Start of escape sequence
                skip_until_letter = True
                continue

            if skip_until_letter:
                if char.isalpha():  # End of escape sequence
                    skip_until_letter = False
                continue

            result.append(char)

        return "".join(result)

    @staticmethod
    def simulate_ctrl_c():
        print("^C", end="")
        raise KeyboardInterrupt


class TestSpinnerInitialization:
    def test_default_initialization(self):
        """Verify spinner initializes with default settings."""
        spinner = Snurr()
        output = StringIO()

        with redirect_stdout(output):
            spinner.start()
            time.sleep(0.002)
            spinner.stop()

        # Verify default spinner produces output
        assert len(output.getvalue()) > 0

    def test_custom_initialization(self):
        """Verify spinner initializes with custom settings."""
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

    def test_raises_on_negative_delay(self):
        """Verify ValueError is raised for negative delay values."""
        with pytest.raises(ValueError, match="delay must be non-negative"):
            Snurr(delay=-1)

    def test_raises_on_invalid_symbols(self):
        """Verify ValueError is raised for invalid symbol strings."""
        with pytest.raises(ValueError, match="symbols cannot be empty"):
            Snurr(symbols="")

        with pytest.raises(ValueError, match="symbols string too long"):
            Snurr(symbols="x" * 101)  # Exceeds max length


class TestSpinnerBehavior:
    def test_start_stop(self):
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

    def test_spinner_animation(self):
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


class TestSpinnerDisplay:
    def test_wide_character_display(self):
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

    def test_spinner_at_end_of_line(self):
        """Test spinner appears at end of line"""
        spinner = Snurr(delay=0.001, symbols="_")
        output = StringIO()

        with redirect_stdout(output):
            print("Text", end="")
            spinner.start()
            time.sleep(0.002)
            spinner.stop()
            print("More", end="")  # Should be able to continue the line

        # Clean up output for verification
        output_value = output.getvalue()
        output_no_escapes = TestUtils.clean_escape_sequences(output_value)
        cleaned = TestUtils.simulate_backspaces(output_no_escapes)

        # Verify output structure
        assert regex.match(r"Text(_*)More", cleaned)

    def test_spinner_at_end_of_line_wide_chars(self):
        """Test spinner appears at end of line with emoji symbols"""
        spinner = Snurr(delay=0.001, symbols="⭐️")
        output = StringIO()

        with redirect_stdout(output):
            print("Text", end="")
            spinner.start()
            time.sleep(0.003)
            spinner.stop()
            print("More", end="")  # Should be able to continue the line

        # Clean up output for verification
        output_value = output.getvalue()
        output_no_escapes = TestUtils.clean_escape_sequences(output_value)
        cleaned = TestUtils.simulate_backspaces(output_no_escapes)

        # Verify output structure
        assert regex.match(r"Text(\X*)More", cleaned)


class TestSpinnerOutput:
    def test_concurrent_output(self):
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

    def test_write_during_spinning(self):
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

        # Clean up output for verification
        output_value = output.getvalue()
        output_no_escapes = TestUtils.clean_escape_sequences(output_value)
        cleaned = TestUtils.simulate_backspaces(output_no_escapes)

        # Verify output structure
        assert regex.match(r"(_*)Hello(_*)There", cleaned)

    def test_write_end_argument(self):
        """Test that write method correctly handles end argument"""
        spinner = Snurr(symbols="_")
        output = StringIO()

        with redirect_stdout(output):
            spinner.start()
            # No newline
            spinner.write("First", end="")
            # Custom end
            spinner.write("Second", end="|")
            # Default newline
            spinner.write("Third")
            spinner.stop()

        # Clean up output for verification
        output_value = output.getvalue()
        output_no_escapes = TestUtils.clean_escape_sequences(output_value)
        cleaned = TestUtils.simulate_backspaces(output_no_escapes)

        # Verify output has correct endings
        assert "FirstSecond|Third\n" in cleaned


class TestErrorHandling:
    def test_keyboard_interrupt_handling(self):
        """Verify spinner cleans up properly when interrupted."""
        spinner = Snurr(symbols="_", delay=0.001)
        output = StringIO()

        with redirect_stdout(output):
            try:
                print("Text")
                with spinner:
                    time.sleep(0.002)  # Let spinner run briefly
                    TestUtils.simulate_ctrl_c()
            except KeyboardInterrupt:
                pass  # Expected

        # Verify cleanup state
        assert not spinner.busy
        assert spinner._current_symbol is None

        # Check thread is cleaned up
        has_thread = spinner._spinner_thread is not None
        is_alive = has_thread and spinner._spinner_thread.is_alive()
        assert not is_alive

        # Clean up output for verification
        output_value = output.getvalue()
        output_no_escapes = TestUtils.clean_escape_sequences(output_value)
        cleaned = TestUtils.simulate_backspaces(output_no_escapes)

        # Verify final output ends with ^C
        assert regex.fullmatch(r"Text\n(_*)\^C", cleaned)
