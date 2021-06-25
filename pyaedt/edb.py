# -*- coding: utf-8 -*-
"""
This module contains all EDB functionalities in the ``Edb`` class. It inherits all objects that belong to EDB.

This module is implicitily loaded in HFSS 3D Layout when launched.


Examples
--------
Create an ``Edb`` object and a new EDB cell.

>>> app = Edb()     

Create an ``Edb`` object and open the specified project.

>>> app = Edb("myfile.aedb")

"""

import os
import sys
import traceback
import warnings

import pyaedt.edb_core.EDB_Data
try:
    import ScriptEnv
    ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
    inside_desktop = True
except:
    inside_desktop = False
try:
    import clr
    from System.Collections.Generic import List, Dictionary
    from System import Convert, String
    import System

    from System import Double, Array
    from System.Collections.Generic import List
    _ironpython = False
    if "IronPython" in sys.version or ".NETFramework" in sys.version:
        _ironpython = True
    edb_initialized = True
except ImportError:
    warnings.warn("The clr is missing. Install Pythonnet or use an Ironpython version if you want to use the EDB Module.")
    edb_initialized = False


from .application.MessageManager import EDBMessageManager
from .edb_core import *

from .generic.general_methods import get_filename_without_extension, generate_unique_name, aedt_exception_handler, env_path, env_value


