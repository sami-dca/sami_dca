import socket
import struct
from pathlib import Path

# FIXME: doesn't work because it's expecting a dictionary configuration,
#  but we're configuring programmatically
# FIXME: ^ NOT ANYMORE !!


config_file = Path(__file__).parent / "dynamic_log_new.config"
configuration_data = config_file.read_bytes()

server_port = int(input("Enter config listening port (integer): "))

config_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
config_socket.connect(("localhost", server_port))
config_socket.send(struct.pack(">L", len(configuration_data)))
config_socket.send(configuration_data)
config_socket.close()
