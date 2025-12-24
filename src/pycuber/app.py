import time

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import DataTable, Digits, Footer, Header, Label, Static

from .scrambler import get_scramble


class ScrambleDisplay(Static):
    """A widget to display the scramble."""

    pass


class TimerDisplay(Digits):
    """A digital clock display."""


    pass


class StatsDisplay(Static):
    """A widget to display session statistics."""

    pass


def format_time(seconds: float) -> str:
    """Formats time as M:SS.ss or S.ss"""
    if seconds < 60:
        return f"{seconds:.2f}"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}:{secs:05.2f}"



class PyCuberApp(App):
    """A Textual app for a Rubik's cube timer."""

    CSS = """
    Screen {
        align: center middle;
    }

    #main_container {
        height: 100%;
        align: center middle;
    }

    #timer_container {
        width: 100%;
        height: 2fr;
        align: center middle;
    }

    #bottom_container {
        height: 1fr;
        width: 100%;
        layout: horizontal;
    }

    ScrambleDisplay {
        text-align: center;
        padding: 1;
        background: $panel;
        color: $text;
        border: solid $accent;
        dock: top;
        height: auto;
    }

    TimerDisplay {
        text-align: center;
        color: $text;
        height: auto;
        min-width: 20;
    }

    .idle {
        color: white;
    }

    .running {
        color: green;
    }

    DataTable {
        width: 2fr;
        height: 100%;
        border: solid $secondary;
    }

    StatsDisplay {
        width: 1fr;
        height: 100%;
        padding: 1;
        background: $surface;
        color: $text;
        border: solid $accent;
        text-align: left;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "new_scramble", "Skip Scramble"),
        ("x", "clear_history", "Clear History"),
    ]

    # Reactive state
    time_elapsed = reactive(0.0)
    timer_state = reactive("IDLE")  # IDLE, RUNNING

    def __init__(self):
        super().__init__()
        self.start_time = 0.0
        self.timer_interval = None
        self.solve_count = 0
        self.current_scramble = ""
        self.solve_times = []  # List of floats

    def compose(self) -> ComposeResult:
        yield Header()

        # specific initial scramble
        initial_scramble = get_scramble()
        self.current_scramble = initial_scramble
        yield ScrambleDisplay(initial_scramble, id="scramble")

        with Container(id="main_container"):
            with Vertical(id="timer_container"):
                yield TimerDisplay("0.00", id="timer")

            with Horizontal(id="bottom_container"):
                yield DataTable(id="history_log")
                yield StatsDisplay("Mean: N/A\nAo5: N/A", id="stats")

        yield Footer()

    def on_mount(self) -> None:
        """Setup the data table."""
        table = self.query_one(DataTable)
        table.add_columns("No.", "Time", "Scramble")
        table.cursor_type = "row"

    def update_timer(self) -> None:
        """Updates the timer display while running."""
        self.time_elapsed = time.monotonic() - self.start_time
        self.query_one(TimerDisplay).update(format_time(self.time_elapsed))

    def start_timer(self) -> None:
        """Starts the timer."""
        self.timer_state = "RUNNING"
        self.start_time = time.monotonic()

        # Update UI
        timer_display = self.query_one(TimerDisplay)
        timer_display.remove_class("idle")
        timer_display.add_class("running")

        # Start the tick loop
        self.timer_interval = self.set_interval(0.03, self.update_timer)

    def stop_timer(self) -> None:
        """Stops the timer and logs the result."""
        self.timer_state = "IDLE"
        if self.timer_interval:
            self.timer_interval.stop()
            self.timer_interval = None

        final_time = time.monotonic() - self.start_time
        self.time_elapsed = final_time

        # Update UI
        timer_display = self.query_one(TimerDisplay)
        timer_display.update(format_time(final_time))
        timer_display.remove_class("running")
        timer_display.add_class("idle")

        # Log to history
        self.log_solve(final_time)

        # Generate new scramble
        self.action_new_scramble()

    def calculate_ao5(self) -> str:
        """Calculates Average of 5 (current WCA style)."""
        if len(self.solve_times) < 5:
            return "N/A"

        last_5 = self.solve_times[-5:]
        sorted_solves = sorted(last_5)
        middle_3 = sorted_solves[1:4]
        avg = sum(middle_3) / 3
        return format_time(avg)

    def calculate_mean(self) -> str:
        """Calculates session mean."""
        if not self.solve_times:
            return "N/A"
        return format_time(sum(self.solve_times) / len(self.solve_times))

    def update_stats(self) -> None:
        """Updates the stats widget."""
        mean_str = self.calculate_mean()
        ao5_str = self.calculate_ao5()

        self.query_one("#stats", StatsDisplay).update(
            f"Count: {self.solve_count}\n\nMean: {mean_str}\nAo5:  {ao5_str}"
        )

    def log_solve(self, solve_time: float) -> None:
        """Adds the solve to the history table."""
        self.solve_count += 1
        self.solve_times.append(solve_time)

        table = self.query_one(DataTable)

        table.add_row(
            str(self.solve_count),
            format_time(solve_time),
            self.current_scramble,
            key=str(self.solve_count),
        )
        table.scroll_end()

        self.update_stats()

    def on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        if event.key == "space":
            if self.timer_state == "RUNNING":
                self.stop_timer()
            elif self.timer_state == "IDLE":
                self.start_timer()

        elif event.key == "q":
            self.exit()

    def action_new_scramble(self) -> None:
        """Generate a new scramble."""
        new_scramble = get_scramble()
        self.current_scramble = new_scramble

        scramble_widget = self.query_one("#scramble", ScrambleDisplay)
        scramble_widget.update(new_scramble)

    def action_clear_history(self) -> None:
        """Clear the session history."""
        table = self.query_one(DataTable)
        table.clear()
        self.solve_count = 0
        self.solve_times = []
        self.update_stats()


def main() -> None:
    app = PyCuberApp()
    app.run()


if __name__ == "__main__":
    main()
