"""This is the desktop module used to initialize AEDT.

This module initializes AEDT and MessageManager to manage the AEDT
desktop.  It can be initialized in standalone way before launching an
app or it is automatically initialized to latest installed AEDT
version.


Examples
--------
Launch Desktop 2020R1 in Non-Graphical Mode and initialize HFSS

>>> import pyaedt
>>> desktop = pyaedt.Desktop("2020.1", NG=True)
>>> hfss = pyaedt.Hfss()

Launch Desktop 2019R3 in Graphical Mode

>>> desktop = Desktop("2019.3")
>>> hfss = pyaedt.Hfss()

The initialize Desktop to latest version installed on your machine in
Graphical Mode and initialize HFSS.

"""
from __future__ import absolute_import

import os
import sys
import traceback
import logging
import pkgutil
import getpass
import re
from .application.MessageManager import AEDTMessageManager
from .misc import list_installed_ansysem

pathname = os.path.dirname(__file__)
if os.path.exists(os.path.join(pathname,'version.txt')):
    with open(os.path.join(pathname,'version.txt'), "r") as f:
        pyaedtversion = f.readline()
elif os.path.exists(os.path.join(pathname, "..", 'version.txt')):
    with open(os.path.join(pathname, "..", 'version.txt'), "r") as f:
        pyaedtversion = f.readline()
else:
    pyaedtversion = "X"

_pythonver = sys.version_info[0]

if os.name == 'nt':
    IsWindows = True
else:
    IsWindows = False
logger = logging.getLogger(__name__)

if "IronPython" in sys.version or ".NETFramework" in sys.version:
    import clr  # IronPython C:\Program Files\AnsysEM\AnsysEM19.4\Win64\common\IronPython\ipy64.exe
    _com = 'pythonnet'
elif IsWindows:
    import pythoncom
    modules = [tup[1] for tup in pkgutil.iter_modules()]
    if 'clr' in modules:
        import clr
        import win32com.client
        _com = 'pythonnet_v3'
    elif 'win32com' in modules:
        import win32com.client
        _com = 'pywin32'
    else:
        raise Exception("Error. No win32com.client or Pythonnet modules found. Please install them")


def exception_to_desktop(self, ex_value, tb_data):
    """Writes the trace stack to the desktop when a python error occurs
    
    It adds the message to AEDT Global message manager and to the log file (if present)

    Parameters
    ----------
    ex_value :
        
    tb_data :
        

    Returns
    -------

    """
    desktop = sys.modules['__main__'].oDesktop
    try:
        oproject = desktop.GetActiveProject()
        proj_name = oproject.GetName()
        try:
            des_name = oproject.GetActiveDesign().GetName()
            if ";" in des_name:
                des_name = des_name.split(";")[1]
        except:
            des_name = ''
    except:
        proj_name = ''
        des_name = ''
    tb_trace = traceback.format_tb(tb_data)
    tblist = tb_trace[0].split('\n')
    desktop.AddMessage(proj_name, des_name, 2, str(ex_value))
    for el in tblist:
        desktop.AddMessage(proj_name, des_name, 2, el)


def update_aedt_registry(key, value, desktop_version="193"):
    """Windows Only
    
    Update aedt options registry keys. value includes "" if needed
    
    Examples
    --------
    
    updateAEDTRegistry("HFSS/HPCLicenseType",'"'12'"')
    
    updateAEDTRegistry("Icepak/HPCLicenseType",'"'8'"')
    
    updateAEDTRegistry("HFSS/UseLegacyElectronicsHPC","0")
    
    updateAEDTRegistry("HFSS/MPIVendor",'"'+"Intel"+'"')

    Parameters
    ----------
    key :
        
    value :
        
    desktop_version :
         (Default value = "193")

    Returns
    -------

    """
    import subprocess

    desktop_install_dir = os.environ["ANSYSEM_ROOT" + str(desktop_version)]

    with open(os.path.join(desktop_install_dir, "config", "ProductList.txt")) as file:
        product_version = next(file).rstrip()  # get first line

    options = '-set -ProductName {} + product_version -RegistryKey "{}" -RegistryValue "{}"'.format(product_version,
                                                                                                    key, value)
    command = '"{}/UpdateRegistry" {}'.format(desktop_install_dir, options)

    subprocess.call([command])


