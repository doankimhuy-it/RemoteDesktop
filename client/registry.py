import json
import socket
import os
import sys
from PySide6 import QtWidgets


class RegistryDialog(QtWidgets.QDialog):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock

        self.setWindowTitle('Registry Edit')
        self.setFixedSize(400, 400)

        self.reg_file_addr = QtWidgets.QLineEdit(self)
        self.reg_file_addr.move(10, 20)
        self.reg_file_addr.setFixedWidth(260)

        self.reg_file_content = QtWidgets.QTextEdit(self)
        self.reg_file_content.move(10, 50)
        self.reg_file_content.setFixedSize(260, 110)

        self.browse_reg_file = QtWidgets.QPushButton('Browse...', self)
        self.browse_reg_file.move(280, 20)

        self.send_content = QtWidgets.QPushButton('Send file content', self)
        self.send_content.move(280, 50)
        self.send_content.setFixedSize(110, 110)

        self.direct_modify_group = QtWidgets.QGroupBox('Directly modify registry', self)
        self.direct_modify_group.move(10, 170)
        self.direct_modify_group.setFixedSize(380, 220)

        self.operation_combo_box = QtWidgets.QComboBox(self.direct_modify_group)
        self.operation_combo_box.move(10, 20)
        self.operation_combo_box.addItems(['Create key', 'Delete key', 'Get value', 'Set value', 'Delete value'])
        self.operation_combo_box.setFixedWidth(360)

        self.reg_addr = QtWidgets.QLineEdit(self.direct_modify_group)
        self.reg_addr.move(10, 50)
        self.reg_addr.setFixedWidth(360)
        self.reg_addr.setPlaceholderText('Enter full address of the registry key')

        self.value_name = QtWidgets.QLineEdit(self.direct_modify_group)
        self.value_name.move(10, 80)
        self.value_name.setFixedWidth(110)
        self.value_name.setPlaceholderText('Name of key')

        self.value = QtWidgets.QLineEdit(self.direct_modify_group)
        self.value.move(130, 80)
        self.value.setFixedWidth(110)
        self.value.setPlaceholderText('Value of key')

        self.value_type_combo_box = QtWidgets.QComboBox(self.direct_modify_group)
        self.value_type_combo_box.move(250, 80)
        self.value_type_combo_box.addItems(['String', 'Binary', 'DWORD', 'QWORD', 'Multi-String', 'Expandable String'])
        self.value_type_combo_box.setFixedWidth(120)

        self.return_message_box = QtWidgets.QTextEdit(self.direct_modify_group)
        self.return_message_box.move(10, 110)
        self.return_message_box.setFixedSize(360, 75)

        self.direct_send = QtWidgets.QPushButton('Send', self.direct_modify_group)
        self.direct_send.move(80, 190)

        self.clear_box = QtWidgets.QPushButton('Clear', self.direct_modify_group)
        self.clear_box.move(220, 190)

        self.value_name.hide()
        self.value.hide()
        self.value_type_combo_box.hide()

        self.browse_reg_file.clicked.connect(self.click_browse_button)
        self.send_content.clicked.connect(self.click_send_content)
        self.operation_combo_box.activated.connect(self.change_operation_combo_box)
        self.direct_send.clicked.connect(self.click_direct_send)
        self.clear_box.clicked.connect(self.click_clear_box)

    def click_browse_button(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'C:\\', 'Registry files (*.reg)')
        file_name = file[0]
        self.reg_file_addr.setText(file_name)
        data = open(file_name, 'r')
        self.reg_file_content.setText(data.read())

    def click_send_content(self):
        message = {'type': 'reg_edit', 'request': 'reg_file', 'data': self.reg_file_content.toPlainText()}
        message = json.dumps(message).encode('utf-8')
        self.sock.sendall(message)

    def change_operation_combo_box(self):
        current_op = self.operation_combo_box.currentText()
        if current_op == 'Create key':
            self.value_name.hide()
            self.value.hide()
            self.value_type_combo_box.hide()
        elif current_op == 'Delete key':
            self.value_name.hide()
            self.value.hide()
            self.value_type_combo_box.hide()
        elif current_op == 'Get value':
            self.value_name.show()
            self.value.hide()
            self.value_type_combo_box.hide()
        elif current_op == 'Set value':
            self.value_name.show()
            self.value.show()
            self.value_type_combo_box.show()
        elif current_op == 'Delete value':
            self.value_name.show()
            self.value.hide()
            self.value_type_combo_box.hide()

    def click_direct_send(self):
        message = {'type': 'reg_edit', 'request': 'direct_edit', 'data': self.operation_combo_box.currentText() + '~' + self.reg_addr.text() + '~'
                   + self.value_name.text() + '~' + self.value.text() + '~' + self.value_type_combo_box.currentText()}
        self.sock.sendall(json.dumps(message).encode('utf8'))

        s = self.sock.recv(4096).decode('utf8')
        self.return_message_box.append(s)

    def click_clear_box(self):
        self.return_message_box.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = RegistryDialog(0)
    window.show()
    sys.exit(app.exec())
