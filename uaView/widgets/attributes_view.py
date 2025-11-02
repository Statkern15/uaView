from textual.widgets import DataTable


class AttributesView(DataTable):
    CSS_PATH = "style.tcss"

    def __init__(self, **kwargs):
        super().__init__(id="attributes_view", **kwargs)
        # Initialize with two columns; rows will be provided dynamically
        self.add_columns(("Attribute", "Attribute"), ("Value", "Value"))

    def set_rows(self, rows: list[tuple[str, str]]):
        """Replace table content with provided rows.

        Expects rows in the form [("Attribute", "Value"), ...]. If the first
        row looks like headers, it will be skipped to avoid duplicating headers.
        """
        if not rows:
            return
        start_index = 0
        if isinstance(rows[0], (list, tuple)) and len(rows[0]) == 2 and rows[0][0].lower() == "attribute":
            start_index = 1
        for pair in rows[start_index:]:
            # Be defensive with input
            if isinstance(pair, (list, tuple)) and len(pair) == 2:
                self.add_row(str(pair[0]), str(pair[1]))
