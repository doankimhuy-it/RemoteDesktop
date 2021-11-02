import sys
from PySide6 import QtCore, QtWidgets, QtGui
import logging

logging.basicConfig(level=logging.DEBUG)

STATUS_DISCONNECTED = 0
STATUS_CONNECTED = 1
STATUS_TIMEOUT = -1
STATUS_CONNECTING = 2

class ClientWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.update_gui_timer = QtCore.QTimer()

        # create windows title and its size
        self.setWindowTitle('Controler')
        self.setFixedSize(600, 70)

        # IP box
        self.ip_textbox = QtWidgets.QLineEdit("127.0.0.1", self)
        self.ip_textbox.move(20, 20)
        self.ip_textbox.setFixedWidth(200)

        # port box
        self.port_textbox = QtWidgets.QLineEdit("65432", self)
        self.port_validator = QtGui.QIntValidator(0, 65535, self)
        self.port_textbox.setValidator(self.port_validator)
        self.port_textbox.move(240, 20)
        self.port_textbox.setFixedWidth(70)

        # connect button
        self.connect_button = QtWidgets.QPushButton("Connect", self)
        self.connect_button.move(340, 20)

        # connection status
        self.connection_status = QtWidgets.QLabel(
            "DISCONNECTED", self, alignment=QtCore.Qt.AlignCenter)
        self.connection_status.move(470, 20)
        self.connection_status.setStyleSheet(
            "QLabel { border: 1.5px solid black;font-weight: bold; color : red; }")

    def show_error(self, message, title='Error', width=None, info_icon=None):
        message_box = QtWidgets.QMessageBox(self)
        message_box.setText(message)
        message_box.setWindowTitle(title)
        if width:
            message_box.setFixedWidth(width)
        if info_icon:
            message_box.setIcon(QtWidgets.QMessageBox.Information)
        message_box.exec()

    def change_gui_status(self, connection_status):
        if connection_status == STATUS_CONNECTING:
            connecting_status = ['Connecting', 'Connecting.',
                                'Connecting..', 'Connecting...']
            text = self.connect_button.text()
            index = 3
            if (text != 'Connect'):
                index = connecting_status.index(text)
            index = (index + 1) % 4
            self.connect_button.setText(connecting_status[index])

        if connection_status == STATUS_CONNECTED:
            self.connect_button.setText('Disconnect')
            self.connection_status.setText('CONNECTED')
            self.connection_status.setStyleSheet(
                "border: 1.5px solid black; font-weight: bold; color: green;")

        if connection_status == STATUS_DISCONNECTED:
            self.connect_button.setText('Connect')
            self.connection_status.setText('DISCONNECTED')
            self.connection_status.setStyleSheet(
                "border: 1.5px solid black; font-weight: bold; color: red;")

        if connection_status == STATUS_TIMEOUT:
            self.connect_button.setText('Connect')
            self.connection_status.setText('TIMED OUT')
            self.connection_status.setStyleSheet(
                "border: 1.5px solid black; font-weight: bold; color: brown;")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = ClientWindow()
    window.show()

    sys.exit(app.exec())
