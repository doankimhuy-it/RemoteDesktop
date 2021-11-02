import json
import psutil
import ctypes

from process import Process

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(
    ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId

class Application:
    def __init__(self, sock, request, data):
        self._sock = sock
        self.request = request
        self.data = data
        self.list_app_data = []

    def do_task(self):
        if self.opcode == 'get_list':
            self.send_process_list()
        if self.opcode == 'kill_process':
            self.kill_proc_tree(pid=int(self.message))
        if self.opcode == 'start_process':
            self.start_process(self.message)

    def foreach_window(self, hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            if (length > 0):
                name = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, name, length + 1)

                pid = ctypes.c_ulong()
                result = ctypes.windll.user32.GetWindowThreadProcessId(
                    hwnd, ctypes.byref(pid))
                process_id = pid.value

                self.list_app_data.append([name.value, pid.value])
        return True

    def send_process_list(self):
        EnumWindows(EnumWindowsProc(self.foreach_window), 0)
        for proc in self.list_app_data:
            try:
                # Get process name & pid from process object.
                process_name = proc[0]
                process_id = proc[1]
                message = {'request': '', 'data': process_name +
                           ',' + str(process_id) + '~'}
                self.sock.sendall(json.dumps(message).encode('utf-8'))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass