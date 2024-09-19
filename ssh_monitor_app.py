#!/usr/bin/env python3

import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFrame, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPalette
from dotenv import load_dotenv

from resources.core.ssh_management import create_ssh_tunnel, is_port_open, load_servers
from resources.ui.status_indicator import StatusIndicator
from resources.ui.server_dialog import AddServerDialog

load_dotenv()


class SshMonitorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.add_server_button = None
        self.layout = None
        self.servers = load_servers()
        self.status_widgets = {}  # Store widgets for each server
        self.init_ui()
        self.init_connections()

    def init_ui(self):
        self.setWindowTitle('SSH Tunnel Manager')
        self.setStyleSheet("background-color: #282828; color: white;")
        self.resize(800, 600)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.add_server_button = QPushButton("Manage Servers")
        self.add_server_button.clicked.connect(self.show_add_server_dialog)
        self.layout.addWidget(self.add_server_button)
        for server in self.servers:
            server_widget, status_indicator, status_label = self.create_server_widget(server)
            self.layout.addWidget(server_widget)
            self.status_widgets[server["host"]] = {"indicator": status_indicator, "label": status_label}
        self.setLayout(self.layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_statuses)
        self.timer.start(5000)

    def create_server_widget(self, server):
        server_frame = QFrame()
        server_frame.setFrameShape(QFrame.StyledPanel)
        server_frame.setStyleSheet("background-color: #3c3c3c; border-radius: 10px;")
        server_layout = QHBoxLayout(server_frame)
        server_layout.setContentsMargins(10, 10, 10, 10)
        server_label = QLabel(f"Server: {server['display_name']}")
        server_label.setStyleSheet("color: white;")
        server_layout.addWidget(server_label)

        status_indicator = StatusIndicator()
        server_layout.addWidget(status_indicator)

        status_label = QLabel("Checking...")
        status_label.setStyleSheet("color: white;")
        server_layout.addWidget(status_label)

        button = QPushButton("Restart Tunnel")
        button.setStyleSheet("""
                    QPushButton {
                        background-color: #282828; 
                        color: white; 
                        border: 2px solid #3c3c50; 
                        border-radius: 5px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #505050;
                        border: 2px solid #707070;
                    }
                    QPushButton:pressed {
                        background-color: #3c3c50;
                        border: 2px solid #505050;
                    }
                """)
        button.clicked.connect(lambda _, s=server: self.restart_tunnel(s))
        server_layout.addWidget(button)

        return server_frame, status_indicator, status_label

    def init_connections(self):
        for server in self.servers:
            subprocess.call(['pkill', '-f', f'ssh.*{server["host"]}'])
            create_ssh_tunnel(server)

    def update_statuses(self):
        for server in self.servers:
            status_label = self.status_widgets[server["host"]]["label"]
            status_indicator = self.status_widgets[server["host"]]["indicator"]
            if is_port_open(server["port"]):
                status_label.setText("Open")
                status_indicator.set_status("open")
            else:
                status_label.setText("Closed")
                status_indicator.set_status("closed")

    def restart_tunnel(self, server):
        subprocess.call(['pkill', '-f', f'ssh.*{server["host"]}'])
        status_label = self.status_widgets[server["host"]]["label"]
        status_indicator = self.status_widgets[server["host"]]["indicator"]
        status_label.setText("Checking...")
        status_indicator.set_status("waiting")
        create_ssh_tunnel(server)

    def closeEvent(self, event):
        for server in self.servers:
            subprocess.call(['pkill', '-f', f'ssh.*{server["host"]}'])
        event.accept()

    def fetch_servers(self):
        load_dotenv()
        self.servers = load_servers()
        self.update_server_ui()

    def update_server_ui(self):
        # Clear the grid before adding new servers
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        self.add_server_button = QPushButton("Manage Servers")
        self.add_server_button.clicked.connect(self.show_add_server_dialog)
        self.layout.addWidget(self.add_server_button)
        for server in self.servers:
            server_widget, status_indicator, status_label = self.create_server_widget(server)
            self.layout.addWidget(server_widget)
            self.status_widgets[server["host"]] = {"indicator": status_indicator, "label": status_label}
            create_ssh_tunnel(server)

    def show_add_server_dialog(self):
        dialog = AddServerDialog(self)
        if dialog.exec_():
            self.fetch_servers()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SshMonitorApp()

    # Set up dark theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#282828"))
    palette.setColor(QPalette.Button, QColor("#3c3c3c"))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor("#3c3c3c"))
    palette.setColor(QPalette.Text, Qt.white)
    app.setPalette(palette)

    window.show()
    sys.exit(app.exec_())
