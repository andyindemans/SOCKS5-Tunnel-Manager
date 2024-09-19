import os
import subprocess
import socket


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
