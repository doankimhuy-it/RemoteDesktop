import socket
from PySide6 import QtWidgets, QtGui, QtCore
import sys
import json

class StandardItem(QtGui.QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False):
        super().__init__()
        self.path = ''

        self.setEditable(False)
        self.setText(txt)

class FileExplorerDialog(QtWidgets.QDialog, QtWidgets.QMainWindow):
    def __init__(self, sock):
        super().__init__()

        self.sock = sock
        self.setWindowTitle("File Explorer")
        self.resize(500, 400)

        self.treeView = QtWidgets.QTreeView(self)
        self.treeView.setHeaderHidden(True)
        self.treeView.resize(320, 400)

        self.treeModel = QtGui.QStandardItemModel()
        self.rootNode = self.treeModel.invisibleRootItem()

        self.treeView.setModel(self.treeModel)
        self.treeView.expandAll()
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #begin test right click
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.openContextMenu)

        self.myMenu = QtWidgets.QMenu('Menu', self)
        copy_btn = QtGui.QAction('Copy',self)
        copy_btn.triggered.connect(self.click_copy_button)
        copy_btn.setCheckable(True)
        self.myMenu.addAction(copy_btn)
        delete_btn = QtGui.QAction('Delete',self)
        delete_btn.triggered.connect(self.click_delete_button)
        delete_btn.setCheckable(True)
        self.myMenu.addAction(delete_btn)
        #end test right click
        self.treeView.clicked.connect(self.click_get_child_dir)

        # self.model = QtWidgets.QFileSystemModel()
        # self.model.setRootPath((QtCore.QDir.rootPath()))
        # self.treeView.setModel(self.model)
        # self.treeView.setSortingEnabled(True)
        # self.rootNode = self.model.invisibleRootItem()

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

    #function test right click
    def openContextMenu(self):
        self.myMenu.exec_(QtGui.QCursor.pos())
    #end test

    def click_get_button(self):
        message_to_send = {'type': 'file_explorer', 'request': 'get', 'data': ''}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        message_recvd = self.sock.recv(4096).decode('utf8')
        message_recvd = json.loads(message_recvd)
        list_recvd = message_recvd['data'].split('|')
        for data in list_recvd:
            rootName = StandardItem(data)
            rootName.path += data
            self.rootNode.appendRow(rootName)

    def click_copy_button(self, val):
        message_to_send = {'type': 'file_explorer', 'request': 'copy', 'data': val.data()}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        message_recvd = self.sock.recv(4096).decode('utf8')
        message_recvd = json.loads(message_recvd)

    def click_delete_button(self, val):
        message_to_send = {'type': 'file_explorer', 'request': 'delete', 'data': val.data()}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        message_recvd = self.sock.recv(4096).decode('utf8')
        message_recvd = json.loads(message_recvd)

    # def keyPressEvent(self, event):

    #     if event.key() == QtWidgets.Key_Space or event.key() == QtWidgets.Key_Return:
    #         index = self.selectedIndexes()[0].model()
    #         crawler = index.model().itemFromIndex(index)
    #     QtWidgets.QTreeView.keyPressEvent(self, event)
    #     return index

    @QtCore.Slot(QtCore.QModelIndex)
    def click_get_child_dir(self, val):
        # indexItem = self.treeView.model.index(index.row(), 0, index.parent())
        # path = self.treeView.model.fileName(indexItem)
        print('---------')
        index_path = self.treeView.selectedIndexes()[0]
        path = index_path.model().itemFromIndex(index_path).path
        print(path)
        print('----------')
        message_to_send = {'type': 'file_explorer', 'request': 'get_child_dir', 'data': '{}'.format(path)}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        message_recvd = self.sock.recv(4096).decode('utf8')
        message_recvd = json.loads(message_recvd)
        list_recvd = message_recvd['data'].split('|')
        print(list_recvd)
        for data in list_recvd:
            #test if i can change the name
            rootName = StandardItem(data)
            #test rootName.path
            rootName.path = rootName.path + path + '\\' + data
            print(rootName.path + '|||||||||||')
            index = self.treeView.selectedIndexes()[0]
            #test get path
            # txt = index.model().itemFromIndex(index).path + '\\' + data
            # print(txt)
            index.model().itemFromIndex(index).appendRow(rootName)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = FileExplorerDialog(0)
    window.show()
    sys.exit(app.exec())
