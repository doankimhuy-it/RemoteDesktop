from client_base_gui import *
from client_connection import *

STATUS_DISCONNECTED = 0
STATUS_CONNECTED = 1
STATUS_TIMEOUT = -1
STATUS_CONNECTING = 2

class Client:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.client_connection = ClientConnection()
        self.window = ClientWindow()

    def click_connect_button(self):
        if (self.client_connection.connection_status == STATUS_DISCONNECTED
                or self.client_connection.connection_status == STATUS_TIMEOUT):
            host = self.window.ip_textbox.text()
            port = self.window.port_textbox.text()
            pos = 0
            if self.window.port_validator.validate(port, pos)[0] != self.window.port_validator.Acceptable:
                err_diag = self.window.show_error(
                    'Invalid Address', 'Invalid Port')
                err_diag.exec()
                return -1
            port = int(port)
            # try to connect to server for the first time, after disconnecting or timing out
            # turn status to connecting
            self.client_connection.connection_status = STATUS_CONNECTING
            self.window.change_gui_status(STATUS_CONNECTING)
            # try to connect to host
            self.client_connection.start_connection(host, port)

            # start timer - update GUI and send sample data to server (PING)
            self.window.update_gui_timer.start(500)

        elif (self.client_connection.connection_status == STATUS_CONNECTED):
            # user choose to close the connection
            self.client_connection.stop_connection()
            self.window.change_gui_status(STATUS_DISCONNECTED)
            # stop the timer
            self.window.update_gui_timer.stop()

    def update_gui(self):
        if (self.client_connection.connection_status == STATUS_CONNECTING):
            self.window.change_gui_status(STATUS_CONNECTING)
        elif (self.client_connection.connection_status == STATUS_TIMEOUT):
            self.window.change_gui_status(STATUS_TIMEOUT)
        elif (self.client_connection.connection_status == STATUS_DISCONNECTED):
            # if server loses connection to client, it will inform the client
            if (self.client_connection.lost_connection == True):
                self.client_connection.lost_connection = False
                self.window.show_error(
                    'Lost connection', 'Lost connection to server')
            self.window.change_gui_status(STATUS_DISCONNECTED)
        elif (self.client_connection.connection_status == STATUS_CONNECTED):
            self.window.change_gui_status(STATUS_CONNECTED)
            # send ping request after every 500ms to check server's signal
            self.client_connection.send_message(
                {'type': 'connection', 'request': 'ping', 'data': ''})

    def on_quit(self):
        if self.client_connection.connection_status == STATUS_CONNECTING \
                or self.client_connection.connection_status == STATUS_CONNECTED:
            self.client_connection.stop_connection()
        self.app.exit()

    def connect_gui_features(self):
        self.app.lastWindowClosed.connect(self.on_quit)
        self.window.update_gui_timer.timeout.connect(self.update_gui)
        self.window.connect_button.clicked.connect(self.click_connect_button)

    def start(self):
        self.window.show()
        self.connect_gui_features()
        self.app.exec()


if __name__ == '__main__':
    client = Client()

    client.start()
