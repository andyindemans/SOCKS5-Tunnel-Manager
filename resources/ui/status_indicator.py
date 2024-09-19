from PyQt5.QtWidgets import QFrame


class StatusIndicator(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedSize(15, 15)
        self.setStyleSheet("border-radius: 7px; background-color: yellow;")

    def set_status(self, status):
        color = {"open": "green", "closed": "red", "waiting": "yellow"}.get(status, "yellow")
        self.setStyleSheet(f"border-radius: 7px; background-color: {color};")
