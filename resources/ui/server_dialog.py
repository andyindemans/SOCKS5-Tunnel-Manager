from PyQt5.QtWidgets import (
    QPushButton, QVBoxLayout, QLineEdit, QDialog
)
from dotenv import set_key
from resources.core.ssh_management import load_servers


class AddServerDialog(QDialog):
    def __init__(self, parent=None):
        super(AddServerDialog, self).__init__(parent)
        self.setWindowTitle("Add New Server")
        self.layout = QVBoxLayout()
        self.resize(300, 200)

        self.host_input = QLineEdit(self)
        self.host_input.setPlaceholderText("Host")
        self.port_input = QLineEdit(self)
        self.port_input.setPlaceholderText("Port")
        self.display_name_input = QLineEdit(self)
        self.display_name_input.setPlaceholderText("Display Name (Optional)")

        self.add_button = QPushButton("Add Server")
        self.add_button.clicked.connect(self.add_server)

        self.layout.addWidget(self.host_input)
        self.layout.addWidget(self.port_input)
        self.layout.addWidget(self.display_name_input)
        self.layout.addWidget(self.add_button)
        self.setLayout(self.layout)

    def add_server(self):
        servers = load_servers()
        host = self.host_input.text()
        port = self.port_input.text()
        display_name = self.display_name_input.text()
        server_index = len(servers) + 1

        if host and port:
            set_key(".env", f'SERVER_{server_index}_HOST', host)
            set_key(".env", f'SERVER_{server_index}_PORT', port)

            if display_name:
                set_key(".env", f'SERVER_{server_index}_DISPLAY_NAME', display_name)

            self.accept()
