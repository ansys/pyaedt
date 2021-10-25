import os
import random
import subprocess
import tempfile
import threading
import site
import rpyc
from rpyc import ThreadedServer

from pyaedt import generate_unique_name
from pyaedt.generic.general_methods import env_path


class PyaedtServiceWindows(rpyc.Service):
    """Server Pyaedt rpyc Service.
    """

    def on_connect(self, connection):
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.connection = connection
        self.app = []
        pass

    def on_disconnect(self, connection):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        if self.app:
            try:
                self.app[0].release_desktop()
            except:
                pass
        pass

    def exposed_close_connection(self):
        if self.app:
            try:
                self.app[0].release_desktop()
            except:
                pass
        return True

    def exposed_run_script(self, script, aedt_version="2021.1", ansysem_path=None):
        script_file = os.path.join(tempfile.gettempdir(), generate_unique_name("pyaedt_script")+".py")
        with open(script_file, "w") as f:
            for line in script:
                f.write(line+"\n")
        executable = "ansysedt.exe"

        if env_path(aedt_version) or ansysem_path:
            if not ansysem_path:
                ansysem_path = env_path(aedt_version)
            command = os.path.join(ansysem_path, executable) + " -RunScriptAndExit " + script_file
            p = subprocess.Popen(command)
            p.wait()
            print("Command Executed.")

        else:
            print("Ansys EM not found or wrong AEDT Version.")

        pass

    def exposed_edb(self, edbpath=None, cellname=None, isreadonly=False, edbversion="2021.1", use_ppe=False, ):
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
            Version of ``edb_core`` to use. The default is ``"2021.1"``.

        Returns
        -------
        :class:`pyaedt.edb.Edb`
        """
        from pyaedt import Edb
        aedtapp = Edb(edbpath=edbpath, cellname=cellname, isreadonly=isreadonly, edbversion=edbversion,
                      isaedtowned=False, oproject=None, student_version=False, use_ppe=use_ppe)
        self.app.append(aedtapp)
        return aedtapp

    def exposed_hfss(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                     specified_version=None, non_graphical=False):
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
            is``False``, in which case AEDT is launched in the graphical mode.

        Returns
        -------
        :class:`pyaedt.hfss.Hfss`
        """
        if os.name == "posix":
            print("Direct Call of AEDT is not supported on linux. Use run_script.")
            return False
        from pyaedt import Hfss
        aedtapp = Hfss(projectname=projectname, designname=designname, solution_type=solution_type,
                    setup_name=setup_name, specified_version=specified_version, non_graphical=non_graphical,
                    new_desktop_session=True, close_on_exit=True, student_version=False, )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_hfss3dlayout(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                     specified_version=None, non_graphical=False):
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
            is``False``, in which case AEDT is launched in the graphical mode.

        Returns
        -------
        :class:`pyaedt.hfss3dlayout.Hfss3dLayout`
        """
        from pyaedt import Hfss3dLayout
        aedtapp = Hfss3dLayout(projectname=projectname, designname=designname, solution_type=solution_type,
                    setup_name=setup_name, specified_version=specified_version, non_graphical=non_graphical,
                    new_desktop_session=True, close_on_exit=True, student_version=False, )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_maxwell3d(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                          specified_version=None, non_graphical=False):
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
            is``False``, in which case AEDT is launched in the graphical mode.

        Returns
        -------
        :class:`pyaedt.maxwell.Maxwell3d`
        """
        from pyaedt import Maxwell3d

        aedtapp = Maxwell3d(projectname=projectname, designname=designname, solution_type=solution_type,
                         setup_name=setup_name, specified_version=specified_version, non_graphical=non_graphical,
                         new_desktop_session=True, close_on_exit=True, student_version=False, )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_maxwell2d(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                          specified_version=None, non_graphical=False):
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
            is``False``, in which case AEDT is launched in the graphical mode.

        Returns
        -------
        :class:`pyaedt.maxwell.Maxwell32`
        """
        from pyaedt import Maxwell2d

        aedtapp = Maxwell2d(projectname=projectname, designname=designname, solution_type=solution_type,
                         setup_name=setup_name, specified_version=specified_version, non_graphical=non_graphical,
                         new_desktop_session=True, close_on_exit=True, student_version=False, )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_icepak(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                       specified_version=None, non_graphical=False):
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
            is``False``, in which case AEDT is launched in the graphical mode.

        Returns
        -------
        :class:`pyaedt.icepak.Icepak`
        """
        from pyaedt import Icepak

        aedtapp = Icepak(projectname=projectname, designname=designname, solution_type=solution_type,
                      setup_name=setup_name, specified_version=specified_version, non_graphical=non_graphical,
                      new_desktop_session=True, close_on_exit=True, student_version=False, )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_circuit(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                        specified_version=None, non_graphical=False):
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
            is``False``, in which case AEDT is launched in the graphical mode.

        Returns
        -------
        :class:`pyaedt.circuit.Circuit`
        """
        from pyaedt import Circuit

        aedtapp = Circuit(projectname=projectname, designname=designname, solution_type=solution_type,
                       setup_name=setup_name, specified_version=specified_version, non_graphical=non_graphical,
                       new_desktop_session=True, close_on_exit=True, student_version=False, )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_mechanical(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                           specified_version=None, non_graphical=False):
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
            is``False``, in which case AEDT is launched in the graphical mode.

        Returns
        -------
        :class:`pyaedt.mechanical.Mechanical`
        """
        from pyaedt import Mechanical

        aedtapp = Mechanical(projectname=projectname, designname=designname, solution_type=solution_type,
                          setup_name=setup_name, specified_version=specified_version, non_graphical=non_graphical,
                          new_desktop_session=True, close_on_exit=True, student_version=False, )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_q3d(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                    specified_version=None, non_graphical=False):
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
            is``False``, in which case AEDT is launched in the graphical mode.

        Returns
        -------
        :class:`pyaedt.q3d.Q3d`
        """
        from pyaedt import Q3d

        aedtapp = Q3d(projectname=projectname, designname=designname, solution_type=solution_type,
                   setup_name=setup_name, specified_version=specified_version, non_graphical=non_graphical,
                   new_desktop_session=True, close_on_exit=True, student_version=False, )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_q2d(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                    specified_version=None, non_graphical=False):
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
            is``False``, in which case AEDT is launched in the graphical mode.

        Returns
        -------
        :class:`pyaedt.q3d.Q2d`
        """
        from pyaedt import Q2d

        aedtapp = Q2d(projectname=projectname, designname=designname, solution_type=solution_type,
                   setup_name=setup_name, specified_version=specified_version, non_graphical=non_graphical,
                   new_desktop_session=True, close_on_exit=True, student_version=False, )
        self.app.append(aedtapp)
        return aedtapp


