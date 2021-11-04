import json
import logging
from subprocess import *
import os
import string

class FileManager:
    def __init__(self, sock, request, filename):
        self.sock = sock
        self.request = request
        self.filename = filename

    def get_base_file_directory(self):
        dir = []
        for startpath in string.ascii_uppercase:
            path = '{}:\\'.format(startpath)
            check = os.path.exists(path)
            if check:
                # (root, dirs, files) = os.walk(path)
                # dir += (root, dirs, files)
                for (root, dirs, files) in os.walk(path):
                    print(root)
                    dir.append(root)
                    break
        myDir = ",".join(dir)
        print(myDir)
        message = {'type': '', 'request': '', 'data': myDir}
        self.sock.sendall(json.dumps(message).encode('utf-8'))
        
    def get_file_directory(self):
        if (os.path.isdir(self.filename)):
            print(self.filename)
            # (root, dirs, files) = os.walk(self.filename)
            for (root, dirs, files) in os.walk(self.filename):
                data = dirs + files
                dir = ','.join(data)
                message = {'type': '', 'request': '', 'data': dir}
                logging.debug(message)
                self.sock.sendall(json.dumps(message).encode('utf-8'))
                break


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
        elif self.request == 'get':
            self.get_base_file_directory()
        elif self.request == 'get_child_dir':
            self.get_file_directory()
