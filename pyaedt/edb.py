"""This module contains the ``Edb`` class.

This module is implicitily loaded in HFSS 3D Layout when launched.

"""
import datetime
import gc
import logging
import os
import re
import shutil
import sys
import tempfile
import time
import traceback
import warnings

try:
    import clr
    from System.Collections.Generic import List
except ImportError:  # pragma: no cover
    if os.name != "posix":
        warnings.warn("PythonNET is needed to run PyAEDT.")
    elif sys.version[0] == 3 and sys.version[1] < 7:
        warnings.warn("EDB requires Linux Python 3.7 or later.")
from pyaedt import settings
from pyaedt.aedt_logger import AedtLogger
from pyaedt.edb_core import Components
from pyaedt.edb_core import EdbHfss
from pyaedt.edb_core import EdbLayout
from pyaedt.edb_core import EdbNets
from pyaedt.edb_core import EdbPadstacks
from pyaedt.edb_core import EdbSiwave
from pyaedt.edb_core import EdbStackup
from pyaedt.edb_core.EDB_Data import EdbBuilder
from pyaedt.edb_core.EDB_Data import SimulationConfiguration
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.constants import CutoutSubdesignType
from pyaedt.generic.constants import SolverType
from pyaedt.generic.constants import SourceType
from pyaedt.generic.general_methods import env_path
from pyaedt.generic.general_methods import env_path_student
from pyaedt.generic.general_methods import env_value
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import inside_desktop
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.process import SiwaveSolve
from pyaedt.misc.misc import list_installed_ansysem

if os.name == "posix" and is_ironpython:
    import subprocessdotnet as subprocess
else:
    import subprocess
try:
    import clr
    from System import Convert

    edb_initialized = True
except ImportError:
    if os.name != "posix":
        warnings.warn(
            "The clr is missing. Install PythonNET or use an IronPython version if you want to use the EDB module."
        )
        edb_initialized = False


