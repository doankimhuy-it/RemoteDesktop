from client_base_gui import ClientWindow
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

        self.tree_view = QtWidgets.QTreeView(self)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.resize(320, 400)

        self.tree_model = QtGui.QStandardItemModel()
        self.root_node = self.tree_model.invisibleRootItem()

        self.tree_view.setModel(self.tree_model)
        self.tree_view.expandAll()
        self.tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.open_context_menu)

        self.menu = QtWidgets.QMenu('Menu', self)
        delete_action = QtGui.QAction('Delete', self)
        delete_action.triggered.connect(self.right_click_delete_button)
        self.menu.addAction(delete_action)
        self.tree_view.clicked.connect(self.click_get_child_dir)

        self.get_view_button = QtWidgets.QPushButton(self)
        self.get_view_button.move(330, 20)
        self.get_view_button.setFixedSize(160, 50)
        self.get_view_button.setText('View remote\'s disks')

        self.copy_button = QtWidgets.QPushButton(self)
        self.copy_button.move(330, 80)
        self.copy_button.setFixedSize(160, 50)
        self.copy_button.setText('Copy to selected folder')

        self.delete_button = QtWidgets.QPushButton(self)
        self.delete_button.move(330, 140)
        self.delete_button.setFixedSize(160, 50)
        self.delete_button.setText('Delete selected file')

        self.clear_button = QtWidgets.QPushButton(self)
        self.clear_button.move(330, 220)
        self.clear_button.setFixedSize(160, 50)
        self.clear_button.setText('Clear view')

        self.label = QtWidgets.QLabel(self)
        self.label.move(330, 280)
        self.label.setFixedSize(160, 80)
        self.label.setWordWrap(True)
        self.label.setText('*Notes*\nChoose destination folder before copying.\nDelete files only.')

        self.get_view_button.clicked.connect(self.click_get_view_button)
        self.copy_button.clicked.connect(self.click_copy_button)
        self.delete_button.clicked.connect(self.click_delete_button)
        self.clear_button.clicked.connect(self.click_clear_button)

        self.index_path = 0
        self.path = ''

    def open_context_menu(self):
        self.menu.exec(QtGui.QCursor.pos())

    def click_clear_button(self):
        self.tree_model.clear()
        self.root_node = self.tree_model.invisibleRootItem()

    def click_get_view_button(self):
        self.tree_model.clear()
        self.root_node = self.tree_model.invisibleRootItem()

        message_to_send = {'type': 'file_explorer', 'request': 'get', 'data': ''}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        data = ''
        message_recvd = self.sock.recv(4096).decode('utf-8')
        while message_recvd and message_recvd[-2:] != '\r\n':
            data += message_recvd
            message_recvd = self.sock.recv(4096).decode('utf-8')
        data += message_recvd[:-2]
        list_recvd = data.split('|')
        for data in list_recvd:
            rootName = StandardItem(data)
            rootName.path += data
            self.root_node.appendRow(rootName)

    def click_copy_button(self):
        if self.path == '':
            ClientWindow.show_error('Select a directory for copying', title='Error')
            return

        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'C:\\', 'All files (*.*)')
        file_name = file[0]
        name = ntpath.basename(file_name)

        if name == '':
            ClientWindow.show_error('Choose a file to copy', title='Error')
            return

        message_to_send = {'type': 'file_explorer', 'request': 'copy', 'data': '{}'.format(self.path + '\\' + name)}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))
        self.sock.recv(1)

        logging.debug('start send file')

        fi = open(file_name, 'rb')
        file_data = fi.read()
        self.sock.sendall(file_data)

        self.sock.sendall(b'\r\n')

    def right_click_delete_button(self):
        index_path = self.tree_view.selectedIndexes()[0]
        path = index_path.model().itemFromIndex(index_path).path
        message_to_send = {'type': 'file_explorer', 'request': 'delete', 'data': path}
        logging.debug(message_to_send)
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

    def click_delete_button(self):
        message_to_send = {'type': 'file_explorer', 'request': 'delete', 'data': self.path}
        logging.debug(message_to_send)
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

    @QtCore.Slot(QtCore.QModelIndex)
    def click_get_child_dir(self):
        self.index_path = self.tree_view.selectedIndexes()[0]
        check_update = self.index_path.model().itemFromIndex(self.index_path).check_update
        if check_update == True:
            return
        self.path = self.index_path.model().itemFromIndex(self.index_path).path
        self.index_path.model().itemFromIndex(self.index_path).check_update = True

        message_to_send = {'type': 'file_explorer', 'request': 'get_child_dir', 'data': '{}'.format(self.path)}
        message_to_send = json.dumps(message_to_send)
        self.sock.sendall(message_to_send.encode('utf-8'))

        data = ''
        message_recvd = self.sock.recv(4096).decode('utf-8')
        if message_recvd == '??':
            logging.debug('Cannot process selected item')
            logging.debug(self.path)
            return
        while message_recvd and message_recvd[-2:] != '\r\n':
            data += message_recvd
            message_recvd = self.sock.recv(4096).decode('utf-8')
        data += message_recvd[:-2]
        list_recvd = data.split('|')

        for data in list_recvd:
            rootName = StandardItem(data)
            rootName.path = rootName.path + self.path + '\\' + data

            index = self.tree_view.selectedIndexes()[0]
            index.model().itemFromIndex(index).appendRow(rootName)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = FileExplorerDialog(0)
    window.show()
    sys.exit(app.exec())
