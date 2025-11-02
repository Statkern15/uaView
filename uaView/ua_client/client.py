import asyncio
from datetime import datetime
from textual import log
from asyncua import Client, ua


class SubHandler:
    """Handler for OPC-UA subscription data change notifications."""

    def __init__(self, node_meta: dict, callback):
        """
        node_meta: {"node_id": str, "display_name": str, "data_type": str}
        callback: async or sync callable expecting payload dict
        """
        self.node_meta = node_meta
        self.callback = callback

    def datachange_notification(self, node, val, data):
        """Called when a subscribed node's value changes."""
        # Try to extract SourceTimestamp; fallback to now
        src_ts = None
        log.info("datachange_notification %r %s", node, val)
        try:
            v = data.monitored_item.Value
            src_ts = getattr(v, "SourceTimestamp", None) or getattr(v, "ServerTimestamp", None)
        except Exception:
            pass
        if src_ts is None:
            src_ts = datetime.now()

        payload = {
            "node_id": self.node_meta["node_id"],
            "display_name": self.node_meta["display_name"],
            "data_type": self.node_meta["data_type"],
            "value": val,
            "source_timestamp": src_ts,
        }

        # Support async and sync callbacks safely
        try:
            result = self.callback(payload)
            if asyncio.iscoroutine(result):
                asyncio.create_task(result)
        except Exception:
            # Swallow callback exceptions to avoid breaking the subscription loop
            pass


