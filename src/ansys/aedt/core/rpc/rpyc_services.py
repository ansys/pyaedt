import logging
import os
import shutil
import signal
import socket
import subprocess  # nosec
import sys
import tempfile
import time
from typing import List

import rpyc

from ansys.aedt.core import Circuit
from ansys.aedt.core import Edb
from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Icepak
from ansys.aedt.core import Maxwell2d
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core import Mechanical
from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from ansys.aedt.core import is_windows
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import env_path
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.aedt_versions import aedt_versions
from ansys.aedt.core.internal.filesystem import is_safe_path

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)


class FileManagement(object):
    """Class to manage file transfer."""

    def __init__(self, client):
        self.client = client

    def upload(self, localpath, remotepath, overwrite=False):
        """Upload a file or a directory to the given remote path.

        Parameters
        ----------
        localpath : str
            Path to the local file or directory.
        remotepath : str
            Remote path.
        overwrite : bool, optional
            Either if overwrite the local file or not.
        """
        if os.path.isdir(localpath):
            self._upload_dir(localpath, remotepath)
        elif os.path.isfile(localpath):
            self._upload_file(localpath, remotepath)

    def download_folder(self, remotepath, localpath, overwrite=True):
        """Download a directory from a given remote path to the local path.

        Parameters
        ----------
        remotepath : str
            Remote path.
        localpath : str
            Path to the local file or directory.
        overwrite : bool, optional
            Either if overwrite the local file or not.
        """
        self._download_dir(remotepath, localpath, overwrite=True)

    def download_file(self, remotepath, localpath, overwrite=True):
        """Download a file from a given remote path to the local path.

        Parameters
        ----------
        remotepath : str
            Remote path.
        localpath : str
            Path to the local file or directory.
        overwrite : bool, optional
            Either if overwrite the local file or not.
        """
        self._download_file(remotepath, localpath, overwrite=overwrite)

    def _upload_file(self, local_file, remote_file, overwrite=False):
        if self.client.root.pathexists(remote_file):
            if overwrite:
                logger.warning("File already exists on server. Overwriting it.")
            else:
                logger.error("File already exists on the server. Skipping it")
                return False
        new_file = self.client.root.create(remote_file)
        local = open(local_file, "rb")
        shutil.copyfileobj(local, new_file)
        new_file.close()
        logger.info("File %s uploaded to %s", local_file, remote_file)

    def _upload_dir(self, localpath, remotepath, overwrite=False):
        if self.client.root.pathexists(remotepath):
            logger.warning("Folder already exists on the server.")
        self.client.root.makedirs(remotepath)
        i = 0
        for fn in os.listdir(localpath):
            lfn = os.path.join(localpath, fn)
            rfn = remotepath + "/" + fn
            if os.path.isdir(rfn):
                self._upload_dir(lfn, rfn, overwrite=overwrite)
            else:
                self._upload_file(lfn, rfn, overwrite=overwrite)
            i += 1
        logger.info("Directory %s uploaded. %s files copied", localpath, i)

    def _download_file(self, remote_file, local_file, overwrite=True):
        if self.client.root.pathexists(local_file):
            if overwrite:
                logger.warning("File already exists on the client. Overwriting it.")
            else:
                logger.warning("File already exists on the client, skipping it.")
                return
        remote = self.client.root.open(remote_file)
        new_file = open(local_file, "wb")
        shutil.copyfileobj(remote, new_file)
        logger.info("File %s downloaded to %s", remote_file, local_file)

    def _download_dir(self, remotepath, localpath, overwrite=True):
        if os.path.exists(localpath):
            logger.warning("Folder already exists on the local machine.")
        if not os.path.isdir(localpath):
            os.makedirs(localpath)
        i = 0
        for fn in self.client.root.listdir(remotepath):
            lfn = os.path.join(localpath, fn)
            rfn = remotepath + "/" + fn
            if self.client.root.isdir(rfn):
                self._download_dir(rfn, lfn, overwrite=overwrite)
            else:
                self._download_file(rfn, lfn, overwrite=overwrite)
            i += 1
        logger.info("Directory %s downloaded. %s files copied", localpath, i)

    def open_file(self, remote_file, open_options="r", encoding=None):
        return self.client.root.open(remote_file, open_options=open_options, encoding=encoding)

    def create_file(self, remote_file, create_options="w", encoding=None, override=True):
        return self.client.root.create(remote_file, open_options=create_options, encoding=encoding, override=override)

    def makedirs(self, remotepath):
        if self.client.root.pathexists(remotepath):
            return "Directory Exists!"
        self.client.root.makedirs(remotepath)
        return "Directory created."

    def walk(self, remotepath):
        if self.client.root.pathexists(remotepath):
            return self.client.root.walk(remotepath)

    def listdir(self, remotepath):
        if self.client.root.pathexists(remotepath):
            return self.client.root.listdir(remotepath)
        return []

    def pathexists(self, remotepath):
        if self.client.root.pathexists(remotepath):
            return True
        return False

    def unlink(self, remotepath):
        if self.client.root.unlink(remotepath):
            return True
        return False

    def normpath(self, remotepath):
        return self.client.root.normpath(remotepath)

    def isdir(self, remotepath):
        return self.client.root.isdir(remotepath)

    def temp_dir(self):
        return self.client.root.temp_dir()


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
            s.bind(("127.0.0.1", port))
            check = True
        except socket.error:
            port += 1
            # stop search at port 30000 (range search 18000 30000 is more then enough for rpc)
            if port > 29999:
                return 0
    s.close()
    return port


