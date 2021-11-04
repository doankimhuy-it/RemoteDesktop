import json
from PySide6 import QtWidgets, QtCore
import sys

class GetMACAddressDialog(QtWidgets.QDialog):
    def __init__(self, sock):
        super().__init__()

        self.sock = sock
        self.setWindowTitle('MAC Address')
        self.setFixedSize(200, 100)

        self.mac_addr = QtWidgets.QLineEdit(self)
        self.mac_addr.move(10, 10)
        self.mac_addr.setFixedSize(180, 30)
        self.mac_addr.setReadOnly(True)
        self.mac_addr.setAlignment(QtCore.Qt.AlignCenter)

        self.get_button = QtWidgets.QPushButton('Get', self)
        self.get_button.move(60, 60)

        self.get_button.clicked.connect(self.click_get_button)

    def click_get_button(self):
        message_to_send = {'type': 'mac_address', 'request': 'get', 'data': ''}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        message_recvd = self.sock.recv(4096).decode('utf8')
        message_recvd = json.loads(message_recvd)
        self.mac_addr.setText(message_recvd['data'])


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = GetMACAddressDialog(0)
    window.show()
    sys.exit(app.exec())
