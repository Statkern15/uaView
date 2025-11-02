import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from textual import log
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Footer, Header, Select
from ua_client.client import UAViewerClient
from widgets.address_space import AddressSpace
from widgets.attributes_view import AttributesView
from widgets.connection_select import ConnectionSelect
from widgets.settings_screen import SettingsScreen
from widgets.data_view import DataView
from widgets.logs import LogView

load_dotenv()


class uaViewer(App):
    """A Textual App to view and interact with OPC-UA servers."""

    CSS_PATH = "style.tcss"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit the app"),
        ("Tab", "next_view", "Next view"),
        ("s", "subscribe_selected", "Subscribe node"),
        ("u", "unsubscribe_selected", "Unsubscribe node"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ua_client = None
        self.settings = self._load_settings()
        # Track active subscriptions: node_id -> {"sub": subscription, "handle": handle}
        self._subscriptions: dict[str, dict] = {}

    def _load_settings(self) -> dict:
        """Load connection settings from a path in UAVIEW_SETTINGS or default location."""
        env_path = os.environ.get("UAVIEW_SETTINGS")
        if env_path and Path(env_path).exists():
            try:
                log(f"Loading settings from {env_path}")
                return json.loads(Path(env_path).read_text(encoding="utf-8"))
            except Exception as exc:
                log(f"Failed to load settings from {env_path}: {exc}")
                # Fallback to default if env file is invalid
        # Default path
        settings_path = Path(__file__).parent / "config" / "settings.json"
        if settings_path.exists():
            return json.loads(settings_path.read_text(encoding="utf-8"))
        return {}

    def compose(self) -> ComposeResult:
        # Header
        yield Header(
            show_clock=True,
            name="uaViewer",
            id="header",
            icon="⚙️",
        )

        # Connection bar
        with Horizontal(id="connection_bar"):
            yield ConnectionSelect(settings=self.settings)
            yield Button("Connect", id="connect_button", variant="success")
            yield Button("Disconnect", id="disconnect_button", variant="error", disabled=True)
            yield Button("View Settings", id="view_settings_button", variant="primary")

        # Main area (address space, data view, attributes)
        with Horizontal(id="main_area"):
            yield AddressSpace()
            yield DataView()
            yield AttributesView()

        # Logs
        yield LogView()

        # Footer
        yield Footer(
            name="uaViewer",
            id="footer",
            show_command_palette=True,
            compact=True,
        )

    def on_mount(self) -> None:
        """Disable interactive views until a connection is established."""
        try:
            self.query_one(AddressSpace).disabled = True
            self.query_one(DataView).disabled = True
            self.query_one(AttributesView).disabled = True
        except Exception:
            # If layout changes or widgets not present yet, ignore
            pass

    def _log_message(self, message: str):
        """Write a timestamped message to the log view."""
        log_view = self.query_one(LogView)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_view.write_line(f"{timestamp} {message}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id

        if button_id == "connect_button":
            await self._handle_connect()
        elif button_id == "disconnect_button":
            await self._handle_disconnect()
        elif button_id == "view_settings_button":
            self._handle_view_settings()

    async def _handle_connect(self):
        """Handle the connect button press."""
        # Get selected connection from the select widget
        connection_select = self.query_one(ConnectionSelect)
        selected_connection = connection_select.value

        if selected_connection == Select.BLANK:
            self._log_message("No connection selected")
            return

        # Get connection config from settings
        if selected_connection not in self.settings:
            self._log_message(f"Connection '{selected_connection}' not found in settings")
            return

        config = self.settings[selected_connection]

        try:
            self._log_message(f"Connecting to {config['endpoint_url']}...")

            # Create and connect the UA client
            self.ua_client = UAViewerClient(config)
            await self.ua_client.connect()

            self._log_message(f"Connected to {selected_connection}")

            # Update button states
            self.query_one("#connect_button", Button).disabled = True
            self.query_one("#connection_select", Select).disabled = True
            self.query_one("#disconnect_button", Button).disabled = False

            # Load only the root's children (lazy browsing from here on)
            addr = self.query_one(AddressSpace)
            addr.set_client(self.ua_client)
            await addr.load_root()

            # Enable interactive views now that we're connected
            try:
                addr.disabled = False
                self.query_one(DataView).disabled = False
                self.query_one(AttributesView).disabled = False
            except Exception:
                pass

        except Exception as exc:
            self._log_message(f"Connection failed: {str(exc)}")
            self.ua_client = None

    async def _handle_disconnect(self):
        """Handle the disconnect button press."""
        if not self.ua_client:
            self._log_message("No active connection")
            return

        try:
            self._log_message("Disconnecting...")
            # Unsubscribe all monitored items if any
            for _, rec in list(self._subscriptions.items()):
                try:
                    await rec["sub"].unsubscribe(rec["handle"])
                except Exception:
                    pass
            self._subscriptions.clear()

            # Clear data view rows
            try:
                dv = self.query_one(DataView)
                dv.clear_values()
            except Exception:
                pass
            await self.ua_client.disconnect()
            self._log_message("Disconnected")

            # Update button states
            self.query_one("#connect_button", Button).disabled = False
            self.query_one("#disconnect_button", Button).disabled = True
            self.query_one("#connection_select", Select).disabled = False

            # Reset the AddressSpace tree to just the root
            addr = self.query_one(AddressSpace)
            for child in list(addr.root.children):
                child.remove()
            addr.root.data = {"node_id": "i=84", "loaded": False}
            addr.root.allow_expand = True

            # Disable interactive views when disconnected
            try:
                addr.disabled = True
                self.query_one(DataView).disabled = True
                self.query_one(AttributesView).disabled = True
            except Exception:
                pass

            self.ua_client = None

        except Exception as exc:
            self._log_message(f"Disconnect failed: {str(exc)}")

    def _handle_view_settings(self) -> None:
        """Display the settings for the selected connection in a modal screen."""
        connection_select = self.query_one(ConnectionSelect)
        selected_connection = connection_select.value

        if selected_connection == Select.BLANK:
            self._log_message("No connection selected")
            return

        config = self.settings[selected_connection]
        self.push_screen(SettingsScreen(config, selected_connection))

    def _apply_data_view_update(self, payload: dict) -> None:
        """Apply a single update to the DataView from a subscription payload."""
        try:
            dv = self.query_one(DataView)
            dv.upsert_value(
                node_id=payload["node_id"],
                display_name=payload["display_name"],
                value=payload["value"],
                data_type=payload["data_type"],
                source_ts=payload["source_timestamp"],
            )
        except Exception as e:
            log.error(f"Failed to apply data view update: {payload!r}")
            log.error(f"Error: {e}")
            # Avoid crashing the UI on malformed payloads or transient lookup errors
            pass

    def _on_subscription_change(self, payload: dict) -> None:
        """Handle data change notifications."""
        self._apply_data_view_update(payload)

    async def subscribe_node(self, node_id: str) -> None:
        """Subscribe to a node's value changes and stream updates to the DataView.

        Avoids duplicate subscriptions for the same node id.
        """
        if not self.ua_client or not getattr(self.ua_client, "connected", False):
            self._log_message("Not connected; cannot subscribe")
            return
        if node_id in self._subscriptions:
            self._log_message(f"Already subscribed: {node_id}")
            return

        # Ensure the node is a Variable before subscribing; otherwise asyncua will error
        try:
            node_class_name = await self.ua_client.get_node_class_name(node_id)
        except Exception:
            node_class_name = None
        if node_class_name and node_class_name.lower() != "variable":
            self._log_message(
                f"Cannot subscribe to node class '{node_class_name}' for {node_id}. Only Variable nodes are supported."
            )
            return

        try:
            sub, handle = await self.ua_client.subscribe_to_node(node_id, self._on_subscription_change)
            self._subscriptions[node_id] = {"sub": sub, "handle": handle}
            self._log_message(f"Subscribed to {node_id}")
        except Exception as exc:
            self._log_message(f"Subscribe failed for {node_id}: {exc}")

    async def action_unsubscribe_selected(self) -> None:
        """Unsubscribe the currently selected node in the Address Space tree (key: 'u')."""
        try:
            addr = self.query_one(AddressSpace)
            node = getattr(addr, "cursor_node", None)
            if not node or not node.data or "node_id" not in node.data:
                self._log_message("No node selected")
                return
            await self.unsubscribe_node(node.data["node_id"])
        except Exception as exc:
            self._log_message(f"Unsubscribe failed: {exc}")

    async def unsubscribe_node(self, node_id: str) -> None:
        """Unsubscribe a node if currently subscribed and remove it from the DataView."""
        rec = self._subscriptions.pop(node_id, None)
        if not rec:
            self._log_message(f"Not subscribed: {node_id}")
            return
        try:
            await rec["sub"].unsubscribe(rec["handle"])
        except Exception:
            pass
        try:
            dv = self.query_one(DataView)
            dv.remove_node(node_id)
        except Exception:
            pass
        self._log_message(f"Unsubscribed from {node_id}")

    async def action_subscribe_selected(self) -> None:
        """Subscribe to the currently selected node in the Address Space tree."""
        try:
            addr = self.query_one(AddressSpace)
            node = getattr(addr, "cursor_node", None)
            if not node or not node.data or "node_id" not in node.data:
                self._log_message("No node selected")
                return
            node_id = node.data["node_id"]
            await self.subscribe_node(node_id)
        except Exception as exc:
            self._log_message(f"Subscribe failed: {exc}")

    async def action_quit(self) -> None:
        """Quit the app, performing a clean disconnect first if connected."""
        if self.ua_client:
            try:
                await self._handle_disconnect()
            except Exception as exc:
                self._log_message(f"Cleanup failed: {exc}")
                # Even if disconnect fails, proceed to quit to avoid trapping the user
        self.exit()


if __name__ == "__main__":
    app = uaViewer()
    app.run()