def release_desktop(close_projects=True, close_desktop=True):
    """Release the Desktop API

    Parameters
    ----------
    close_projects :
        Boolean, Close the projects opened in the session (Default value = True)
    close_desktop :
        Boolean, Close the active Desktop Session (Default value = True)

    Returns
    -------
    type
        None

    """
    if _com == "pythonnet":
        Module = sys.modules['__main__']
        desktop = Module.oDesktop
        scopeID = desktop.ScopeID
        i = 0
        if close_projects:
            proj_list = desktop.GetProjectList()
            for prj in proj_list:
                desktop.CloseProject(prj)

        while i <= scopeID:
            Module.COMUtil.ReleaseCOMObjectScope(Module.COMUtil.PInvokeProxyAPI, i)
            i += 1
        try:
            del Module.oDesktop
        except:
            Module.oMessenger.add_info_message("Attributes not present")

    elif _com == "pythonnet_v3":
        Module = sys.modules['__main__']
        desktop = Module.oDesktop
        i = 0
        if close_projects:
            proj_list = desktop.GetProjectList()
            for prj in proj_list:
                desktop.CloseProject(prj)

        if close_desktop:
            scopeID = 5
            while i <= scopeID:
                Module.COMUtil.ReleaseCOMObjectScope(Module.COMUtil.PInvokeProxyAPI, 0)
                i += 1
            Module = sys.modules['__main__']
            pid = Module.oDesktop.GetProcessID()
            try:
                os.kill(pid, 9)
                del Module.oDesktop
                return True
            except:
                Module.oMessenger.add_error_message("something went wrong in Closing AEDT")
                return False
        else:
            scopeID = 5
            while i <= scopeID:
                Module.COMUtil.ReleaseCOMObjectScope(Module.COMUtil.PInvokeProxyAPI,i)
                i += 1
            try:
                del Module.oDesktop
            except:
                Module.oMessenger.add_info_message("Attributes not present")
            try:
                del Module.pyaedt_initialized
            except:
                pass


def force_close_desktop():
    """Close all the projects and kill oDesktop
    
    :return: True (Closed) | False (Failed to Close)

    Parameters
    ----------

    Returns
    -------

    """
    Module = sys.modules['__main__']
    pid = Module.oDesktop.GetProcessID()
    if pid > 0:
        try:
            plist = Module.oDesktop.GetProjectList()
            for el in plist:
                Module.oDesktop.CloseProject(el)
        except:
            logger.error("No Projects. Closing Desktop Connection")
        try:
            scopeID = 5
            while i <= scopeID:
                Module.COMUtil.ReleaseCOMObjectScope(Module.COMUtil.PInvokeProxyAPI, 0)
                i += 1
        except:
            logger.error("No COM UTIL. Closing the Desktop....")
        try:
            del Module.pyaedt_initialized
        except:
            pass
        try:
            os.kill(pid, 9)
            del Module.oDesktop
            log= logging.getLogger(__name__)
            handlers = log.handlers[:]
            for handler in handlers:
                handler.close()
                log.removeHandler(handler)
            return True
        except:
            Module.oMessenger.add_error_message("something went wrong in Closing AEDT")
            log= logging.getLogger(__name__)
            handlers = log.handlers[:]
            for handler in handlers:
                handler.close()
                log.removeHandler(handler)
            return False


