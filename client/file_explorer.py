import time
from PySide6 import QtWidgets, QtGui, QtCore
import sys
import json
import logging
import ntpath

class StandardItem(QtGui.QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False):
        super().__init__()
        self.path = ''
        self.check_update = False

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
        delete_btn = QtGui.QAction('Delete',self)
        delete_btn.triggered.connect(self.right_click_delete_button)
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

        self.resetButton = QtWidgets.QPushButton(self)
        self.resetButton.move(350, 80)
        self.resetButton.setFixedWidth(120)
        self.resetButton.setText('Reset')

        self.copyButton = QtWidgets.QPushButton(self)
        self.copyButton.move(350, 140)
        self.copyButton.setFixedWidth(120)
        self.copyButton.setText('Copy')

        self.deleteButton = QtWidgets.QPushButton(self)
        self.deleteButton.move(350, 200)
        self.deleteButton.setFixedWidth(120)
        self.deleteButton.setText('Delete')

        self.inputText = QtWidgets.QLineEdit(self)
        self.inputText.move(335, 260)
        self.inputText.setFixedWidth(150)
        self.inputText.setPlaceholderText('Enter path to delete file')
        self.inputText.setText('')

        self.clearButton = QtWidgets.QPushButton(self)
        self.clearButton.move(350, 320)
        self.clearButton.setFixedWidth(120)
        self.clearButton.setText('Clear')

        self.getView.clicked.connect(self.click_get_button)
        self.resetButton.clicked.connect(self.click_reset_button)
        self.copyButton.clicked.connect(self.click_copy_button)
        self.deleteButton.clicked.connect(self.click_delete_button)
        self.clearButton.clicked.connect(self.click_clear_button)

        self.index_path = 0
        self.path = ''

    #function test right click
    def openContextMenu(self):
        self.myMenu.exec_(QtGui.QCursor.pos())
    #end test

    def click_clear_button(self):
        self.treeModel.clear()
        self.rootNode = self.treeModel.invisibleRootItem()

    def click_reset_button(self):
        self.treeModel.clear()
        self.rootNode = self.treeModel.invisibleRootItem()
        self.click_get_button()

    def click_get_button(self):
        self.treeModel.clear()
        self.rootNode = self.treeModel.invisibleRootItem()
        
        message_to_send = {'type': 'file_explorer', 'request': 'get', 'data': ''}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        data = ''
        message_recvd = self.sock.recv(4096).decode('utf8')
        while message_recvd and message_recvd[-2:] != '\r\n':
            data += message_recvd
            message_recvd = self.sock.recv(4096).decode('utf8')
        data += message_recvd[:-2]
        list_recvd = data.split('|')
        for data in list_recvd:
            rootName = StandardItem(data)
            rootName.path += data
            self.rootNode.appendRow(rootName)

    def click_copy_button(self):

        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'C:\\', 'All files (*.*)')
        file_name = file[0]
        name = ntpath.basename(file_name)

        message_to_send = {'type': 'file_explorer', 'request': 'copy', 'data': '{}'.format(self.path + '\\' + name)}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        fi = open(file_name, 'rb')
        file_data = fi.read(4096)
        while file_data:
            self.sock.sendall(file_data)
            file_data = fi.read(4096)
        self.sock.sendall(b'\r\n')

    def right_click_delete_button(self):
        index_path = self.treeView.selectedIndexes()[0]
        path = index_path.model().itemFromIndex(index_path).path
        message_to_send = {'type': 'file_explorer', 'request': 'delete', 'data': path}
        logging.debug(message_to_send)
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

    def click_delete_button(self):
        message_to_send = {'type': 'file_explorer', 'request': 'delete', 'data': self.inputText.text()}
        logging.debug(message_to_send)
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        # data = ''
        # message_recvd = self.sock.recv(4096).decode('utf8')
        # while message_recvd and message_recvd[-2:] != '\r\n':
        #     data += message_recvd
        #     message_recvd = self.sock.recv(4096).decode('utf8')
        # data += message_recvd[:-2]

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
        self.index_path = self.treeView.selectedIndexes()[0]
        check_update = self.index_path.model().itemFromIndex(self.index_path).check_update
        if check_update == True:
            return
        self.path = self.index_path.model().itemFromIndex(self.index_path).path
        self.index_path.model().itemFromIndex(self.index_path).check_update = True
        print(self.path)
        print('----------')
        message_to_send = {'type': 'file_explorer', 'request': 'get_child_dir', 'data': '{}'.format(self.path)}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        data = ''
        message_recvd = self.sock.recv(4096).decode('utf8')
        if message_recvd == ' ':
            logging.debug('return because it is not a directory')
            return
        while message_recvd and message_recvd[-2:] != '\r\n':
            data += message_recvd
            message_recvd = self.sock.recv(4096).decode('utf8')
        data += message_recvd[:-2]
        list_recvd = data.split('|')
        print(list_recvd)
        for data in list_recvd:
            #test if i can change the name
            rootName = StandardItem(data)
            #test rootName.path
            rootName.path = rootName.path + self.path + '\\' + data
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
