from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Footer, Pretty, Button


class SettingsScreen(Screen):
    """Modal screen to display the connection settings in a styled modal."""

    BINDINGS = [("escape", "dismiss", "Close"), ("q", "dismiss", "Close")]

    def __init__(self, config: dict, connection_name: str):
        super().__init__(id="settings_screen")
        self.config = config
        self.connection_name = connection_name

    def compose(self) -> ComposeResult:
        # Mask sensitive fields before rendering
        masked = self._mask_sensitive(self.config)

        with Container():
            yield Pretty(masked)
            # Close button in the modal footer
            yield Container(Button("Close", id="settings_close", classes="close-button"), classes="button-container")
        yield Footer()

    def action_dismiss(self) -> None:
        """Close the settings screen and return to main app."""
        self.app.pop_screen()

    async def on_button_pressed(self, event) -> None:
        """Handle the Close button in the modal."""
        if getattr(event, "button", None) is not None and event.button.id == "settings_close":
            self.action_dismiss()

    def _mask_sensitive(self, data):
        """Return a copy of data with sensitive values (passwords, tokens) masked.

        Works recursively for dicts and lists.
        """
        sensitive_keys = {"password", "passwd", "pwd", "secret", "token", "key", "access_token"}

        def _mask(obj):
            if isinstance(obj, dict):
                out = {}
                for k, v in obj.items():
                    if isinstance(k, str) and k.lower() in sensitive_keys:
                        out[k] = "******"
                    else:
                        out[k] = _mask(v)
                return out
            if isinstance(obj, list):
                return [_mask(x) for x in obj]
            # primitives
            return obj

        try:
            return _mask(data)
        except Exception:
            # If masking fails, return a shallow copy with top-level passwords masked
            if isinstance(data, dict):
                out = dict(data)
                for k in list(out.keys()):
                    if isinstance(k, str) and k.lower() in sensitive_keys:
                        out[k] = "******"
                return out
            return data
