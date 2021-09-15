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
import warnings
import gc
import time
import datetime
from pyaedt.application.MessageManager import AEDTMessageManager
from pyaedt.misc import list_installed_ansysem
from pyaedt import is_ironpython, _pythonver, inside_desktop

from .import log_handler


pathname = os.path.dirname(__file__)
if os.path.exists(os.path.join(pathname, "version.txt")):
    with open(os.path.join(pathname, "version.txt"), "r") as f:
        pyaedtversion = f.readline().strip()
elif os.path.exists(os.path.join(pathname, "..", "version.txt")):
    with open(os.path.join(pathname, "..", "version.txt"), "r") as f:
        pyaedtversion = f.readline().strip()
else:
    pyaedtversion = "X"


if os.name == "nt":
    IsWindows = True
else:
    IsWindows = False
logger = logging.getLogger(__name__)

if is_ironpython:
    import clr  # IronPython C:\Program Files\AnsysEM\AnsysEM19.4\Win64\common\IronPython\ipy64.exe

    _com = "ironpython"
elif IsWindows:
    import pythoncom

    modules = [tup[1] for tup in pkgutil.iter_modules()]
    if "clr" in modules:
        import clr
        import win32com.client

        _com = "pythonnet_v3"
    elif "win32com" in modules:
        import win32com.client

        _com = "pywin32"
    else:
        raise Exception("Error. No win32com.client or Pythonnet modules found. Please install them.")


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
    desktop = sys.modules["__main__"].oDesktop
    try:
        oproject = desktop.GetActiveProject()
        project_name = oproject.GetName()
        try:
            design_name = oproject.GetActiveDesign().GetName()
            if ";" in design_name:
                design_name = design_name.split(";")[1]
        except:
            design_name = ""
    except:
        project_name = ""
        design_name = ""
    tb_trace = traceback.format_tb(tb_data)
    tblist = tb_trace[0].split("\n")
    desktop.AddMessage(project_name, design_name, 2, str(ex_value))
    for el in tblist:
        desktop.AddMessage(project_name, design_name, 2, el)


def update_aedt_registry(key, value, desktop_version="211"):
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
        Version of AEDT to use. The default is ``"211"``
        to use 2021 R1.

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
    if os.name == "posix":
        import subprocessdotnet as subprocess
    else:
        import subprocess
    desktop_install_dir = os.environ["ANSYSEM_ROOT" + str(desktop_version)]

    with open(os.path.join(desktop_install_dir, "config", "ProductList.txt")) as file:
        product_version = next(file).rstrip()  # get first line

    options = '-set -ProductName {} + product_version -RegistryKey "{}" -RegistryValue "{}"'.format(
        product_version, key, value
    )
    command = '"{}/UpdateRegistry" {}'.format(desktop_install_dir, options)

    subprocess.call([command])


def _delete_objects():
    module = sys.modules["__main__"]
    if "COMUtil" in dir(module):
        del module.COMUtil
    if "Hfss" in dir(module):
        del module.Hfss
    if "Edb" in dir(module):
        del module.Edb
    if "Q3d" in dir(module):
        del module.Q3d
    if "Q2d" in dir(module):
        del module.Q2d
    if "Maxwell3d" in dir(module):
        del module.Maxwell3d
    if "Maxwell2d" in dir(module):
        del module.Maxwell2d
    if "Icepak" in dir(module):
        del module.Icepak
    if "Mechanical" in dir(module):
        del module.Mechanical
    if "Emit" in dir(module):
        del module.Emit
    if "Circuit" in dir(module):
        del module.Circuit
    if "Simplorer" in dir(module):
        del module.Simplorer
    if "Hfss3dLayout" in dir(module):
        del module.Hfss3dLayout
    if "oMessenger" in dir(module):
        del module.oMessenger
    if "oDesktop" in dir(module):
        del module.oDesktop
    if "pyaedt_initialized" in dir(module):
        del module.pyaedt_initialized
    gc.collect()


