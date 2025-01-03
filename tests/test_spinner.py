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
        custom_frames = "↑↓"
        custom_delay = 0.002
        spinner = Snurr(delay=custom_delay, frames=custom_frames)
        output = StringIO()

        with redirect_stdout(output):
            spinner.start()
            time.sleep(custom_delay * 2)  # Wait for at least one cycle
            spinner.stop()

        # Verify custom frames are used
        assert any(frame in output.getvalue() for frame in custom_frames)

    def test_initial_status(self):
        """Verify spinner can be initialized with a status message."""
        initial_status = "Initial status"

        spinner = Snurr(delay=0.001, status=initial_status)
        assert spinner.status == initial_status

        output = StringIO()
        with redirect_stdout(output):
            spinner.start()
            time.sleep(0.02)
            spinner.stop()

        # Clean up output for verification
        output_value = output.getvalue()
        output_no_escapes = TestUtils.clean_escape_sequences(output_value)
        cleaned = TestUtils.simulate_backspaces(output_no_escapes)

        # Verify initial status appears in output
        assert initial_status in cleaned

    def test_raises_on_negative_delay(self):
        """Verify ValueError is raised for negative delay values."""
        with pytest.raises(ValueError, match="delay must be non-negative"):
            Snurr(delay=-1)

    def test_raises_on_invalid_frames(self):
        """Verify ValueError is raised for invalid frame strings."""
        with pytest.raises(ValueError, match="frames cannot be empty"):
            Snurr(frames="")

        with pytest.raises(ValueError, match="frames string too long"):
            Snurr(frames="x" * 101)  # Exceeds max length


class TestSpinnerBehavior:
    def test_start_stop(self):
        """Test starting and stopping behavior"""
        spinner = Snurr(frames="X")  # Single char for simpler testing
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
        """Test that spinner animates through its frames"""
        spinner = Snurr(delay=0.001, frames="AB")  # Two distinct chars
        output = StringIO()

        with redirect_stdout(output):
            spinner.start()
            time.sleep(0.005)  # Allow for multiple cycles
            spinner.stop()

        captured = output.getvalue()
        # Verify both frames appeared
        assert "A" in captured and "B" in captured


class TestSpinnerDisplay:
    def test_wide_character_display(self):
        """Test handling of wide (emoji) characters"""
        test_emoji = "🌍"
        spinner = Snurr(delay=0.001, frames=test_emoji)
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
        spinner = Snurr(delay=0.001, frames="_")
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
        """Test spinner appears at end of line with emoji frames"""
        spinner = Snurr(delay=0.001, frames="⭐️")
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

    def test_status_during_spinning(self):
        """Test that status works correctly while spinner is running"""
        spinner = Snurr(delay=0.001, frames="_")
        output = StringIO()

        with redirect_stdout(output):
            spinner.start()
            time.sleep(0.005)  # Let spinner run a bit
            spinner.status = "Hello"
            time.sleep(0.005)
            spinner.status = "World"
            time.sleep(0.005)  # Let spinner continue after status
            spinner.stop()

        # Clean up output for verification
        output_value = output.getvalue()
        output_no_escapes = TestUtils.clean_escape_sequences(output_value)
        cleaned = TestUtils.simulate_backspaces(output_no_escapes)

        # Verify output contains status messages
        assert "Hello" in cleaned
        assert "World" in cleaned

    def test_status_updates(self):
        """Test that status updates work correctly"""
        spinner = Snurr(frames="_", delay=0.001)
        output = StringIO()

        with redirect_stdout(output):
            spinner.start()
            # Initial status
            spinner.status = "First"
            time.sleep(0.01)  # Increased sleep time
            # Update status
            spinner.status = "Second"
            time.sleep(0.01)  # Increased sleep time
            # Final status
            spinner.status = "Third"
            time.sleep(0.01)  # Increased sleep time
            spinner.stop()

        # Clean up output for verification
        output_value = output.getvalue()
        output_no_escapes = TestUtils.clean_escape_sequences(output_value)
        cleaned = TestUtils.simulate_backspaces(output_no_escapes)

        # Verify all status messages appear
        assert "First" in cleaned
        assert "Second" in cleaned
        assert "Third" in cleaned

    def test_status_property(self):
        """Test that status property can be get and set."""
        spinner = Snurr()
        assert spinner.status == ""  # Default empty status

        spinner.status = "Processing..."
        assert spinner.status == "Processing..."

        spinner.status = "Done!"
        assert spinner.status == "Done!"

    def test_status_updates_while_running(self):
        """Test that status can be updated while spinner is running."""
        spinner = Snurr(delay=0.01)

        try:
            spinner.start()
            assert spinner.status == ""

            spinner.status = "Working..."
            assert spinner.status == "Working..."

            spinner.status = "Almost done..."
            assert spinner.status == "Almost done..."
        finally:
            spinner.stop()

    def test_status_position(self):
        """Test that status appears before the spinner."""
        spinner = Snurr(delay=0.001, frames="_")  # Simple frame for testing
        output = StringIO()

        with redirect_stdout(output):
            spinner.start()
            spinner.status = "Working"
            time.sleep(0.01)
            spinner.stop()

        # Clean up output for verification
        output_value = output.getvalue()
        cleaned = TestUtils.clean_escape_sequences(output_value)

        # Verify last status appears before last spinner
        assert cleaned.rindex("Working") < cleaned.rindex("_")


class TestErrorHandling:
    def test_keyboard_interrupt_handling(self):
        """Verify spinner cleans up properly when interrupted."""
        spinner = Snurr(frames="_", delay=0.001)
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
        assert not spinner._busy
        assert spinner._buffer == ""

        # Check thread is cleaned up
        has_thread = spinner._spinner_thread is not None
        is_alive = has_thread and spinner._spinner_thread.is_alive()
        assert not is_alive

        # Clean up output for verification
        output_value = output.getvalue()
        output_no_escapes = TestUtils.clean_escape_sequences(output_value)
        cleaned = TestUtils.simulate_backspaces(output_no_escapes)

        # Verify final output ends with ^C
        assert "Text" in cleaned
        assert cleaned.endswith("^C")
