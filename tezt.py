from textual.app import App
from textual.widgets import Static, Button
from textual.reactive import reactive

class DayStatusApp(App):
    status = reactive("closed")

    def on_mount(self) -> None:
        """Initialize the status when the app starts."""
        self.status = "opened" if self.mock_get_status() else "closed"

    def mock_get_status(self) -> bool:
        """Mock method to get status. Returns True for opened and False for closed."""
        return False  # Change to True to test the "opened" state

    def compose(self):
        """Build the UI."""
        # Status message based on the current status
        yield Static(f"Day is {self.status.upper()}")
        # Button label based on the current status
        button_label = "Close Day" if self.status == "opened" else "Open Day"
        yield Button(label=button_label, id="status-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "status-button":
            # Toggle status
            if self.status == "opened":
                self.status = "closed"
            else:
                self.status = "opened"
            
            # Refresh the status label
            status_flag = self.query_one(Static)  # Get the Static widget displaying status
            status_flag.update(f"Day is {self.status.upper()}")  # Update the text
            
            # Update the button label based on the new status
            button_label = "Close Day" if self.status == "opened" else "Open Day"
            button = self.query_one(Button)  # Get the button widget
            button.label = button_label  # Update button label

            # Refresh the button to apply the new label
            self.refresh()

if __name__ == "__main__":
    DayStatusApp().run()
