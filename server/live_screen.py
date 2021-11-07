from PIL import ImageGrab
import socket
import logging
import json

from PySide6.QtCore import QThread, QMutex


logging.basicConfig(level=logging.DEBUG)

class LiveScreen:
    def __init__(self, sock):
        self.sock = sock
        self.sending_thread = None

    def do_task(self, request, data):
        if request == 'stop':
            if self.sending_thread:
                self.sending_thread.stop()
                self.sending_thread.quit()
                self.sending_thread.wait()
                self.sending_thread = None
        elif request == 'start':
            if not self.sending_thread:
                self.sending_thread = self.SendingThread(self.sock.getpeername()[0], data)
                self.sending_thread.start()

    class SendingThread(QThread):
        def __init__(self, host, port):
            super().__init__()
            self.mutex = QMutex()
            self.host = host
            self.port = port
            self.keep_running = True

        def stop(self):
            self.mutex.lock()
            self.keep_running = False
            self.mutex.unlock()

        def run(self):
            connection = self.setup_tunnel()
            keep_running = self.keep_running

            while keep_running:
                self.mutex.lock()
                self.send_img(connection)
                QThread.msleep(10)
                keep_running = self.keep_running
                self.mutex.unlock()

        def setup_tunnel(self):
            tcpsock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            tcpsock.connect((self.host, self.port))
            return tcpsock

        def send_img(self, connection):
            screenshot = ImageGrab.grab()
            img_to_byte = screenshot.tobytes()

            w, h = screenshot.size
            properties = {'size': format(len(img_to_byte), '08d'),
                          'w': format(w, '08d'),
                          'h': format(h, '08d')}
            try:
                connection.sendall(json.dumps(properties).encode('utf-8'))
                connection.sendall(img_to_byte)
            except:
                pass
