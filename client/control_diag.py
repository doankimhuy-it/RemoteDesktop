import json
import sys
from PySide6 import QtWidgets
import threading
from application import ApplicationDialog
from process import ProcessDialog
from get_mac_address import GetMACAddressDialog
from key_control import KeyControlDialog
from power import PowerDialog
from file_explorer import FileExplorerDialog
from file_explorer import *

class ControlDiag(QtWidgets.QDialog):
    def __init__(self, sock):
        super().__init__()

        self.sock = sock

        self.setWindowTitle('Control Actions')
        self.setFixedSize(300, 220)

        key_control_button = QtWidgets.QPushButton(
            'Control Keyboard', self)
        key_control_button.move(90, 10)
        key_control_button.setFixedSize(120, 40)

        live_screen_button = QtWidgets.QPushButton(
            'Stream Screen', self)
        live_screen_button.move(10, 60)
        live_screen_button.setFixedSize(120, 40)

        shutdown_logoff_button = QtWidgets.QPushButton(
            'Shutdown/Logoff', self)
        shutdown_logoff_button.move(10, 110)
        shutdown_logoff_button.setFixedSize(120, 40)

        mac_addr_button = QtWidgets.QPushButton(
            'Get MAC Address', self)
        mac_addr_button.move(10, 160)
        mac_addr_button.setFixedSize(120, 40)

        file_explorer_button = QtWidgets.QPushButton(
            'Explore Remote Files', self)
        file_explorer_button.move(160, 60)
        file_explorer_button.setFixedSize(120, 40)

        application_button = QtWidgets.QPushButton(
            'Application Manager', self)
        application_button.move(160, 110)
        application_button.setFixedSize(120, 40)

        process_button = QtWidgets.QPushButton('Process Manager', self)
        process_button.move(160, 160)
        process_button.setFixedSize(120, 40)

        key_control_button.clicked.connect(self.click_key_control_button)
        #live_screen_button.clicked.connect(self.click_live_screen_button)
        shutdown_logoff_button.clicked.connect(self.click_power_button)
        mac_addr_button.clicked.connect(self.click_mac_addr_button)
        file_explorer_button.clicked.connect(self.click_file_explorer_button)
        application_button.clicked.connect(self.click_app_button)
        process_button.clicked.connect(self.click_process_button)

    def click_key_control_button(self):
        key_control_diag = KeyControlDialog(self.sock)
        target=key_control_diag.exec()

    # def click_live_screen_button(self):
    #     live_screen_diag = LiveScreenDiag(self.sock)
    #     thread = threading.Thread(target=live_screen_diag.exec(), args=())
    #     thread.start()

    def click_power_button(self):
        power_diag = PowerDialog(self.sock)
        target=power_diag.exec()

    def click_mac_addr_button(self):
        mac_addr_diag = GetMACAddressDialog(self.sock)
        mac_addr_diag.exec()

    def click_file_explorer_button(self):
        file_explorer_diag = FileExplorerDialog(self.sock)
        file_explorer_diag.exec()

    def click_app_button(self):
        app_diag = ApplicationDialog(self.sock)
        app_diag.exec()

    def click_process_button(self):
        process_diag = ProcessDialog(self.sock)
        process_diag.exec()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = ControlDiag(0)
    window.show()
    sys.exit(app.exec())
