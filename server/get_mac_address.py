import json
import uuid
import re

class GetMACAddress:
    def __init__(self, sock):
        self.sock = sock

    def do_task(self):
        mac_addr = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        message_to_send = {'type': '', 'request': '', 'data': mac_addr}
        self.sock.sendall(json.dumps(message_to_send).encode('utf-8'))
