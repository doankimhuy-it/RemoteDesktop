from PySide6 import QtWidgets
from PySide6.QtCore import QThread, Signal, QMutex
import json
import sys
import socket

class KeyControlDialog(QtWidgets.QDialog):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock

        self.init_ui()
        self.link_buttons()

        tcpsock = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpsock.bind(('0.0.0.0', 0))
        self.port = tcpsock.getsockname()[1]

        self.get_thread = self.GettingThread(tcpsock)
        self.get_thread.key_pressed.connect(self.receive_data)

    def link_buttons(self):
        self.hook_button.clicked.connect(self.click_hook_button)
        self.unhook_button.clicked.connect(self.click_unhook_button)
        self.clear_button.clicked.connect(self.click_clear_button)
        self.lock_button.clicked.connect(self.click_lock_button)
        self.unlock_button.clicked.connect(self.click_unlock_button)

    def init_ui(self):
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

    def click_hook_button(self):
        message_to_send = {'type': 'key_control',
                           'request': 'hook_key', 'data': self.port}
        self.sock.sendall(json.dumps(message_to_send).encode(('utf-8')))

        # self.receive_data()
        self.get_thread.start()

    def click_unhook_button(self):
        message_to_send = {'type': 'key_control',
                           'request': 'unhook_key', 'data': ''}
        self.sock.sendall(json.dumps(message_to_send).encode(('utf-8')))

    def receive_data(self, key):
        self.result_box.setText(str(self.result_box.toPlainText()) + key)

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

    # overrided
    def closeEvent(self, event):
        message_to_send = {'type': 'key_control',
                           'request': 'stop', 'data': ''}
        self.sock.sendall(json.dumps(message_to_send).encode(('utf8')))
        if self.get_thread:
            self.get_thread.stop()
            self.get_thread.quit()
            self.get_thread.wait()

    class GettingThread(QThread):
        key_pressed = Signal(str)
        def __init__(self, tcpsock):
            self.tcpsock = tcpsock
            self.mutex = QMutex()
            super().__init__()

        def run(self):
            self.sock = self.setup_tunnel(self.tcpsock)
            self.keep_running = True
            keep_running = self.keep_running
            while (keep_running):
                self.mutex.lock()
                self.wait_key()
                keep_running = self.keep_running
                self.mutex.unlock()

        def stop(self):
            self.mutex.lock()
            self.keep_running = False
            self.mutex.unlock()

        def setup_tunnel(self, tcpsock):
            tcpsock.listen(100)
            tcpsock_connection, tcpsock_address = tcpsock.accept()
            tcpsock_connection.setblocking(False)
            return tcpsock_connection

        def wait_key(self):
            try:
                data_byte = self.sock.recv(1024)
            except:
                pass
            else:
                data_json = json.loads(data_byte)
                key = data_json['key']
                self.key_pressed.emit(key)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = KeyControlDialog(0)
    window.show()
    sys.exit(app.exec())
