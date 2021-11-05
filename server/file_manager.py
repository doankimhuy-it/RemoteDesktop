import json
import logging
from subprocess import *
import os
import string

class FileManager:
    def __init__(self, sock):
        self.sock = sock

    def get_base_file_directory(self):
        dir = []
        for start_path in string.ascii_uppercase:
            path = '{}:\\'.format(start_path)
            check = os.path.exists(path)
            if check:
                # (root, dirs, files) = os.walk(path)
                # dir += (root, dirs, files)
                for (root, dirs, files) in os.walk(path):
                    print(root)
                    dir.append(root)
                    break
        my_dir = "|".join(dir)
        print(my_dir)
        message = my_dir
        self.sock.sendall(message.encode('utf-8'))
        self.sock.sendall('\r\n'.encode('utf-8'))

    def get_file_directory(self, name):
        logging.debug(name + '\\\\\\\\\\\\ ')
        logging.debug(os.path.isdir(name))
        logging.debug(os.path.isfile(name))
        if os.path.isdir(name):
            print(name)
            for (root, dirs, files) in os.walk(name):
                data = dirs + files
                dir = '|'.join(data)
                message = dir
                logging.debug(message)
                self.sock.sendall(message.encode('utf-8'))
                self.sock.sendall('\r\n'.encode('utf-8'))
                break
        elif os.path.isfile(name):
            message = ' '
            logging.debug('helo world')
            self.sock.sendall(message.encode('utf-8'))
            logging.debug('sent')

    def copy_file(self, name):
        file = open(name, 'wb')
        data = self.sock.recv(4096)
        while data:
            file.write(data)
            data = self.sock.recv(4096)

    def delete_file(self, name):
        if os.path.exists(name):
            os.remove(name)

    def do_task(self, request, data):
        if request == 'copy':
            self.copy_file(data)
        elif request == 'delete':
            self.delete_file(data)
        elif request == 'get':
            self.get_base_file_directory()
        elif request == 'get_child_dir':
            self.get_file_directory(data)
