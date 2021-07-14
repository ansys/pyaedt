"""
This module contains the `Desktop` class.

This module is used to initialize AEDT and Message Manager to manage AEDT.

You can initialize this module before launching an app or 
have the app automatically initialize it to the latest installed AEDT version.
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
    _com = 'ironpython'
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
    """Writes the trace stack to the desktop when a Python error occurs.
    
    The message is added to the AEDT global Message Manager and to the log file (if present).

    Parameters
    ----------
    ex_value : str
        Type of exception.
    tb_data : str
        Traceback information.

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
    """Update the AEDT registry key.
    
    .. note::
       This method is only supported on Windows.
    
    Parameters
    ----------
    key : str
        Registry key.
    value : str
        Value for the registry key. The value includes "" if needed.
    desktop_version : str, optional
        Version of AEDT to use. The default is ``"193"`` 
        to use 2019 R3.
    
    Examples
    --------
    Update the HPC license type for HFSS in the AEDT registry.
    
    >>> update_aedt_registry("HFSS/HPCLicenseType", "12") # doctest: +SKIP
    
    Update the HPC license type for Icepak in the AEDT registry.
    
    >>> update_aedt_registry("Icepak/HPCLicenseType", "8") # doctest: +SKIP
    
    Update the legacy HPC license type for HFSS in the AEDT registry.
    
    >>> update_aedt_registry("HFSS/UseLegacyElectronicsHPC", "0") # doctest: +SKIP
    
    Update the MPI vendor for HFSS in the AEDT registry.
    
    >>> update_aedt_registry("HFSS/MPIVendor", "Intel") # doctest: +SKIP

    """
    if os.name == 'posix':
        import subprocessdotnet as subprocess
    else:
        import subprocess
    desktop_install_dir = os.environ["ANSYSEM_ROOT" + str(desktop_version)]

    with open(os.path.join(desktop_install_dir, "config", "ProductList.txt")) as file:
        product_version = next(file).rstrip()  # get first line

    options = '-set -ProductName {} + product_version -RegistryKey "{}" -RegistryValue "{}"'.format(product_version,
                                                                                                    key, value)
    command = '"{}/UpdateRegistry" {}'.format(desktop_install_dir, options)

    subprocess.call([command])