class Edb(object):
    """EDB object

    Parameters
    ----------
    edbpath : str
        Full path to the ``aedb`` folder.
    cellname : str
        Name of the cell to select.
    isreadonly : bool, optional
        Whether to open ``edb_core`` in read-only mode when it is owned by HFSS 3D Layout. The default is ``False``.
    edbversion : str, optional
        Version of ``edb_core`` to use. The default is ``"2021.1"``.
    isaedtowned : bool, optional
        Whether to launch ``edb_core`` from HFSS 3D Layout. The default is ``False``.

    Returns
    -------

    """
    @aedt_exception_handler
    def _init_dlls(self):
        """ """
        sys.path.append(os.path.join(os.path.dirname(__file__), "dlls", "EDBLib"))
        if os.name == 'posix':
            if env_value(self.edbversion) in os.environ:
                self.base_path = env_path(self.edbversion)
                sys.path.append(self.base_path)
            else:
                main = sys.modules["__main__"]
                if "oDesktop" in dir(main):
                    self.base_path = main.oDesktop.GetExeDir()
                    sys.path.append(main.oDesktop.GetExeDir())
                    os.environ[env_value(self.edbversion)] = self.base_path
            clr.AddReferenceToFile('Ansys.Ansoft.Edb.dll')
            clr.AddReferenceToFile('Ansys.Ansoft.EdbBuilderUtils.dll')
            clr.AddReferenceToFile('EdbLib.dll')
            clr.AddReferenceToFileAndPath(os.path.join(self.base_path, 'Ansys.Ansoft.SimSetupData.dll'))
        else:
            self.base_path = env_path( self.edbversion)
            sys.path.append(self.base_path)
            clr.AddReference('Ansys.Ansoft.Edb')
            clr.AddReference('Ansys.Ansoft.EdbBuilderUtils')
            clr.AddReference('EdbLib')
            clr.AddReference('Ansys.Ansoft.SimSetupData')

        os.environ["ECAD_TRANSLATORS_INSTALL_DIR"] = self.base_path
        oaDirectory = os.path.join(self.base_path, 'common', 'oa')
        os.environ['ANSYS_OADIR'] = oaDirectory
        os.environ['PATH'] = '{};{}'.format(os.environ['PATH'], self.base_path)
        edb =__import__('Ansys.Ansoft.Edb')
        self.edb = edb.Ansoft.Edb
        edbbuilder=__import__('Ansys.Ansoft.EdbBuilderUtils')
        self.edblib = __import__('EdbLib')
        self.edbutils = edbbuilder.Ansoft.EdbBuilderUtils
        self.simSetup = __import__('Ansys.Ansoft.SimSetupData')
        self.layout_methods = self.edblib.Layout.LayoutMethods
        self.simsetupdata = self.simSetup.Ansoft.SimSetupData.Data


    @aedt_exception_handler
    def open_edb(self, init_dlls=False):
        """

        Parameters
        ----------
        init_dlls : bool
             Whether to initialize DLLs. The default is ``False``.

        Returns
        -------

        """
        if init_dlls:
            self._init_dlls()

        if not self.isreadonly:
            print(self.edbpath)
            print(self.edbversion)
            print(_ironpython)
            print(dir())

            if _ironpython and  inside_desktop:
                print("opening from DB")
                self._db = self.edb.Database.Open(self.edbpath, self.isreadonly)
                self._active_cell =  list(self._db.TopCircuitCells)[0]
                self.builder = self.layout_methods.GetBuilder(self._db, self._active_cell)
            else:
                print("opening from EDBLib")
                self.builder = self.layout_methods.OpenEdbStandAlone(self.edbpath, self.edbversion)
                self._db = self.builder.EdbHandler.dB
                self._active_cell = self.builder.EdbHandler.cell
        else:
            if _ironpython and  inside_desktop:
                self._db = self.edb.Database.Open(self.edbpath, self.isreadonly)
                self._active_cell =  list(self._db.TopCircuitCells)[0]
                self.builder = self.layout_methods.GetBuilder(self._db, self._active_cell)
            else:
                self.builder = self.layout_methods.OpenEdbInAedt(self.edbpath, self.edbversion)
                self._db = self.builder.EdbHandler.dB
                self._active_cell = self.builder.EdbHandler.cell
        return self.builder

    @aedt_exception_handler
    def open_edb_inside_aedt(self, init_dlls=False):
        """

        Parameters
        ----------
        init_dlls :
             Whether to initialize DLLs. The default is ``False``.

        Returns
        -------

        """
        if init_dlls:
            self._init_dlls()
        self._messenger.add_info_message("Opening EDB from HDL")
        self.edb.Database.SetRunAsStandAlone(False)
        hdl = Convert.ToUInt64(self.oproject.GetEDBHandle())
        print(hdl)
        self._db = self.edb.Database.Attach(hdl)
        print(self._db)
        print(self.cellname)
        self._active_cell = self.edb.Cell.Cell.FindByName(self.db, self.edb.Cell.CellType.CircuitCell, self.cellname)
        self.builder = self.layout_methods.GetBuilder(self.db, self._active_cell)
        print("active cell set")
        return self.builder

    @aedt_exception_handler
    def create_edb(self, init_dlls=False):
        """

        Parameters
        ----------
        init_dlls :
             Whether to initialize DLLs. The default is ``False``.

        Returns
        -------

        """
        if init_dlls:
            self._init_dlls()
        self.edb.Database.SetRunAsStandAlone(True)
        self._db = self.edb.Database.Create(self.edbpath)
        if not self.cellname:
            self.cellname = generate_unique_name("Cell")

        self._active_cell = self.edb.Cell.Cell.Create(self._db,  self.edb.Cell.CellType.CircuitCell, self.cellname)

        self.builder = self.layout_methods.GetBuilder(self.db, self._active_cell)
        print("active cell set")
        return self.builder

    @aedt_exception_handler
    def import_layout_pcb(self, input_file, working_dir, init_dlls=False):
        """Import a brd file and generate an ``edb.def`` file in the working directory.

        Parameters
        ----------
        input_file : str
            Full path to the brd file.
        working_dir : str
            Directory in which to create the ``aedb`` folder. The aedb name will be the same as the brd name.
        init_dlls : bool
             Whether to initialize DLLs. The default is ``False``.

        Returns
        -------
        type
            Full path to the aedb file.

        """
        if init_dlls:
            self._init_dlls()
        aedb_name= os.path.splitext(os.path.basename(input_file))[0] + ".aedb"
        output = self.layout_methods.ImportCadToEdb(input_file, os.path.join(working_dir, aedb_name), self.edbversion)
        assert output.Item1, "Error Importing File"
        self.builder = output.Item2
        self._db = self.builder.EdbHandler.dB
        self._active_cell = self.builder.EdbHandler.cell
        return self.builder


    def __init__(self, edbpath=None, cellname=None, isreadonly=False, edbversion="2021.1", isaedtowned=False, oproject=None):
        if edb_initialized:
            self.oproject = oproject
            if isaedtowned:
                self._main = sys.modules['__main__']
                self._messenger = self._main.oMessenger
            else:
                if not edbpath or not os.path.exists(edbpath):
                    self._messenger = EDBMessageManager(r'C:\Temp')
                elif os.path.exists(edbpath):
                    self._messenger = EDBMessageManager(edbpath)


            self._messenger.add_info_message("Messenger Initialized in EDB")
            self.edbversion = edbversion
            self.isaedtowned = isaedtowned


            self._init_dlls()
            self._db = None
            # self._edb.Database.SetRunAsStandAlone(not isaedtowned)
            self.isreadonly = isreadonly
            self.cellname = cellname
            self.edbpath = edbpath
            if not os.path.exists(self.edbpath):
                self.create_edb()
            elif ".aedb" in edbpath:
                self.edbpath = edbpath
                if isaedtowned and "isoutsideDesktop" in dir(self._main) and not self._main.isoutsideDesktop:
                    self.open_edb_inside_aedt()
                else:
                    self.open_edb()
            elif edbpath[-3:] in ["brd", "gds", "xml", "dxf"]:
                self.edbpath = edbpath[-3:] + ".aedb"
                working_dir = os.path.dirname(edbpath)
                self.import_layout_pcb(edbpath, working_dir)
            self._components = None
            self._core_primitives = None
            self._stackup = None
            self._padstack = None
            self._siwave = None
            self._hfss = None
            self._nets = None
        else:
            self._db = None
            self._edb = None
            pass

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type:
            self.edb_exception(ex_value, ex_traceback)

    def edb_exception(self, ex_value, tb_data):
        """Write the trace stack to the desktop when a python error occurs.

        Parameters
        ----------
        ex_value :
            
        tb_data :
            

        Returns
        -------

        """
        tb_trace = traceback.format_tb(tb_data)
        tblist = tb_trace[0].split('\n')
        self._messenger.add_error_message(str(ex_value))
        for el in tblist:
            self._messenger.add_error_message(el)

    @property
    def messenger(self):
        """ """
        return self._messenger

    @property
    def db(self):
        """ """
        # if self.builder:
        #     self._db = self.builder.EdbHandler.dB
        #     return self._db
        # else:
        #     self.db = self.edbpath
        return self._db

    # @db.setter
    # def db(self, edbpath):
    #     # if self.edb_core:
    #     #     if os.path.exists(os.path.join(edbpath, "edb.def")):
    #     #         self._db = self.edb_core.Database.Open(edbpath, self.isreadonly)
    #     #     else:
    #     #         self._db = None
    #     #         self._messenger.add_error_message("Edb path not found")
    #     try:
    #         if self.oproject:
    #             if self._main.isoutsideDesktop:
    #                 self._messenger.add_info_message("Opening EDB from File")
    #                 self.edb_core.Database.SetRunAsStandAlone(True)
    #                 if self.edbutils:
    #                     if os.path.exists(os.path.join(edbpath, "edb.def")):
    #                         self.builder = self.edbutils.HfssUtilities(edbpath)
    #                         self._db = self.builder.dB
    #                     else:
    #                         self._db = None
    #                         self._messenger.add_warning_message("Edb path not found")
    #             else:
    #                 self._messenger.add_info_message("Opening EDB from HDL")
    #                 self.edb_core.Database.SetRunAsStandAlone(False)
    #                 hdl = Convert.ToUInt64(self.oproject.GetEDBHandle())
    #                 self._db = self.edb_core.Database.Attach(hdl)
    #
    #         else:
    #             self.edb_core.Database.SetRunAsStandAlone(True)
    #             if self.edbutils:
    #                 if os.path.exists(os.path.join(edbpath, "edb.def")):
    #                     self.builder = self.edbutils.HfssUtilities(edbpath)
    #                     self._db = self.builder.dB
    #                 else:
    #                     self._db = None
    #                     self._messenger.add_warning_message("Edb path not found")
    #         self.active_cell = self.cellname
    #     except:
    #         self._db = None

    @property
    def active_cell(self):
        """ """
        return self._active_cell


    @property
    def core_components(self):
        """ """
        if not self._components:
            self._components = Components(self)
        return self._components

    @property
    def core_stackup(self):
        """ """
        if not self._stackup:
            self._stackup = EdbStackup(self)
        return self._stackup

    @property
    def core_padstack(self):
        """ """
        if not self._padstack:
            self._padstack = EdbPadstacks(self)
        return self._padstack

    @property
    def core_siwave(self):
        """ """
        if not self._siwave:
            self._siwave = EdBSiwave(self)
        return self._siwave

    @property
    def core_hfss(self):
        """ """
        if not self._hfss:
            self._hfss = Edb3DLayout(self)
        return self._hfss

    @property
    def core_nets(self):
        """ """
        if not self._nets:
            self._nets = EdbNets(self)
        return self._nets

    @property
    def core_primitives(self):
        """ """
        if not self._core_primitives:
            self._core_primitives = EdbLayout(self)
        return self._core_primitives

    @property
    def active_layout(self):
        """ """
        return self.active_cell.GetLayout()

    # @property
    # def builder(self):
    #     return self.edbutils.HfssUtilities(self.edbpath)

    @property
    def pins(self):
        """:return:List of All Pins"""
        pins=[]
        for el in self.core_components.components:
            comp = self.edb.Cell.Hierarchy.Component.FindByName(self.active_layout, el)
            temp = [p for p in comp.LayoutObjs if
                    p.GetObjType() == self.edb.Cell.LayoutObjType.PadstackInstance and p.IsLayoutPin()]
            pins += temp
        return pins



    class Boundaries:
        """ """
        (Port, Pec, RLC, CurrentSource, VoltageSource, NexximGround, NexximPort, DcTerminal, VoltageProbe) = range(0, 9)

    @aedt_exception_handler
    def edb_value(self, val):
        """

        Parameters
        ----------
        val :
            

        Returns
        -------

        """
        return self.edb.Utility.Value(val)

    @aedt_exception_handler
    def close_edb(self):
        """ """
        self._db.Close()
        return True

    @aedt_exception_handler
    def save_edb(self):
        """ """
        self._db.Save()
        return True

    @aedt_exception_handler
    def save_edb_as(self, fname):
        """

        Parameters
        ----------
        fname

        Returns
        -------

        """
        self._db.SaveAs(fname)
        return True

    @aedt_exception_handler
    def execute(self, func):
        """

        Parameters
        ----------
        func :
            

        Returns
        -------

        """
        return self.edb.Utility.Command.Execute(func)



    @aedt_exception_handler
    def import_cadence_file(self, inputBrd, WorkDir=None):
        """Import a brd file and generate an ``edb.def`` file in the working directory.

        Parameters
        ----------
        inputBrd : str
            Full path to the brd file.
        WorkDir : str
            The directory in which to create the ``aedb`` folder. The aedb name will be the same as the brd name. The default value is ``None``.

        Returns
        -------
        type
            Boolean

        """
        if self.import_layout_pcb(inputBrd, working_dir=WorkDir):
            return True
        else:
            return False

    @aedt_exception_handler
    def import_gds_file(self, inputGDS, WorkDir=None):
        """Import a brd file and generate an ``edb.def`` file in the working directory.

        Parameters
        ----------
        inputGDS : str
            Full path to the brd file.
        WorkDir : str
            The directory in which to create the ``aedb` folder. The aedb name will be the same as the brd name. The default value is ``None``.

        Returns
        -------
        type
            The full path to the aedb file.

        """
        if self.import_layout_pcb(inputGDS, working_dir=WorkDir):
            return True
        else:
            return False

    def create_cutout(self, signal_list, reference_list=["GND"], extent_type="Conforming", expansion_size=0.002,
                      use_round_corner=False, output_aedb_path=None, replace_design_with_cutout=True):
        """
        Create a new Cutout and Save it to a new aedb file.

        Parameters
        ----------
        signal_list: list
            list of signal strings
        reference_list: list
            list of reference lists to be added. Default ["GND"]
        extent_type: str
            type of extension: "Conforming" or "Bounding"
        expansion_size: float
            expansion size ratio in meter. Default 2mm
        use_round_corner: bool
        output_aedb_path: str, optional
            the full path to new aedb file
        replace_design_with_cutout

        Returns
        -------

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
        _netsClip = [self.edb.Cell.Net.FindByName(self.active_layout, reference_list[i]) for i, p in
                     enumerate(reference_list)]
        _netsClip = convert_py_list_to_net_list(_netsClip)
        net_signals= convert_py_list_to_net_list(_signal_nets)
        if extent_type == "Conforming":
            _poly = self.active_layout.GetExpandedExtentFromNets(net_signals,
                                                           self.edb.Geometry.ExtentType.Conforming,
                                                           expansion_size,
                                                           False,
                                                           use_round_corner,
                                                           1)
        else:
            _poly = self.active_layout.GetExpandedExtentFromNets(net_signals,
                                                           self.edb.Geometry.ExtentType.BoundingBox,
                                                           expansion_size,
                                                           False,
                                                           use_round_corner,
                                                           1)

        _cutout = self.active_cell.CutOut(net_signals, _netsClip, _poly)  # Create new cutout cell/design

        for _setup in self.active_cell.SimulationSetups:  # The analysis setup(s) do not come over with the clipped design copy, so add the analysis setup(s) from the original here
            _setup_name = _setup.GetName()  # Empty string '' if coming from setup copy and don't set explicitly.
            if "GetSimSetupInfo" in dir(_setup):
                _hfssSimSetupInfo = _setup.GetSimSetupInfo()  # setup is an Ansys.Ansoft.Edb.Utility.HFSSSimulationSetup object
                _hfssSimSetupInfo.Name = 'HFSS Setup 1'  # Set name of analysis setup
                _setup.SetSimSetupInfo(_hfssSimSetupInfo)  # Write the simulation setup info into the cell/design setup
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design

        _dbCells = [_cutout]
        if replace_design_with_cutout == True:
            self.active_cell.Delete()
        else:
            _dbCells.append(self.active_cell)

        if output_aedb_path:
            db2 = self.edb.Database.Create(
                output_aedb_path)  # Function input is the name of a .aedb folder inside which the edb.def will be created. Ex: 'D:/backedup/EDB/TEST PROJECTS/CUTOUT/N1.aedb'
            _dbCells = convert_py_list_to_net_list(_dbCells)
            db2.CopyCells(_dbCells)  # Copies cutout cell/design to db2 project
            _success = db2.Save()
            self._db = db2
            self.edbpath = output_aedb_path
            self._active_cell = _cutout
        return True

