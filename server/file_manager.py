import logging
from subprocess import *
import os
import string

class FileManager:
    def __init__(self, sock):
        self.sock = sock

    def get_base_directory(self):
        dir = []
        for start_path in string.ascii_uppercase:
            path = '{}:\\'.format(start_path)
            check = os.path.exists(path)
            if check:
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
        if os.path.isdir(name):
            try:
                os.listdir(name)
            except:
                message = '??'
                self.sock.sendall(message.encode('utf-8'))
                logging.debug('Error processing selected item')
            else:
                for (root, dirs, files) in os.walk(name):
                    data = dirs + files
                    dir = '|'.join(data)
                    message = dir
                    logging.debug(message)
                    self.sock.sendall(message.encode('utf-8'))
                    self.sock.sendall('\r\n'.encode('utf-8'))
                    break
        elif os.path.isfile(name):
            message = '??'
            self.sock.sendall(message.encode('utf-8'))
            logging.debug('Error processing selected item')

    def copy_file(self, path):
        try:
            file = open(path, 'wb')
        except:
            tmp = path.split('\\')
            correct_path = '\\'.join(tmp[:-2]) + '\\' + tmp[-1]
            file = open(correct_path, 'wb')
            self.sock.sendall(b'1')
            data = self.sock.recv(1024 * 1024)
            while data and data[-2:] != b'\r\n':
                file.write(data)
                data = self.sock.recv(1024 * 1024)
            file.write(data[:-2])
            file.close()
        else:
            self.sock.sendall(b'1')
            data = self.sock.recv(1024 * 1024)
            while data and data[-2:] != b'\r\n':
                file.write(data)
                data = self.sock.recv(1024 * 1024)
            file.write(data[:-2])
            file.close()

    def delete_file(self, name):
        if os.path.exists(name) and os.path.isfile(name):
            os.remove(name)

    def do_task(self, request, data):
        if request == 'copy':
            self.copy_file(data)
        elif request == 'delete':
            self.delete_file(data)
        elif request == 'get':
            self.get_base_directory()
        elif request == 'get_child_dir':
            self.get_file_directory(data)
