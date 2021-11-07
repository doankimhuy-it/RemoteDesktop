import socket
import json
import logging
import selectors

from application import Application
from get_mac_address import GetMACAddress
from key_control import KeyControl
from process import Process
from power import Power
from file_manager import FileManager
from live_screen import LiveScreen
from registry import RegistryEdit

logging.basicConfig(level=logging.DEBUG)

class ServerConnection:
    def __init__(self, host, port):
        self.connection_status = 0
        self.sel = selectors.DefaultSelector()
        self.host = host
        self.port = port

    def start_listen(self):
        self.server_sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)  # use TCP/IP Connection
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sel.register(self.server_sock, selectors.EVENT_READ, data=None)
        self.server_sock.bind((self.host, self.port))

        self.server_sock.listen(10)  # accept 10 connections

        # set to start listening flag, 1 is one socket (server_sock)
        self.connection_status = 1
        logging.debug('Listening on {} : {}'.format(self.host, self.port))
        while self.connection_status:
            try:
                # timeout = 0: wait until event appear
                event = self.sel.select(timeout=0)
            except:
                pass
            else:
                for key, mask in event:
                    if key.data == None:
                        self.start_connect(key.fileobj)
                    else:
                        self.service_connect(key, mask)
        if (not self.connection_status):
            logging.debug('Child thread running listen task ended')

    def stop_listen(self):
        s = self.sel.get_map()
        keys = [i for i in s]
        fileobjs = [s[i] for i in keys]

        socks = [file_obj[0] for file_obj in fileobjs if file_obj[3] != None]

        for sock in socks:
            logging.debug('Stop connection with {}'.format(sock.getpeername()))
            sock.close()
            self.sel.unregister(sock)
        # self.server_sock.shutdown(socket.SHUT_RDWR)
        self.connection_status = 0
        self.server_sock.close()
        self.sel.unregister(self.server_sock)
        logging.debug('Stop listening')

    def start_connect(self, sock):
        conn, addr = sock.accept()  # accpet connection from client
        # conn.setblocking(False)         # set sock not block
        data = addr

        self.live_screen_exec = LiveScreen(conn)
        self.process_exec = Process(conn)
        self.app_exec = Application(conn)
        self.mac_exec = GetMACAddress(conn)
        self.key_control_exec = KeyControl(conn)
        self.power_exec = Power()
        self.file_manager_exec = FileManager(conn)  # Not yet fully implemented
        self.reg_edit_exec = RegistryEdit(conn)

        event = selectors.EVENT_READ | selectors.EVENT_WRITE
        # register this connect to sel, with wait-event are both read & write
        self.sel.register(conn, events=event, data=data)
        self.connection_status += 1
        logging.debug('Start connection with {}'.format(addr))

    def stop_connect(self, sock):
        self.sel.unregister(sock)
        self.connection_status -= 1
        sock.close()

    def service_connect(self, key, mask):
        sock = key.fileobj
        addr = key.data
        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(4096)  # read data
            except ConnectionResetError:
                logging.debug('Lost connection from {}'.format(addr))
                self.stop_connect(sock)
            else:
                if recv_data:
                    logging.debug('Raw Message from client {}'.format(recv_data))
                    message = json.loads(recv_data)
                    logging.debug('Message from {}: {}'.format(addr, message))
                    self.handle_message(sock, message)
                else:
                    logging.debug('Closed connection to {}'.format(addr))
                    self.stop_connect(sock)

        elif mask & selectors.EVENT_WRITE:
            pass

    def handle_message(self, sock, message):
        type = message['type']
        request = message['request']
        data = message['data']
        # send command to correct function
        # do the task and answer the client

        if type == 'connection':
            if request == 'ping':
                pass
            elif request == 'close_connection':
                self.stop_connect(sock)
        elif type == 'application':
            self.app_exec.do_task(request, data)
        elif type == 'process':
            self.process_exec.do_task(request, data)
        elif type == 'key_control':
            self.key_control_exec.do_task(request, data)
        elif type == 'mac_address':
            self.mac_exec.do_task()
        elif type == 'power':
            self.power_exec.do_task(request)
        elif type == 'file_explorer':
            self.file_manager_exec.do_task(request, data)
        elif type == 'live_screen':
            self.live_screen_exec.do_task(request, data)
        elif type == 'reg_edit':
            self.reg_edit_exec.do_task(request, data)


if __name__ == '__main__':
    host = '0.0.0.0'    # all network interface
    port = 65432
    server_connection = ServerConnection(host, port)
    server_connection.start()
