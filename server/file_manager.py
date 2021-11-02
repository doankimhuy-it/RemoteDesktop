from subprocess import *
import os

class FileManager:
    def __init__(self, sock, request, filename):
        self.sock = sock
        self.request = request
        self.filename = filename

    def copy_file(self):
        file = open(self.filename, 'wb')
        data = self.sock.recv(1024)
        while data:
            file.write(data)
            data = self.sock.recv(1024)

    def delete_file(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def do_task(self):
        if self.request == 'copy':
            self.copy_file()
        elif self.request == 'delete':
            self.delete_file()