class UAViewerClient:
    """Client for connecting to and interacting with OPC-UA servers."""

    def __init__(self, config: dict):
        """Initialize the client with connection configuration.

        Args:
            config: Dictionary containing connection parameters like
            endpoint_url, security_policy, security_mode, etc.
        """
        self.config = config
        self.client = Client(self.config["endpoint_url"])

        # Set security if specified
        security_policy = self.config.get("security_policy", "None")
        security_mode = self.config.get("security_mode", "None")
        self.client.set_security_string(f"{security_policy},{security_mode}")
        self.connected = False

    async def connect(self):
        """Connect to the OPC-UA server and authenticate if credentials provided."""
        await self.client.connect()

        # Authenticate with username/password if provided
        username = self.config.get("user_name")
        password = self.config.get("password")
        if username and password:
            await self.client.set_user(username, password)

        self.connected = True

    async def disconnect(self):
        """Disconnect from the OPC-UA server."""
        if self.connected:
            await self.client.disconnect()
            self.connected = False

    async def read_node_value(self, node_id):
        """Read the value of a specific node."""
        node = self.client.get_node(node_id)
        return await node.read_value()

    async def browse_nodes(self, node_id="i=84"):
        """Browse the address space starting from a given node.

        Args:
            node_id: Starting node ID (default is Objects folder i=84)

        Returns:
            List of child nodes
        """
        node = self.client.get_node(node_id)
        return await node.get_children()

    async def browse_children(self, node_id: str = "i=84"):
        """Return child nodes of the given node.

        Each item includes a human-friendly label and the child node's NodeId string.

        Args:
            node_id: The parent node id to browse (defaults to RootFolder i=84).

        Returns:
            A list of dicts: [{"label": str, "node_id": str}, ...]
        """
        node = self.client.get_node(node_id)
        children = await node.get_children()
        items = []
        for child in children:
            try:
                display = await child.read_display_name()
                label = getattr(display, "Text", str(display))
            except Exception:
                label = str(child)
            items.append(
                {
                    "label": label,
                    "node_id": child.nodeid.to_string(),
                }
            )
        return items

    async def get_node_attributes(self, node_id: str):
        """Read key attributes for a node and return rows suitable for AttributesView.

        The attributes returned depend on the NodeClass:
        - Object: nodeId, NodeClass, BrowseName, DisplayName
        - Variable: nodeId, NodeClass, BrowseName, DisplayName, DataType, Value, AccessLevel, Description (if available)
        - Method: nodeId, NodeClass, BrowseName, DisplayName, Executable, UserExecutable

        Returns:
            list[tuple[str, str]]: [("Attribute", "Value"), ...]
        """
        node = self.client.get_node(node_id)

        # Helpers to read attributes safely
        async def _safe(read_coro, default=None):
            try:
                return await read_coro
            except Exception:
                return default

        # NodeClass
        node_class = await _safe(node.read_node_class(), None)
        node_class_name = None
        if isinstance(node_class, ua.NodeClass):
            node_class_name = node_class.name
        elif node_class is not None:
            node_class_name = str(node_class)

        # Common attributes
        browse_name = await _safe(node.read_browse_name(), None)
        display_name = await _safe(node.read_display_name(), None)
        browse_name_str = getattr(browse_name, "Name", str(browse_name)) if browse_name is not None else ""
        display_name_str = getattr(display_name, "Text", str(display_name)) if display_name is not None else ""

        rows = [("Attribute", "Value")]
        rows.append(("NodeId", node_id))
        rows.append(("NodeClass", node_class_name or ""))
        rows.append(("BrowseName", browse_name_str))
        rows.append(("DisplayName", display_name_str))

        # Variable-specific
        if node_class == ua.NodeClass.Variable or (
            isinstance(node_class, int) and node_class == int(ua.NodeClass.Variable)
        ):
            data_type = await _safe(node.read_data_type(), None)
            data_type_str = str(getattr(data_type, "to_string", lambda: data_type)()) if data_type is not None else ""
            value = await _safe(node.read_value(), "")
            # AccessLevel as numeric mask (or enum); use AttributeIds for consistent return type
            access_level_val = await _safe(node.read_attribute(ua.AttributeIds.AccessLevel), None)
            access_level_str = (
                str(getattr(access_level_val, "Value", None).Value)
                if access_level_val is not None and getattr(access_level_val, "Value", None) is not None
                else ""
            )
            description = await _safe(node.read_description(), None)
            desc_str = getattr(description, "Text", str(description)) if description is not None else ""

            rows.append(("DataType", data_type_str))
            rows.append(("Value", str(value)))
            rows.append(("AccessLevel", access_level_str))
            if desc_str:
                rows.append(("Description", desc_str))

        # Method-specific
        if node_class == ua.NodeClass.Method or (
            isinstance(node_class, int) and node_class == int(ua.NodeClass.Method)
        ):
            executable = await _safe(node.read_attribute(ua.AttributeIds.Executable), None)
            user_executable = await _safe(node.read_attribute(ua.AttributeIds.UserExecutable), None)
            rows.append(("Executable", str(executable.Value.Value) if executable is not None else ""))
            rows.append(("UserExecutable", str(user_executable.Value.Value) if user_executable is not None else ""))

        return rows

    async def get_node_class(self, node_id: str):
        """Return the NodeClass enum for the given node id (or None on error)."""
        try:
            node = self.client.get_node(node_id)
            return await node.read_node_class()
        except Exception:
            return None

    async def get_node_class_name(self, node_id: str) -> str | None:
        """Return the NodeClass name (e.g., 'Variable', 'Object', 'Method') or None."""
        nc = await self.get_node_class(node_id)
        if isinstance(nc, ua.NodeClass):
            return nc.name
        return str(nc) if nc is not None else None

    async def subscribe_to_node(self, node_id, callback):
        """Subscribe to data changes on a specific node.

        The callback will receive a dict:
        {
            "node_id": str,
            "display_name": str,
            "data_type": str,
            "value": Any,
            "source_timestamp": datetime,
        }

        Returns:
            (subscription, handle)
        """
        node = self.client.get_node(node_id)

        # Pre-read display name and data type for metadata
        try:
            display = await node.read_display_name()
            display_name = getattr(display, "Text", str(display))
        except Exception:
            display_name = node_id

        try:
            data_type = await node.read_data_type()
            data_type_str = data_type.to_string() if hasattr(data_type, "to_string") else str(data_type)
        except Exception:
            data_type_str = ""

        # Build handler with metadata for subsequent notifications
        handler = SubHandler(
            {"node_id": node_id, "display_name": display_name, "data_type": data_type_str},
            callback,
        )

        # Emit an initial value to the callback so the UI can show a row
        # immediately, even before the first data change notification arrives.
        try:
            dv = await node.read_data_value()
            v_container = getattr(dv, "Value", None)
            initial_value = getattr(v_container, "Value", None) if v_container is not None else None
            initial_ts = getattr(dv, "SourceTimestamp", None) or getattr(dv, "ServerTimestamp", None) or datetime.now()
            initial_payload = {
                "node_id": node_id,
                "display_name": display_name,
                "data_type": data_type_str,
                "value": initial_value,
                "source_timestamp": initial_ts,
            }
            try:
                result = callback(initial_payload)
                if asyncio.iscoroutine(result):
                    asyncio.create_task(result)
            except Exception:
                # Ignore UI callback errors here to avoid blocking subscription creation
                pass
        except Exception:
            # If initial read fails, continue with the subscription
            pass
        sub = await self.client.create_subscription(500, handler)
        handle = await sub.subscribe_data_change(node)
        return sub, handle
