import logging
import subprocess

class Power:
    '''
    Handle shutdown and logoff requests
        '''

    def __init__(self):
        pass

    def shutdown(self):
        subprocess.Popen(['shutdown.exe', '-s'])
        logging.debug('Shut down remote successfully')

    def logoff(self):
        subprocess.Popen(['shutdown.exe', '-l'])
        logging.debug('Logoff remote successfully')

    def do_task(self, operation):
        if (operation == 'shutdown'):
            self.shutdown()
        elif (operation == 'logoff'):
            self.logoff()