class PyaedtServiceLinux(rpyc.Service):
    """Server Pyaedt rpyc Service.
    """

    def on_connect(self, connection):
        self.connection = connection
        self.app = []
        pass

    def on_disconnect(self, connection):
        pass

    def exposed_close_connection(self):
        return True

    def exposed_run_script(self, script, aedt_version="2021.1", ansysem_path=None):
        script_file = os.path.join(tempfile.gettempdir(), generate_unique_name("pyaedt_script")+".py")

        package_paths = site.getsitepackages()
        with open(script_file, "w") as f:
            f.write("import sys\n")
            for pack_path in package_paths:
                f.write("sys.path.append(\"{}\")\n".format(pack_path))
            for line in script:
                f.write(line+"\n")
        executable = "ansysedt"

        if env_path(aedt_version) or ansysem_path:
            if not ansysem_path:
                ansysem_path = env_path(aedt_version)
            command = [os.path.join(ansysem_path, executable), "-RunScriptAndExit", script_file]
            p = subprocess.Popen(command)
            p.wait()
            return "Command Executed."

        else:
            return "Ansys EM not found or wrong AEDT Version."

        return "Command Executed."


class GlobalService(rpyc.Service):
    """Global class to manage rpyc Server of PyAEDT.
    """
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

    def exposed_start_service(self, hostname):
        """Starts a new Pyaedt Service and start listen.

        Returns
        -------
        int
            port number
        """
        port = random.randint(18001, 20000)
        if os.name == "posix":
            t = threading.Thread(target=ThreadedServer(PyaedtServiceLinux, hostname=hostname, port=port,
                                 protocol_config={'sync_request_timeout': None, 'allow_public_attrs': True,
                                                  'allow_setattr': True, 'allow_delattr': True}).start)
            t.start()
        else:
            name = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "misc", "pyaedt_client_windows.py")
            cmd_service = ["python", name, str(port), hostname]
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