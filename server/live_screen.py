from PIL import ImageGrab
import socket
import logging
import json

from PySide6.QtCore import QThread


logging.basicConfig(level=logging.DEBUG)

class LiveScreen:
    def __init__(self, sock):
        self.sock = sock
        self.sending_thread = self.SendingThread()

    def do_task(self, request, data):
        if request == 'stop':
            self.sending_thread.stop()
        elif request == 'start':
            self.sending_thread.start()

    class SendingThread(QThread):
        def __init__(self):
            super().__init__()

        def stop(self):
            self.keepRunning = False

        def run(self):
            connection = self.setup_tunnel()
            self.keepRunning = True
            while self.keepRunning:
                self.send_img(connection)
                QThread.msleep(5)

        def setup_tunnel(self):
            tcpsock = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_STREAM)
            tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcpsock.bind(('127.0.0.1', 23456))
            tcpsock.listen(100)
            tcpsock_connection, tcpsock_address = tcpsock.accept()
            return tcpsock_connection

        def send_img(self, connection):
            screenshot = ImageGrab.grab()
            message = screenshot.tobytes()

            w, h = screenshot.size
            properties = {"size": len(message),
                          "w": w,
                          "h": h}
            connection.sendall(json.dumps(properties).encode('utf-8'))
            connection.sendall(message)
