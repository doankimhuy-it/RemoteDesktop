import logging
import subprocess

class Power:
    '''
    Class which design and handle message for shutdown
        '''

    def __init__(self, operation):
        self._operation = operation

    def shutdown(self):
        subprocess.Popen(['shutdown.exe', '-s'])
        logging.debug('Shut down remote successfully')

    def logoff(self):
        subprocess.Popen(['shutdown.exe', '-l'])
        logging.debug('Logoff remote successfully')

    def do_task(self):
        if (self._operation == 'shutdown'):
            self.shutdown()
        elif (self._operation == 'logoff'):
            self.logoff()