def release_desktop(close_projects=True, close_desktop=True):
    """Release the AEDT API.

    Parameters
    ----------
    close_projects : bool, optional
        Whether to close the AEDT projects open in the session. The default is ``True``.
    close_desktop : bool, optional
        Whether to close the active AEDT session. The default is ``True``.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.

    """

    Module = sys.modules["__main__"]
    if "oDesktop" not in dir(Module):
        _delete_objects()
        return False
    else:
        desktop = Module.oDesktop
        if close_projects:
            projects = desktop.GetProjectList()
            for project in projects:
                desktop.CloseProject(project)
        pid = Module.oDesktop.GetProcessID()
        if not (is_ironpython and inside_desktop):
            i = 0
            scopeID = 5
            while i <= scopeID:
                Module.COMUtil.ReleaseCOMObjectScope(Module.COMUtil.PInvokeProxyAPI, i)
                i += 1
            _delete_objects()

        if close_desktop:
            try:
                os.kill(pid, 9)
                _delete_objects()
                return True
            except:
                warnings.warn("Something went wrong in Closing AEDT")
                return False
    return True


def force_close_desktop():
    """Forcibly close all AEDT projects and shut down AEDT.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.

    """
    Module = sys.modules["__main__"]
    pid = Module.oDesktop.GetProcessID()
    if pid > 0:
        try:
            projects = Module.oDesktop.GetProjectList()
            for project in projects:
                Module.oDesktop.CloseProject(project)
        except:
            logger.warning("No Projects. Closing Desktop Connection")
        try:
            i = 0
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
            Module.oMessenger.add_error_message("Something went wrong in Closing AEDT.")
            successfully_closed = False
        finally:
            log = logging.getLogger(__name__)
            handlers = log.handlers[:]
            for handler in handlers:
                handler.close()
                log.removeHandler(handler)
            return successfully_closed


