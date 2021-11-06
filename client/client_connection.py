import json
import socket

from control_diag import ControlDiag

STATUS_DISCONNECTED = 0
STATUS_CONNECTED = 1
STATUS_TIMEOUT = -1
STATUS_CONNECTING = 2

class ClientConnection:
    def __init__(self):
        self.connection_status = STATUS_DISCONNECTED
        self.host = '0.0.0.0'
        self.port = 0
        self.client_socket = None
        self.lost_connection = False
        self.control_dialog = None

    def start_connection(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
        except (ConnectionRefusedError, TimeoutError) as e:
            self.connection_status = STATUS_TIMEOUT
            return
        else:
            self.connection_status = STATUS_CONNECTED
            self.control_dialog = ControlDiag(self.client_socket)
            self.show_control_diag(is_visible=True)

    def send_message(self, message):
        message = json.dumps(message).encode('utf-8')
        try:
            self.client_socket.sendall(message)
        except:  # ConnectionAbortedError and ConnectionResetError
            self.connection_status = STATUS_DISCONNECTED
            self.lost_connection = True

    def stop_connection(self):
        end_message = {'type': 'connection',
                       'request': 'close_connection', 'data': ''}
        self.send_message(end_message)
        self.connection_status = STATUS_DISCONNECTED
        self.show_control_diag(is_visible=False)

    def show_control_diag(self, is_visible):
        if is_visible:
            self.control_dialog.show()
        else:
            self.control_dialog.hide()


if __name__ == '__main__':
    # the server's hostname or IP address
    HOST = '192.168.1.27'
    PORT = 65432        # the port used by the server (randomly generated)
    client_connect = ClientConnection()
    client_connect.start_connection(HOST, PORT)
