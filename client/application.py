from process import *

class ApplicationDialog(ProcessDialog):
    def __init__(self, sock):
        super().__init__(sock)
        self.setWindowTitle('Application')

    def get_process_list(self):
        self.list_process_data = []
        self.list_process_data_backup = []
        message_to_send = {'type': 'application',
                           'request': 'get_list', 'data': ''}
        self.sock.sendall(json.dumps(message_to_send).encode('utf-8'))
        self.list_process_data = self.receive_list()