class Edb(object):
    """Provides the EDB application interface.

    This module inherits all objects that belong to EDB.

    Parameters
    ----------
    edbpath : str, optional
        Full path to the ``aedb`` folder. The variable can also contain
        the path to a layout to import. Allowed formats are BRD,
        XML (IPC2581), GDS, and DXF. The default is ``None``.
        For GDS import, the Ansys control file (also XML) should have the same
        name as the GDS file. Only the file extension differs.
    cellname : str, optional
        Name of the cell to select. The default is ``None``.
    isreadonly : bool, optional
        Whether to open EBD in read-only mode when it is
        owned by HFSS 3D Layout. The default is ``False``.
    edbversion : str, optional
        Version of EDB to use. The default is ``"2021.2"``.
    isaedtowned : bool, optional
        Whether to launch EDB from HFSS 3D Layout. The
        default is ``False``.
    oproject : optional
        Reference to the AEDT project object.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False.``

    Examples
    --------
    Create an ``Edb`` object and a new EDB cell.

    >>> from pyaedt import Edb
    >>> app = Edb()

    Create an ``Edb`` object and open the specified project.

    >>> app = Edb("myfile.aedb")

    Create an ``Edb`` object from GDS and control files.
    The XML control file resides in the same directory as the GDS file: (myfile.xml).

    >>> app = Edb("/path/to/file/myfile.gds")
    """

    def __init__(
        self,
        edbpath=None,
        cellname=None,
        isreadonly=False,
        edbversion=None,
        isaedtowned=False,
        oproject=None,
        student_version=False,
        use_ppe=False,
    ):
        self._clean_variables()
        if is_ironpython and inside_desktop:
            self.standalone = False
        else:
            self.standalone = True
        if edb_initialized:
            self.oproject = oproject
            self._main = sys.modules["__main__"]
            if isaedtowned and "aedt_logger" in dir(sys.modules["__main__"]):
                self._logger = self._main.aedt_logger
            else:
                if not edbpath or not os.path.exists(os.path.dirname(edbpath)):
                    project_dir = tempfile.gettempdir()
                else:
                    project_dir = os.path.dirname(edbpath)
                if settings.logger_file_path:
                    logfile = settings.logger_file_path
                else:
                    logfile = os.path.join(
                        project_dir, "pyaedt{}.log".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
                    )
                self._logger = AedtLogger(filename=logfile, level=logging.DEBUG)
                self._logger.info("Logger started on %s", logfile)
                self._main.aedt_logger = self._logger

            self.student_version = student_version
            self.logger.info("Logger is initialized in EDB.")
            if not edbversion:
                try:
                    edbversion = "20{}.{}".format(list_installed_ansysem()[0][-3:-1], list_installed_ansysem()[0][-1:])
                    self._logger.info("Edb version " + edbversion)
                except IndexError:
                    raise Exception("No ANSYSEM_ROOTxxx is found.")
            self.edbversion = edbversion
            self.isaedtowned = isaedtowned
            self._init_dlls()
            self._db = None
            # self._edb.Database.SetRunAsStandAlone(not isaedtowned)
            self.isreadonly = isreadonly
            self.cellname = cellname
            if not edbpath:
                if os.name != "posix":
                    edbpath = os.getenv("USERPROFILE")
                    if not edbpath:
                        edbpath = os.path.expanduser("~")
                    edbpath = os.path.join(edbpath, "Documents", generate_unique_name("layout") + ".aedb")
                else:
                    edbpath = os.getenv("HOME")
                    if not edbpath:
                        edbpath = os.path.expanduser("~")
                    edbpath = os.path.join(edbpath, generate_unique_name("layout") + ".aedb")
                self.logger.info("No EDB is provided. Creating a new EDB {}.".format(edbpath))
            self.edbpath = edbpath
            if isaedtowned and (inside_desktop or settings.remote_api):
                self.open_edb_inside_aedt()
            elif edbpath[-3:] in ["brd", "gds", "xml", "dxf", "tgz"]:
                self.edbpath = edbpath[:-4] + ".aedb"
                working_dir = os.path.dirname(edbpath)
                self.import_layout_pcb(edbpath, working_dir, use_ppe=use_ppe)
                self.logger.info("EDB %s was created correctly from %s file.", self.edbpath, edbpath[-2:])
            elif not os.path.exists(os.path.join(self.edbpath, "edb.def")):
                self.create_edb()
                self.logger.info("EDB %s was created correctly.", self.edbpath)
            elif ".aedb" in edbpath:
                self.edbpath = edbpath
                self.open_edb()
            if self.builder:
                self.logger.info("EDB was initialized.")
            else:
                self.logger.info("Failed to initialize DLLs.")
        else:
            warnings.warn("Failed to initialize DLLs.")

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type:
            self.edb_exception(ex_value, ex_traceback)

    def _clean_variables(self):
        """Initialize internal variables and perform garbage collection."""

        self._components = None
        self._core_primitives = None
        self._stackup = None
        self._padstack = None
        self._siwave = None
        self._hfss = None
        self._nets = None
        self._db = None
        self._edb = None
        self.builder = None
        self._edblib = None
        self.edbutils = None
        self.simSetup = None
        self.simsetupdata = None
        # time.sleep(2)
        # gc.collect()

    @pyaedt_function_handler()
    def _init_objects(self):
        time.sleep(1)
        self._components = Components(self)
        self._stackup = EdbStackup(self)
        self._padstack = EdbPadstacks(self)
        self._siwave = EdbSiwave(self)
        self._hfss = EdbHfss(self)
        self._nets = EdbNets(self)
        self._core_primitives = EdbLayout(self)
        self.logger.info("Objects Initialized")

    @property
    def logger(self):
        """Logger for EDB.

        Returns
        -------
        :class:`pyaedt.aedt_logger.AedtLogger`
        """
        return self._logger

    @property
    def cell_names(self):
        """Cell name container.
        Returns
        -------
        list of str, cell names.
        """
        names = []
        for cell in list(self._db.TopCircuitCells):
            names.append(cell.GetName())
        return names

    @pyaedt_function_handler()
    def _init_dlls(self):
        """Initialize DLLs."""
        sys.path.append(os.path.join(os.path.dirname(__file__), "dlls", "EDBLib"))
        if os.name == "posix":
            if env_value(self.edbversion) in os.environ:
                self.base_path = env_path(self.edbversion)
                sys.path.append(self.base_path)
            else:
                main = sys.modules["__main__"]
                if "oDesktop" in dir(main):
                    self.base_path = main.oDesktop.GetExeDir()
                    sys.path.append(main.oDesktop.GetExeDir())
                    os.environ[env_value(self.edbversion)] = self.base_path
                else:
                    edb_path = os.getenv("PYAEDT_SERVER_AEDT_PATH")
                    if edb_path:
                        self.base_path = edb_path
                        sys.path.append(edb_path)
                        os.environ[env_value(self.edbversion)] = self.base_path
            if is_ironpython:
                clr.AddReferenceToFile("Ansys.Ansoft.Edb.dll")
                clr.AddReferenceToFile("Ansys.Ansoft.EdbBuilderUtils.dll")
                clr.AddReferenceToFile("EdbLib.dll")
                clr.AddReferenceToFileAndPath(os.path.join(self.base_path, "Ansys.Ansoft.SimSetupData.dll"))
            else:
                clr.AddReference("Ansys.Ansoft.Edb")
                clr.AddReference("Ansys.Ansoft.EdbBuilderUtils")
                clr.AddReference("EdbLib")
                clr.AddReference("Ansys.Ansoft.SimSetupData")
        else:
            if self.student_version:
                self.base_path = env_path_student(self.edbversion)
            else:
                self.base_path = env_path(self.edbversion)
            sys.path.append(self.base_path)
            clr.AddReference("Ansys.Ansoft.Edb")
            clr.AddReference("Ansys.Ansoft.EdbBuilderUtils")
            clr.AddReference("EdbLib")
            clr.AddReference("Ansys.Ansoft.SimSetupData")
        os.environ["ECAD_TRANSLATORS_INSTALL_DIR"] = self.base_path
        oaDirectory = os.path.join(self.base_path, "common", "oa")
        os.environ["ANSYS_OADIR"] = oaDirectory
        os.environ["PATH"] = "{};{}".format(os.environ["PATH"], self.base_path)
        edb = __import__("Ansys.Ansoft.Edb")
        self.edb = edb.Ansoft.Edb
        edbbuilder = __import__("Ansys.Ansoft.EdbBuilderUtils")
        self._edblib = None
        self.edbutils = edbbuilder.Ansoft.EdbBuilderUtils
        self.simSetup = __import__("Ansys.Ansoft.SimSetupData")
        self.simsetupdata = self.simSetup.Ansoft.SimSetupData.Data

    @property
    def edblib(self):
        """EDB library object containing advanced EDB methods not accessible directly from Python."""
        if not self._edblib:
            if os.name == "posix" and is_ironpython:
                clr.AddReferenceToFile("EdbLib.dll")
                clr.AddReferenceToFile("DataModel.dll")
            else:
                clr.AddReference("EdbLib")
                clr.AddReference("DataModel")
            self._edblib = __import__("EdbLib")
            dllpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "dlls", "EDBLib")
            try:
                self._edblib.Layout.LayoutMethods.LoadDataModel(dllpath, self.edbversion)
            except:
                pass
        return self._edblib

    @pyaedt_function_handler()
    def open_edb(self, init_dlls=False):
        """Open EDB.

        Parameters
        ----------
        init_dlls : bool, optional
            Whether to initialize DLLs. The default is ``False``.

        Returns
        -------

        """
        if init_dlls:
            self._init_dlls()
        self.logger.info("EDB Path %s", self.edbpath)
        self.logger.info("EDB Version %s", self.edbversion)
        self.edb.Database.SetRunAsStandAlone(self.standalone)
        self.logger.info("EDB Standalone %s", self.standalone)
        try:
            db = self.edb.Database.Open(self.edbpath, self.isreadonly)
        except Exception as e:
            db = None
            self.logger.error("Builder is not Initialized.")
        if not db:
            self.logger.warning("Error Opening db")
            self._db = None
            self._active_cell = None
            self.builder = None
            return None
        self._db = db
        self.logger.info("Database Opened")

        self._active_cell = None
        if self.cellname:
            for cell in list(self._db.TopCircuitCells):
                if cell.GetName() == self.cellname:
                    self._active_cell = cell
        # if self._active_cell is still None, set it to default cell
        if self._active_cell is None:
            self._active_cell = list(self._db.TopCircuitCells)[0]
        self.logger.info("Cell %s Opened", self._active_cell.GetName())
        if self._db and self._active_cell:
            dllpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "dlls", "EDBLib")
            self.logger.info(dllpath)
            self.builder = EdbBuilder(self.edbutils, self._db, self._active_cell)
            self._init_objects()
            self.logger.info("Builder was initialized.")
        else:
            self.builder = None
            self.logger.error("Builder was not initialized.")

        return self.builder

    @pyaedt_function_handler()
    def open_edb_inside_aedt(self, init_dlls=False):
        """Open EDB inside of AEDT.

        Parameters
        ----------
        init_dlls : bool, optional
            Whether to initialize DLLs. The default is ``False``.

        Returns
        -------

        """
        if init_dlls:
            self._init_dlls()
        self.logger.info("Opening EDB from HDL")
        self.edb.Database.SetRunAsStandAlone(False)
        if self.oproject.GetEDBHandle():
            hdl = Convert.ToUInt64(self.oproject.GetEDBHandle())
            db = self.edb.Database.Attach(hdl)
            if not db:
                self.logger.warning("Error getting the database.")
                self._db = None
                self._active_cell = None
                self.builder = None
                return None
            self._db = db
            self._active_cell = self.edb.Cell.Cell.FindByName(
                self.db, self.edb.Cell.CellType.CircuitCell, self.cellname
            )
            if self._active_cell is None:
                self._active_cell = list(self._db.TopCircuitCells)[0]
            if self._db and self._active_cell:
                if not os.path.exists(self.edbpath):
                    os.makedirs(self.edbpath)
                time.sleep(3)
                self.builder = EdbBuilder(self.edbutils, self._db, self._active_cell)
                self._init_objects()
                return self.builder
            else:
                self.builder = None
                return None
        else:
            self._db = None
            self._active_cell = None
            self.builder = None
            return None

    @pyaedt_function_handler()
    def create_edb(self, init_dlls=False):
        """Create EDB.

        Parameters
        ----------
        init_dlls : bool, optional
            Whether to initialize DLLs. The default is ``False``.

        """
        if init_dlls:
            self._init_dlls()
        self.edb.Database.SetRunAsStandAlone(self.standalone)
        db = self.edb.Database.Create(self.edbpath)
        if not db:
            self.logger.warning("Error creating the database.")
            self._db = None
            self._active_cell = None
            self.builder = None
            return None
        self._db = db
        if not self.cellname:
            self.cellname = generate_unique_name("Cell")
        self._active_cell = self.edb.Cell.Cell.Create(self._db, self.edb.Cell.CellType.CircuitCell, self.cellname)
        dllpath = os.path.join(os.path.dirname(__file__), "dlls", "EDBLib")
        if self._db and self._active_cell:
            self.builder = EdbBuilder(self.edbutils, self._db, self._active_cell)
            self._init_objects()
            return self.builder
        self.builder = None
        return None

    @pyaedt_function_handler()
    def import_layout_pcb(
        self, input_file, working_dir, init_dlls=False, anstranslator_full_path="", use_ppe=False, control_file=None
    ):
        """Import a board file and generate an ``edb.def`` file in the working directory.

        This function supports all AEDT formats (DXF, GDS, SML (IPC2581), BRD, TGZ ...).

        Parameters
        ----------
        input_file : str
            Full path to the board file.
        working_dir : str
            Directory in which to create the ``aedb`` folder. The name given to the AEDB file
            is the same as the name of the board file.
        init_dlls : bool
            Whether to initialize DLLs. The default is ``False``.
        anstranslator_full_path : str, optional
            Full path to the Ansys translator. The default is ``""``.
        use_ppe : bool
            Whether to use the PPE License. The default is ``False``.
        control_file : str, optional
            Path to the XML file. The default is ``None``, in which case an attempt is made to find
            the XML file in the same directory as the board file. To succeed, the XML file and board file
            must have the same name. Only the extension differs.

        Returns
        -------
        str
            Full path to the AEDB file.
        """
        self._components = None
        self._core_primitives = None
        self._stackup = None
        self._padstack = None
        self._siwave = None
        self._hfss = None
        self._nets = None
        self._db = None
        if init_dlls:
            self._init_dlls()
        aedb_name = os.path.splitext(os.path.basename(input_file))[0] + ".aedb"
        if anstranslator_full_path and os.path.exists(anstranslator_full_path):
            command = anstranslator_full_path
        else:
            command = os.path.join(self.base_path, "anstranslator")
            if os.name != "posix":
                command += ".exe"

        if not working_dir:
            working_dir = os.path.dirname(input_file)
        cmd_translator = [
            command,
            input_file,
            os.path.join(working_dir, aedb_name),
            "-l={}".format(os.path.join(working_dir, "Translator.log")),
        ]
        if not use_ppe:
            cmd_translator.append("-ppe=false")
        if control_file and input_file[-3:] not in ["brd"]:
            if os.name == "posix":
                cmd_translator.append("-c={}".format(control_file))
            else:
                cmd_translator.append('-c="{}"'.format(control_file))
        p = subprocess.Popen(cmd_translator)
        p.wait()
        if not os.path.exists(os.path.join(working_dir, aedb_name)):
            self.logger.error("Translator failed to translate.")
            return False
        self.edbpath = os.path.join(working_dir, aedb_name)
        self.open_edb()

    @pyaedt_function_handler()
    def export_to_ipc2581(self, ipc_path=None, units="millimeter"):
        """Create an XML IPC2581 file from the active EDB.

        .. note::
           This method is still being tested and may need further debugging.
           Any feedback is welcome. Backdrills and custom pads are not supported yet.

        Parameters
        ----------
        ipc_path : str, optional
            Path to the XML IPC2581 file. The default is ``None``, in which case
            an attempt is made to find the XML IPC2581 file in the same directory
            as the active EDB. To succeed, the XML IPC2581 file and the active
            EDT must have the same name. Only the extension differs.
        units : str, optional
            Units of the XML IPC2581 file. Options are ``"millimeter"``,
            ``"inch"``, and ``"micron"``. The default is ``"millimeter"``.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` if failed.
        """
        if units.lower() not in ["millimeter", "inch", "micron"]:
            self.logger.warning("The wrong unit is entered. Setting to the default, millimeter.")
            units = "millimeter"

        if not ipc_path:
            ipc_path = self.edbpath[:-4] + "xml"
        self.logger.info("Export IPC 2581 is starting. This operation can take a while.")
        start = time.time()
        try:
            result = self.edblib.IPC8521.IPCExporter.ExportIPC2581FromLayout(
                self.active_layout, self.edbversion, ipc_path, units.lower()
            )
            end = time.time() - start
            if result:
                self.logger.info("Export IPC 2581 completed in %s sec.", end)
                self.logger.info("File saved as %s", ipc_path)
                return ipc_path
        except Exception as e:
            self.logger.info("Error exporting IPC 2581.")
            self.logger.info(str(e))
            return False

    def edb_exception(self, ex_value, tb_data):
        """Write the trace stack to AEDT when a Python error occurs.

        Parameters
        ----------
        ex_value :

        tb_data :


        Returns
        -------

        """
        tb_trace = traceback.format_tb(tb_data)
        tblist = tb_trace[0].split("\n")
        self.logger.error(str(ex_value))
        for el in tblist:
            self.logger.error(el)

    @property
    def db(self):
        """Database object."""
        return self._db

    @property
    def active_cell(self):
        """Active cell."""
        return self._active_cell

    @property
    def core_components(self):
        """Core components."""
        if not self._components and self.builder:
            self._components = Components(self)
        return self._components

    @property
    def core_stackup(self):
        """Core stackup."""
        if not self._stackup and self.builder:
            self._stackup = EdbStackup(self)
        return self._stackup

    @property
    def core_padstack(self):
        """Core padstack."""
        if not self._padstack and self.builder:
            self._padstack = EdbPadstacks(self)
        return self._padstack

    @property
    def core_siwave(self):
        """Core SI Wave."""
        if not self._siwave and self.builder:
            self._siwave = EdbSiwave(self)
        return self._siwave

    @property
    def core_hfss(self):
        """Core HFSS."""
        if not self._hfss and self.builder:
            self._hfss = EdbHfss(self)
        return self._hfss

    @property
    def core_nets(self):
        """Core nets."""
        if not self._nets and self.builder:
            self._nets = EdbNets(self)
        return self._nets

    @property
    def core_primitives(self):
        """Core primitives."""
        if not self._core_primitives and self.builder:
            self._core_primitives = EdbLayout(self)
        return self._core_primitives

    @property
    def active_layout(self):
        """Active layout."""
        self._active_layout = None
        if self._active_cell:
            self._active_layout = self.active_cell.GetLayout()
        return self._active_layout

    @property
    def pins(self):
        """Pins.

        Returns
        -------
        list
            List of all pins.
        """

        pins = []
        if self.core_components:
            for el in self.core_components.components:
                comp = self.edb.Cell.Hierarchy.Component.FindByName(self.active_layout, el)
                temp = [
                    p
                    for p in comp.LayoutObjs
                    if p.GetObjType() == self.edb.Cell.LayoutObjType.PadstackInstance and p.IsLayoutPin()
                ]
                pins += temp
        return pins

    class Boundaries:
        """Boundaries.

        Parameters
        ----------
        Port :

        Pec :

        RLC :

        CurrentSource :

        VoltageSource :

        NexximGround :

        NexximPort :

        DcTerminal :

        VoltageProbe :

        """

        (Port, Pec, RLC, CurrentSource, VoltageSource, NexximGround, NexximPort, DcTerminal, VoltageProbe) = range(0, 9)

    @pyaedt_function_handler()
    def edb_value(self, val):
        """EDB value.

        Parameters
        ----------
        val : str, float, int


        Returns
        -------

        """
        if isinstance(val, (int, float)):
            return self.edb.Utility.Value(val)
        m1 = re.findall(r"(?<=[/+-/*//^/(/[])([a-z_A-Z/$]\w*)", str(val).replace(" ", ""))
        m2 = re.findall(r"^([a-z_A-Z/$]\w*)", str(val).replace(" ", ""))
        val_decomposed = list(set(m1).union(m2))
        if not val_decomposed:
            return self.edb.Utility.Value(val)
        var_server_db = self.db.GetVariableServer()
        var_names = var_server_db.GetAllVariableNames()
        var_server_cell = self.active_cell.GetVariableServer()
        var_names_cell = var_server_cell.GetAllVariableNames()
        if set(val_decomposed).intersection(var_names):
            return self.edb.Utility.Value(val, var_server_db)
        if set(val_decomposed).intersection(var_names_cell):
            return self.edb.Utility.Value(val, var_server_cell)
        return self.edb.Utility.Value(val)

    @pyaedt_function_handler()
    def _is_file_existing_and_released(self, filename):
        if os.path.exists(filename):
            try:
                os.rename(filename, filename + "_")
                os.rename(filename + "_", filename)
                return True
            except OSError as e:
                return False
        else:
            return False

    @pyaedt_function_handler()
    def _is_file_existing(self, filename):
        if os.path.exists(filename):
            return True
        else:
            return False

    @pyaedt_function_handler()
    def _wait_for_file_release(self, timeout=30, file_to_release=None):
        if not file_to_release:
            file_to_release = os.path.join(self.edbpath)
        tstart = time.time()
        while True:
            if self._is_file_existing_and_released(file_to_release):
                return True
            elif time.time() - tstart > timeout:
                return False
            else:
                time.sleep(0.250)

    @pyaedt_function_handler()
    def _wait_for_file_exists(self, timeout=30, file_to_release=None, wait_count=4):
        if not file_to_release:
            file_to_release = os.path.join(self.edbpath)
        tstart = time.time()
        times = 0
        while True:
            if self._is_file_existing(file_to_release):
                # print 'File is released'
                times += 1
                if times == wait_count:
                    return True
            elif time.time() - tstart > timeout:
                # print 'Timeout reached'
                return False
            else:
                times = 0
                time.sleep(0.250)

    @pyaedt_function_handler()
    def close_edb(self):
        """Close EDB.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._db.Close()
        time.sleep(2)
        start_time = time.time()
        self._wait_for_file_release()
        elapsed_time = time.time() - start_time
        self.logger.info("EDB file release time: {0:.2f}ms".format(elapsed_time * 1000.0))
        self._clean_variables()
        timeout = 4
        time.sleep(2)
        while gc.collect() != 0 and timeout > 0:
            time.sleep(1)
            timeout -= 1
        return True

    @pyaedt_function_handler()
    def save_edb(self):
        """Save the EDB file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._db.Save()
        return True

    @pyaedt_function_handler()
    def save_edb_as(self, fname):
        """Save the EDB file as another file.

        Parameters
        ----------
        fname : str
            Name of the new file to save to.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._db.SaveAs(fname)
        return True

    @pyaedt_function_handler()
    def execute(self, func):
        """Execute a function.

        Parameters
        ----------
        func : str
            Function to execute.


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        return self.edb.Utility.Command.Execute(func)

    @pyaedt_function_handler()
    def import_cadence_file(self, inputBrd, WorkDir=None, anstranslator_full_path="", use_ppe=False):
        """Import a board file and generate an ``edb.def`` file in the working directory.

        Parameters
        ----------
        inputBrd : str
            Full path to the board file.
        WorkDir : str, optional
            Directory in which to create the ``aedb`` folder. The default value is ``None``,
            in which case the AEDB file is given the same name as the board file. Only
            the extension differs.
        anstranslator_full_path : str, optional
            Full path to the Ansys translator.
        use_ppe : bool, optional
            Whether to use the PPE License. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.import_layout_pcb(
            inputBrd, working_dir=WorkDir, anstranslator_full_path=anstranslator_full_path, use_ppe=use_ppe
        ):
            return True
        else:
            return False

    @pyaedt_function_handler()
    def import_gds_file(self, inputGDS, WorkDir=None, anstranslator_full_path="", use_ppe=False, control_file=None):
        """Import a GDS file and generate an ``edb.def`` file in the working directory.

        Parameters
        ----------
        inputGDS : str
            Full path to the GDS file.
        WorkDir : str, optional
            Directory in which to create the ``aedb`` folder. The default value is ``None``,
            in which case the AEDB file is given the same name as the GDS file. Only the extension
            differs.
        anstranslator_full_path : str, optional
            Full path to the Ansys translator.
        use_ppe : bool, optional
            Whether to use the PPE License. The default is ``False``.
        control_file : str, optional
            Path to the XML file. The default is ``None``, in which case an attempt is made to find
            the XML file in the same directory as the GDS file. To succeed, the XML file and GDS file must
            have the same name. Only the extension differs.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.import_layout_pcb(
            inputGDS,
            working_dir=WorkDir,
            anstranslator_full_path=anstranslator_full_path,
            use_ppe=use_ppe,
            control_file=control_file,
        ):
            return True
        else:
            return False

    def create_cutout(
        self,
        signal_list=[],
        reference_list=["GND"],
        extent_type="Conforming",
        expansion_size=0.002,
        use_round_corner=False,
        output_aedb_path=None,
        open_cutout_at_end=True,
        simulation_setup=None,
    ):
        """Create a cutout and save it to a new AEDB file.

        Parameters
        ----------
        signal_list : list
            List of signal strings.
        reference_list : list, optional
            List of references to add. The default is ``["GND"]``.
        extent_type : str, optional
            Type of the extension. Options are ``"Conforming"`` and
            ``"Bounding"``. The default is ``"Conforming"``.
        expansion_size : float, optional
            Expansion size ratio in meters. The default is ``0.002``.
        use_round_corner : bool, optional
            Whether to use round corners. The default is ``False``.
        output_aedb_path : str, optional
            Full path and name for the new AEDB file.
        open_cutout_at_end : bool, optional
            Whether to open the cutout at the end. The default
            is ``True``.
        simulation_setup : EDB_Data.SimulationConfiguration object, optional
            Simulation setup to use to overwrite the other parameters. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        if simulation_setup and isinstance(simulation_setup, SimulationConfiguration):
            signal_list = simulation_setup.signal_nets
            reference_list = simulation_setup.power_nets
            if simulation_setup.cutout_subdesign_type == CutoutSubdesignType.Conformal:
                extent_type = "Conforming"
                expansion_size = float(simulation_setup.cutout_subdesign_expansion)
                use_round_corner = bool(simulation_setup.cutout_subdesign_round_corner)

        # validate nets in layout
        net_signals = convert_py_list_to_net_list(
            [net for net in list(self.active_layout.Nets) if net.GetName() in signal_list]
        )
        # validate references in layout
        _netsClip = convert_py_list_to_net_list(
            [net for net in list(self.active_layout.Nets) if net.GetName() in reference_list]
        )

        if extent_type == "Conforming":
            _poly = self.active_layout.GetExpandedExtentFromNets(
                net_signals, self.edb.Geometry.ExtentType.Conforming, expansion_size, True, use_round_corner, 1
            )
        else:
            _poly = self.active_layout.GetExpandedExtentFromNets(
                net_signals, self.edb.Geometry.ExtentType.BoundingBox, expansion_size, True, use_round_corner, 1
            )

        # Create new cutout cell/design
        included_nets = convert_py_list_to_net_list(
            [net for net in list(self.active_layout.Nets) if net.GetName() in signal_list + reference_list]
        )
        _cutout = self.active_cell.CutOut(included_nets, _netsClip, _poly, True)

        # Analysis setups do not come over with the clipped design copy,
        # so add the analysis setups from the original here.
        id = 1
        for _setup in self.active_cell.SimulationSetups:
            # Empty string '' if coming from setup copy and don't set explicitly.
            _setup_name = _setup.GetName()
            if "GetSimSetupInfo" in dir(_setup):
                # setup is an Ansys.Ansoft.Edb.Utility.HFSSSimulationSetup object
                _hfssSimSetupInfo = _setup.GetSimSetupInfo()
                _hfssSimSetupInfo.Name = "HFSS Setup " + str(id)  # Set name of analysis setup
                # Write the simulation setup info into the cell/design setup
                _setup.SetSimSetupInfo(_hfssSimSetupInfo)
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design
                id += 1
            else:
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design

        _dbCells = [_cutout]

        if output_aedb_path:
            db2 = self.edb.Database.Create(output_aedb_path)
            _success = db2.Save()
            _dbCells = convert_py_list_to_net_list(_dbCells)
            db2.CopyCells(_dbCells)  # Copies cutout cell/design to db2 project
            _success = db2.Save()
            for c in list(self.db.TopCircuitCells):
                if c.GetName() == _cutout.GetName():
                    c.Delete()
            if open_cutout_at_end:  # pragma: no cover
                self._db = db2
                self.edbpath = output_aedb_path
                self._active_cell = list(self._db.TopCircuitCells)[0]
                dllpath = os.path.join(os.path.dirname(__file__), "dlls", "EDBLib")
                self.builder = EdbBuilder(self.edbutils, self._db, self._active_cell)
                self._init_objects()
            else:
                db2.Close()
                source = os.path.join(output_aedb_path, "edb.def.tmp")
                target = os.path.join(output_aedb_path, "edb.def")
                self._wait_for_file_release(file_to_release=output_aedb_path)
                if os.path.exists(source) and not os.path.exists(target):
                    try:
                        shutil.copy(source, target)
                    except:
                        pass
        # else:
        # cells = self.db.CopyCells(convert_py_list_to_net_list(_dbCells))
        elif open_cutout_at_end:
            self._active_cell = _cutout
            self._init_objects()
        return True

    @pyaedt_function_handler()
    def get_conformal_polygon_from_netlist(self, netlist=None):
        """Return an EDB conformal polygon based on a netlist.

        Parameters
        ----------

        netlist : List of net names.
            list[str]

        Returns
        -------

        Edb polygon object
            Edb.Cell.Primitive.Polygon object

        """
        shutil.copytree(self.edbpath, os.path.join(self.edbpath, "_temp_aedb"))
        temp_edb = Edb(os.path.join(self.edbpath, "_temp_aedb"))
        for via in list(temp_edb.core_padstack.padstack_instances.values()):
            via.pin.Delete()
        if netlist:
            nets = convert_py_list_to_net_list(
                [net for net in list(self.active_layout.Nets) if net.GetName() in netlist]
            )
            _poly = temp_edb.active_layout.GetExpandedExtentFromNets(
                nets, self.edb.Geometry.ExtentType.Conforming, 0.0, True, True, 1
            )
        else:
            nets = convert_py_list_to_net_list(
                [net for net in list(temp_edb.active_layout.Nets) if "gnd" in net.GetName().lower()]
            )
            _poly = temp_edb.active_layout.GetExpandedExtentFromNets(
                nets, self.edb.Geometry.ExtentType.Conforming, 0.0, True, True, 1
            )
            temp_edb.close_edb()
        if _poly:
            return _poly
        else:
            return False

    @pyaedt_function_handler()
    def arg_with_dim(self, Value, sUnits):
        """Format arguments with dimensions.

        Parameters
        ----------
        Value :

        sUnits :

        Returns
        -------
        str
            String containing the value or the value and units if ``sUnits`` is not ``None``.
        """
        if type(Value) is str:
            val = Value
        else:
            val = "{0}{1}".format(Value, sUnits)

        return val

    @pyaedt_function_handler()
    def create_cutout_on_point_list(
        self,
        point_list,
        units="mm",
        output_aedb_path=None,
        open_cutout_at_end=True,
        nets_to_include=None,
        include_partial_instances=False,
    ):
        """Create a cutout on a specified shape and save it to a new AEDB file.

        Parameters
        ----------
        point_list : list
            Points list defining the cutout shape.
        units : str
            Units of the point list. The default is ``"mm"``.
        output_aedb_path : str, optional
            Full path and name for the new AEDB file.
            The aedb folder shall not exist otherwise the method will return ``False``.
        open_cutout_at_end : bool, optional
            Whether to open the cutout at the end. The default is ``True``.
        nets_to_include : list, optional
            List of nets to include in the cutout. The default is ``None``, in
            which case all nets are included.
        include_partial_instances : bool, optional
            Whether to include padstack instances that have bounding boxes intersecting with point list polygons.
            This operation may slow down the cutout export.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        if point_list[0] != point_list[-1]:
            point_list.append(point_list[0])
        point_list = [[self.arg_with_dim(i[0], units), self.arg_with_dim(i[1], units)] for i in point_list]
        plane = self.core_primitives.Shape("polygon", points=point_list)
        polygonData = self.core_primitives.shape_to_polygon_data(plane)
        _ref_nets = []
        if nets_to_include:
            self.logger.info("Creating cutout on {} nets.".format(len(nets_to_include)))
        else:
            self.logger.info("Creating cutout on all nets.")  # pragma: no cover

        # Check Padstack Instances overlapping the cutout
        pinstance_to_add = []
        if include_partial_instances:
            if nets_to_include:
                pinst = [
                    i for i in list(self.core_padstack.padstack_instances.values()) if i.net_name in nets_to_include
                ]
            else:
                pinst = [i for i in list(self.core_padstack.padstack_instances.values())]
            for p in pinst:
                if p.in_polygon(polygonData):
                    pinstance_to_add.append(p)
        # validate references in layout
        for _ref in self.core_nets.nets:
            if nets_to_include:
                if _ref in nets_to_include:
                    _ref_nets.append(self.core_nets.nets[_ref].net_object)
            else:
                _ref_nets.append(self.core_nets.nets[_ref].net_object)  # pragma: no cover
        voids = [p for p in self.core_primitives.circles if p.is_void]
        voids2 = [p for p in self.core_primitives.polygons if p.is_void]
        voids.extend(voids2)
        voids_to_add = []
        for circle in voids:
            if polygonData.GetIntersectionType(circle.primitive_object.GetPolygonData()) >= 3:
                voids_to_add.append(circle)

        _netsClip = convert_py_list_to_net_list(_ref_nets)
        net_signals = List[type(_ref_nets[0])]()
        # Create new cutout cell/design
        _cutout = self.active_cell.CutOut(net_signals, _netsClip, polygonData)
        layout = _cutout.GetLayout()
        cutout_obj_coll = layout.GetLayoutInstance().GetAllLayoutObjInstances()
        ids = []
        for obj in cutout_obj_coll.Items:
            lobj = obj.GetLayoutObj()
            if type(lobj) is self.edb.Cell.Primitive.PadstackInstance:
                ids.append(lobj.GetId())

        if include_partial_instances:
            p_missing = [i for i in pinstance_to_add if i.id not in ids]
            self.logger.info("Added {} padstack instances after cutout".format(len(p_missing)))
            for p in p_missing:
                position = self.edb.Geometry.PointData(self.edb_value(p.position[0]), self.edb_value(p.position[1]))
                net = self.core_nets.find_or_create_net(p.net_name)
                rotation = self.edb_value(p.rotation)
                sign_layers = list(self.core_stackup.signal_layers.keys())
                if not p.start_layer:
                    fromlayer = self.core_stackup.signal_layers[sign_layers[-1]]._layer
                else:
                    fromlayer = self.core_stackup.signal_layers[p.start_layer]._layer

                if not p.stop_layer:
                    tolayer = self.core_stackup.signal_layers[sign_layers[0]]._layer
                else:
                    tolayer = self.core_stackup.signal_layers[p.stop_layer]._layer
                padstack = None
                for pad in list(self.core_padstack.padstacks.keys()):
                    if pad == p.padstack_definition:
                        padstack = self.core_padstack.padstacks[pad].edb_padstack
                        padstack_instance = self.edb.Cell.Primitive.PadstackInstance.Create(
                            _cutout.GetLayout(),
                            net,
                            p.name,
                            padstack,
                            position,
                            rotation,
                            fromlayer,
                            tolayer,
                            None,
                            None,
                        )
                        padstack_instance.SetIsLayoutPin(p.is_pin)
                        break

        for void_circle in voids_to_add:
            if void_circle.type == "Circle":
                if is_ironpython:  # pragma: no cover
                    res, center_x, center_y, radius = void_circle.primitive_object.GetParameters()
                else:
                    res, center_x, center_y, radius = void_circle.primitive_object.GetParameters(0.0, 0.0, 0.0)
                cloned_circle = self.edb.Cell.Primitive.Circle.Create(
                    layout,
                    void_circle.layer_name,
                    void_circle.net,
                    self.edb_value(center_x),
                    self.edb_value(center_y),
                    self.edb_value(radius),
                )
                cloned_circle.SetIsNegative(True)
            elif void_circle.type == "Polygon":
                cloned_polygon = self.edb.Cell.Primitive.Polygon.Create(
                    layout, void_circle.layer_name, void_circle.net, void_circle.primitive_object.GetPolygonData()
                )
                cloned_polygon.SetIsNegative(True)
        layers = self.core_stackup.stackup_layers.signal_layers
        for layer in list(layers.keys()):
            layer_primitves = self.core_primitives.get_primitives(layer_name=layer)
            if len(layer_primitves) == 0:
                self.core_primitives.create_polygon(plane, layer, net_name="DUMMY")
        self.logger.info("Cutout %s created correctly", _cutout.GetName())
        id = 1
        for _setup in self.active_cell.SimulationSetups:
            # Empty string '' if coming from setup copy and don't set explicitly.
            _setup_name = _setup.GetName()
            if "GetSimSetupInfo" in dir(_setup):
                # setup is an Ansys.Ansoft.Edb.Utility.HFSSSimulationSetup object
                _hfssSimSetupInfo = _setup.GetSimSetupInfo()
                _hfssSimSetupInfo.Name = "HFSS Setup " + str(id)  # Set name of analysis setup
                # Write the simulation setup info into the cell/design setup
                _setup.SetSimSetupInfo(_hfssSimSetupInfo)
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design
                id += 1
            else:
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design

        _dbCells = [_cutout]
        if output_aedb_path:
            db2 = self.edb.Database.Create(output_aedb_path)
            if not db2.Save():
                self.logger.error("Failed to create new Edb. Check if the path already exists and remove it.")
                return False
            _dbCells = convert_py_list_to_net_list(_dbCells)
            cell_copied = db2.CopyCells(_dbCells)  # Copies cutout cell/design to db2 project
            cell = list(cell_copied)[0]
            cell.SetName(os.path.basename(output_aedb_path[:-5]))
            db2.Save()
            for c in list(self.db.TopCircuitCells):
                if c.GetName() == _cutout.GetName():
                    c.Delete()
            if open_cutout_at_end:  # pragma: no cover
                _success = db2.Save()
                self._db = db2
                self.edbpath = output_aedb_path
                self._active_cell = cell
                self.builder = EdbBuilder(self.edbutils, self._db, self._active_cell)
                self._init_objects()
            else:
                db2.Close()
                source = os.path.join(output_aedb_path, "edb.def.tmp")
                target = os.path.join(output_aedb_path, "edb.def")
                self._wait_for_file_release(file_to_release=output_aedb_path)
                if os.path.exists(source) and not os.path.exists(target):
                    try:
                        shutil.copy(source, target)
                        self.logger.warning("aedb def file manually created.")
                    except:
                        pass
        return True

    @pyaedt_function_handler()
    def write_export3d_option_config_file(self, path_to_output, config_dictionaries=None):
        """Write the options for a 3D export to a configuration file.

        Parameters
        ----------
        path_to_output : str
            Full path to the configuration file to save 3D export options to.

        config_dictionaries : dict, optional
            Configuration dictionaries. The default is ``None``.

        """
        option_config = {
            "UNITE_NETS": 1,
            "ASSIGN_SOLDER_BALLS_AS_SOURCES": 0,
            "Q3D_MERGE_SOURCES": 0,
            "Q3D_MERGE_SINKS": 0,
            "CREATE_PORTS_FOR_PWR_GND_NETS": 0,
            "PORTS_FOR_PWR_GND_NETS": 0,
            "GENERATE_TERMINALS": 0,
            "SOLVE_CAPACITANCE": 0,
            "SOLVE_DC_RESISTANCE": 0,
            "SOLVE_DC_INDUCTANCE_RESISTANCE": 1,
            "SOLVE_AC_INDUCTANCE_RESISTANCE": 0,
            "CreateSources": 0,
            "CreateSinks": 0,
            "LAUNCH_Q3D": 0,
            "LAUNCH_HFSS": 0,
        }
        if config_dictionaries:
            for el, val in config_dictionaries.items():
                option_config[el] = val
        with open(os.path.join(path_to_output, "options.config"), "w") as f:
            for el, val in option_config.items():
                f.write(el + " " + str(val) + "\n")
        return os.path.join(path_to_output, "options.config")

    @pyaedt_function_handler()
    def export_hfss(self, path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False):
        """Export EDB to HFSS.

        Parameters
        ----------
        path_to_output : str
            Full path and name for saving the AEDT file.
        net_list : list, optional
            List of nets to export if only certain ones are to be exported.
            The default is ``None``, in which case all nets are eported.
        num_cores : int, optional
            Number of cores to use for the export. The default is ``None``.
        aedt_file_name : str, optional
            Name of the AEDT output file without the ``.aedt`` extension. The default is ``None``,
            in which case the default name is used.
        hidden : bool, optional
            Open Siwave in embedding mode. User will only see Siwave Icon but UI will be hidden.

        Returns
        -------
        str
            Full path to the AEDT file.

        Examples
        --------

        >>> from pyaedt import Edb

        >>> edb = Edb(edbpath=r"C:\temp\myproject.aedb", edbversion="2021.2")

        >>> options_config = {'UNITE_NETS' : 1, 'LAUNCH_Q3D' : 0}
        >>> edb.write_export3d_option_config_file(r"C:\temp", options_config)
        >>> edb.export_hfss(r"C:\temp")
        "C:\\temp\\hfss_siwave.aedt"

        """
        siwave_s = SiwaveSolve(self.edbpath, aedt_installer_path=self.base_path)
        return siwave_s.export_3d_cad("HFSS", path_to_output, net_list, num_cores, aedt_file_name, hidden=hidden)

    @pyaedt_function_handler()
    def export_q3d(self, path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False):
        """Export EDB to Q3D.

        Parameters
        ----------
        path_to_output : str
            Full path and name for saving the AEDT file.
        net_list : list, optional
            List of nets to export only if certain ones are to be exported.
            The default is ``None``, in which case all nets are eported.
        num_cores : int, optional
            Number of cores to use for the export. The default is ``None``.
        aedt_file_name : str, optional
            Name of the AEDT output file without the ``.aedt`` extension. The default is ``None``,
            in which case the default name is used.
        hidden : bool, optional
            Open Siwave in embedding mode. User will only see Siwave Icon but UI will be hidden.

        Returns
        -------
        str
            Full path to the AEDT file.

        Examples
        --------

        >>> from pyaedt import Edb

        >>> edb = Edb(edbpath=r"C:\temp\myproject.aedb", edbversion="2021.2")

        >>> options_config = {'UNITE_NETS' : 1, 'LAUNCH_Q3D' : 0}
        >>> edb.write_export3d_option_config_file(r"C:\temp", options_config)
        >>> edb.export_q3d(r"C:\temp")
        "C:\\temp\\q3d_siwave.aedt"

        """

        siwave_s = SiwaveSolve(self.edbpath, aedt_installer_path=self.base_path)
        return siwave_s.export_3d_cad(
            "Q3D", path_to_output, net_list, num_cores=num_cores, aedt_file_name=aedt_file_name, hidden=hidden
        )

    @pyaedt_function_handler()
    def export_maxwell(self, path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False):
        """Export EDB to Maxwell 3D.

        Parameters
        ----------
        path_to_output : str
            Full path and name for saving the AEDT file.
        net_list : list, optional
            List of nets to export only if certain ones are to be
            exported. The default is ``None``, in which case all nets are exported.
        num_cores : int, optional
            Number of cores to use for the export. The default is ``None.``
        aedt_file_name : str, optional
            Name of the AEDT output file without the ``.aedt`` extension. The default is ``None``,
            in which case the default name is used.
        hidden : bool, optional
            Open Siwave in embedding mode. User will only see Siwave Icon but UI will be hidden.

        Returns
        -------
        str
            Full path to the AEDT file.

        Examples
        --------

        >>> from pyaedt import Edb

        >>> edb = Edb(edbpath=r"C:\temp\myproject.aedb", edbversion="2021.2")

        >>> options_config = {'UNITE_NETS' : 1, 'LAUNCH_Q3D' : 0}
        >>> edb.write_export3d_option_config_file(r"C:\temp", options_config)
        >>> edb.export_maxwell(r"C:\temp")
        "C:\\temp\\maxwell_siwave.aedt"

        """
        siwave_s = SiwaveSolve(self.edbpath, aedt_installer_path=self.base_path)
        return siwave_s.export_3d_cad(
            "Maxwell",
            path_to_output,
            net_list,
            num_cores=num_cores,
            aedt_file_name=aedt_file_name,
            hidden=hidden,
        )

    @pyaedt_function_handler()
    def solve_siwave(self):
        """Close EDB and solve it with Siwave.

        Returns
        -------
        bool
        """
        process = SiwaveSolve(self.edbpath, aedt_version=self.edbversion)
        try:
            self._db.Close()
        except:
            pass
        process.solve()
        return True

    @pyaedt_function_handler()
    def add_design_variable(self, variable_name, variable_value, is_parameter=False):
        """Add a design variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable. To added the variable as a project variable, the name
            must begin with ``$``.
        variable_value : str, float
            Value of the variable with units.
        is_parameter : bool, optional
            Whether to add the variable as a local variable. The default is ``False``.
            When ``True``, the variable is added as a parameter default.

        Returns
        -------
        tuple
            Tuple containing the ``AddVariable`` result and variable server.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edb_app = Edb()
        >>> boolean_1, ant_length = edb_app.add_design_variable("my_local_variable", "1cm")
        >>> boolean_2, para_length = edb_app.change_design_variable_value("my_parameter", "1m", is_parameter=True
        >>> boolean_3, project_length = edb_app.change_design_variable_value("$my_project_variable", "1m")


        """
        if "$" in variable_name:
            if variable_name.index("$") == 0:
                var_server = self.db.GetVariableServer()
                is_parameter = False
                string_message = [
                    "Creating project variable %s.",
                    "Project variable %s already exists. You can use it.",
                ]
            else:
                var_server = self.active_cell.GetVariableServer()
                self.logger.warning(
                    "The character ``$`` must be placed at the beginning of your variable name,"
                    " to make it a project variable."
                )

                string_message = ["Creating local variable %s.", "Local variable %s already exists. You can use it."]
        else:
            var_server = self.active_cell.GetVariableServer()
            string_message = ["Creating local variable %s.", "Local variable %s already exists. You can use it."]
        variables = var_server.GetAllVariableNames()
        if variable_name in list(variables):
            if var_server.IsVariableParameter(variable_name):
                string_message[1] = "Parameter default %s already exists. You can use it."
            self.logger.warning(string_message[1], variable_name)
            return False, var_server
        else:
            if is_parameter:
                string_message[0] = "Creating parameter default %s"
            self.logger.info(string_message[0], variable_name)
            var_server.AddVariable(variable_name, self.edb_value(variable_value), is_parameter)
            return True, var_server

    @pyaedt_function_handler()
    def change_design_variable_value(self, variable_name, variable_value):
        """Change a variable value.

        Parameters
        ----------
        variable_name : str
            Name of the variable.
        variable_value : str, float
            Value of the variable with units.

        Returns
        -------
        tuple
            Tuple containing the ``SetVariableValue`` result and variable server.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edb_app = Edb()
        >>> boolean, ant_length = edb_app.add_design_variable("ant_length", "1cm")
        >>> boolean, ant_length = edb_app.change_design_variable_value("ant_length", "1m")

        """
        if "$" in variable_name:
            if variable_name.index("$") == 0:
                var_server = self.db.GetVariableServer()
                string_message = [
                    "Value of the project variable %s has been changed from %s to %s.",
                    "Project variable %s doesn't exist. You can create it using the method add_design_variable.",
                ]
            else:
                var_server = self.active_cell.GetVariableServer()
                string_message = [
                    "Value of the local variable %s has been changed from %s to %s.",
                    "Local variable or parameter default %s doesn't exist."
                    " You can create it using method add_design_variable.",
                ]
        else:
            var_server = self.active_cell.GetVariableServer()
            string_message = [
                "Value of the local variable %s has been changed from %s to %s.",
                "Local variable or parameter default %s doesn't exist."
                " You can create it using the method add_design_variable.",
            ]
        variables = var_server.GetAllVariableNames()
        if variable_name in list(variables):
            if is_ironpython:
                tuple_value = var_server.GetVariableValue(variable_name)
            else:
                out_value = self.edb.Utility.Value("")
                tuple_value = var_server.GetVariableValue(variable_name, out_value)
            var_server.SetVariableValue(variable_name, self.edb_value(variable_value))
            if var_server.IsVariableParameter(variable_name):
                string_message[0] = "Value of the parameter default %s has been changed from %s to %s."
            self.logger.info(string_message[0], variable_name, tuple_value[1], variable_value)
            return True, var_server
        else:
            self.logger.error(string_message[1], variable_name)
            return False

    @pyaedt_function_handler()
    def get_bounding_box(self):
        """Get the layout bounding box.

        Returns
        -------
        list of list of double
            Bounding box as a [lower-left X, lower-left Y], [upper-right X, upper-right Y]) pair in meters.
        """
        bbox = self.edbutils.HfssUtilities.GetBBox(self.active_layout)
        return [[bbox.Item1.X.ToDouble(), bbox.Item1.Y.ToDouble()], [bbox.Item2.X.ToDouble(), bbox.Item2.Y.ToDouble()]]

    @pyaedt_function_handler()
    def build_simulation_project(self, simulation_setup=None):
        """Build a ready-to-solve simulation project.

        Parameters
        ----------
        simulation_setup : EDB_Data.SimulationConfiguratiom object.
            SimulationConfiguration object that can be instantiated or directly loaded with a
            configuration file.

        Returns
        -------
        bool
            ``True`` when successful, False when ``Failed``.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> from pyaedt.edb_core.EDB_Data import SimulationConfiguration
        >>> config_file = path_configuration_file
        >>> source_file = path_to_edb_folder
        >>> edb = Edb(source_file)
        >>> sim_setup = SimulationConfiguration(config_file)
        >>> edb.build_simulation_project(sim_setup)
        >>> edb.save_edb()
        >>> edb.close_edb()
        """
        self.logger.info("Building simulation project.")
        try:
            if not simulation_setup or not isinstance(simulation_setup, SimulationConfiguration):  # pragma: no cover
                return False
            self.core_nets.classify_nets(simulation_setup)
            if simulation_setup.do_cutout_subdesign:
                self.logger.info("Cutting out using method: {0}".format(simulation_setup.cutout_subdesign_type))
                old_cell_name = self.active_cell.GetName()
                if self.create_cutout(simulation_setup=simulation_setup, output_aedb_path=simulation_setup.output_aedb):
                    self.logger.info("Cutout processed.")
                    old_cell = self.active_cell.FindByName(self._db, self.edb.Cell.CellType.CircuitCell, old_cell_name)
                    if old_cell:
                        old_cell.Delete()
                else:  # pragma: no cover
                    self.logger.error("Cutout failed.")
            self.logger.info("Deleting existing ports.")
            map(lambda port: port.Delete(), list(self.active_layout.Terminals))
            map(lambda pg: pg.Delete(), list(self.active_layout.PinGroups))
            if simulation_setup.solver_type == SolverType.Hfss3dLayout:
                self.logger.info("Creating HFSS ports for signal nets.")
                for cmp in simulation_setup.components:
                    self.core_components.create_port_on_component(
                        cmp,
                        net_list=simulation_setup.signal_nets,
                        do_pingroup=False,
                        reference_net=simulation_setup.power_nets,
                        port_type=SourceType.CoaxPort,
                    )
                if not self.core_hfss.set_coax_port_attributes(simulation_setup):  # pragma: no cover
                    self.logger.error("Failed to configure coaxial port attributes.")
                self.logger.info("Number of ports: {}".format(self.core_hfss.get_ports_number()))
                self.logger.info("Configure HFSS extents.")
                if simulation_setup.trim_reference_size:  # pragma: no cover
                    self.logger.info(
                        "Trimming the reference plane for coaxial ports: {0}".format(
                            bool(simulation_setup.trim_reference_size)
                        )
                    )
                    self.core_hfss.trim_component_reference_size(simulation_setup)  # pragma: no cover
                self.core_hfss.configure_hfss_extents(simulation_setup)
                if not self.core_hfss.configure_hfss_analysis_setup(simulation_setup):
                    self.logger.error("Failed to configure HFSS simulation setup.")
            if simulation_setup.solver_type == SolverType.SiwaveSYZ:
                for cmp in simulation_setup.components:
                    self.core_components.create_port_on_component(
                        cmp,
                        net_list=simulation_setup.signal_nets,
                        do_pingroup=True,
                        reference_net=simulation_setup.power_nets,
                        port_type=SourceType.CircPort,
                    )
                self.logger.info("Configuring analysis setup.")
                if not self.core_siwave.configure_siw_analysis_setup(simulation_setup):  # pragma: no cover
                    self.logger.error("Failed to configure Siwave simulation setup.")

            if simulation_setup.solver_type == SolverType.SiwaveDC:
                self.core_components.create_source_on_component(simulation_setup.sources)
                if not self.core_siwave.configure_siw_analysis_setup(simulation_setup):  # pragma: no cover
                    self.logger.error("Failed to configure Siwave simulation setup.")
            return True
        except:  # pragma: no cover
            return False

    @pyaedt_function_handler()
    def get_statistics(self, compute_area=False):
        """Get the EDBStatistics object.

        Returns
        -------
        EDBStatistics object from the loaded layout.
        """
        return self.core_primitives.get_layout_statistics(evaluate_area=compute_area, net_list=None)