class PyaedtServiceWindows(rpyc.Service):
    """Server Pyaedt rpyc Service."""

    def on_connect(self, connection):
        """Run when a connection is created.

        Parameters
        ----------
        connection : :class:`rpyc.core.protocol.Connection`
            The Connection object representing the connection that was created.

        Returns
        -------
        None
        """
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.connection = connection
        self.app = []
        self._beta_options = []
        pass

    def on_disconnect(self, connection):
        """Run after the connection was closed.

        Returns
        -------
        None
        """
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        if self.app:
            if not is_linux:
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

        .. warning::

            Do not execute this function with untrusted function argument, environment
            variables or pyaedt global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

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
            return "Wrong file or wrong commands."
        if not is_safe_path(script_file):
            return f"Script file {script_file} not safe."
        executable = "ansysedt.exe"
        if is_linux and not ansysem_path and not env_path(aedt_version):
            ansysem_path = os.getenv("PYAEDT_SERVER_AEDT_PATH", "")
        if env_path(aedt_version) or ansysem_path:
            if not ansysem_path:
                ansysem_path = env_path(aedt_version)
            exe_path = os.path.join(ansysem_path, executable)
            if not is_safe_path(exe_path):
                return "Ansys EM path not safe."
            command = [exe_path]
            if non_graphical:
                command.append("-ng")
            ng_feature = "-features=SF159726_SCRIPTOBJECT"
            if self._beta_options:
                for opt in range(self._beta_options.__len__()):
                    if self._beta_options[opt] not in ng_feature:
                        ng_feature += "," + self._beta_options[opt]
            if non_graphical:
                ng_feature += ",SF6694_NON_GRAPHICAL_COMMAND_EXECUTION"
            command.append(ng_feature)
            command = [exe_path, ng_feature, "-RunScriptAndExit", script_file]
            try:
                subprocess.run(command, check=True)  # nosec
            except subprocess.CalledProcessError as e:
                msg = f"Command failed with error: {e}"
                logger.error(msg)
                return msg
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
        """Start a new Hfss session.

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
        :class:`ansys.aedt.core.edb.Edb`
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
        project=None,
        design=None,
        solution_type=None,
        setup=None,
        version=None,
        non_graphical=True,
    ):
        """Start a new Hfss session.

        Parameters
        ----------
        project : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        design : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        version : str, int, float, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`ansys.aedt.core.hfss.Hfss`
        """
        self._beta()
        aedtapp = Hfss(
            project=project,
            design=design,
            solution_type=solution_type,
            setup=setup,
            version=version,
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_hfss3dlayout(
        self,
        project=None,
        design=None,
        solution_type=None,
        setup=None,
        version=None,
        non_graphical=True,
    ):
        """Start a new Hfss3dLayout session.

        Parameters
        ----------
        project : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        design : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        version : str, int, float, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`ansys.aedt.core.hfss3dlayout.Hfss3dLayout`
        """
        self._beta()
        aedtapp = Hfss3dLayout(
            project=project,
            design=design,
            solution_type=solution_type,
            setup=setup,
            version=version,
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_maxwell3d(
        self,
        project=None,
        design=None,
        solution_type=None,
        setup=None,
        version=None,
        non_graphical=True,
    ):
        """Start a new Maxwell3d session.

        Parameters
        ----------
        project : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        design : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        version : str, int, float, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`ansys.aedt.core.maxwell.Maxwell3d`
        """
        self._beta()
        aedtapp = Maxwell3d(
            project=project,
            design=design,
            solution_type=solution_type,
            setup=setup,
            version=version,
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_maxwell2d(
        self,
        project=None,
        design=None,
        solution_type=None,
        setup=None,
        version=None,
        non_graphical=True,
    ):
        """Start a new Maxwell32 session.

        Parameters
        ----------
        project : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        design : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        version : str, int, float, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`ansys.aedt.core.maxwell.Maxwell32`
        """
        self._beta()
        aedtapp = Maxwell2d(
            project=project,
            design=design,
            solution_type=solution_type,
            setup=setup,
            version=version,
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_icepak(
        self,
        project=None,
        design=None,
        solution_type=None,
        setup=None,
        version=None,
        non_graphical=True,
    ):
        """Start a new Icepak session.

        Parameters
        ----------
        project : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        design : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        version : str, int, float, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`ansys.aedt.core.icepak.Icepak`
        """
        self._beta()
        aedtapp = Icepak(
            project=project,
            design=design,
            solution_type=solution_type,
            setup=setup,
            version=version,
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_circuit(
        self,
        project=None,
        design=None,
        solution_type=None,
        setup=None,
        version=None,
        non_graphical=True,
    ):
        """Start a new Circuit session.

        Parameters
        ----------
        project : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        design : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        version : str, int, float, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`ansys.aedt.core.circuit.Circuit`
        """
        self._beta()
        aedtapp = Circuit(
            project=project,
            design=design,
            solution_type=solution_type,
            setup=setup,
            version=version,
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_mechanical(
        self,
        project=None,
        design=None,
        solution_type=None,
        setup=None,
        version=None,
        non_graphical=True,
    ):
        """Start a new Mechanical session.

        Parameters
        ----------
        project : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        design : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        version : str, int, float, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`ansys.aedt.core.mechanical.Mechanical`
        """
        self._beta()
        aedtapp = Mechanical(
            project=project,
            design=design,
            solution_type=solution_type,
            setup=setup,
            version=version,
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_q3d(
        self,
        project=None,
        design=None,
        solution_type=None,
        setup=None,
        version=None,
        non_graphical=True,
    ):
        """Start a new Q3d session.

        Parameters
        ----------
        project : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        design : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        version : str, int, float, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`ansys.aedt.core.q3d.Q3d`
        """
        self._beta()
        aedtapp = Q3d(
            project=project,
            design=design,
            solution_type=solution_type,
            setup=setup,
            version=version,
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp

    def exposed_q2d(
        self,
        project=None,
        design=None,
        solution_type=None,
        setup=None,
        version=None,
        non_graphical=True,
    ):
        """Start a new Q2d session.

        Parameters
        ----------
        project : str, optional
            Name of the project to select or the full path to the project
            or AEDTZ archive to open.  The default is ``None``, in which
            case an attempt is made to get an active project. If no
            projects are present, an empty project is created.
        design : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``None``, in which case the default type is applied.
        setup : str, optional
            Name of the setup to use as the nominal. The default is
            ``None``, in which case the active setup is used or
            nothing is used.
        version : str, int, float, optional
            Version of AEDT to use. The default is ``None``, in which case
            the active version or latest installed version is used.
        non_graphical : bool, optional
            Whether to launch AEDT in the non-graphical mode. The default
            is``True``, in which case AEDT is launched in the non graphical mode.

        Returns
        -------
        :class:`ansys.aedt.core.q3d.Q2d`
        """
        self._beta()
        aedtapp = Q2d(
            project=project,
            design=design,
            solution_type=solution_type,
            setup=setup,
            version=version,
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=False,
        )
        self.app.append(aedtapp)
        return aedtapp


class GlobalService(rpyc.Service):
    """Global class to manage rpyc Server of PyAEDT."""

    def on_connect(self, connection):
        """Initialize the service when the connection is created."""
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.connection = connection
        pass

    def on_disconnect(self, connection):
        """Finalize the service when the connection is closed."""
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        if is_windows:
            sys.stdout = sys.__stdout__

    @staticmethod
    def exposed_stop():
        from ansys.aedt.core.generic.settings import settings

        settings.remote_rpc_session = None

        pid = os.getpid()
        os.kill(pid, signal.SIGTERM)

    def exposed_redirect(self, stdout):
        sys.stdout = stdout

    def exposed_restore(self):
        sys.stdout = sys.__stdout__

    @staticmethod
    def aedt_grpc(
        port=None, beta_options: List[str] = None, use_aedt_relative_path=False, non_graphical=True, check_interval=2
    ):
        """Start a new AEDT session on a specified gRPC port.

        .. warning::

            Do not execute this function with untrusted function argument, environment
            variables or pyaedt global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

        Returns
        -------
        port : int
            gRPC port on which the AEDT session has started.
        """
        from ansys.aedt.core.generic.general_methods import grpc_active_sessions

        sessions = grpc_active_sessions()
        if not port:
            import secrets

            secure_random = secrets.SystemRandom()
            port = check_port(secure_random.randint(18500, 20000))
        if port == 0:
            print("Error. No ports are available.")
            return False
        elif port in sessions:
            print(f"AEDT Session already opened on port {port}.")
            return True

        ansysem_path = os.getenv("PYAEDT_SERVER_AEDT_PATH", "")
        if is_linux:
            executable = "ansysedt"
        else:
            executable = "ansysedt.exe"
        if ansysem_path and not use_aedt_relative_path:
            aedt_exe = os.path.join(ansysem_path, executable)
            if not is_safe_path(aedt_exe):
                logger.warning("Ansys EM path not safe.")
                return False
        else:
            aedt_exe = executable
        if non_graphical:
            ng_feature = "-features=SF6694_NON_GRAPHICAL_COMMAND_EXECUTION,SF159726_SCRIPTOBJECT"
        else:
            ng_feature = "-features=SF159726_SCRIPTOBJECT"
        if beta_options:
            for option in beta_options:
                if option not in ng_feature:
                    ng_feature += f",{option}"
        command = [aedt_exe, "-grpcsrv", str(port), ng_feature]
        if non_graphical:
            command.append("-ng")

        process = subprocess.Popen(command)  # nosec
        timeout = 60
        while timeout > 0:
            with socket.socket() as s:
                try:
                    s.connect(("127.0.0.1", port))
                    logger.info(f"Service accessible on port {port}")
                    return port
                except socket.error:
                    logger.debug(f"Service not available yet, new try in {check_interval}s.")
                    timeout -= 2
                    time.sleep(check_interval)

        process.terminate()
        logger.error(f"Service did not start within the timeout of {timeout} seconds.")
        return False

    @property
    def aedt_port(self):
        """Aedt active port.

        Returns
        -------
        int
        """
        from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

        if _desktop_sessions:
            return list(_desktop_sessions.values())[0].port
        return 0

    @property
    def aedt_version(self):
        """Aedt Version.

        Returns
        -------
        str
        """
        from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

        if _desktop_sessions:
            return list(_desktop_sessions.values())[0].aedt_version_id
        return ""

    @property
    def student_version(self):
        """Student version flag.

        Returns
        -------
        bool
        """
        from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

        if _desktop_sessions:
            return list(_desktop_sessions.values())[0].student_version
        return False

    @property
    def server_name(self):
        """Machine name.

        Returns
        -------
        str
        """
        import socket

        return socket.getfqdn()

    @staticmethod
    def edb(
        edbpath=None,
        cellname=None,
        isreadonly=False,
        edbversion=None,
        isaedtowned=False,
        oproject=None,
        student_version=False,
        use_ppe=False,
    ):
        """Starts a new EDB Session.

        Parameters
        ----------
        edbpath : str, optional
            Full path to the ``aedb`` folder. The variable can also contain
            the path to a layout to import. Allowed formats are BRD,
            XML (IPC2581), GDS, and DXF. The default is ``None``.
            For GDS import, the Ansys control file, which is also XML, should have the same
            name as the GDS file. Only the extensions of the two files should differ.
        cellname : str, optional
            Name of the cell to select. The default is ``None``.
        isreadonly : bool, optional
            Whether to open ``edb_core`` in read-only mode when it is
            owned by HFSS 3D Layout. The default is ``False``.
        edbversion : str, optional
            Version of ``edb_core`` to use. The default is ``None``, in which case
            the latest installed version is used.
        isaedtowned : bool, optional
            Whether to launch ``edb_core`` from HFSS 3D Layout. The
            default is ``False``.
        oproject : optional
            Reference to the AEDT project object. The default is ``None``.
        student_version : bool, optional
            Whether to open the AEDT student version. The default is ``False.``
        use_ppe : bool, optional
            Whether to use PPE licensing. The default is ``False``.

        Returns
        -------
        :class:`ansys.aedt.core.edb.Edb`
            Edb class.
        """
        return Edb(
            edbpath=edbpath,
            cellname=cellname,
            isreadonly=isreadonly,
            edbversion=edbversion,
            isaedtowned=isaedtowned,
            oproject=oproject,
            student_version=student_version,
            use_ppe=use_ppe,
        )

    @staticmethod
    def exposed_open(filename, open_options="rb", encoding=None):
        f = open(filename, open_options, encoding=encoding)
        return rpyc.restricted(f, ["read", "readlines", "close"], [])

    @staticmethod
    def exposed_create(filename, create_options="wb", encoding=None, override=True):
        if os.path.exists(filename) and not override:
            return "File already exists"
        f = open(filename, create_options, encoding=encoding)
        return rpyc.restricted(f, ["read", "readlines", "write", "writelines", "close"], [])

    @staticmethod
    def exposed_makedirs(remotepath):
        if os.path.exists(remotepath):
            return "Directory Exists!"
        os.makedirs(remotepath)
        return "Directory created!"

    @staticmethod
    def exposed_listdir(remotepath):
        if os.path.exists(remotepath):
            return os.listdir(remotepath)
        return []

    @staticmethod
    def exposed_pathexists(remotepath):
        if os.path.exists(remotepath):
            return True
        return False

    @staticmethod
    def exposed_unlink(remotepath):
        if os.unlink(remotepath):
            return True
        return False

    @staticmethod
    def exposed_isdir(remotepath):
        return os.path.isdir(remotepath)

    @staticmethod
    def exposed_tempdir():
        return tempfile.gettempdir()

    @staticmethod
    def normpath(remotepath):
        return os.path.normpath(remotepath)


class ServiceManager(rpyc.Service):
    """Global class to manage rpyc Server of PyAEDT."""

    def on_connect(self, connection):
        """Initiate the service when a connection is created."""
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.connection = connection
        self._processes = {}
        self._edb = []

    def on_disconnect(self, connection):
        """Finalize the service when the connection is closed."""
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        if is_windows:
            sys.stdout = sys.__stdout__
        for edb in self._edb:
            try:
                edb.close_edb()
            except Exception:
                logger.warning("Error when trying to close EDB.")

    def start_service(self, port):
        """Connect to remove service manager and run a new server on specified port.

        .. warning::

            Do not execute this function with untrusted function argument, environment
            variables or pyaedt global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

        Parameters
        ----------
        aedt_client_port : int
            Port that the RPyC server is running on inside AEDT.

        Returns
        -------
        RPyC object.
        """
        try:
            port = check_port(port)
            ansysem_path = os.getenv("PYAEDT_SERVER_AEDT_PATH")
            if ansysem_path and not os.path.exists(ansysem_path):
                raise FileNotFoundError(f"The ANSYSEM path '{ansysem_path}' does not exist.")
            else:
                version_list = aedt_versions.list_installed_ansysem
                if version_list:
                    ansysem_path = os.environ[version_list[0]]
                else:
                    raise Exception("No ANSYSEM_ROOTXXX environment variable is defined.")

            script_path = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "local_server.py"))
            command = [sys.executable, script_path, ansysem_path, "1", str(port)]
            p = subprocess.Popen(command)  # nosec
            time.sleep(2)
            self._processes[port] = p
            return port
        except Exception:
            logger.error("Error. No connection exists. Check if AEDT is running and if the port number is correct.")
            return False

    def exposed_stop_service(self, port):
        """Stops a given Pyaedt Service on specified port.

        Parameters
        ----------
        port : int
            Port id on which there is the service to kill.

        Returns
        -------
        bool
        """
        if port in list(self._processes.keys()):
            try:
                self._processes[port].terminate()
                return True
            except Exception:
                return False

        return True

    @staticmethod
    def exposed_check_port():
        """Check if a random port is available."""
        import secrets

        secure_random = secrets.SystemRandom()
        port = check_port(secure_random.randint(18500, 20000))
        return port
