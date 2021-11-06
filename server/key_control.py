import keyboard as kb
from pynput import keyboard
import json
import socket
import logging
from PySide6.QtCore import QThread, QWaitCondition, QMutex

class KeyControl:
    def __init__(self, sock):
        self.sock = sock
        self.send_thread = None
        self.hooked = False
        self.locked = False
        self.listener = None

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.do_task('unhook_key', '')
            return False

        try:
            key_name = key.char
            logging.debug('get key: {}'.format(key_name))
            self.send_thread.send(key_name)
        except:
            pass

    def lock_key(self):
        # locks all keys of keyboard
        self.locked = True
        for i in range(150):
            kb.block_key(i)

    def unlock_key(self):
        # unlocks all keys of keyboard
        if self.locked:
            for i in range(150):
                kb.unblock_key(i)
            self.locked = False

    def do_task(self, request, data):
        # if not self.listener:
        self.listener = keyboard.Listener(
            on_press=self.on_press)

        if request == 'hook_key':
            if not self.hooked:
                self.hooked = True
                self.listener.start()
                if not self.send_thread:
                    self.send_thread = self.SendingThread(self.sock.getpeername()[0], data)

        elif request == 'unhook_key':
            if self.hooked:
                self.hooked = False
                self.listener.stop()
                self.listener = None

        elif (request == 'lock_key'):
            self.lock_key()
        elif (request == 'unlock_key'):
            self.unlock_key()
        elif (request == 'stop'):
            self.do_task('unlock_key', '')
            self.do_task('unhook_key', '')

            logging.debug('start stop')
            self.send_thread.stop()
            logging.debug('start quit')
            self.send_thread.quit()
            logging.debug('start wait')
            self.send_thread.wait()
            logging.debug('wait done')
            self.send_thread = None

    class SendingThread(QThread):
        def __init__(self, host, port):
            super().__init__()
            self.mutex = QMutex()
            self.host = host
            self.port = port
            self.condition = QWaitCondition()
            self.keep_running = True

        def run(self):
            self.sock = self.setup_tunnel(self.host, self.port)
            keep_running = self.keep_running
            while keep_running:
                self.mutex.lock()
                key = self.key
                self.mutex.unlock()

                logging.debug('send key: {}'.format(key))
                key_json = {'key': key}
                self.sock.sendall(json.dumps(key_json).encode('utf-8'))

                self.mutex.lock()
                logging.debug('sending thread go to sleep')
                self.condition.wait(self.mutex)

                logging.debug('Get unlock in run')
                keep_running = self.keep_running
                self.mutex.unlock()

        def stop(self):
            self.mutex.lock()
            self.keep_running = False
            self.condition.wakeOne()
            self.mutex.unlock()

        def setup_tunnel(self, host, port):
            sock = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.setblocking(False)
            return sock

        def send(self, key):
            self.key = key
            logging.debug('get to thread.send()')
            if not self.isRunning():
                logging.debug('start sending thread')
                self.start()
            else:
                logging.debug('sending thread go wake')
                self.condition.wakeOne()
