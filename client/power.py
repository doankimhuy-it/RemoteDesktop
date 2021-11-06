import json
import sys
from PySide6 import QtWidgets

class PowerDialog(QtWidgets.QDialog):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock

        self.setWindowTitle('Shutdown/Logoff')
        self.setFixedSize(200, 50)

        self.shutdown_button = QtWidgets.QPushButton('Shutdown', self)
        self.shutdown_button.move(10, 10)
        self.shutdown_button.setFixedSize(80, 30)
        self.shutdown_button.clicked.connect(self.click_shutdown_button)

        self.logoff_button = QtWidgets.QPushButton('Logoff', self)
        self.logoff_button.move(110, 10)
        self.logoff_button.setFixedSize(80, 30)
        self.logoff_button.clicked.connect(self.click_logoff_button)

    def click_shutdown_button(self):
        message_to_send = {'type': 'power', 'request': 'shutdown', 'data': ''}
        self.sock.sendall(json.dumps(message_to_send).encode('utf-8'))

    def click_logoff_button(self):
        message_to_send = {'request': 'logoff'}
        self.sock.sendall(json.dumps(message_to_send).encode('utf-8'))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = PowerDialog(0)
    window.show()
    sys.exit(app.exec())
