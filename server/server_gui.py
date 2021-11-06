import sys
import random
from PySide6 import QtCore, QtWidgets


class ServerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.update_gui_timer = QtCore.QTimer()

        # create windows title and its size
        self.setWindowTitle("Server")
        self.setFixedSize(260, 170)

        # listen button
        self.listen_button = QtWidgets.QPushButton("Start listening", self)
        self.listen_button.move(10, 10)
        self.listen_button.setFixedSize(240, 150)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = ServerWindow()
    window.show()
    sys.exit(app.exec())
