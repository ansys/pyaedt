import socket
import os
import random
import tempfile
import threading
import site

import sys
from pyaedt import generate_unique_name
from pyaedt.generic.general_methods import env_path

from pyaedt import is_ironpython

if os.name == "posix" and is_ironpython:
    import subprocessdotnet as subprocess
else:
    import subprocess

if is_ironpython:
    import pyaedt.third_party.ironpython.rpyc_27 as rpyc
    from pyaedt.third_party.ironpython.rpyc_27 import ThreadedServer
else:
    import rpyc
    from rpyc import ThreadedServer

from pyaedt import Edb
from pyaedt import Hfss
from pyaedt import Hfss3dLayout
from pyaedt import Maxwell3d
from pyaedt import Maxwell2d
from pyaedt import Q3d
from pyaedt import Q2d
from pyaedt import Circuit
from pyaedt import Icepak
from pyaedt import Mechanical


def check_port(port):
    """Check for an available port on the machine starting from input port.

     Parameters
    ----------
    port : int
        Ports to search.

    Returns
    -------
    int
        Next Port available.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    check = False
    while not check:
        try:
            s.bind((socket.getfqdn(), port))
            check = True
        except socket.error as e:
            port += 1
            # stop search at port 30000 (range search 18000 30000 is more then enough for rpc)
            if port > 29999:
                return 0
    s.close()
    return port


class PyaedtServiceWindows(rpyc.Service):
    """Server Pyaedt rpyc Service."""

    def on_connect(self, connection):
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.connection = connection
        self.app = []
        self._beta_options = []
        pass

    def on_disconnect(self, connection):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        if self.app:
            if not os.name == "posix":
                if self.app and "release_desktop" in dir(self.app[0]):
                    self.app[0].release_desktop()

        pass

    def exposed_close_connection(self):
        if self.app and "release_desktop" in dir(self.app[0]):
            self.app[0].release_desktop()

    def _beta(self):
        os.environ["ANSYSEM_FEATURE_SF6694_NON_GRAPHICAL_COMMAND_EXECUTION_ENABLE"] = "1"
        os.environ["ANSYSEM_FEATURE_SF159726_SCRIPTOBJECT_ENABLE"] = "1"
        if self._beta_options and not self.app:
            for opt in range(self._beta_options.__len__()):
                os.environ["ANSYSEM_FEATURE_" + self._beta_options[opt] + "_ENABLE"] = "1"

    def exposed_run_script(self, script, aedt_version="2021.2", ansysem_path=None, non_graphical=True):
        """Run script on AEDT in the server.

        Parameters
        ----------
        script : str or list
            It can be the full path of the script file or a list of command to execute on the server.
        aedt_version : str, optional
            Aedt Version to run.
        ansysem_path : str, optional
            Full path to AEDT Installation folder.
        non_graphical : bool, optional
            Set AEDT to run either in graphical or non graphical. Default is non-grahical

        Returns
        -------
        str
        """
        if isinstance(script, list):
            script_file = os.path.join(tempfile.gettempdir(), generate_unique_name("pyaedt_script") + ".py")
            with open(script_file, "w") as f:
                for line in script:
                    f.write(line + "\n")
        elif os.path.exists(script):
            script_file = script
        else:
            return "File wrong or wrong commands."
        executable = "ansysedt.exe"
        if os.name == "posix" and not ansysem_path and not env_path(aedt_version):
            ansysem_path = os.getenv("PYAEDT_SERVER_AEDT_PATH", "")
        if env_path(aedt_version) or ansysem_path:
            if not ansysem_path:
                ansysem_path = env_path(aedt_version)

            ng_feature = " -features=SF159726_SCRIPTOBJECT"
            if self._beta_options:
                for opt in range(self._beta_options.__len__()):
                    if self._beta_options[opt] not in ng_feature:
                        ng_feature += "," + self._beta_options[opt]
            if non_graphical:
                ng_feature += ",SF6694_NON_GRAPHICAL_COMMAND_EXECUTION -ng"
            command = os.path.join(ansysem_path, executable) + ng_feature + " -RunScriptAndExit " + script_file
            p = subprocess.Popen(command)
            p.wait()
            return "Script Executed."

        else:
            return "Ansys EM not found or wrong AEDT Version."

    def exposed_edb(
        self,
        edbpath=None,
        cellname=None,
        isreadonly=False,
        edbversion="2021.2",
        use_ppe=False,
    ):
        """Starts a new Hfss session.

        Parameters
        ----------
        edbpath : str, optional
            Full path to the ``aedb`` folder. The variable can also contain
            the path to a layout to import. Allowed formarts are BRD,
            XML (IPC2581), GDS, and DXF. The default is ``None``.
        cellname : str, optional
            Name of the cell to select. The default is ``None``.
        isreadonly : bool, optional
            Whether to open ``edb_core`` in read-only mode. The default is ``False``.
        edbversion : str, optional
            Version of ``edb_core`` to use. The default is ``"2021.2"``.

        Returns
        -------
        :class:`pyaedt.edb.Edb`
        """
        self._beta()
        aedtapp = Edb(
            edbpath=edbpath,
            cellname=cellname,
            isreadonly=isreadonly,
            edbversion=edbversion,
            isaedtowned=False,
            oproject=None,
            student_version=False,
            use_ppe=use_ppe,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_hfss(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=True,
    ):
        """Starts a new Hfss session.

        Parameters
        ----------
        projectname : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        designname : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup_name : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        specified_version : str, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`pyaedt.hfss.Hfss`
        """
        self._beta()
        aedtapp = Hfss(
            projectname=projectname,
            designname=designname,
            solution_type=solution_type,
            setup_name=setup_name,
            specified_version=specified_version,
            non_graphical=non_graphical,
            new_desktop_session=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_hfss3dlayout(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=True,
    ):
        """Starts a new Hfss3dLayout session.

        Parameters
        ----------
        projectname : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        designname : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup_name : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        specified_version : str, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`pyaedt.hfss3dlayout.Hfss3dLayout`
        """
        self._beta()
        aedtapp = Hfss3dLayout(
            projectname=projectname,
            designname=designname,
            solution_type=solution_type,
            setup_name=setup_name,
            specified_version=specified_version,
            non_graphical=non_graphical,
            new_desktop_session=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_maxwell3d(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=True,
    ):
        """Starts a new Maxwell3d session.

        Parameters
        ----------
        projectname : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        designname : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup_name : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        specified_version : str, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`pyaedt.maxwell.Maxwell3d`
        """
        self._beta()
        aedtapp = Maxwell3d(
            projectname=projectname,
            designname=designname,
            solution_type=solution_type,
            setup_name=setup_name,
            specified_version=specified_version,
            non_graphical=non_graphical,
            new_desktop_session=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_maxwell2d(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=True,
    ):
        """Starts a new Maxwell32 session.

        Parameters
        ----------
        projectname : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        designname : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup_name : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        specified_version : str, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`pyaedt.maxwell.Maxwell32`
        """
        self._beta()
        aedtapp = Maxwell2d(
            projectname=projectname,
            designname=designname,
            solution_type=solution_type,
            setup_name=setup_name,
            specified_version=specified_version,
            non_graphical=non_graphical,
            new_desktop_session=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_icepak(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=True,
    ):
        """Starts a new Icepak session.

        Parameters
        ----------
        projectname : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        designname : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup_name : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        specified_version : str, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`pyaedt.icepak.Icepak`
        """
        self._beta()
        aedtapp = Icepak(
            projectname=projectname,
            designname=designname,
            solution_type=solution_type,
            setup_name=setup_name,
            specified_version=specified_version,
            non_graphical=non_graphical,
            new_desktop_session=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_circuit(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=True,
    ):
        """Starts a new Circuit session.

        Parameters
        ----------
        projectname : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        designname : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup_name : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        specified_version : str, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`pyaedt.circuit.Circuit`
        """
        self._beta()
        aedtapp = Circuit(
            projectname=projectname,
            designname=designname,
            solution_type=solution_type,
            setup_name=setup_name,
            specified_version=specified_version,
            non_graphical=non_graphical,
            new_desktop_session=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_mechanical(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=True,
    ):
        """Starts a new Mechanical session.

        Parameters
        ----------
        projectname : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        designname : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup_name : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        specified_version : str, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`pyaedt.mechanical.Mechanical`
        """
        self._beta()
        aedtapp = Mechanical(
            projectname=projectname,
            designname=designname,
            solution_type=solution_type,
            setup_name=setup_name,
            specified_version=specified_version,
            non_graphical=non_graphical,
            new_desktop_session=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_q3d(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=True,
    ):
        """Starts a new Q3d session.

        Parameters
        ----------
        projectname : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        designname : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup_name : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        specified_version : str, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`pyaedt.q3d.Q3d`
        """
        self._beta()
        aedtapp = Q3d(
            projectname=projectname,
            designname=designname,
            solution_type=solution_type,
            setup_name=setup_name,
            specified_version=specified_version,
            non_graphical=non_graphical,
            new_desktop_session=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_q2d(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=True,
    ):
        """Starts a new Q2d session.

        Parameters
        ----------
        projectname : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        designname : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup_name : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        specified_version : str, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`pyaedt.q3d.Q2d`
        """
        self._beta()
        aedtapp = Q2d(
            projectname=projectname,
            designname=designname,
            solution_type=solution_type,
            setup_name=setup_name,
            specified_version=specified_version,
            non_graphical=non_graphical,
            new_desktop_session=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp


class PyaedtServiceLinux(rpyc.Service):
    """Server Pyaedt rpyc Service."""

    def on_connect(self, connection):
        self.connection = connection
        self.app = []
        self._beta_options = []

    def on_disconnect(self, connection):
        pass

    def exposed_close_connection(self):
        return True

    def exposed_run_script(self, script, ansysem_path=None, non_graphical=True):
        """Run script on AEDT in the server.

        Parameters
        ----------
        script : str or list
            It can be the full path of the script file or a list of command to execute on the server.
        ansysem_path : str, optional
            Full path to AEDT Installation folder.
        non_graphical : bool, optional
            Set AEDT to run either in graphical or non graphical. Default is non-grahical

        Returns
        -------
        str
        """
        if isinstance(script, list):
            script_file = os.path.join(tempfile.gettempdir(), generate_unique_name("pyaedt_script") + ".py")
            package_paths = site.getsitepackages()
            with open(script_file, "w") as f:
                f.write("import sys\n")
                for pack_path in package_paths:
                    f.write('sys.path.append("{}")\n'.format(pack_path))
                for line in script:
                    f.write(line + "\n")
        elif os.path.exists(script):
            script_file = script
        else:
            return "File wrong or wrong commands."
        executable = "ansysedt"
        if not ansysem_path:
            ansysem_path = os.getenv("PYAEDT_SERVER_AEDT_PATH", "")
        if not non_graphical:
            non_graphical = os.getenv("PYAEDT_SERVER_AEDT_NG", "True").lower() in ("true", "1", "t")
        if ansysem_path:
            if non_graphical:
                ng_feature = "-features=SF6694_NON_GRAPHICAL_COMMAND_EXECUTION,SF159726_SCRIPTOBJECT"
                if self._beta_options:
                    for opt in range(self._beta_options.__len__()):
                        if self._beta_options[opt] not in ng_feature:
                            ng_feature += "," + self._beta_options[opt]
                command = [os.path.join(ansysem_path, executable), ng_feature, "-ng", "-RunScriptAndExit", script_file]
            else:
                ng_feature = "-features=SF159726_SCRIPTOBJECT"
                if self._beta_options:
                    for opt in range(self._beta_options.__len__()):
                        if self._beta_options[opt] not in ng_feature:
                            ng_feature += "," + self._beta_options[opt]
                command = [os.path.join(ansysem_path, executable), ng_feature, "-RunScriptAndExit", script_file]
            p = subprocess.Popen(command)
            p.wait()
            return "Script Executed."

        else:
            return "Ansys EM not found or wrong AEDT Version."


class GlobalService(rpyc.Service):
    """Global class to manage rpyc Server of PyAEDT."""

    def on_connect(self, connection):
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.connection = connection
        self._processes = {}
        pass

    def on_disconnect(self, connection):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_start_service(self, hostname, beta_options=None, use_aedt_relative_path=False):
        """Starts a new Pyaedt Service and start listen.

        Returns
        -------
        hostname : str
            Hostname.
        """

        port = check_port(random.randint(18500, 20000))
        if port == 0:
            print("Error. No Available ports.")
            return False
        ansysem_path = ""
        non_graphical = True
        if os.name == "posix":
            ansysem_path = os.getenv("PYAEDT_SERVER_AEDT_PATH", "")
            non_graphical = os.getenv("PYAEDT_SERVER_AEDT_NG", "True").lower() in ("true", "1", "t")
        if is_ironpython and os.name == "posix":
            if ansysem_path:
                executable = "ansysedt"
                pyaedt_path = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", ".."))
                script_file = os.path.normpath(
                    os.path.join(os.path.abspath(os.path.dirname(__file__)), "pyaedt_client_linux.py")
                )
                dest_file = os.path.join(tempfile.gettempdir(), "pyaedt_client_linux_{}.py".format(port))
                print(dest_file)
                with open(dest_file, "w") as f:
                    f.write("port={}\n".format(port))
                    f.write("hostname='{}'\n".format(hostname))
                    f.write("pyaedt_path='{}'\n".format(pyaedt_path))
                    with open(script_file, "r") as f1:
                        lines = f1.readlines()
                        for line in lines:
                            f.write(line)
                if not use_aedt_relative_path:
                    aedt_exe = os.path.join(ansysem_path, executable)
                else:
                    aedt_exe = executable
                if non_graphical:
                    ng_feature = "-features=SF6694_NON_GRAPHICAL_COMMAND_EXECUTION,SF159726_SCRIPTOBJECT"
                    if beta_options:
                        for option in range(beta_options.__len__()):
                            if beta_options[option] not in ng_feature:
                                ng_feature += "," + beta_options[option]

                    command = [
                        aedt_exe,
                        ng_feature,
                        "-ng",
                        "-RunScriptAndExit",
                        dest_file,
                    ]
                else:
                    ng_feature = "-features=SF159726_SCRIPTOBJECT"
                    if beta_options:
                        for option in range(beta_options.__len__()):
                            if beta_options[option] not in ng_feature:
                                ng_feature += "," + beta_options[option]
                    command = [aedt_exe, ng_feature, "-RunScriptAndExit", dest_file]
                print(command)
                subprocess.Popen(command)
                return port
            else:
                return "Error. Ansys EM Path has to be provided"

        elif os.name == "posix":
            t = threading.Thread(
                target=ThreadedServer(
                    PyaedtServiceLinux,
                    hostname=hostname,
                    port=port,
                    protocol_config={
                        "sync_request_timeout": None,
                        "allow_public_attrs": True,
                        "allow_setattr": True,
                        "allow_delattr": True,
                    },
                ).start
            )
            t.start()
        else:
            name = os.path.normpath(
                os.path.join(os.path.abspath(os.path.dirname(__file__)), "pyaedt_client_windows.py")
            )
            cmd_service = [sys.executable, name, str(port), hostname]
            print(" ".join(cmd_service))
            p = subprocess.Popen(" ".join(cmd_service))
            self._processes[port] = p
        print("Service Started on Port {}".format(port))
        return port

    def exposed_stop_service(self, port_number):
        """Stops a given Pyaedt Service on specified port.

        Parameters
        ----------
        port_number : int
            port id on which there is the service to kill.

        Returns
        -------
        bool
        """
        if port_number in list(self._processes.keys()):
            try:
                self._processes[port_number].terminate()
                return True
            except:
                return False

        return True

    def exposed_open(self, filename):
        f = open(filename, "rb")
        return rpyc.restricted(f, ["readlines", "close"], [])

    def exposed_create(self, filename):
        if os.path.exists(filename):
            return "File already exists"
        f = open(filename, "wb")
        return rpyc.restricted(f, ["read", "write", "close"], [])

    def exposed_makedirs(self, remotepath):
        if os.path.exists(remotepath):
            return "Directory Exists!"
        os.makedirs(remotepath)
        return "Directory created!"

    def exposed_listdir(self, remotepath):
        if os.path.exists(remotepath):
            return os.listdir(remotepath)
        return []

    def exposed_path_exists(self, remotepath):
        if os.path.exists(remotepath):
            return True
        return False
