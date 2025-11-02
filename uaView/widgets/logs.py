from datetime import datetime

from textual.widgets import Log


class LogView(Log):
    CSS_PATH = "style.tcss"

    def __init__(self, **kwargs):
        super().__init__(id="log_view", highlight=True, **kwargs)

    def on_mount(self) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        init_msg = f"{ts} Log Initialized."
        self.write_line(init_msg)
