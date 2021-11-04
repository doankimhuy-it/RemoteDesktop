import json
import uuid
import re
import logging

class GetMACAddress:
    def __init__(self, sock):
        self.sock = sock

    def do_task(self):
        mac_addr = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        print(mac_addr)
        message_to_send = {'type': '', 'request': '', 'data': mac_addr}
        self.sock.sendall(json.dumps(message_to_send).encode('utf-8'))
        logging.debug('Get MAC address successfully')
