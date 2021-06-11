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
            if env_path(self.edbversion) in os.environ:
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
            self.builder = self.layout_methods.OpenEdbStandAlone(self.edbpath, self.edbversion)
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
                if not edbpath:
                    self._messenger = EDBMessageManager(r'C:\Temp')
                else:
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

            if ".aedb" in edbpath:
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
            self._primitives = None
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
        if not self._primitives:
            self._primitives = EdbLayout(self)
        return self._primitives

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
        if self.import_layout_pcb(inputBrd, working_dir=WorkDir):
            return True
        else:
            return False



    # def get_padstack_data_parameters(self, PadStackDef):
    #     """
    #     Get all Padstak data parameters.
    #
    #
    #     :param PadStackDef:  Padstack Definition object
    #     :return: dictionary of parameters
    #     """
    #     Antipad = self.edb_core.Definition.PadType.AntiPad
    #     Pad = self.edb_core.Definition.PadType.RegularPad
    #     GeometryType = self.edb_core.Definition.PadGeometryType.Rectangle
    #     PadStackDefName = PadStackDef.GetName()
    #     PadStackDefData = PadStackDef.GetData()
    #     LayerNames = PadStackDefData.GetLayerNames()
    #     padstack_pars={}
    #     for Layer in LayerNames:
    #         if _ironpython:
    #             LayPad = PadStackDefData.GetPadParametersValue(Layer, Pad)
    #         else:
    #             value0 = self.edb_value("0.0um")
    #             xOffset = Double(0.0)
    #             yOffset = Double(0.0)
    #             rotation = Double(0.0)
    #             padparam_array = Array[Double]([])
    #             PadStackDefData.GetPadParameters(11, Pad, GeometryType, padparam_array, xOffset,
    #                                                            yOffset, rotation)
    #
    #         if LayPad[0]:
    #             PadDiameter = LayPad[2][0]
    #
    #         LayAntipad = PadStackDefData.GetPadParametersValue(Layer, Antipad)
    #         if LayAntipad[0]:
    #             AntiPadDiameter = LayAntipad[2][0]
    #
    #         padstack_pars[PadStackDefName] ={"Layer": Layer, "PadDiameter": PadDiameter, "AntiPadDiameter": AntiPadDiameter}
    #     return padstack_pars


    @aedt_exception_handler
    def get_rlc_from_signal_nets(self, CmpDict=None):
        """Get RLC from signal Nets.

        Parameters
        ----------
        CmpDict :
            Dictionary of components. The default value is ``None``.

        Returns
        -------
        type
            List of components that belong to signal Nets.

        """
        # CmpInf = self.GetCmpInf(layout)
        RlcFromSignalNets = {}
        for cmp in CmpDict.keys():
            if CmpDict[cmp]['PartType'] in ['Capacitor', 'Resistor', 'Inductor']:
                if not self.is_power_gound_net(CmpDict[cmp]['Nets']):
                    CmpNets = CmpDict[cmp]['Nets']
                    RlcFromSignalNets[cmp] = CmpNets
        return RlcFromSignalNets

    @aedt_exception_handler
    def is_power_gound_net(self, NetNameList):
        """Return ``True`` if one of the nets in the list is power or ground.

        Parameters
        ----------
        NetNameList :
            List of net names.

        Returns
        -------
        type
            ``True`` if one of the net names is ``power`` or ``ground``.

        """
        for nn in range(len(NetNameList)):
            net = self.edb.Cell.Net.FindByName(self.active_layout, NetNameList[nn])
            if net.IsPowerGround():
                return True
        return False

    @aedt_exception_handler
    def get_rl_from_nets(self, CmpDict):
        """Return an array of components with RL based on a component dictionary.

        Parameters
        ----------
        CmpDict :
            Input component dictionary

        Returns
        -------
        type
            Componenet nets for the component dictionary.

        """
        RlFromNets = {}
        for cmp in CmpDict.keys():
            if CmpDict[cmp]['PartType'] in ['Resistor', 'Inductor']:
                CmpNets = CmpDict[cmp]['Nets']
                RlFromNets[cmp] = CmpNets
        return RlFromNets

    @aedt_exception_handler
    def get_rl_for_DC_path(self, CmpDict, ResMaxValue=10):
        """Return the Rl DC path of a specific dictionary list.

        Parameters
        ----------
        CmpDict :
            Dictionary of components.
        ResMaxValue :
            Maximum value of resistance to consider in the DC path. The default value is ``10``.

        Returns
        -------
        type
            Dictionary of components with nets.

        """
        RlDCPath = {}
        for cmp in CmpDict.keys():
            if CmpDict[cmp]['PartType'] in ['Resistor', 'Inductor']:
                CmpNets = CmpDict[cmp]['Nets']
                if CmpDict[cmp]['ResValue']:
                    if len(CmpNets) == 2:
                        if not 'gnd' in [net.lower() for net in CmpNets]:
                            if CmpDict[cmp]['ResValue'] < ResMaxValue:
                                RlDCPath[cmp] = CmpNets
                    elif len(CmpNets) > 2:
                        NetList = list(set([net.lower() for net in CmpNets]))
                        if (len(NetList) == 2) and not ('gnd' in NetList) and (CmpDict[cmp]['ResValue'] < ResMaxValue):
                            RlDCPath[cmp] = CmpNets
                        elif (len(NetList) > 2) and (CmpDict[cmp]['ResValue'] < ResMaxValue):
                            RlDCPath[cmp] = CmpNets
                        else:
                            pass
                else:
                    pass
        return RlDCPath





    @aedt_exception_handler
    def create_multipin_rlc(self, componentType, baseComponent, positiveNetName, negativeNetName, value=None, s2pPath=None):
        """

        Parameters
        ----------
        componentType :
            
        baseComponent :
            
        positiveNetName :
            
        negativeNetName :
            
        value :
             The default is ``None``.
        s2pPath :
             The default is ``None``.

        Returns
        -------

        """
        returnOnError = None

        baseComponentName = baseComponent.GetName()
        layout = baseComponent.GetLayout()

        positivePins, negativePins, componentTransform = self.dissolve_component(baseComponent, positiveNetName, negativeNetName)
        if positivePins is None or negativePins is None:
            self._messenger.add_error_message('Component {} - failed to dissolve'.format(baseComponentName))
            return returnOnError

        twoPinComponent, extraPinsComponent = self.create_divided_componenets(positivePins, negativePins, componentTransform, baseComponentName, layout)
        if twoPinComponent is None or twoPinComponent.IsNull() or \
            extraPinsComponent is None or extraPinsComponent.IsNull():
            self._messenger.add_error_message('Component {} - failed to create divided component'.format(baseComponentName))
            return returnOnError

        positiveGroupName = '{}_positive_group'.format(baseComponentName)
        positiveGroup = self.create_pingroup_from_pins(positivePins, positiveGroupName, layout)
        if positiveGroup is None or positiveGroup.IsNull():
            self._messenger.add_error_message('Component {} - failed to create positive pin group'.format(baseComponentName))
            return returnOnError

        negativeGroupName = '{}_negative_group'.format(baseComponentName)
        negativeGroup = self.create_pingroup_from_pins(negativePins, negativeGroupName, layout)
        if negativeGroup is None or negativeGroup.IsNull():
            self._messenger.add_error_message('Component {} - failed to create negative pin group'.format(baseComponentName))
            return returnOnError

        if not self.create_model_on_component(componentType, twoPinComponent, value, s2pPath, negativeNetName):
            self._messenger.add_error_message('Component {} - failed to create model on component'.format(baseComponentName))
            return returnOnError

        return twoPinComponent

    @aedt_exception_handler
    def dissolve_component(self, component, positiveNetName, negativeNetName):
        """

        Parameters
        ----------
        component :
            
        positiveNetName :
            
        negativeNetName :
            

        Returns
        -------

        """
        returnOnError = (None, None)

        positivePins = self.get_pin_from_component(component, positiveNetName)
        if positivePins is None:
            self._messenger.add_error_message('Failed to get positive pins when dissolving component.')
            return returnOnError
        if len(positivePins) < 1:
            self._messenger.add_error_message('No positive pins in net {} on component {}'.format(positiveNetName, component.GetName()))
            return returnOnError

        negativePins = self.get_pin_from_component(component, negativeNetName)
        if negativePins is None:
            self._messenger.add_error_message('Failed to get negative pins when dissolving component.')
            return returnOnError
        if len(negativePins) < 1:
            self._messenger.add_error_message('No negative pins are present in net {} on component {}'.format(negativeNetName, component.GetName()))
            return returnOnError

        for pin in positivePins + negativePins:
            if not component.RemoveMember(pin):
                self._messenger.add_error_message('Failed to remove pin {} from component {}'.format(pin.GetName(), component.GetName()))

        componentTransform = component.GetTransform()
        component.Delete()

        return positivePins, negativePins, componentTransform

    @aedt_exception_handler
    def create_divided_componenets(self, positivePins, negativePins, componentTransform, baseComponentName, layout):
        """

        Parameters
        ----------
        positivePins :
            
        negativePins :
            
        componentTransform :
            
        baseComponentName :
            
        layout :
            

        Returns
        -------

        """
        returnOnError = (None, None)

        if positivePins is None or len(positivePins) < 1:
            self._messenger.add_error_message('No positive pins supplied for component')
            return returnOnError

        if negativePins is None or len(negativePins) < 1:
            self._messenger.add_error_message('No negative pins supplied for component')
            return returnOnError

        if len(positivePins) < 2 and len(negativePins) < 2:
            self._messenger.add_error_message('Less than two pins in both positive and negative pin lists')
            return returnOnError

        if any(map(lambda p: not p.GetComponent().IsNull(), positivePins)):
            self._messenger.add_error_message('At least one positive pin already belongs to a component')
            return returnOnError

        if any(map(lambda p: not p.GetComponent().IsNull(), negativePins)):
            self._messenger.add_error_message('At least one negative pin already belongs to a component')
            return returnOnError

        twoPinPositivePin = positivePins[0]
        twoPinNegativePin = negativePins[0]

        extraPinsPositivePins = positivePins[1:]
        extraPinsNegativePins = negativePins[1:]

        twoPinComponentName = '{}_two_pin'.format(baseComponentName)
        twoPinComponent = self.create_component_from_pins([twoPinPositivePin, twoPinNegativePin], componentTransform, twoPinComponentName, layout)
        if twoPinComponent is None or twoPinComponent.IsNull():
            self._messenger.add_error_message('Failed to create two pin component of divided pair')
            return returnOnError

        extraPinsComponentName = '{}_extra_pins'.format(baseComponentName)
        extraPinsComponent = self.create_component_from_pins(extraPinsPositivePins + extraPinsNegativePins, componentTransform, extraPinsComponentName, layout)
        if extraPinsComponent is None or extraPinsComponent.IsNull():
            self._messenger.add_error_message('Failed to create extra pins component of divided pair')
            return returnOnError

        return twoPinComponent, extraPinsComponent

