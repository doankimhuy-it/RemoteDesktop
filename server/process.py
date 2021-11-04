import signal
import psutil

class Process:
    def __init__(self, sock):
        self.sock = sock

    def do_task(self, request, data):
        if request == 'get_list':
            self.send_process_list()
        if request == 'kill_process':
            self.kill_proc_tree(pid=int(data))
        if request == 'start_process':
            self.start_process(data)

    def send_process_list(self):
        process_list = psutil.process_iter()
        for proc in process_list:
            try:
                # get process name & pid from process object
                process_name = proc.name()
                process_id = proc.pid
                message = process_name + ',' + str(process_id) + '~'
                self.sock.sendall(message.encode('utf-8'))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        end_message = '\r\n'
        self.sock.sendall(end_message.encode('utf-8'))

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
