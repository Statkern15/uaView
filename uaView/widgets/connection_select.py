from textual import on
from textual.widgets import Select


class ConnectionSelect(Select):
    CSS_PATH = "style.tcss"

    def __init__(self, settings: dict, **kwargs):
        super().__init__(
            options=[],  # start with no options; populate on_mount
            prompt="Select Connection",
            id="connection_select",
            **kwargs,
        )
        self.settings = settings

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle selection changes."""
        self.log(f"Selected connection: {event.value}")

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        """React to selection changes in the dropdown.

        Updates the widget title to reflect the currently selected value.

        Parameters:
            event: The Textual Select.Changed event carrying the new selection.
        """
        self.title = str(event.value)

    def on_mount(self) -> None:
        """Load settings and populate the select with top-level keys."""
        keys = list(self.settings.keys())
        # Build (label, value) tuples from keys
        new_options = [(k, k) for k in keys]
        self.set_options(new_options)

        # Ensure the select is not focused so it starts closed
        if hasattr(self, "blur"):
            self.blur()
