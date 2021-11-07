from PySide6.QtCore import QThread, Qt, Signal, QSize, QMutex
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
        self.main_sock = sock
        self.init_ui()

        self.img_queue = queue.Queue()

        self.get_thread = None

        self.render_thread = None

    def init_ui(self):

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

    def set_image(self, image):
        self.count_frame += 1
        if self.count_frame == 10:
            self.start_time = time.time()
        self.picture_box.setPixmap(QPixmap.fromImage(image))

    def click_start_button(self):
        if not self.get_thread:
            img_recv_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            img_recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            img_recv_sock.bind(('0.0.0.0', 55555))
            self.port = 55555
            print(self.port)
            self.get_thread = self.GetScreenshotThread(self.img_queue, img_recv_sock)

        if not self.render_thread:
            self.render_thread = self.RenderThread(self.img_queue)
            self.render_thread.change_pixmap.connect(self.set_image)

        message = {'type': 'live_screen', 'request': 'start', 'data': self.port}
        self.main_sock.sendall(json.dumps(message).encode('utf-8'))
        logging.debug('start send: {}'.format(message))

        self.get_thread.start()
        self.render_thread.start()

        self.count_frame = 0
        self.start_time = 0
        self.stop_time = 0

    def click_stop_button(self):
        message = {'type': 'live_screen', 'request': 'stop', 'data': ''}
        self.main_sock.sendall(json.dumps(message).encode('utf-8'))
        if self.get_thread:
            self.get_thread.stop()
            self.get_thread.quit()
            self.get_thread.wait()
            self.get_thread = None

        logging.debug('finished get thread')
        if self.render_thread:
            self.render_thread.stop()
            self.render_thread.quit()
            self.render_thread.wait()
            self.render_thread = None

        self.stop_time = time.time()
        logging.debug('frame: {}'.format((self.count_frame - 10)))
        logging.debug('start: {}'.format((self.start_time)))
        logging.debug('stop: {}'.format((self.stop_time)))
        logging.debug('time: {}'.format((self.stop_time - self.start_time)))
        logging.debug('fps is: {}'.format((self.count_frame - 10) / (self.stop_time - self.start_time)))

    def closeEvent(self, event):
        message_to_send = {'type': 'live_screen', 'request': 'stop', 'data': ''}
        self.main_sock.sendall(json.dumps(message_to_send).encode(('utf-8')))
        if self.get_thread:
            self.get_thread.stop()
            self.get_thread.quit()
            self.get_thread.wait()

        if self.render_thread:
            self.render_thread.stop()
            self.render_thread.quit()
            self.render_thread.wait()

    # threading
    class GetScreenshotThread(QThread):
        def __init__(self, queue, tcpsock):
            super().__init__()
            self.mutex = QMutex()
            self.tcpsock = tcpsock
            self.queue = queue
            self.keep_running = True

        def stop(self):
            self.mutex.lock()
            self.keep_running = False
            self.mutex.unlock()

        def run(self):
            sock = self.setup_tunnel(self.tcpsock)

            keep_running = self.keep_running
            while keep_running:
                self.mutex.lock()

                try:
                    properties = sock.recv(54)
                except:
                    pass
                else:
                    logging.debug('properties = {}'.format(properties))
                    properties = json.loads(properties.decode('utf-8'))
                    img_size = int(properties['size'])
                    w = int(properties['w'])
                    h = int(properties['h'])
                    data = b''
                    img = b''

                    while len(img) < img_size:
                        try:
                            data = sock.recv(img_size)
                        except:
                            pass
                        else:
                            img += data
                    img_format = Image.frombytes(
                        mode='RGB', size=(w, h), data=img)
                    convertToQtFormat = ImageQt(img_format)
                    p = convertToQtFormat.scaled(
                        QSize(700, 393), Qt.KeepAspectRatio)
                    self.queue.put(p)

                keep_running = self.keep_running
                self.mutex.unlock()

        def setup_tunnel(self, img_recv_sock):
            img_recv_sock.listen(100)
            tcpsock_connection, tcpsock_address = img_recv_sock.accept()
            tcpsock_connection.setblocking(False)
            return tcpsock_connection

    class RenderThread(QThread):
        change_pixmap = Signal(QImage)

        def __init__(self, queue):
            super().__init__()
            self.mutex = QMutex()
            self.queue = queue
            self.keep_running = True

        def run(self):
            keep_running = self.keep_running
            while keep_running:
                self.mutex.lock()
                try:
                    p = self.queue.get(False)
                except:
                    pass
                else:
                    self.change_pixmap.emit(p)
                keep_running = self.keep_running
                self.mutex.unlock()

        def stop(self):
            self.mutex.lock()
            self.keep_running = False
            self.mutex.unlock()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = LiveScreenDialog(0)
    window.show()
    sys.exit(app.exec())
