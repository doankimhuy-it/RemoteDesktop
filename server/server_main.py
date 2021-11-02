import server_gui
from server_connection import ServerConnection
import sys
import threading
from PySide6 import QtWidgets

host = '0.0.0.0'    # all network interface
port = 65432

class Server:
    def __init__(self):
        self.server_connection = ServerConnection(host, port)
        self.app = QtWidgets.QApplication([])
        self.app.setQuitOnLastWindowClosed(False)
        self.window = server_gui.ServerWindow()

    def click_listen_button(self):
        # global self.window
        if self.server_connection.connection_status == 0:
            self.window.listen_button.setText(
                'Waiting for client\nClick to stop listening')
            connection_thread = threading.Thread(
                target=self.server_connection.start_listen)
            connection_thread.start()
            self.window.update_gui_timer.start(500)
            print(self.server_connection.connection_status)
        else:
            self.server_connection.stop_listen()
            self.window.listen_button.setText('Start Listening')
            self.window.update_gui_timer.stop()

    def update_gui(self):
        if self.server_connection.connection_status > 1:
            self.window.listen_button.setText('Connected to client\n' +
                                              'Click to stop listening')
        elif self.server_connection.connection_status == 1:
            self.window.listen_button.setText(
                'Waiting for client\nClick to stop listening')

    def on_quit(self):
        if self.server_connection.connection_status:
            self.server_connection.stop_listen()
        self.app.exit()

    def connect_gui_features(self):
        self.app.lastWindowClosed.connect(self.on_quit)
        self.window.listen_button.clicked.connect(self.click_listen_button)
        self.window.update_gui_timer.timeout.connect(self.update_gui)

    def run(self):
        self.window.show()
        self.connect_gui_features()
        sys.exit(self.app.exec())


if __name__ == '__main__':
    server = Server()

    server.run()
