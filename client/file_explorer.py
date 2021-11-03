import socket
from PySide6 import QtWidgets, QtGui, QtCore
import sys
import json

class StandardItem(QtGui.QStandardItem):
    def __init__(self, txt = '', font_size = 12, set_bold = False):
        super().__init__()

        self.setEditable(False)
        self.setText(txt)

class FileExplorerDialog(QtWidgets.QDialog):
    def __init__(self, sock):
        super().__init__()

        self.sock = sock
        self.setWindowTitle("File explorer")
        self.resize(500, 400)

        self.treeView = QtWidgets.QTreeView(self)
        self.treeView.setHeaderHidden(True)
        self.treeView.resize(320, 400)

        self.treeModel = QtGui.QStandardItemModel()
        self.rootNode = self.treeModel.invisibleRootItem()

        self.treeView.setModel(self.treeModel)
        self.treeView.expandAll()
        # self.treeView.SelectedClicked(self.click_get_child_dir())

        self.getView = QtWidgets.QPushButton(self)
        self.getView.move(350, 20)
        self.getView.setFixedWidth(120)
        self.getView.setText('View directory')

        self.copyButton = QtWidgets.QPushButton(self)
        self.copyButton.move(350, 80)
        self.copyButton.setFixedWidth(120)
        self.copyButton.setText('Copy')

        self.deleteButton = QtWidgets.QPushButton(self)
        self.deleteButton.move(350, 140)
        self.deleteButton.setFixedWidth(120)
        self.deleteButton.setText('Delete')

        self.inputText = QtWidgets.QLineEdit(self)
        self.inputText.move(350, 200)
        self.inputText.setFixedWidth(120)
        self.inputText.setText('')

        self.getView.clicked.connect(self.click_get_button)
        self.copyButton.clicked.connect(self.click_copy_button)
        self.deleteButton.clicked.connect(self.click_delete_button)
        
    def click_get_button(self):
        message_to_send = {'type': 'file_explorer', 'request': 'get', 'data': ''}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        message_recvd = self.sock.recv(1024).decode('utf8')
        message_recvd = json.loads(message_recvd)
        list_recvd = message_recvd['data'].split(',')
        for data in list_recvd:
            rootName = StandardItem(data)
            self.rootNode.appendRow(rootName)

    def click_copy_button(self):
        message_to_send = {'type': 'file_explorer', 'request': 'copy', 'data': ''}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        message_recvd = self.sock.recv(1024).decode('utf8')
        message_recvd = json.loads(message_recvd)

    def click_delete_button(self):
        message_to_send = {'type': 'file_explorer', 'request': 'delete', 'data': ''}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        message_recvd = self.sock.recv(1024).decode('utf8')
        message_recvd = json.loads(message_recvd)

    def click_get_child_dir(self):
        return 1


# if __name__ == '__main__':
#     app = QtWidgets.QApplication([])
#     window = FileExplorerDialog(0)
#     window.show()
#     sys.exit(app.exec())