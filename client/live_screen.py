from PySide6.QtCore import QThread, Qt, Signal, QSize
from PySide6.QtGui import QImage, QPixmap
from PIL.ImageQt import ImageQt
from PySide6 import QtWidgets
from PIL import Image
import sys
import socket
import json
import logging
import time
import queue

logging.basicConfig(level=logging.DEBUG)

class LiveScreenDialog(QtWidgets.QDialog):
    def __init__(self, sock):
        super().__init__()

        self.sock = sock
        self.setWindowTitle('Live Screen')
        self.setFixedSize(720, 480)
        self.picture_box = QtWidgets.QLabel(self)
        self.picture_box.setFixedSize(700, 390)
        self.picture_box.move(10, 10)

        self.start_button = QtWidgets.QPushButton('Start', self)
        self.start_button.move(200, 420)
        self.start_button.setFixedSize(100, 50)

        self.stop_button = QtWidgets.QPushButton('Stop', self)
        self.stop_button.move(420, 420)
        self.stop_button.setFixedSize(100, 50)

        self.start_button.clicked.connect(self.click_start_button)
        self.stop_button.clicked.connect(self.click_stop_button)

        self.img_queue = queue.Queue()
        self.get_thread = self.GetScreenshotThread(self.img_queue)

        self.render_thread = self.RenderThread(self.img_queue)
        self.render_thread.change_pixmap.connect(self.set_image)

    def set_image(self, image):
        self.count_frame += 1
        if self.count_frame == 10:
            logging.debug('10!')
            self.start_time = time.time()
        self.picture_box.setPixmap(QPixmap.fromImage(image))

    def click_start_button(self):
        message = {'type': 'live_screen', 'request': 'start', 'data': ''}
        self.sock.sendall(json.dumps(message).encode('utf-8'))
        self.count_frame = 0
        self.start_time = 0
        self.stop_time = 0
        self.get_thread.start()
        self.render_thread.start()

    def click_stop_button(self):
        message = {'type': 'live_screen', 'request': 'stop', 'data': ''}
        self.sock.sendall(json.dumps(message).encode('utf-8'))
        self.get_thread.stop()
        self.render_thread.stop()
        self.stop_time = time.time()
        logging.debug('frame: {}'.format((self.count_frame - 10)))
        logging.debug('start: {}'.format((self.start_time)))
        logging.debug('stop: {}'.format((self.stop_time)))
        logging.debug('time: {}'.format((self.stop_time - self.start_time)))
        logging.debug('fps is: {}'.format((self.count_frame - 10) / (self.stop_time - self.start_time)))

    # threading
    class GetScreenshotThread(QThread):
        def __init__(self, queue):
            super().__init__()
            self.queue = queue

        def stop(self):
            self.keep_running = False

        def run(self):
            self.keep_running = True
            tcpsock = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_STREAM)
            tcpsock.connect(('127.0.0.1', 23456))
            while self.keep_running:
                properties = b''
                properties = tcpsock.recv(1024 * 1024)
                if properties:
                    properties = json.loads(properties.decode('utf-8'))
                    img_size = properties["size"]
                    w = properties["w"]
                    h = properties["h"]
                    data = b''
                    img = b''
                    
                    while len(img) < img_size:
                        data = tcpsock.recv(3547264)
                        img += data
                    img_format = Image.frombytes(
                        mode="RGB", size=(w, h), data=img)
                    convertToQtFormat = ImageQt(img_format)
                    p = convertToQtFormat.scaled(
                        QSize(700, 393), Qt.KeepAspectRatio)
                    self.queue.put(p)

    class RenderThread(QThread):
        change_pixmap = Signal(QImage)

        def __init__(self, queue):
            super().__init__()
            self.queue = queue

        def run(self):
            self.keep_running = True
            while self.keep_running:
                p = self.queue.get()
                if p:
                    self.change_pixmap.emit(p)

        def stop(self):
            self.keep_running = False


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = LiveScreenDialog(0)
    window.show()
    sys.exit(app.exec())
