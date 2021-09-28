"""This module contains the `Edb` class.

This module is implicitily loaded in HFSS 3D Layout when launched.

"""
import gc
import os
import sys
import time
import traceback
import warnings

from pyaedt import inside_desktop, is_ironpython
from pyaedt.application.MessageManager import EDBMessageManager
from pyaedt.edb_core import Components, EdbNets, EdbPadstacks, EdbLayout, Edb3DLayout, EdbSiwave, EdbStackup
from pyaedt.edb_core.EDB_Data import EdbBuilder
from pyaedt import retry_ntimes
from pyaedt.generic.general_methods import (
    aedt_exception_handler,
    env_path,
    env_path_student,
    env_value,
    generate_unique_name,
)
from pyaedt.generic.process import SiwaveSolve

if os.name == "posix":
    try:
        import subprocessdotnet as subprocess
    except:
        warnings.warn("Pythonnet is needed to run pyaedt within Linux")
else:
    import subprocess
try:
    import clr
    from System import Convert

    edb_initialized = True
except ImportError:
    warnings.warn(
        "The clr is missing. Install Python.NET or use an IronPython version if you want to use the EDB module."
    )
    edb_initialized = False


class Edb(object):
    """Provides the EDB application interface.

    This module inherits all objects that belong to EDB.

    Parameters
    ----------
    edbpath : str, optional
        Full path to the ``aedb`` folder. The variable can also contain
        the path to a layout to import. Allowed formarts are BRD,
        XML (IPC2581), GDS, and DXF. The default is ``None``.
    cellname : str, optional
        Name of the cell to select. The default is ``None``.
    isreadonly : bool, optional
        Whether to open ``edb_core`` in read-only mode when it is
        owned by HFSS 3D Layout. The default is ``False``.
    edbversion : str, optional
        Version of ``edb_core`` to use. The default is ``"2021.1"``.
    isaedtowned : bool, optional
        Whether to launch ``edb_core`` from HFSS 3D Layout. The
        default is ``False``.
    oproject : optional
        Reference to the AEDT project object.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False.``

    Examples
    --------
    Create an `Edb` object and a new EDB cell.

    >>> from pyaedt import Edb
    >>> app = Edb()

    Create an `Edb` object and open the specified project.

    >>> app = Edb("myfile.aedb")

    """

    def __init__(
        self,
        edbpath=None,
        cellname=None,
        isreadonly=False,
        edbversion="2021.1",
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
            if isaedtowned:
                self._main = sys.modules["__main__"]
                self._messenger = self._main.oMessenger
            else:
                if not edbpath or not os.path.exists(edbpath):
                    self._messenger = EDBMessageManager()
                elif os.path.exists(edbpath):
                    self._messenger = EDBMessageManager(os.path.dirname(edbpath))

            self.student_version = student_version
            self._messenger.add_info_message("Messenger Initialized in EDB")
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
                self._messenger.add_info_message("No Edb Provided. Creating new EDB {}.".format(edbpath))
            self.edbpath = edbpath
            if isaedtowned and inside_desktop:
                self.open_edb_inside_aedt()
            elif edbpath[-3:] in ["brd", "gds", "xml", "dxf", "tgz"]:
                self.edbpath = edbpath[:-4] + ".aedb"
                working_dir = os.path.dirname(edbpath)
                self.import_layout_pcb(edbpath, working_dir, use_ppe=use_ppe)
                self._messenger.add_info_message(
                    "Edb {} Created Correctly from {} file".format(self.edbpath, edbpath[-2:])
                )
            elif not os.path.exists(os.path.join(self.edbpath, "edb.def")):
                self.create_edb()
                self._messenger.add_info_message("Edb {} Created Correctly".format(self.edbpath))
            elif ".aedb" in edbpath:
                self.edbpath = edbpath
                self.open_edb()
            if self.builder:
                self._messenger.add_info_message("Edb Initialized")
            else:
                self._messenger.add_info_message("Failed to initialize Dlls")
        else:
            warnings.warn("Failed to initialize Dlls")

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
        if "edbutils" in dir(self):
            self.edbutils.Logger.Disable = True
        self.builder = None
        self.edblib = None
        self.edbutils = None
        self.simSetup = None
        self.layout_methods = None
        self.simsetupdata = None
        if os.name == "posix":
            clr.ClearProfilerData()
        gc.collect()

    @aedt_exception_handler
    def _init_objects(self):
        time.sleep(2)
        self._components = Components(self)
        self._stackup = EdbStackup(self)
        self._padstack = EdbPadstacks(self)
        self._siwave = EdbSiwave(self)
        self._hfss = Edb3DLayout(self)
        self._nets = EdbNets(self)
        self._core_primitives = EdbLayout(self)
        self._messenger.add_info_message("Objects Initialized")

    @aedt_exception_handler
    def add_info_message(self, message_text):
        """Add a type 0 "Info" message to the active design level of the Message Manager tree.

        Also add an info message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the info message.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edb = Edb()
        >>> edb.add_info_message("Design info message")

        """
        self._messenger.add_info_message(message_text)
        return True

    @aedt_exception_handler
    def add_warning_message(self, message_text):
        """Add a type 0 "Warning" message to the active design level of the Message Manager tree.

        Also add an info message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the warning message.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edb = Edb()
        >>> edb.add_warning_message("Design warning message")

        """
        self._messenger.add_warning_message(message_text)
        return True

    @aedt_exception_handler
    def add_error_message(self, message_text):
        """Add a type 0 "Error" message to the active design level of the Message Manager tree.

        Also add an error message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the error message.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.


        Examples
        --------
        >>> from pyaedt import Edb
        >>> edb = Edb()
        >>> edb.add_error_message("Design error message")

        """
        self._messenger.add_error_message(message_text)
        return True

    @aedt_exception_handler
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
            clr.AddReferenceToFile("Ansys.Ansoft.Edb.dll")
            clr.AddReferenceToFile("Ansys.Ansoft.EdbBuilderUtils.dll")
            clr.AddReferenceToFile("EdbLib.dll")
            clr.AddReferenceToFile("DataModel.dll")
            clr.AddReferenceToFileAndPath(os.path.join(self.base_path, "Ansys.Ansoft.SimSetupData.dll"))
        else:
            if self.student_version:
                self.base_path = env_path_student(self.edbversion)
            else:
                self.base_path = env_path(self.edbversion)
            sys.path.append(self.base_path)
            clr.AddReference("Ansys.Ansoft.Edb")
            clr.AddReference("Ansys.Ansoft.EdbBuilderUtils")
            clr.AddReference("EdbLib")
            clr.AddReference("DataModel")
            clr.AddReference("Ansys.Ansoft.SimSetupData")
        os.environ["ECAD_TRANSLATORS_INSTALL_DIR"] = self.base_path
        oaDirectory = os.path.join(self.base_path, "common", "oa")
        os.environ["ANSYS_OADIR"] = oaDirectory
        os.environ["PATH"] = "{};{}".format(os.environ["PATH"], self.base_path)
        edb = __import__("Ansys.Ansoft.Edb")

        self.edb = edb.Ansoft.Edb
        edbbuilder = __import__("Ansys.Ansoft.EdbBuilderUtils")
        self.edblib = __import__("EdbLib")
        self.edbutils = edbbuilder.Ansoft.EdbBuilderUtils
        self.simSetup = __import__("Ansys.Ansoft.SimSetupData")
        self.layout_methods = self.edblib.Layout.LayoutMethods
        self.simsetupdata = self.simSetup.Ansoft.SimSetupData.Data

    @aedt_exception_handler
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
        self._messenger.add_info_message("EDB Path {}".format(self.edbpath))
        self._messenger.add_info_message("EDB Version {}".format(self.edbversion))
        self.edb.Database.SetRunAsStandAlone(self.standalone)
        self._messenger.add_info_message("EDB Standalone {}".format(self.standalone))
        try:
            db = self.edb.Database.Open(self.edbpath, self.isreadonly)
        except Exception as e:
            db = None
            self._messenger.add_error_message("Builder is not Initialized.")
        if not db:
            self._messenger.add_warning_message("Error Opening db")
            self._db = None
            self._active_cell = None
            self.builder = None
            return None
        self._db = db
        self._messenger.add_info_message("Database Opened")

        self._active_cell = None
        if self.cellname:
            for cell in list(self._db.TopCircuitCells):
                if cell.GetName() == self.cellname:
                    self._active_cell = cell
        # if self._active_cell is still None, set it to default cell
        if self._active_cell is None:
            self._active_cell = list(self._db.TopCircuitCells)[0]
        self._messenger.add_info_message("Cell {} Opened".format(self._active_cell.GetName()))

        if self._db and self._active_cell:
            dllpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "dlls", "EDBLib", "DataModel.dll")
            self._messenger.add_info_message(dllpath)
            self.layout_methods.LoadDataModel(dllpath)
            dllpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "dlls", "EDBLib",
                                   "IPC_2581_DataModel.dll")
            self.layout_methods.LoadDataModel(dllpath)

            time.sleep(3)
            self.builder = retry_ntimes(
                10,
                self.layout_methods.GetBuilder,
                self._db,
                self._active_cell,
                self.edbpath,
                self.edbversion,
                self.standalone,
            )
            self._init_objects()
            self._messenger.add_info_message("Builder Initialized")
        else:
            self.builder = None
            self._messenger.add_error_message("Builder Not Initialized")

        return self.builder

    @aedt_exception_handler
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
        self._messenger.add_info_message("Opening EDB from HDL")
        self.edb.Database.SetRunAsStandAlone(False)
        if self.oproject.GetEDBHandle():
            hdl = Convert.ToUInt64(self.oproject.GetEDBHandle())
            db = self.edb.Database.Attach(hdl)
            if not db:
                self._messenger.add_warning_message("Error Getting db")
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
            dllpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "dlls", "EDBLib", "DataModel.dll")
            if self._db and self._active_cell:
                self.layout_methods.LoadDataModel(dllpath)
                dllpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "dlls", "EDBLib",
                                       "IPC_2581_DataModel.dll")
                self.layout_methods.LoadDataModel(dllpath)
                if not os.path.exists(self.edbpath):
                    os.makedirs(self.edbpath)
                time.sleep(3)
                self.builder = EdbBuilder(self.edbutils, self._db, self._active_cell)
                # self.builder = retry_ntimes(
                #     10,
                #     self.layout_methods.GetBuilder,
                #     self._db,
                #     self._active_cell,
                #     self.edbpath,
                #     self.edbversion,
                #     self.standalone,
                #     True
                # )
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

    @aedt_exception_handler
    def create_edb(self, init_dlls=False):
        """Create EDB.

        Parameters
        ----------
        init_dlls : bool, optional
            Whether to initialize DLLs. The default is ``False``.

        Returns
        -------

        """
        if init_dlls:
            self._init_dlls()
        self.edb.Database.SetRunAsStandAlone(self.standalone)
        db = self.edb.Database.Create(self.edbpath)
        if not db:
            self._messenger.add_warning_message("Error Creating db")
            self._db = None
            self._active_cell = None
            self.builder = None
            return None
        self._db = db
        if not self.cellname:
            self.cellname = generate_unique_name("Cell")
        self._active_cell = self.edb.Cell.Cell.Create(self._db, self.edb.Cell.CellType.CircuitCell, self.cellname)
        dllpath = os.path.join(os.path.dirname(__file__), "dlls", "EDBLib", "DataModel.dll")
        if self._db and self._active_cell:
            self.layout_methods.LoadDataModel(dllpath)
            dllpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "dlls", "EDBLib",
                                   "IPC_2581_DataModel.dll")
            self.layout_methods.LoadDataModel(dllpath)
            time.sleep(3)
            self.builder = retry_ntimes(
                10,
                self.layout_methods.GetBuilder,
                self._db,
                self._active_cell,
                self.edbpath,
                self.edbversion,
                self.standalone
            )
            self._init_objects()
            return self.builder
        self.builder = None
        return None

    @aedt_exception_handler
    def import_layout_pcb(self, input_file, working_dir, init_dlls=False, anstranslator_full_path="", use_ppe=False):
        """Import a BRD file and generate an ``edb.def`` file in the working directory.

        Parameters
        ----------
        input_file : str
            Full path to the BRD file.
        working_dir : str
            Directory in which to create the ``aedb`` folder. The AEDB file name will be the
            same as the BRD file name.
        init_dlls : bool
            Whether to initialize DLLs. The default is ``False``.
        anstranslator_full_path : str, optional
            Whether to use or not PPE License. The default is ``False``.
        use_ppe : bool
            Whether to use or not PPE License. The default is ``False``.
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
        cmd_translator = command + " " + input_file + " " + os.path.join(working_dir, aedb_name)
        cmd_translator += " -l=" + os.path.join(working_dir, "Translator.log")
        if not use_ppe:
            cmd_translator += " -ppe=false"
        p = subprocess.Popen(cmd_translator)
        p.wait()
        if not os.path.exists(os.path.join(working_dir, aedb_name)):
            self._messenger.add_error_message("Translator failed to translate.")
            return False
        self.edbpath = os.path.join(working_dir, aedb_name)
        return self.open_edb()

    @aedt_exception_handler
    def export_to_ipc2581(self, ipc_path=None, units="millimeter"):
        """Create an XML IPC2581 File from active Edb.

    .. note::
       This Method is still under test and need further Debug. Any feedback is welcome. Actually, backdrills and
       custom pads are not supported yet.

        Parameters
        ----------
        ipc_path : str, optional
            Path to the xml file
        units : str, optional
            Units of IPC2581 file. Default ``millimeter``. It can be ``millimeter``,
            ``inch``, ``micron``.
        Returns
        -------
        bool
            ``True`` if succeeded.

        """
        if units.lower() not in ["millimeter", "inch", "micron"]:
            self._messenger.add_warning_message("Wrong unit entered. Setting default to millimiter")
            units = "millimeter"

        if not ipc_path:
            ipc_path = self.edbpath[:-4]+"xml"
        self._messenger.add_info_message("Export IPC 2581 is starting. This operation can take a while...")
        start = time.time()
        result = self.layout_methods.ExportIPC2581FromBuilder(self.builder, ipc_path, units.lower())
        end = time.time() - start
        if result:
            self._messenger.add_info_message("Export IPC 2581 completed in {} sec.".format(end))
            self._messenger.add_info_message("File saved in {}".format(ipc_path))
            return ipc_path
        self._messenger.add_info_message("Error Exporting IPC 2581.")
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
        self._messenger.add_error_message(str(ex_value))
        for el in tblist:
            self._messenger.add_error_message(el)

    @property
    def db(self):
        """Db object."""
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
            self._hfss = Edb3DLayout(self)
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
        if self._active_cell:
            return self.active_cell.GetLayout()
        return None

    # @property
    # def builder(self):
    #     return self.edbutils.HfssUtilities(self.edbpath)

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

    @aedt_exception_handler
    def edb_value(self, val):
        """EDB value.

        Parameters
        ----------
        val :


        Returns
        -------

        """
        return self.edb.Utility.Value(val)

    @aedt_exception_handler
    def close_edb(self):
        """Close EDB.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._db.Close()

        self._clean_variables()
        props = [a for a in dir(self) if not a.startswith("__")]

        for a in props:
            self.__dict__.pop(a, None)
        gc.collect()
        return True

    @aedt_exception_handler
    def save_edb(self):
        """Save the EDB file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._db.Save()
        return True

    @aedt_exception_handler
    def save_edb_as(self, fname):
        """Save the EDB as another file.

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

    @aedt_exception_handler
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

    @aedt_exception_handler
    def import_cadence_file(self, inputBrd, WorkDir=None, anstranslator_full_path="", use_ppe=False):
        """Import a BRD file and generate an ``edb.def`` file in the working directory.

        Parameters
        ----------
        inputBrd : str
            Full path to the BRD file.
        WorkDir : str
            Directory in which to create the ``aedb`` folder. The AEDB file name will be
            the same as the BRD file name. The default value is ``None``.
        anstranslator_full_path : str, optional
            Optional AnsTranslator full path.
        use_ppe : bool
            Whether to use or not PPE License. The default is ``False``.
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

    @aedt_exception_handler
    def import_gds_file(self, inputGDS, WorkDir=None, anstranslator_full_path="", use_ppe=False):
        """Import a GDS file and generate an ``edb.def`` file in the working directory.

        Parameters
        ----------
        inputGDS : str
            Full path to the GDS file.
        WorkDir : str
            Directory in which to create the ``aedb`` folder. The AEDB file name will be
            the same as the GDS file name. The default value is ``None``.
        anstranslator_full_path : str, optional
            Optional AnsTranslator full path.
        use_ppe : bool
            Whether to use or not PPE License. The default is ``False``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.import_layout_pcb(
            inputGDS, working_dir=WorkDir, anstranslator_full_path=anstranslator_full_path, use_ppe=use_ppe
        ):
            return True
        else:
            return False

    def create_cutout(
        self,
        signal_list,
        reference_list=["GND"],
        extent_type="Conforming",
        expansion_size=0.002,
        use_round_corner=False,
        output_aedb_path=None,
        replace_design_with_cutout=True,
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
        replace_design_with_cutout : bool, optional
            Whether to replace the design with the cutout. The default
            is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        _signal_nets = []
        # validate nets in layout
        for _sig in signal_list:
            _netobj = self.edb.Cell.Net.FindByName(self.active_layout, _sig)
            _signal_nets.append(_netobj)

        _ref_nets = []
        # validate references in layout
        for _ref in reference_list:
            _netobj = self.edb.Cell.Net.FindByName(self.active_layout, _ref)
            _ref_nets.append(_netobj)

        from .edb_core.general import convert_py_list_to_net_list

        _netsClip = [
            self.edb.Cell.Net.FindByName(self.active_layout, reference_list[i]) for i, p in enumerate(reference_list)
        ]
        _netsClip = convert_py_list_to_net_list(_netsClip)
        net_signals = convert_py_list_to_net_list(_signal_nets)
        if extent_type == "Conforming":
            _poly = self.active_layout.GetExpandedExtentFromNets(
                net_signals, self.edb.Geometry.ExtentType.Conforming, expansion_size, False, use_round_corner, 1
            )
        else:
            _poly = self.active_layout.GetExpandedExtentFromNets(
                net_signals, self.edb.Geometry.ExtentType.BoundingBox, expansion_size, False, use_round_corner, 1
            )

        # Create new cutout cell/design
        _cutout = self.active_cell.CutOut(net_signals, _netsClip, _poly)

        # The analysis setup(s) do not come over with the clipped design copy,
        # so add the analysis setup(s) from the original here
        for _setup in self.active_cell.SimulationSetups:
            # Empty string '' if coming from setup copy and don't set explicitly.
            _setup_name = _setup.GetName()
            if "GetSimSetupInfo" in dir(_setup):
                # setup is an Ansys.Ansoft.Edb.Utility.HFSSSimulationSetup object
                _hfssSimSetupInfo = _setup.GetSimSetupInfo()
                _hfssSimSetupInfo.Name = "HFSS Setup 1"  # Set name of analysis setup
                # Write the simulation setup info into the cell/design setup
                _setup.SetSimSetupInfo(_hfssSimSetupInfo)
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design

        _dbCells = [_cutout]
        if replace_design_with_cutout == True:
            self.active_cell.Delete()
        else:
            _dbCells.append(self.active_cell)

        if output_aedb_path:
            db2 = self.edb.Database.Create(output_aedb_path)
            # Function input is the name of a .aedb folder inside which the edb.def will be created.
            # Ex: 'D:/backedup/EDB/TEST PROJECTS/CUTOUT/N1.aedb'
            _dbCells = convert_py_list_to_net_list(_dbCells)
            db2.CopyCells(_dbCells)  # Copies cutout cell/design to db2 project
            _success = db2.Save()
            self._db = db2
            self.edbpath = output_aedb_path
            self._active_cell = list(self._db.TopCircuitCells)[0]
            self.builder = retry_ntimes(
                10,
                self.layout_methods.GetBuilder,
                self._db,
                self._active_cell,
                self.edbpath,
                self.edbversion,
                self.standalone,
            )
            self._init_objects()
        return True

    @aedt_exception_handler
    def write_export3d_option_config_file(self, path_to_output, config_dictionaries=None):
        """Write the options for a 3D export to a configuration file.

        Parameters
        ----------
        path_to_output : str
            Full path to the configuration file where the 3D export options are to be saved.

        config_dictionaries : dict, optional

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

    @aedt_exception_handler
    def export_hfss(self, path_to_output, net_list=None, num_cores=None):
        """Export EDB to HFSS.

        Parameters
        ----------
        path_to_output : str
            Full path and name for saving the AEDT file.
        net_list : list, optional
            List of nets to export if only certain ones are to be
            included.
        num_cores : int, optional
            Define number of cores to use during export

        Returns
        -------
        str
            Full path to the AEDT file.

        Examples
        --------

        >>> from pyaedt import Edb

        >>> edb = Edb(edbpath=r"C:\temp\myproject.aedb", edbversion="2021.1")

        >>> options_config = {'UNITE_NETS' : 1, 'LAUNCH_Q3D' : 0}
        >>> edb.write_export3d_option_config_file(r"C:\temp", options_config)
        >>> edb.export_hfss(r"C:\temp")
        "C:\\temp\\hfss_siwave.aedt"

        """
        siwave_s = SiwaveSolve(self.edbpath, aedt_installer_path=self.base_path)
        return siwave_s.export_3d_cad("HFSS", path_to_output, net_list, num_cores)

    @aedt_exception_handler
    def export_q3d(self, path_to_output, net_list=None, num_cores=None):
        """Export EDB to Q3D.

        Parameters
        ----------
        path_to_output : str
            Full path and name for saving the AEDT file.
        net_list : list, optional
            List of nets only if certain ones are to be
            exported.
        num_cores : int, optional
            Define number of cores to use during export

        Returns
        -------
        str
            Path to the AEDT file.

        Examples
        --------

        >>> from pyaedt import Edb

        >>> edb = Edb(edbpath=r"C:\temp\myproject.aedb", edbversion="2021.1")

        >>> options_config = {'UNITE_NETS' : 1, 'LAUNCH_Q3D' : 0}
        >>> edb.write_export3d_option_config_file(r"C:\temp", options_config)
        >>> edb.export_q3d(r"C:\temp")
        "C:\\temp\\q3d_siwave.aedt"

        """

        siwave_s = SiwaveSolve(self.edbpath, aedt_installer_path=self.base_path)
        return siwave_s.export_3d_cad("Q3D", path_to_output, net_list, num_cores=num_cores)

    @aedt_exception_handler
    def export_maxwell(self, path_to_output, net_list=None, num_cores=None):
        """Export EDB to Maxwell 3D.

        Parameters
        ----------
        path_to_output : str
            Full path and name for saving the AEDT file.
        net_list : list, optional
            List of nets only if certain ones are to be
            exported.
        num_cores : int, optional
            Define number of cores to use during export

        Returns
        -------
        str
            Path to the AEDT file.

        Examples
        --------

        >>> from pyaedt import Edb

        >>> edb = Edb(edbpath=r"C:\temp\myproject.aedb", edbversion="2021.1")

        >>> options_config = {'UNITE_NETS' : 1, 'LAUNCH_Q3D' : 0}
        >>> edb.write_export3d_option_config_file(r"C:\temp", options_config)
        >>> edb.export_maxwell(r"C:\temp")
        "C:\\temp\\maxwell_siwave.aedt"

        """
        siwave_s = SiwaveSolve(self.edbpath, aedt_installer_path=self.base_path)
        return siwave_s.export_3d_cad("Maxwell", path_to_output, net_list, num_cores=num_cores)

    @aedt_exception_handler
    def solve_siwave(self):
        """Close Edb and Solves it with Siwave.

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

    @aedt_exception_handler
    def add_design_variable(self, variable_name, variable_value):
        """Add a Design Variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable
        variable_value : str, float
            Value of the variable with units.

        Returns
        -------
        tuple
            tuple containing AddVariable Result and variableserver.
        """
        var_server = self.active_cell.GetVariableServer()
        variables = var_server.GetAllVariableNames()
        if variable_name in list(variables):
            self._messenger.add_warning_message("Parameter {} exists. Using it.".format(variable_name))
            return False, var_server
        else:
            self._messenger.add_info_message("Creating Parameter {}.".format(variable_name))
            var_server.AddVariable(variable_name, self.edb_value(variable_value), True)
            return True, var_server
