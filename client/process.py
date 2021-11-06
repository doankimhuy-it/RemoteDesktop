import json
import socket
import sys
from PySide6 import QtCore, QtWidgets
import logging
import operator

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.mylist[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        else:
            return QtCore.QAbstractTableModel.headerData(self, col, orientation, role)

    def sort(self, col, order):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist,
                             key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))


class ProcessDialog(QtWidgets.QDialog):
    def __init__(self, sock):
        super().__init__()
        self.setWindowTitle('Process')
        self.sock = sock
        self.resize(500, 400)

        self.main_widget = QtWidgets.QTableView(self)
        self.main_widget.move(10, 10)
        self.main_widget.setFixedSize(320, 380)
        self.main_widget.setSortingEnabled(True)
        self.list_process_data = []

        self.view_button = QtWidgets.QPushButton('View', self)
        self.view_button.move(350, 10)
        self.view_button.setFixedWidth(120)

        self.kill_button = QtWidgets.QPushButton('Kill', self)
        self.kill_button.move(350, 45)
        self.kill_button.setFixedWidth(120)

        self.start_button = QtWidgets.QPushButton('Start', self)
        self.start_button.move(350, 80)
        self.start_button.setFixedWidth(120)

        self.clear_button = QtWidgets.QPushButton('Clear', self)
        self.clear_button.move(350, 115)
        self.clear_button.setFixedWidth(120)

        self.direct_modify_groupbox = QtWidgets.QGroupBox('Filter', self)
        self.direct_modify_groupbox.move(340, 160)
        self.direct_modify_groupbox.setFixedSize(150, 220)

        self.filter_label = QtWidgets.QLabel(
            'Filter by:', self.direct_modify_groupbox)
        self.filter_label.move(10, 20)

        self.value_type_combo_box = QtWidgets.QComboBox(
            self.direct_modify_groupbox)
        self.value_type_combo_box.move(10, 40)
        self.value_type_combo_box.addItems(['Name', 'PID'])
        self.value_type_combo_box.setFixedWidth(130)

        self.value_label = QtWidgets.QLabel(
            'Value:', self.direct_modify_groupbox)
        self.value_label.move(10, 70)

        self.filter_text_box = QtWidgets.QLineEdit(
            '', self.direct_modify_groupbox)
        self.filter_text_box.move(10, 90)
        self.filter_text_box.setFixedWidth(130)

        self.filter_button = QtWidgets.QPushButton(
            'Filter', self.direct_modify_groupbox)
        self.filter_button.move(10, 130)
        self.filter_button.setFixedWidth(130)
        self.filter_button.setStyleSheet('color: green; font-weight: bold;')

        self.clear_filter_button = QtWidgets.QPushButton(
            'Clear filter', self.direct_modify_groupbox)
        self.clear_filter_button.move(10, 170)
        self.clear_filter_button.setFixedWidth(130)
        self.clear_filter_button.setStyleSheet('color: red;')

        self.view_button.clicked.connect(self.click_view_button)
        self.kill_button.clicked.connect(self.click_kill_process)
        self.start_button.clicked.connect(self.click_start_process)
        self.clear_button.clicked.connect(self.click_clear_process)
        self.filter_button.clicked.connect(self.click_filter_button)
        self.clear_filter_button.clicked.connect(
            self.click_clear_filter_button)

    def receive_list(self):
        message_recvd = ''
        data = self.sock.recv(4096).decode('utf-8')
        while data and data[-2:] != '\r\n':
            message_recvd = message_recvd + str(data)
            data = self.sock.recv(4096).decode('utf-8')
        message_recvd += str(data[:-2])
        list_recvd = message_recvd.split('~')
        list_recvd = list_recvd[:-1]
        process_list = []
        for item in list_recvd:
            name, pid = item.split(',')
            pid = int(pid)
            process_list.append([name, pid])
        return process_list

    def get_process_list(self):
        self.list_process_data = []
        self.list_process_data_backup = []
        message = {'type': 'process', 'request': 'get_list', 'data': ''}
        self.sock.sendall(json.dumps(message).encode('utf-8'))
        self.list_process_data = self.receive_list()

    def set_data(self):
        header = ['Name', 'PID']
        model = TableModel(self, self.list_process_data, header)
        self.main_widget.setModel(model)
        self.main_widget.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.main_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)

    def click_view_button(self):
        self.get_process_list()
        self.set_data()
        logging.debug('Done')

    def click_kill_process(self):
        index = self.main_widget.selectedIndexes()
        if not index:
            logging.debug('No process selected')
        else:
            cell = index[0]
            row = cell.row()
            x = self.main_widget.model().index(row, 1).data()
            message = {'type': 'process',
                       'request': 'kill_process', 'data': str(x)}
            self.sock.sendall(json.dumps(message).encode('utf-8'))

    def click_start_process(self):
        process, ok = QtWidgets.QInputDialog.getText(
            self, 'Start', 'Enter process/application name:')
        if ok:
            message = {'type': 'process',
                       'request': 'start_process', 'data': str(process)}
            self.sock.sendall(json.dumps(message).encode('utf-8'))

    def click_clear_process(self):
        self.main_widget.model().deleteLater()

    def click_filter_button(self):
        option = self.value_type_combo_box.currentText()
        value = self.filter_text_box.text()
        self.list_process_data_backup = self.list_process_data
        newlist = []
        if option == 'Name':
            for name, pid in self.list_process_data:
                if value in name:
                    newlist.append([name, pid])
        if option == 'PID':
            for name, pid in self.list_process_data:
                if value in str(pid):
                    newlist.append([name, pid])
        if not newlist:
            errbox = QtWidgets.QMessageBox()
            errbox.setText('No processes found')
            errbox.setWindowTitle('Warning')
            errbox.setIcon(QtWidgets.QMessageBox.Information)
            errbox.exec()
        else:
            self.list_process_data = newlist
            self.set_data()

    def click_clear_filter_button(self):
        self.list_process_data = self.list_process_data_backup
        self.set_data()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = ProcessDialog(0)
    # print(window.list_process_data)
    window.show()
    sys.exit(app.exec())
