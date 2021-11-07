import winreg
import subprocess
import sys

class RegistryEdit:
    def __init__(self, sock):
        self.sock = sock

    def base_registry(self, link):
        a = None
        if (link.index('\\') >= 0):
            base_str = link[:link.index('\\')]
            if base_str == 'HKEY_CLASSES_ROOT':
                a = winreg.HKEY_CLASSES_ROOT
            elif base_str == 'HKEY_CURRENT_USER':
                a = winreg.HKEY_CURRENT_USER
            elif base_str == 'HKEY_LOCAL_MACHINE':
                a = winreg.HKEY_LOCAL_MACHINE
            elif base_str == 'HKEY_USERS':
                a = winreg.HKEY_USERS
            elif base_str == 'HKEY_CURRENT_CONFIG':
                a = winreg.HKEY_CURRENT_CONFIG
        return a

    def get_value(self, a, link2, valueName):
        try:
            a = winreg.OpenKey(a, link2)
        except:
            return 'Error'
        data = winreg.QueryValueEx(a, valueName)[0]
        return str(data)

    def set_value(self, a, link2, valueName, value, valueType):
        try:
            a = winreg.OpenKey(a, link2, 0, winreg.KEY_SET_VALUE)
        except:
            return 'Error'
        type = None
        if valueType == 'String':
            type = winreg.REG_SZ
        elif valueType == 'Binary':
            type = winreg.REG_BINARY
            value = value.encode('utf-8')
        elif valueType == 'DWORD':
            type = winreg.REG_DWORD
            value = int(value)
        elif valueType == 'QWORD':
            type = winreg.REG_QWORD
            value = int(value)
        elif valueType == 'Multi-String':
            type = winreg.REG_MULTI_SZ
        elif valueType == 'Expandable String':
            type = winreg.REG_EXPAND_SZ
        else:
            return 'Error'
        try:
            winreg.SetValueEx(a, valueName, 0, type, value)
        except:
            return 'Error'
        return 'Value set successfully'

    def delete_value(self, a, link2, valueName):
        try:
            a = winreg.OpenKey(a, link2, 0, winreg.KEY_SET_VALUE)
        except:
            return 'Error'

        try:
            winreg.DeleteValue(a, valueName)
        except:
            return 'Error'
        else:
            return 'Value deleted successfully'

    def delete_key(self, a, link2):
        try:
            winreg.DeleteKey(a, link2)
        except:
            return 'Error'
        else:
            return 'Key deleted successfully'

    def do_task(self, request, data):
        if request == 'reg_file':  # open a registry file
            fin = open(sys.path[0] + '\\fileReg.reg', 'w')
            fin.write(data)
            fin.close()
            s = sys.path[0] + '\\fileReg.reg'
            print(s)
            is_successful = False
            try:
                subprocess.run('reg import \"' + s + '\"', timeout=20)
                is_successful = True
            except:
                is_successful = False
            if is_successful:
                s = 'Registry key successfully created'
                print(s)
            else:
                s = 'Failed to create registry key'
                print(s)

        elif request == 'direct_edit':  # send multiple registry data
            s = data
            option, link, valueName, value, valueType = s.split('~')

            a = self.base_registry(link)
            link2 = link[(link.index('\\') + 1):]

            if a == None:
                s = 'Error'
            else:
                if option == 'Create key':
                    try:
                        key = winreg.CreateKey(a, link2)
                        s = 'Key successfully created'
                    except:
                        s = 'Cannot create key'
                elif option == 'Delete key':
                    s = self.delete_key(a, link2)
                elif option == 'Get value':
                    s = self.get_value(a, link2, valueName)
                elif option == 'Set value':
                    s = self.set_value(a, link2, valueName, value, valueType)
                elif option == 'Delete value':
                    s = self.delete_value(a, link2, valueName)
                else:
                    s = 'Error'

            self.sock.sendall(s.encode('utf-8'))