class Desktop:
    """The core module that initialize Ansys Electronics Desktop tool based on inputs provided:"""
    @property
    def version_keys(self):
        """ """

        self._version_keys = []
        self._version_ids = {}

        version_list = list_installed_ansysem()
        for version_env_var in version_list:
            current_version_id = version_env_var.replace("ANSYSEM_ROOT", '')
            version = int(current_version_id[0:2])
            release = int(current_version_id[2])
            if version < 20:
                if release < 3:
                    version -= 1
                else:
                    release -= 2
            v_key = "20{0}.{1}".format(version, release)
            self._version_keys.append(v_key)
            self._version_ids[v_key] = version_env_var
        return self._version_keys

    @property
    def current_version(self):
        """ """
        return self.version_keys[0]

    def __init__(self, specified_version=None, NG=False, AlwaysNew=True, release_on_exit=True):
        """
        Init Electronic Desktop. On Windows it works without limitations in IronPython and CPython. On Linux it works only in embedded Ironpython in AEDT

        :param specified_version: Version of AEDT to be used. if None. Latest version of AEDT is used
        :param NG: Non Graphical Boolean. True launch AEDT in NG Mode
        :param AlwaysNew: New Thread Boolean. if True it launches a new instance of AEDT even if another one of the specified_version is active on the machine
        :param release_on_exit: Boolean. Release Desktop on Exit
        """
        self._main = sys.modules['__main__']
        self._main.close_on_exit = False
        self._main.isoutsideDesktop = False
        self._main.pyaedt_version = pyaedtversion
        self.release = release_on_exit
        logger.debug("Launching Desktop Init")
        if "oDesktop" in dir(self._main) and self._main.oDesktop is not None:
            self._main.AEDTVersion = self._main.oDesktop.GetVersion()[0:6]
            self._main.oDesktop.RestoreWindow()
            self._main.oMessenger = AEDTMessageManager()
            base_path = self._main.oDesktop.GetExeDir()
            self._main.sDesktopinstallDirectory = base_path
            self.release = False
        else:
            if specified_version:
                assert specified_version in self.version_keys, \
                    "Specified version {} not known.".format(specified_version)
                version_key = specified_version
            else:
                version_key = self.current_version
            base_path = os.getenv(self._version_ids[version_key])
            self._main = sys.modules['__main__']
            self._main.sDesktopinstallDirectory = base_path
            version = "Ansoft.ElectronicsDesktop." + version_key
            self._main.AEDTVersion = version_key
            self._main.interpreter = _com
            self._main.interpreter_ver = _pythonver
            if "oDesktop" in dir(self._main):
                del self._main.oDesktop
            if _com == 'pythonnet':
                sys.path.append(base_path)
                sys.path.append(os.path.join(base_path, 'PythonFiles', 'DesktopPlugin'))
                clr.AddReference("Ansys.Ansoft.CoreCOMScripting")
                AnsoftCOMUtil = __import__("Ansys.Ansoft.CoreCOMScripting")
                self.COMUtil = AnsoftCOMUtil.Ansoft.CoreCOMScripting.Util.COMUtil
                self._main.COMUtil = self.COMUtil
                StandalonePyScriptWrapper = AnsoftCOMUtil.Ansoft.CoreCOMScripting.COM.StandalonePyScriptWrapper
                if NG or AlwaysNew:
                    # forcing new thread to start in non-graphical
                    oAnsoftApp = StandalonePyScriptWrapper.CreateObjectNew(NG)
                else:
                    oAnsoftApp = StandalonePyScriptWrapper.CreateObject(version)

                self._main.oDesktop = oAnsoftApp.GetAppDesktop()
                self._main.isoutsideDesktop = True
            elif _com == 'pythonnet_v3':
                sys.path.append(base_path)
                sys.path.append(os.path.join(base_path, 'PythonFiles', 'DesktopPlugin'))
                print(base_path)
                clr.AddReference("Ansys.Ansoft.CoreCOMScripting")
                AnsoftCOMUtil = __import__("Ansys.Ansoft.CoreCOMScripting")
                self.COMUtil = AnsoftCOMUtil.Ansoft.CoreCOMScripting.Util.COMUtil
                self._main.COMUtil = self.COMUtil
                StandalonePyScriptWrapper = AnsoftCOMUtil.Ansoft.CoreCOMScripting.COM.StandalonePyScriptWrapper
                oAnsoftApp = None
                logger.debug("Launching AEDT with Module Pythonnet")
                processID = []
                if IsWindows:
                    username = getpass.getuser()
                    process = "ansysedt.exe"
                    output = os.popen('tasklist /FI "IMAGENAME eq ansysedt.exe" /v').readlines()
                    pattern = r'^(?i)(?:{})\s+?(\d+)\s+.+[\s|\\](?:{})\s+'.format(process, username)
                    for l in output:
                        m = re.search(pattern, l)
                        if m:
                            processID.append(m.group(1))

                if NG or AlwaysNew or not processID:
                    # forcing new object in case of non-graphical run or if no process already exists
                    App = StandalonePyScriptWrapper.CreateObjectNew(NG)
                else:
                    App = StandalonePyScriptWrapper.CreateObject(version)
                processID2 = []
                if IsWindows:
                    print("Info: Using Windows TaskManager to Load processes")
                    username = getpass.getuser()
                    process = "ansysedt.exe"
                    output = os.popen('tasklist /FI "IMAGENAME eq ansysedt.exe" /v').readlines()
                    pattern = r'^(?i)(?:{})\s+?(\d+)\s+.+[\s|\\](?:{})\s+'.format(process, username)
                    for l in output:
                        m = re.search(pattern, l)
                        if m:
                            processID2.append(m.group(1))

                proc = [i for i in processID2 if i not in processID]
                if not proc:
                    if NG:
                        self._main.close_on_exit = False
                    else:
                        self._main.close_on_exit = False
                    oAnsoftApp = win32com.client.Dispatch(version)
                    self._main.oDesktop = oAnsoftApp.GetAppDesktop()
                    self._main.isoutsideDesktop = True
                elif version_key>="2021.1":
                    self._main.close_on_exit = True
                    print("Info: {} Started with Process ID {}".format(version, proc[0]))
                    context = pythoncom.CreateBindCtx(0)
                    running_coms = pythoncom.GetRunningObjectTable()
                    monikiers = running_coms.EnumRunning()
                    for monikier in monikiers:
                        m = re.search(version[10:]+r"\.\d:"+str(proc[0]), monikier.GetDisplayName(context, monikier))
                        if m:
                            obj = running_coms.GetObject(monikier)
                            self._main.isoutsideDesktop = True
                            # self._main.oDesktop = win32com.client.gencache.EnsureDispatch(
                            #     obj.QueryInterface(pythoncom.IID_IDispatch))
                            self._main.oDesktop = win32com.client.Dispatch(obj.QueryInterface(pythoncom.IID_IDispatch))
                            break
                else:
                    logger.warning("pyaedt is not supported in versions older than 2021.1")
                    oAnsoftApp = win32com.client.Dispatch(version)
                    self._main.oDesktop = oAnsoftApp.GetAppDesktop()
                    self._main.isoutsideDesktop = True
            else:
                logger.debug("Launching AEDT with Module win32com.client")
                oAnsoftApp = win32com.client.Dispatch(version)
                self._main.oDesktop = oAnsoftApp.GetAppDesktop()
                self._main.isoutsideDesktop = True

            self._main.AEDTVersion = version_key
            self._main.oDesktop.RestoreWindow()
            self._main.oMessenger = AEDTMessageManager()
        self._main.pyaedt_initialized = True
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            project_dir = self._main.oDesktop.GetProjectDirectory()
            logging.basicConfig(
                filename=os.path.join(project_dir, "pyaedt.log"),
                level=logging.DEBUG,
                format='%(asctime)s:%(name)s:%(levelname)-8s:%(message)s',
                datefmt='%Y/%m/%d %H.%M.%S')
            self.logger = logging.getLogger(__name__)
        info_msg0 = 'pyaedt v{} started'.format(pyaedtversion)
        info_msg1 = 'Started external COM connection with module {0}'.format(_com)
        info_msg2 = 'Python version {0}'.format(sys.version)
        info_msg3 = 'Exe path: {0}'.format(sys.executable)
        self._main.oMessenger.add_info_message(info_msg0, 'Global')
        self._main.oMessenger.add_info_message(info_msg1, 'Global')
        self._main.oMessenger.add_info_message(info_msg2, 'Global')
        self._main.oMessenger.add_info_message(info_msg3, 'Global')
        if _com == 'pywin32' and (AlwaysNew or NG):
            info_msg5 = 'AlwaysNew or NG option is not available for pywin32 connection only. Install Pythonnet to support it.'
            self._main.oMessenger.add_info_message(info_msg5, 'Global')
        elif _com == 'pythonnet':
            dll_path = os.path.join(base_path,"common","IronPython", "dlls")
            sys.path.append(dll_path)
            info_msg5 = 'Adding IronPython common dlls to sys.path: {0}'.format(dll_path)
            self._main.oMessenger.add_info_message(info_msg5, 'Global')

    @property
    def install_path(self):
        """ """
        version_key = self._main.AEDTVersion
        root = self._version_ids[version_key]
        return os.environ[root]

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        # Write the trace stack to the log file if an exception occurred in the main script
        if ex_type:
            err = self._exception(ex_value, ex_traceback)
        if self.release:
            self.release_desktop(close_projects=self._main.close_on_exit, close_on_exit=self._main.close_on_exit)

    def _exception(self, ex_value, tb_data):
        """Writes the trace stack to the desktop when a python error occurs

        Parameters
        ----------
        ex_value :
            
        tb_data :
            

        Returns
        -------

        """
        try:
            oproject = self._main.oDesktop.GetActiveProject()
            proj_name = oproject.GetName()
            try:
                des_name = oproject.GetActiveDesign().GetName()
                if ";" in des_name:
                    des_name = des_name.split(";")[1]
            except:
                des_name = ''
        except:
            proj_name = ''
            des_name = ''
        tb_trace = traceback.format_tb(tb_data)
        tblist = tb_trace[0].split('\n')
        self._main.oMessenger.add_error_message(str(ex_value), 'Global')
        #self._main.oDesktop.AddMessage(proj_name, des_name, 2, str(ex_value))
        for el in tblist:
            #self._main.oDesktop.AddMessage(proj_name, des_name, 2, el)
            self._main.oMessenger.add_error_message(el, 'Global')

        return str(ex_value)

    def release_desktop(self, close_projects=True, close_on_exit=True):
        """

        Parameters
        ----------
        close_projects :
             (Default value = True)
        close_on_exit :
             (Default value = True)

        Returns
        -------

        """
        release_desktop(close_projects, close_on_exit)

    def force_close_desktop(self):
        """ """
        force_close_desktop()

    def close_desktop(self):
        """ """
        force_close_desktop()

    def enable_autosave(self):
        """ """
        self._main.oDesktop.EnableAutoSave(True)

    def disable_autosave(self):
        """ """
        self._main.oDesktop.EnableAutoSave(False)


def get_version_env_variable(version_id):
    """

    Parameters
    ----------
    version_id :
        

    Returns
    -------

    """
    version_env_var = "ANSYSEM_ROOT"
    values = version_id.split('.')
    version = int(values[0][2:])
    release = int(values[1])
    if version < 20:
        if release < 3:
            version += 1
        else:
            release += 2
    version_env_var += str(version) + str(release)
    return version_env_var


def get_version_key(version_id):
    """

    Parameters
    ----------
    version_id :
        

    Returns
    -------

    """
    values = version_id.split('.')
    version = int(values[0][2:])
    release = int(values[1])
    version_key = str(version) + str(release)
    return version_key
