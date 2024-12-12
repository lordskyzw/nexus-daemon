from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static, Button
from textual.reactive import reactive
from textual.driver import Driver
import asyncio

class SafeDriver(Driver):
    """Custom driver to avoid termios dependency."""
    def enable_input(self):
        pass

    def disable_input(self):
        pass

    def start_application_mode(self):
        pass

    def stop_application_mode(self):
        pass

    def write(self, data: str) -> None:
        pass

class DayStatusApp(App):
    CSS = """
    .status-container {
        align: center middle;
        height: 100%;
        width: 100%;
    }
    .status-flag {
        text-align: center;
    }
    .action-button {
        width: 50%;
        align: center middle;
    }
    .opened {
        background: green;
    }
    .closed {
        background: red;
    }
    """

    status = reactive("closed")

    def on_mount(self) -> None:
        """Called when the app starts to initialize the status."""
        print("App Mounted")  # Debugging statement to ensure it's running
        # Mock a "get status" call here
        # Replace this with real backend integration later
        self.status = "opened" if self.mock_get_status() else "closed"
        print(f"Status set to: {self.status}")  # Check status

    def mock_get_status(self) -> bool:
        """Mock method to get status. Returns True for opened and False for closed."""
        return False  # Change to True to test the "opened" state

    def compose(self) -> ComposeResult:
        """Compose the user interface."""
        print("Composing UI...")  # Check if the UI composition is triggered
        container_class = "opened" if self.status == "opened" else "closed"
        
        with Container(classes=container_class):  # Use string instead of list
            print("Adding Static Widget...")  # Debugging statement
            status_flag = Static(
                "Day is OPENED" if self.status == "opened" else "Day is CLOSED"
            )
            status_flag.add_class("status-flag")
            yield status_flag

            print("Adding Button Widget...")  # Debugging statement
            button_label = "Close Day" if self.status == "opened" else "Open Day"
            button = Button(label=button_label, id="status-button")
            button.add_class("action-button")
            yield button

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        print(f"Button {event.button.id} pressed.")  # Check button press
        if event.button.id == "status-button":
            # Mock button action here (real API call logic goes here later)
            if self.status == "opened":
                self.status = "closed"
            else:
                self.status = "opened"
            # Refresh UI
            self.refresh()

if __name__ == "__main__":
    app = DayStatusApp(driver_class=SafeDriver)
    app.run()  # Explicitly running the app
