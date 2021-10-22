import sys
import warnings
import tempfile
import os
import subprocess
from pyaedt.generic.general_methods import env_path, generate_unique_name
try:
    import rpyc
    from rpyc.utils.server import ThreadedServer
except ImportError:
    warnings.warn("rpyc is needed to run the service")


class PyaedtService(rpyc.Service):
    """Server Pyaedt rpyc Service.
    """

    def on_connect(self, conn):
        # code that runs when a connection is created
        # (to init the service, if needed)

        self.app = []
        pass

    def on_disconnect(self, conn):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        if self.app:
            try:
                self.app[0].release_desktop()
            except:
                pass
        pass

    def exposed_run_script(self, script, aedt_version="2021.1", ansysem_path=None):
        script_file = os.path.join(tempfile..gettempdir(), generate_unique_name("pyaedt_script")+".py")
        with open(script_file, "w") as f:
            for line in script:
                f.write(line+"\n")
        if os.name == "posix":
            executable = "ansysedt"
        else:
            executable = "ansysedt.exe"

        if env_path(aedt_version) or ansysem_path:
            if not ansysem_path:
                ansysem_path =  env_path(aedt_version)
            command = os.path.join(ansysem_path, executable) + " -RunScriptAndExit " +script_file
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


if __name__ == "__main__":
    port = sys.argv[1]
    print(port)
    safe_attrs = {'__abs__', '__add__', '__and__', '__bool__', '__code__', '__cmp__', '__contains__', '__delitem__',
                  '__delslice__', '__div__', '__divmod__', '__doc__', '__eq__', '__float__', '__floordiv__', '__func__',
                  '__ge__',
                  '__getitem__', '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__', '__idiv__',
                  '__ifloordiv__',
                  '__ilshift__', '__imod__', '__imul__', '__index__', '__int__', '__invert__', '__ior__', '__ipow__',
                  '__irshift__', '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__', '__long__',
                  '__lshift__', '__lt__', '__mod__', '__mul__', '__name__', '__ne__', '__neg__', '__new__',
                  '__nonzero__',
                  '__oct__', '__or__', '__pos__', '__pow__', '__radd__', '__rand__', '__rdiv__', '__rdivmod__',
                  '__repr__',
                  '__rfloordiv__', '__rlshift__', '__rmod__', '__rmul__', '__ror__', '__rpow__', '__rrshift__',
                  '__rshift__', '__rsub__', '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__str__',
                  '__sub__',
                  '__truediv__', '__xor__', 'next', '__length_hint__', '__enter__', '__exit__', '__next__',
                  '__format__'}
    t = ThreadedServer(PyaedtService, hostname="MLNMCFERRO", port=port,
                       protocol_config={'sync_request_timeout': None, 'allow_public_attrs': True, 'allow_setattr': True,
                                        'safe_attrs': safe_attrs,
                                        'allow_delattr': True})
    t.start()