class Desktop:
    """Initializes AEDT based on the inputs provided.

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
        is ``False``, in which case AEDT is launched in the graphical mode.
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the machine.
        The default is ``True``.
    release_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``True``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is
        ``False``.

    Examples
    --------
    Launch AEDT 2021 R1 in non-graphical mode and initialize HFSS.

    >>> import pyaedt
    >>> desktop = pyaedt.Desktop("2021.1", NG=True)
    pyaedt Info: pyaedt v...
    pyaedt Info: Python version ...
    >>> hfss = pyaedt.Hfss(designname="HFSSDesign1")
    pyaedt Info: Project...
    pyaedt Info: Added design 'HFSSDesign1' of type HFSS.

    Launch AEDT 2021 R1 in graphical mode and initialize HFSS.

    >>> desktop = Desktop("2021.1")
    pyaedt Info: pyaedt v...
    pyaedt Info: Python version ...
    >>> hfss = pyaedt.Hfss(designname="HFSSDesign1")
    pyaedt Info: No project is defined. Project...
    """

    @property
    def version_keys(self):
        """Version keys for AEDT."""

        self._version_keys = []
        self._version_ids = {}
        version_list = list_installed_ansysem()
        for version_env_var in version_list:
            if "ANSYSEMSV_ROOT" in version_env_var:
                current_version_id = version_env_var.replace("ANSYSEMSV_ROOT", "")
                student = True
            else:
                current_version_id = version_env_var.replace("ANSYSEM_ROOT", "")
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
        """Current student version of AEDT."""
        for version_key in self.version_keys:
            if "SV" in version_key:
                return version_key
        return None

    def _init_desktop(self):
        self._main.AEDTVersion = self._main.oDesktop.GetVersion()[0:6]
        self._main.oDesktop.RestoreWindow()
        self._main.oMessenger = AEDTMessageManager()
        self._main.sDesktopinstallDirectory = self._main.oDesktop.GetExeDir()
        self._main.pyaedt_initialized = True

    def _set_version(self, specified_version, student_version):
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
        if student_version and version_student:
            version = "Ansoft.ElectronicsDesktop." + version_key[:-2]
        else:
            version = "Ansoft.ElectronicsDesktop." + version_key
        self._main.sDesktopinstallDirectory = os.getenv(self._version_ids[version_key])
        self._main.AEDTVersion = version_key
        return version_student, version_key, version

    def _init_ironpython(self, non_graphical, new_aedt_session, version):
        base_path = self._main.sDesktopinstallDirectory
        sys.path.append(base_path)
        sys.path.append(os.path.join(base_path, 'PythonFiles', 'DesktopPlugin'))
        clr.AddReference("Ansys.Ansoft.CoreCOMScripting")
        AnsoftCOMUtil = __import__("Ansys.Ansoft.CoreCOMScripting")
        self.COMUtil = AnsoftCOMUtil.Ansoft.CoreCOMScripting.Util.COMUtil
        self._main.COMUtil = self.COMUtil
        StandalonePyScriptWrapper = AnsoftCOMUtil.Ansoft.CoreCOMScripting.COM.StandalonePyScriptWrapper
        if non_graphical or new_aedt_session:
            # forcing new thread to start in non-graphical
            oAnsoftApp = StandalonePyScriptWrapper.CreateObjectNew(non_graphical)
        else:
            oAnsoftApp = StandalonePyScriptWrapper.CreateObject(version)
        if non_graphical:
            os.environ['PYAEDT_DESKTOP_LOGS'] = 'False'
        self._main.oDesktop = oAnsoftApp.GetAppDesktop()
        self._main.isoutsideDesktop = True
        return True

    def _get_tasks_list_windows(self, student_version):
        processID2 = []
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
        return processID2

    def _run_student(self):
        import subprocess
        DETACHED_PROCESS = 0x00000008
        pid = subprocess.Popen([os.path.join(self._main.sDesktopinstallDirectory, "ansysedtsv.exe")],
                               creationflags=DETACHED_PROCESS).pid
        time.sleep(5)

    def _dispatch_win32(self,version):
        o_ansoft_app = win32com.client.Dispatch(version)
        self._main.oDesktop = o_ansoft_app.GetAppDesktop()
        self._main.isoutsideDesktop = True

    def _init_cpython(self, non_graphical, new_aedt_session, version, student_version, version_key):
        base_path = self._main.sDesktopinstallDirectory
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
        print("Launching AEDT with module Pythonnet.")
        processID = []
        if IsWindows:
           processID = self._get_tasks_list_windows(student_version)
        if student_version and not processID:
            self._run_student()
        elif non_graphical or new_aedt_session or not processID:
            # Force new object if no non-graphical instance is running or if there is not an already existing process.
            StandalonePyScriptWrapper.CreateObjectNew(non_graphical)
        else:
            StandalonePyScriptWrapper.CreateObject(version)
        if non_graphical:
            os.environ['PYAEDT_DESKTOP_LOGS'] = 'False'
        processID2 = []
        if IsWindows:
            processID2 = self._get_tasks_list_windows(student_version)
        proc = [i for i in processID2 if i not in processID]
        if not proc:
            proc = processID2
        if len(processID2) > 1:
            if non_graphical:
                self._main.close_on_exit = False
            else:
                self._main.close_on_exit = False
                self._dispatch_win32(version)
        elif version_key >= "2021.1":
            self._main.close_on_exit = True
            if student_version:
                print("Info: {} Student version started with process ID {}.".format(version, proc[0]))
            else:
                print("Info: {} Started with process ID {}.".format(version, proc[0]))
            context = pythoncom.CreateBindCtx(0)
            running_coms = pythoncom.GetRunningObjectTable()
            monikiers = running_coms.EnumRunning()
            for monikier in monikiers:
                m = re.search(version[10:] + r"\.\d:" + str(proc[0]), monikier.GetDisplayName(context, monikier))
                if m:
                    obj = running_coms.GetObject(monikier)
                    self._main.isoutsideDesktop = True
                    self._main.oDesktop = win32com.client.Dispatch(obj.QueryInterface(pythoncom.IID_IDispatch))
                    break
        else:
            warnings.warn(
                "PyAEDT is not supported in AEDT versions older than 2021.1. Trying to launch it with PyWin32.")
            self._dispatch_win32(version)

    def _init_logger(self):
        # Set up the log file in the AEDT project directory
        self.logger = logging.getLogger(__name__)
        self._global_log.addHandler(log_handler._LogHandler(self._main.oMessenger, 'Global', logging.DEBUG))
        if not self.logger.handlers:
            if "oDesktop" in dir(self._main):
                project_dir = self._main.oDesktop.GetProjectDirectory()
            else:
                if os.name == "posix":
                    project_dir = os.environ["TMPDIR"]
                else:
                    project_dir = os.environ["TEMP"]
            self.logfile = os.path.join(project_dir,
                                        "pyaedt{}.log".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
            logging.basicConfig(filename=self.logfile, format='%(asctime)s:%(name)s:%(levelname)-8s:%(message)s',
                                level=logging.DEBUG, datefmt='%Y/%m/%d %H.%M.%S', filemode='w')
        return True

    def __init__(self, specified_version=None, NG=False, AlwaysNew=True, release_on_exit=True, student_version=False):
        """Initialize desktop."""
        self._main = sys.modules["__main__"]
        self._main.interpreter = _com
        self._main.close_on_exit = False
        self._main.isoutsideDesktop = False
        self._main.pyaedt_version = pyaedtversion
        self._main.interpreter_ver = _pythonver
        self.release = release_on_exit
        self.logfile = None
        self._global_log = logging.getLogger("global")
        self._global_log.setLevel(logging.DEBUG)
        self._project_log = logging.getLogger(self._main.oDesktop.GetProjectDirectory())
        self._project_log.setLevel(logging.DEBUG)
        self._design_log = logging.getLogger(self._main.oDesktop.GetActiveProject().GetActiveDesign().GetName())
        self._design_log.setLevel(logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        if "oDesktop" in dir(self._main) and self._main.oDesktop is not None:
            self.release = False
        else:
            if "oDesktop" in dir(self._main):
                del self._main.oDesktop
            version_student, version_key, version = self._set_version(specified_version, student_version)
            if _com == 'ironpython':
                print("Launching PyAEDT outside Electronics Desktop with IronPython")
                self._init_ironpython(NG, AlwaysNew, version)
            elif _com == 'pythonnet_v3':
                print("Launching PyAEDT outside Electronics Desktop with CPython and Pythonnet")
                self._init_cpython(NG, AlwaysNew, version, student_version, version_key)
            else:
                self.add_info_message("Launching PyAEDT outside AEDT with CPython and PyWin32.")
                oAnsoftApp = win32com.client.Dispatch(version)
                self._main.oDesktop = oAnsoftApp.GetAppDesktop()
                self._main.isoutsideDesktop = True
            self._main.AEDTVersion = version_key
        self._init_logger()
        self._init_desktop()
        self._main.oMessenger.add_info_message("pyaedt v{}".format(self._main.pyaedt_version))
        self._main.oMessenger.add_info_message("Python version {}".format(sys.version))

    @property
    def messenger(self):
        """Messenger manager for AEDT Log."""
        return self.messenger

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
            Type of the exception.
        tb_data : str
            Traceback data.

        Returns
        -------
        str
            Type of the exception.

        """
        try:
            oproject = self._main.oDesktop.GetActiveProject()
            try:
                design_name = oproject.GetActiveDesign().GetName()
                if ";" in design_name:
                    design_name = design_name.split(";")[1]
            except:
                design_name = ""
        except:
            design_name = ""
        tb_trace = traceback.format_tb(tb_data)
        tblist = tb_trace[0].split("\n")
        self._main.oMessenger.add_error_message(str(ex_value), "Global")
        for el in tblist:
            self._main.oMessenger.add_error_message(el, "Global")

        return str(ex_value)

    def release_desktop(self, close_projects=True, close_on_exit=True):
        """Release AEDT.

        Parameters
        ----------
        close_projects : bool, optional
            Whether to close the AEDT projects opened in the session.
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
        props = [a for a in dir(self) if not a.startswith("__")]
        for a in props:
            self.__dict__.pop(a, None)
        gc.collect()

    def force_close_desktop(self):
        """Forcibly close all AEDT projects and shut down AEDT.

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
        """Enable the auto save option.

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
        """Disable the auto save option.

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
        Full AEDT version number, such as ``"2021.1"``.

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
    values = version_id.split(".")
    version = int(values[0][2:])
    release = int(values[1])
    if version < 20:
        if release < 3:
            version += 1
        else:
            release += 2
    version_env_var += str(version) + str(release)
    return version_env_var
