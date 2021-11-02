import json
import signal
import psutil
import ctypes

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(
    ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId

class Process:
    def __init__(self, sock, request, data):
        self.sock = sock
        self.request = request
        self.data = data

    def do_task(self):
        if self.request == 'get_list':
            self.send_process_list()
        if self.request == 'kill_process':
            self.kill_proc_tree(pid=int(self.message))
        if self.request == 'start_process':
            self.start_process(self.message)

    def send_process_list(self):
        for proc in psutil.process_iter():
            try:
                # get process name & pid from process object.
                process_name = proc.name()
                process_id = proc.pid
                message = {'request': '', 'data': process_name + ',' + str(process_id) + '~'}
                self.sock.sendall(json.dumps(message).encode('utf-8'))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def kill_proc_tree(self, pid, sig=signal.SIGTERM, include_parent=True,
                       timeout=None, on_terminate=None):
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        if include_parent:
            children.append(parent)
        for p in children:
            p.send_signal(sig)
        gone, alive = psutil.wait_procs(children, timeout=timeout,
                                        callback=on_terminate)
        return (gone, alive)

    def start_process(self, process):
        psutil.Popen(str(process))
