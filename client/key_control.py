import threading
from PySide6 import QtWidgets
import logging
import json
import sys

logging.basicConfig(level=logging.DEBUG)

class KeyControlDialog(QtWidgets.QDialog):
    def __init__(self, sock):
        super().__init__()

        self.sock = sock
        self.setWindowTitle('Keyboard Control')
        self.resize(380, 360)

        self.hook_button = QtWidgets.QPushButton('Hook', self)
        self.hook_button.move(40, 20)
        self.hook_button.setFixedSize(80, 30)

        self.unhook_button = QtWidgets.QPushButton('Unhook', self)
        self.unhook_button.move(150, 20)
        self.unhook_button.setFixedSize(80, 30)

        self.clear_button = QtWidgets.QPushButton('Clear', self)
        self.clear_button.move(260, 20)
        self.clear_button.setFixedSize(80, 30)

        self.lock_button = QtWidgets.QPushButton('Lock Keyboard', self)
        self.lock_button.move(80, 60)
        self.lock_button.setFixedSize(100, 40)

        self.unlock_button = QtWidgets.QPushButton('Unlock Keyboard', self)
        self.unlock_button.move(210, 60)
        self.unlock_button.setFixedSize(100, 40)

        self.result_box = QtWidgets.QTextEdit(self)
        self.result_box.move(20, 110)
        self.result_box.setFixedSize(340, 240)
        self.result_box.setReadOnly(True)

        self.hook_button.clicked.connect(self.click_hook_button)
        self.unhook_button.clicked.connect(self.click_unhook_button)
        self.clear_button.clicked.connect(self.click_clear_button)
        self.lock_button.clicked.connect(self.click_lock_button)
        self.unlock_button.clicked.connect(self.click_unlock_button)

    def click_hook_button(self):
        message_to_send = {'type': 'key_control', 'request': 'hook_key', 'data': ''}
        self.sock.sendall(json.dumps(message_to_send).encode(('utf-8')))

        list_key_thread = threading.Thread(target=self.receive_data)
        list_key_thread.start()

    def click_unhook_button(self):
        message_to_send = {'type': 'key_control',
                           'request': 'unhook_key', 'data': ''}
        self.sock.sendall(json.dumps(message_to_send).encode(('utf-8')))

    def receive_data(self):
        key_str = ''
        while True:
            message_recvd = self.sock.recv(1024)
            key_str += str.format(message_recvd.decode('utf-8'))
            if not message_recvd:
                break
        print(key_str)
        self.result_box.setText(str(key_str))

    def click_clear_button(self):
        self.result_box.clear()
    
    def click_lock_button(self):
        message_to_send = {'type': 'key_control',
                           'request': 'lock_key', 'data': ''}
        self.sock.sendall(json.dumps(message_to_send).encode(('utf-8')))

    def click_unlock_button(self):
        message_to_send = {'type': 'key_control',
                           'request': 'unlock_key', 'data': ''}
        self.sock.sendall(json.dumps(message_to_send).encode(('utf8')))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = KeyControlDialog(0)
    window.show()
    sys.exit(app.exec())
