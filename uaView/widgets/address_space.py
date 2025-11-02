from datetime import datetime

from textual.events import MouseDown
from textual.widgets import Log, Tree
from widgets.attributes_view import AttributesView


class AddressSpace(Tree):
    CSS_PATH = "style.tcss"
    # Press "s" to subscribe to the currently selected node
    BINDINGS = [("s", "subscribe_selected", "Subscribe node")]

    def __init__(self, **kwargs):
        """Tree widget showing the OPC UA address space with lazy loading."""
        super().__init__("Address Space", id="address_space", **kwargs)
        self._client = None  # Set by the app after connecting
        self._selection_via_mouse = False  # track if the next selection was initiated by mouse
        # Start at RootFolder (i=84). We only set up the root; children load later.
        self.root.data = {"node_id": "i=84", "loaded": False}
        # Indicate the node can be expanded before children are loaded.
        self.root.allow_expand = True

    def set_client(self, client) -> None:
        """Attach an active UA client to browse from."""
        self._client = client

    async def action_subscribe_selected(self) -> None:
        """Subscribe to the currently selected node (triggered by 's')."""
        node = getattr(self, "cursor_node", None)
        if not node:
            return
        data = node.data or {}
        node_id = data.get("node_id")
        if not node_id:
            return

        # Delegate to the App's subscribe method (handles duplicates and logging)
        try:
            await self.app.subscribe_node(node_id)
        except Exception:
            log = self.app.query_one("#log_view", Log)
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write_line(f"{ts} Subscribe requested for {node_id} (no handler found)")

    async def load_root(self) -> None:
        """Load only the direct children of the RootFolder (i=84)."""
        if not self._client:
            return
        # Clear any previous children (e.g., after reconnect)
        for child in list(self.root.children):
            child.remove()

        await self._load_children_for_node(self.root)

    async def _load_children_for_node(self, tree_node) -> None:
        """Load children for the given tree node if not already loaded."""
        if not self._client:
            return

        data = tree_node.data or {}
        if data.get("loaded"):
            return  # Already loaded

        node_id = data.get("node_id", "i=84")
        children = await self._client.browse_children(node_id)

        if not children:
            # No children: stop showing expand affordance
            tree_node.allow_expand = False
            data["loaded"] = True
            tree_node.data = data
            return

        # Add children with lazy placeholders (allow_expand=True)
        for item in children:
            child_node = tree_node.add(item["label"])
            child_node.data = {"node_id": item["node_id"], "loaded": False}
            child_node.allow_expand = True

        data["loaded"] = True
        tree_node.data = data

    async def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        """When a node is expanded, log the browse action and load children on demand.

        Logs: "Browse on node 'node_id'" to the application's LogView (if present).
        Then performs lazy loading of the expanded node's direct children.
        """
        # Attempt to log the browse action with the node_id stored in node.data
        try:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = event.node.data or {}
            node_id = data.get("node_id")
            if node_id:
                log = self.app.query_one("#log_view", Log)
                message = f"{ts} Browse on node '{node_id}'"
                log.write_line(message)
        except Exception:
            # If logging isn't available yet, proceed without failing the UI
            pass

        # Lazy-load this node's children when expanded
        await self._load_children_for_node(event.node)

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """When a node is selected, fetch and display its attributes."""
        if not self._client:
            return
        data = event.node.data or {}
        node_id = data.get("node_id")
        if not node_id:
            return

        try:
            rows = await self._client.get_node_attributes(node_id)
        except Exception as exc:
            # Log the error if possible, then bail
            try:
                log = self.app.query_one("#log_view", Log)
                msg = f"[red]Failed to read attributes for {node_id}: {exc}[/red]"
                if hasattr(log, "write_line"):
                    log.write_line(msg)
                else:
                    log.write(msg)
            except Exception:
                pass
            return

        # Update the attributes view
        try:
            attr_view = self.app.query_one("#attributes_view", AttributesView)
            attr_view.set_rows(rows)
        except Exception:
            pass

        # Also subscribe this node for live value updates in DataView,
        # but skip if selection was triggered via mouse click (keyboard only)
        via_mouse = self._selection_via_mouse
        self._selection_via_mouse = False
        if not via_mouse:
            try:
                if hasattr(self.app, "subscribe_node"):
                    await self.app.subscribe_node(node_id)
            except Exception:
                pass

    def on_mouse_down(self, event: MouseDown) -> None:
        """Mark that the next selection (if any) originates from a mouse click.

        This allows us to avoid auto-subscribing on mouse selection to prevent
        unintended subscriptions. Keyboard-driven selection will still subscribe.
        """
        self._selection_via_mouse = True
