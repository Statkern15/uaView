from datetime import datetime
from textual.widgets import DataTable
from textual import log


class DataView(DataTable):
    """Displays live values of subscribed nodes."""

    def __init__(self, **kwargs):
        super().__init__(id="data_view", **kwargs)
        self.add_columns(
            ("NodeId", "NodeId"),
            ("DisplayName", "DisplayName"),
            ("Value", "Value"),
            ("DataType", "DataType"),
            ("SourceTimestamp", "SourceTimestamp"),
        )
        # Map node_id -> row_key for quick updates
        self._row_by_node: dict[str, DataTable.RowKey] = {}

    def clear_values(self) -> None:
        """Clear table and row index."""
        try:
            self.clear(columns=False)
        except TypeError:
            self.clear()
        self._row_by_node.clear()

    def upsert_value(
        self,
        node_id: str,
        display_name: str,
        value,
        data_type: str,
        source_ts,
    ) -> None:
        """Insert or update a row for the given node_id."""
        if isinstance(source_ts, datetime):
            ts_str = source_ts.isoformat()
        elif source_ts:
            ts_str = str(source_ts)

        val_str = str(value)

        if node_id in self._row_by_node:
            row_key = self._row_by_node[node_id]
            try:
                self.update_cell(row_key, "Value", val_str)
                self.update_cell(row_key, "SourceTimestamp", ts_str)
            except Exception as exc:
                log.error(f"Error updating existing row {row_key} for {node_id}: {exc}")
        else:
            row_key = self.add_row(node_id, display_name, val_str, data_type, ts_str, key=node_id)
            self._row_by_node[node_id] = row_key

    def remove_node(self, node_id: str) -> None:
        """Remove the row for a node id from the table (if present)."""
        row_key = self._row_by_node.pop(node_id, None)
        if row_key is not None:
            try:
                self.remove_row(row_key)
            except Exception:
                # Fallback: update value cell to indicate unsubscribed
                try:
                    self.update_cell(row_key, 2, "<unsubscribed>")
                except Exception:
                    pass
