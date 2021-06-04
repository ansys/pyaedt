"""
Siwave Class
----------------


Description
==========

This class initialize Siwave, MessageManager and manage Siwave Release and Closing.
It can be initialized in standalone way before launching an app or it is automatically initialized by the APP to latest installed AEDT version



================

"""
from __future__ import absolute_import
from .generic.general_methods import aedt_exception_handler, generate_unique_name
import os
import sys
import pkgutil

from .misc import list_installed_ansysem

_pythonver = sys.version_info[0]

if "IronPython" in sys.version or ".NETFramework" in sys.version:
    import clr  # IronPython C:\Program Files\AnsysEM\AnsysEM19.4\Win64\common\IronPython\ipy64.exe
    _com = 'pythonnet'
    import System
elif os.name == 'nt':
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


# if _pythonver == 3:
#     from .MessageManager import AEDTMessageManager
# else:
#     from MessageManager import AEDTMessageManager


class Siwave:
    """====================================
    The core module that initialize Ansys Siwave based on inputs provided:

    Parameters
    ----------

    Returns
    -------

    """
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

    def __init__(self, specified_version=None):
        self._main = sys.modules['__main__']
        print ("Launching Siwave Init")
        if  "oSiwave" in dir(self._main) and self._main.oSiwave is not None:
            self._main.AEDTVersion = self._main.oSiwave.GetVersion()[0:6]
            self._main.oSiwave.RestoreWindow()
            #self._main.oMessenger = AEDTMessageManager()
            specified_version = self.current_version
            assert specified_version in self.version_keys, \
                "Specified version {} not known.".format(specified_version)
            version_key = specified_version
            base_path = os.getenv(self._version_ids[specified_version])
            self._main.sDesktopinstallDirectory = base_path
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
            version = "Siwave.Application." + version_key
            self._main.AEDTVersion = version_key
            self._main.interpreter = _com
            self._main.interpreter_ver = _pythonver
            if "oSiwave" in dir(self._main):
                del self._main.oSiwave

            if _com == 'pythonnet':
                self._main.oSiwave = System.Activator.CreateInstance(System.Type.GetTypeFromProgID(version))

            elif _com == 'pythonnet_v3': #TODO check if possible to use pythonnet. at the moment the tool open AEDt but doesn't return the wrapper of oApp
                print("Launching AEDT with Module win32com")

                self._main.oSiwave=win32com.client.Dispatch("Siwave.Application.2020.2")

            self._main.AEDTVersion = version_key
            self.oSiwave = self._main.oSiwave
            self._main.oSiwave.RestoreWindow()
            #self._main.oMessenger = AEDTMessageManager()
        self._main.siwave_initialized = True
        self._oproject = self.oSiwave.GetActiveProject()
        pass
        # self.logger = logging.getLogger(__name__)
        # if not self.logger.handlers:
        #     project_dir = self._main.oSiwave.GetProjectDirectory()
        #     logging.basicConfig(
        #         filename=os.path.join(project_dir, "pyaedt.log"),
        #         level=logging.DEBUG,
        #         format='%(asctime)s:%(name)s:%(levelname)-8s:%(message)s',
        #         datefmt='%Y/%m/%d %H.%M.%S')
        #     self.logger = logging.getLogger(__name__)

        # info_msg1 = 'Started external COM connection with module {0}'.format(_com)
        # info_msg2 = 'Python version {0}'.format(sys.version)
        # info_msg3 = 'Exe path: {0}'.format(sys.executable)
        # self._main.oMessenger.add_info_message(info_msg1, 'Global')
        # self._main.oMessenger.add_info_messge(info_msg2, 'Global')
        # self._main.oMessenger.add_info_message(info_msg3, 'Global')



    @property
    def project_name(self):
        """ """
        return self._oproject.GetName()


    @property
    def project_path(self):
        """ """
        return os.path.normpath(self.oSiwave.GetProjectDirectory())

    @property
    def project_file(self):
        """ """
        return os.path.join(self.project_path, self.project_name + '.siw')

    @property
    def lock_file(self):
        """ """
        return os.path.join(self.project_path, self.project_name + '.siw.lock')

    @property
    def results_directory(self):
        """ """
        return os.path.join(self.project_path, self.project_name + '.siwresults')


    @property
    def src_dir(self):
        """ """
        return os.path.dirname(os.path.realpath(__file__))

    @property
    def pyaedt_dir(self):
        """ """
        return os.path.realpath(os.path.join(self.src_dir, '..'))


    @property
    def oproject(self):
        """ """
        return self._oproject

    @aedt_exception_handler
    def open_project(self, proj_path=None):
        """

        Parameters
        ----------
        proj_path :
             (Default value = None)

        Returns
        -------

        """

        if os.path.exists(proj_path):
            self.oSiwave.OpenProject(proj_path)
            self._oproject = self.oSiwave.GetActiveProject()


    @aedt_exception_handler
    def save_project(self, projectpath=None, projectName=None):
        """

        Parameters
        ----------
        projectpath :
             (Default value = None)
        projectName :
             (Default value = None)

        Returns
        -------

        """
        if projectName and projectpath:
            self.oproject.ScrSaveProjectAs(os.path.join(projectpath, projectName+".siw"))
        else:
            self.oproject.Save()
        return True


    @aedt_exception_handler
    def quit_application(self):
        """ """

        self._main.oSiwave.Quit()
        return True