def release_desktop(close_projects=True, close_desktop=True):
    """Release the AEDT API.

    Parameters
    ----------
    close_projects : bool, optional
        Whether to close the projects opened in the session. The default is ``True``.
    close_desktop : bool, optional
        Whether to close the active AEDT session. The default is ``True``.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.

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
            return True
        except:
            Module.oMessenger.add_info_message("Attributes not present")
            return False

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
                return True
            except:
                return False


def force_close_desktop():
    """Close all AEDT projects and shut down AEDT.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.

    """
    Module = sys.modules['__main__']
    pid = Module.oDesktop.GetProcessID()
    if pid > 0:
        try:
            plist = Module.oDesktop.GetProjectList()
            for el in plist:
                Module.oDesktop.CloseProject(el)
        except:
            logger.warning("No Projects. Closing Desktop Connection")
        try:
            scopeID = 5
            while i <= scopeID:
                Module.COMUtil.ReleaseCOMObjectScope(Module.COMUtil.PInvokeProxyAPI, 0)
                i += 1
        except:
            logger.warning("No COM UTIL. Closing the Desktop....")
        try:
            del Module.pyaedt_initialized
        except:
            pass
        try:
            os.kill(pid, 9)
            del Module.oDesktop
            successfully_closed = True
        except:
            Module.oMessenger.add_error_message("something went wrong in Closing AEDT")
            successfully_closed = False
        finally:
            log = logging.getLogger(__name__)
            handlers = log.handlers[:]
            for handler in handlers:
                handler.close()
                log.removeHandler(handler)
            return successfully_closed



class Desktop:
    """Initialize AEDT based on the inputs provided.
    
    .. note::
       On Windows, this class works without limitations in IronPython and CPython.
       On Linux, this class works only in embedded IronPython in AEDT.

    Parameters
    ----------
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``, in which case the
        active setup or latest installed version is used.
    NG: bool, optional
        Whether to launch AEDT in the non-graphical mode. The default 
        is ``False``, in which case AEDT launches in the graphical mode.
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if 
        another instance of the ``specified_version`` is active on the machine.
        The default is ``True``.
    release_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``True``.
    student_version : bool, optional
        Whether to enable the student version of AEDT. The default is
        ``False``.

    Examples
    --------
    Launch AEDT 2021 R1 in non-graphical mode and initialize HFSS.

    >>> import pyaedt
    >>> desktop = pyaedt.Desktop("2021.1", NG=True)
    pyaedt Info: pyaedt v...
    pyaedt Info: Python version ...
    >>> hfss = pyaedt.Hfss(designname="HFSSDesign1")
    pyaedt Info: Added design 'HFSSDesign1' of type HFSS.

    Launch AEDT 2021 R1 in graphical mode and initialize HFSS.

    >>> desktop = Desktop("2021.1")
    pyaedt Info: pyaedt v...
    pyaedt Info: Python version ...
    >>> hfss = pyaedt.Hfss(designname="HFSSDesign1")
    
    """
            
    @property
    def version_keys(self):
        """Version keys."""

        self._version_keys = []
        self._version_ids = {}
        version_list = list_installed_ansysem()
        for version_env_var in version_list:
            if "ANSYSEMSV_ROOT" in version_env_var:
                current_version_id = version_env_var.replace("ANSYSEMSV_ROOT", '')
                student=True
            else:
                current_version_id = version_env_var.replace("ANSYSEM_ROOT", '')
                student = False
            version = int(current_version_id[0:2])
            release = int(current_version_id[2])
            if version < 20:
                if release < 3:
                    version -= 1
                else:
                    release -= 2
            if student:
                v_key = "20{0}.{1}SV".format(version, release)
                self._version_keys.append(v_key)
                self._version_ids[v_key] = version_env_var
            else:
                v_key = "20{0}.{1}".format(version, release)
                self._version_keys.append(v_key)
                self._version_ids[v_key] = version_env_var

        return self._version_keys

    @property
    def current_version(self):
        """Current version of AEDT."""
        return self.version_keys[0]

    @property
    def current_version_student(self):
        """Current student version of AEDT. """
        for el in self.version_keys:
            if "SV" in el:
                return el
        return None

    def __init__(self, specified_version=None, NG=False, AlwaysNew=True, release_on_exit=True, student_version=False):
        """Initialize desktop."""
        self._main = sys.modules['__main__']
        self._main.close_on_exit = False
        self._main.isoutsideDesktop = False
        self._main.pyaedt_version = pyaedtversion
        self.release = release_on_exit
        self.logfile = None
        module_logger = logging.getLogger(__name__)

        if "oDesktop" in dir(self._main) and self._main.oDesktop is not None:
            self._main.AEDTVersion = self._main.oDesktop.GetVersion()[0:6]
            self._main.oDesktop.RestoreWindow()
            self._main.oMessenger = AEDTMessageManager()
            base_path = self._main.oDesktop.GetExeDir()
            self._main.sDesktopinstallDirectory = base_path
            self.release = False
        else:
            version_student = False
            if specified_version:
                if student_version:
                    specified_version += "SV"
                    version_student = True
                assert specified_version in self.version_keys, \
                    "Specified version {} not known.".format(specified_version)
                version_key = specified_version
            else:
                if student_version and self.current_version_student:
                    version_key = self.current_version_student
                    version_student = True
                else:
                    version_key = self.current_version
                    version_student = False
            base_path = os.getenv(self._version_ids[version_key])
            self._main = sys.modules['__main__']
            self._main.sDesktopinstallDirectory = base_path
            if student_version and version_student:
                version = "Ansoft.ElectronicsDesktop." + version_key[:-2]
            else:
                version = "Ansoft.ElectronicsDesktop." + version_key
            self._main.AEDTVersion = version_key
            self._main.interpreter = _com
            self._main.interpreter_ver = _pythonver
            if "oDesktop" in dir(self._main):
                del self._main.oDesktop
            if _com == 'ironpython':
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
                launch_msg = "Launching AEDT installation {}".format(base_path)
                print(launch_msg)
                print("===================================================================================")
                clr.AddReference("Ansys.Ansoft.CoreCOMScripting")
                AnsoftCOMUtil = __import__("Ansys.Ansoft.CoreCOMScripting")
                self.COMUtil = AnsoftCOMUtil.Ansoft.CoreCOMScripting.Util.COMUtil
                self._main.COMUtil = self.COMUtil
                StandalonePyScriptWrapper = AnsoftCOMUtil.Ansoft.CoreCOMScripting.COM.StandalonePyScriptWrapper

                module_logger.debug("Launching AEDT with Module Pythonnet")
                processID = []
                if IsWindows:
                    username = getpass.getuser()
                    if student_version:
                        process = "ansysedtsv.exe"
                    else:
                        process = "ansysedt.exe"
                    with os.popen('tasklist /FI "IMAGENAME eq {}" /v'.format(process)) as tasks_list:
                        output = tasks_list.readlines()
                    pattern = r'(?i)^(?:{})\s+?(\d+)\s+.+[\s|\\](?:{})\s+'.format(process, username)
                    for l in output:
                        m = re.search(pattern, l)
                        if m:
                            processID.append(m.group(1))
                if student_version and not processID:
                    import subprocess
                    DETACHED_PROCESS = 0x00000008
                    pid = subprocess.Popen([os.path.join(base_path, "ansysedtsv.exe")],
                                           creationflags=DETACHED_PROCESS).pid
                if NG or AlwaysNew or not processID:
                    # Force new object if no non-graphical instance is running or if there is not an already existing process.
                    App = StandalonePyScriptWrapper.CreateObjectNew(NG)
                else:
                    App = StandalonePyScriptWrapper.CreateObject(version)
                processID2 = []
                if IsWindows:
                    module_logger.debug("Info: Using Windows TaskManager to Load processes")
                    username = getpass.getuser()
                    if student_version:
                        process = "ansysedtsv.exe"
                    else:
                        process = "ansysedt.exe"
                    with os.popen('tasklist /FI "IMAGENAME eq {}" /v'.format(process)) as tasks_list:
                        output = tasks_list.readlines()
                    pattern = r'(?i)^(?:{})\s+?(\d+)\s+.+[\s|\\](?:{})\s+'.format(process, username)
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
                    module_logger.debug("Info: {} Started with Process ID {}".format(version, proc[0]))
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
                    module_logger.warning("PyAEDT is not supported in AEDT versions older than 2021.1.")
                    oAnsoftApp = win32com.client.Dispatch(version)
                    self._main.oDesktop = oAnsoftApp.GetAppDesktop()
                    self._main.isoutsideDesktop = True
            else:
                module_logger.debug("Launching AEDT with Module win32com.client")
                oAnsoftApp = win32com.client.Dispatch(version)
                self._main.oDesktop = oAnsoftApp.GetAppDesktop()
                self._main.isoutsideDesktop = True

            self._main.AEDTVersion = version_key
            self._main.oDesktop.RestoreWindow()
            self._main.oMessenger = AEDTMessageManager()
        self._main.pyaedt_initialized = True

        # Set up the log file in the AEDT project directory
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            project_dir = self._main.oDesktop.GetProjectDirectory()
            self.logfile = os.path.join(project_dir, "pyaedt.log")
            logging.basicConfig(
                filename=self.logfile,
                level=logging.DEBUG,
                format='%(asctime)s:%(name)s:%(levelname)-8s:%(message)s',
                datefmt='%Y/%m/%d %H.%M.%S',
                filemode='w')

        info_msg1 = 'pyaedt v{}'.format(pyaedtversion.strip())
        info_msg2 = 'Python version {}'.format(sys.version)
        self._main.oMessenger.add_info_message(info_msg1, 'Global')
        self._main.oMessenger.add_info_message(info_msg2, 'Global')

        info_msg3 = 'Started external COM connection with module {}'.format(_com)
        info_msg4 = 'Exe path: {}'.format(sys.executable)
        logger.info(info_msg3)
        logger.info(info_msg4)

        if _com == 'pywin32' and (AlwaysNew or NG):
            info_msg5 = 'The ``AlwaysNew`` or ``NG`` option is not available for a pywin32 connection only. Install Python.NET to support these options.'
            self._main.oMessenger.add_info_message(info_msg5, 'Global')
        elif _com == 'ironpython':
            dll_path = os.path.join(base_path,"common","IronPython", "dlls")
            sys.path.append(dll_path)
            info_msg5 = 'Adding IronPython common dlls to the sys.path: {0}'.format(dll_path)
            self._main.oMessenger.add_info_message(info_msg5, 'Global')

    @property
    def install_path(self):
        """Installation path for AEDT."""
        version_key = self._main.AEDTVersion
        root = self._version_ids[version_key]
        return os.environ[root]

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        # Write the trace stack to the log file if an exception occurred in the main script.
        if ex_type:
            err = self._exception(ex_value, ex_traceback)
        if self.release:
            self.release_desktop(close_projects=self._main.close_on_exit, close_on_exit=self._main.close_on_exit)

    def _exception(self, ex_value, tb_data):
        """Write the trace stack to the desktop when a Python error occurs.

        Parameters
        ----------
        ex_value : str
            Type of exception.
        tb_data : str
            Traceback information.
            
        Returns
        -------
        str
            Type of exception.

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
        for el in tblist:
            self._main.oMessenger.add_error_message(el, 'Global')

        return str(ex_value)

    def release_desktop(self, close_projects=True, close_on_exit=True):
        """Release AEDT.

        Parameters
        ----------
        close_projects : bool, optional
            Whether to close the projects opened in the session. 
            The default is ``True``.
        close_on_exit : bool, optional
            Whether to close the active AEDT session on exiting AEDT. 
            The default is ``True``.

        Examples
        --------
        >>> import pyaedt
        >>> desktop = pyaedt.Desktop("2021.1")
        pyaedt Info: pyaedt v...
        pyaedt Info: Python version ...
        >>> desktop.release_desktop(close_projects=False, close_on_exit=False) # doctest: +SKIP

        """
        release_desktop(close_projects, close_on_exit)

    def force_close_desktop(self):
        """Close all AEDT projects and shut down AEDT.
    
        Examples
        --------
        >>> import pyaedt
        >>> desktop = pyaedt.Desktop("2021.1")
        pyaedt Info: pyaedt v...
        pyaedt Info: Python version ...
        >>> desktop.force_close_desktop() # doctest: +SKIP

        """
        force_close_desktop()

    def close_desktop(self):
        """Close all AEDT projects and shut down AEDT.
    
        Examples
        --------
        >>> import pyaedt
        >>> desktop = pyaedt.Desktop("2021.1")
        pyaedt Info: pyaedt v...
        pyaedt Info: Python version ...
        >>> desktop.close_desktop() # doctest: +SKIP

        """
        force_close_desktop()

    def enable_autosave(self):
        """Enable auto save option.

        Examples
        --------
        >>> import pyaedt
        >>> desktop = pyaedt.Desktop("2021.1")
        pyaedt Info: pyaedt v...
        pyaedt Info: Python version ...
        >>> desktop.enable_autosave()

        """
        self._main.oDesktop.EnableAutoSave(True)

    def disable_autosave(self):
        """Disable auto save option.

        Examples
        --------
        >>> import pyaedt
        >>> desktop = pyaedt.Desktop("2021.1")
        pyaedt Info: pyaedt v...
        pyaedt Info: Python version ...
        >>> desktop.disable_autosave()

        """
        self._main.oDesktop.EnableAutoSave(False)


def get_version_env_variable(version_id):
    """Retrieve the environment variable for the AEDT version.

    Parameters
    ----------
    version_id : str
        Full AEDT version number, such as "2021.1".

    Returns
    -------
    str
        Environment variable for the version.

    Examples
    --------
    >>> from pyaedt import desktop
    >>> desktop.get_version_env_variable("2021.1")
    'ANSYSEM_ROOT211'

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
