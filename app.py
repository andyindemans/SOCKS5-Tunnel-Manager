import sys
import subprocess
import socket
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFrame, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPalette
from dotenv import load_dotenv
import os

load_dotenv()


def load_servers():
    servers = []
    i = 1
    while True:
        host = os.getenv(f'SERVER_{i}_HOST')
        port = os.getenv(f'SERVER_{i}_PORT')
        display_name = os.getenv(f'SERVER_{i}_DISPLAY_NAME', "").strip()
        if not host or not port:
            break
        if not display_name:
            display_name = host
        servers.append({"host": host, "port": int(port), "display_name": display_name})
        i += 1
    return servers


def create_ssh_tunnel(server):
    command = [
        "ssh",
        "-D", str(server["port"]),
        "-o", "ServerAliveInterval=60",
        "-o", "ServerAliveCountMax=5",
        server["host"]
    ]
    subprocess.Popen(command)


def is_port_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0


class StatusIndicator(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedSize(15, 15)
        self.setStyleSheet("border-radius: 7px; background-color: yellow;")

    def set_status(self, status):
        color = {"open": "green", "closed": "red", "waiting": "yellow"}.get(status, "yellow")
        self.setStyleSheet(f"border-radius: 7px; background-color: {color};")


class TunnelApp(QWidget):
    def __init__(self):
        super().__init__()
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


def main():
    app = QApplication(sys.argv)
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(40, 40, 40))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(60, 60, 60))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(dark_palette)
    ex = TunnelApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()