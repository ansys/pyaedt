"""This module contains the `Components` class.

"""
import re
import random

import pyaedt.edb_core.EDB_Data
from .EDB_Data import EDBComponent

from .general import *
from ..generic.general_methods import get_filename_without_extension

try:
    import clr
    clr.AddReference("System")
    from System import Convert, String
    from System import Double, Array
    from System.Collections.Generic import List
except ImportError:
    warnings.warn('This module requires PythonNet.')
from collections import defaultdict

def resistor_value_parser(RValue):
    """Convert a resistor value.

    Parameters
    ----------
    RValue : float
        Resistor value.
        
    Returns
    -------
    float
        Resistor value.
 
    """
    if type(RValue) is str:
        RValue = RValue.replace(" ", "")
        RValue = RValue.replace("meg", "m")
        RValue = RValue.replace("Ohm", "")
        RValue = RValue.replace("ohm", "")
        RValue = RValue.replace("k", "e3")
        RValue = RValue.replace("m", "e-3")
        RValue = RValue.replace("M", "e6")
    RValue = float(RValue)
    return RValue


class Components(object):
    """HFSS 3D application interface.

    This class manages EDB components and related methods.

    Parameters
    ----------
    parent : str
    
    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder")
    >>> edbapp.core_components

    """
    def __init__(self, parent):
        self.parent = parent
        self._cmp = {}
        self._res = {}
        self._cap = {}
        self._ind = {}
        self._ios = {}
        self._ics = {}
        self._others = {}
        self._pins = {}
        self._comps_by_part = {}
        self._init_parts()

    @property
    def _messenger(self):
        """_messenger."""
        return self.parent._messenger

    @property
    def _edb(self):
        return self.parent.edb

    @aedt_exception_handler
    def _init_parts(self):
        a = self.components
        a = self.resistors
        a = self.ICs
        a = self.Others
        a = self.inductors
        a = self.IOs
        a = self.components_by_partname
        return True

    @property
    def _builder(self):
        return self.parent.builder

    @property
    def _edb_value(self):
        return self.parent.edb_value

    @property
    def _edbutils(self):
        return self.parent.edbutils

    @property
    def _active_layout(self):
        return self.parent.active_layout

    @property
    def _cell(self):
        return self.parent.cell

    @property
    def _db(self):
        return self.parent.db

    @property
    def _components_methods(self):
        return self.parent.edblib.Layout.ComponentsMethods

    @property
    def components(self):
        """Component setup information.
                
        Returns
        -------
        dict
            Default dictionary for the EDB comopnent.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.components
        
        """
        if not self._cmp:
            self.refresh_components()
        return self._cmp

    @aedt_exception_handler
    def refresh_components(self):
        """Refresh the component dictionary.

        Returns
        -------
        dict
            Default dictionary for the EDB component.

        """
        self._messenger.add_info_message("Refreshing the Components dictionary.")
        try:
            cmplist = self.get_component_list()
            self._cmp = {}
            for cmp in cmplist:
                self._cmp[cmp.RefDes] = EDBComponent(self, cmp, cmp.RefDes)
        except:
            pass

    @property
    def resistors(self):
        """Resistors.

        Returns
        -------
        dict
            Dictionary of resistors.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.resistors
        """
        self._res = {}
        for el, val in self.components.items():
            if val.type == 'Resistor':
                self._res[el] = val
        return self._res

    @property
    def capacitors(self):
        """Capacitors.
                
        Returns
        -------
        dict
            Dictionary of capacitors.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.capacitors
        """
        self._cap = {}
        for el, val in self.components.items():
            if val.type == 'Capacitor':
                self._cap[el] = val
        return self._cap

    @property
    def inductors(self):
        """Inductors.
                
        Returns
        -------
        dict
            Dictionary of inductors.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.inductors
        
        """
        self._ind = {}
        for el, val in self.components.items():
            if val.type == 'Inductor':
                self._ind[el] = val
        return self._ind


    @property
    def ICs(self):
        """Integrated circuits.
        
        Returns
        -------
        dict
            Dictionary of integrated circuits.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.ICs 
        
        """
        self._ics = {}
        for el, val in self.components.items():
            if val.type == 'IC':
                self._ics[el] = val
        return self._ics


    @property
    def IOs(self):
        """Circuit inupts and outputs.

        Returns
        -------
        dict
            Dictionary of circuit inputs and outputs.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.IOs
        
        """
        self._ios = {}
        for el, val in self.components.items():
            if val.type == 'IO':
                self._ios[el] = val
        return self._ios


    @property
    def Others(self):
        """Other core components.
                
        Parameters
        ----------

        Returns
        -------
        dict
            Dictionary of other core components.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.others
        
        """
        self._others = {}
        for el, val in self.components.items():
            if val.type == 'Other':
                self._others[el] = val
        return self._others


    @property
    def components_by_partname(self):
        """Components by part name.
        
        Returns
        -------
        dict
            Dictionary of components by part name.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.components_by_partname
        
        """
        self._comps_by_part = {}
        for el, val in self.components.items():
            if val.partname in self._comps_by_part.keys():
                self._comps_by_part[val.partname].append(val)
            else:
                self._comps_by_part[val.partname] = [val]
        return self._comps_by_part


    @aedt_exception_handler
    def get_component_list(self):
        """Retrieve a list of the component's EDB objects.

        Returns
        -------
        list
            List of component setup information.

        """
        cmp_setup_info_list = self._edbutils.ComponentSetupInfo.GetFromLayout(
            self._builder.EdbHandler.layout)
        cmp_list = []
        for comp in cmp_setup_info_list:
            cmp_list.append(comp)
        return cmp_list

    @aedt_exception_handler
    def get_component_by_name(self, name):
        """Retrieve a component by name.

        Parameters
        ----------
        name : str
            Name of the component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        edbcmp = self._edb.Cell.Hierarchy.Component.FindByName(self._active_layout, name)
        if edbcmp is not None:
            return edbcmp
        else:
            pass

    @aedt_exception_handler
    def get_components_from_nets(self, netlist=None):
        """Retrieve components from a net list.

        Parameters
        ----------
        netlist : str, optional
            Name of the net list. The default is ``None``.

        Returns
        -------
        list
            List of components that belong to the signal nets.

        """
        cmp_list = []
        if type(netlist) is str:
            netlist = [netlist]
        components = list(self.components.keys())
        for refdes in components:
            cmpnets = self._cmp[refdes].nets
            if set(cmpnets).intersection(set(netlist)):
                cmp_list.append(refdes)
        return cmp_list


    @aedt_exception_handler
    def create_component_from_pins(self, pins, component_name):
        """Create a component from pins.

        Parameters
        ----------
        pins : list
            List of EDB core pins.
        component_name : str
            Name of the reference designator for the component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
       
        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> pins = edbapp.core_components.get_pin_from_component("A1")
        >>> edbapp.core_components.create_component_from_pins(pins, "A1New")
        
        """
        try:
            new_cmp = self._edb.Cell.Hierarchy.Component.Create(self._builder.EdbHandler, component_name)
            new_group = self._edb.Cell.Hierarchy.Group.Create(self._builder.EdbHandler.layout,
                                                                    component_name)
            for pin in pins:
                new_group.AddMember(pin)
            new_cmp.SetGroup(new_group)
            new_cmp_layer_name = pins[0].GetPadstackDef().GetData().GetLayerNames().First()
            new_cmp_placement_layer = self._edb.Cell.Layer.FindByName(
                self._builder.EdbHandler.layout.GetLayerCollection(), new_cmp_layer_name)
            new_cmp.SetPlacementLayer(new_cmp_placement_layer)
            return (True, new_cmp)
        except:
            return (False, None)

    @aedt_exception_handler
    def set_component_model(self, componentname, model_type="Spice", modelpath=None, modelname=None):
        """Assign a Spice or Touchstone model to a component.
        
        Parameters
        ----------
        componentname : str
            Name of the component.
        model_type : str, optional
            Type of the model. Options are ``"Spice"`` and
            ``"Touchstone"``.  The default is ``"Spice"``.
        modelpath : str, optional
            Full path to the model file. The default is ``None``.
        modelname : str, optional
            Name of the model. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        Examples
        --------    

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.set_component_model("A1", model_type="Spice", 
        ...                                            modelpath="pathtospfile", 
        ...                                            modelname="spicemodelname")
        
        """
        if not modelname:
            modelname = get_filename_without_extension(modelpath)
        edbComponent = self.get_component_by_name(componentname)
        if str(edbComponent.EDBHandle)=="0":
            return False
        edbRlcComponentProperty = edbComponent.GetComponentProperty().Clone()

        componentPins = self.get_pin_from_component(componentname)
        componentNets = self.get_nets_from_pin_list(componentPins)
        pinNumber = len(componentPins)
        if model_type =="Spice":
            with open(modelpath, "r") as f:
                for line in f:
                    if "subckt" in line.lower():
                        pinNames = [i.strip() for i in re.split(' |\t', line) if i]
                        pinNames.remove(pinNames[0])
                        pinNames.remove(pinNames[0])
                        break
            if len(pinNames) == pinNumber:
                spiceMod = self._edb.Cell.Hierarchy.SPICEModel()
                spiceMod.SetModelPath(modelpath)
                spiceMod.SetModelName(modelname)
                terminal = 1
                for pn in pinNames:
                    spiceMod.AddTerminalPinPair(pn, str(terminal))
                    terminal+=1

                edbRlcComponentProperty.SetModel(spiceMod)
                if not edbComponent.SetComponentProperty(edbRlcComponentProperty):
                    self._messenger.add_error_message("Error Assigning the Touchstone model")
                    return False
            else:
                self._messenger.add_error_message("Wrong number of Pins")
                return False

        elif model_type=="Touchstone":

            nPortModelName = modelname
            edbComponentDef = edbComponent.GetComponentDef()
            nPortModel = self._edb.Definition.NPortComponentModel.FindByName(edbComponentDef, nPortModelName)
            if nPortModel.IsNull():
                nPortModel = self._edb.Definition.NPortComponentModel.Create(nPortModelName)
                nPortModel.SetReferenceFile(modelpath)
                edbComponentDef.AddComponentModel(nPortModel)

            sParameterMod = self._edb.Cell.Hierarchy.SParameterModel()
            sParameterMod.SetComponentModelName(nPortModel)
            gndnets=filter(lambda x: 'gnd' in x.lower(), componentNets)
            if len(gndnets)>0:

                net = gndnets[0]
            else:
                net = componentNets[len(componentNets)-1]
            sParameterMod.SetReferenceNet(net)
            edbRlcComponentProperty.SetModel(sParameterMod)
            if not edbComponent.SetComponentProperty(edbRlcComponentProperty):
                self._messenger.add_error_message("Error Assigning the Touchstone model")
                return False
        return True

    @aedt_exception_handler
    def create_pingroup_from_pins(self, pins, group_name=None):
        """Create a pin group on a component.
        
        Parameters
        ----------
        pins : list
            List of EDB core pins.
        group_name : str, optional
            Name for the group. The default is ``None``, in which case 
            a default name is assigned as follows: ``[component Name] [NetName]``.

        Returns
        -------
        tuple
            (bool, pingroup)

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.create_pingroup_from_pins(gndpinlist, "MyGNDPingroup")  
        
        """
        if len(pins) < 1:
            self._messenger.add_error_message('No pins specified for pin group {}'.format(group_name))
            return (False, None)
        if group_name is None:
            cmp_name = pins[0].GetComponent().GetName()
            net_name = pins[0].GetNet().GetName()
            group_name = "{}_{}_{}".format(cmp_name, net_name, random.randint(0, 100))
        pingroup = self._edb.Cell.Hierarchy.PinGroup.Create(self._active_layout, group_name, convert_py_list_to_net_list(pins))
        if pingroup.IsNull():
            return (False, None)
        else:
            return (True, pingroup)


    @aedt_exception_handler
    def delete_single_pin_rlc(self):
        """Delete all RLC components with a single pin.

        Returns
        -------
        list
           List of deleted RLC components.
             

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> list_of_deleted_rlcs = edbapp.core_components.delete_single_pin_rlc()
        >>> print(list_of_deleted_rlcs)
        
        """
        deleted_comps = []
        for comp, val in self.components.items():
            if val.numpins<2 and (val.type == "Resistor" or val.type == "Capacitor" or val.type == "Inductor"):
                edb_cmp = self.get_component_by_name(comp)
                if edb_cmp is not None:
                    edb_cmp.Delete()
                    deleted_comps.append(comp)
                    self.parent._messenger.add_info_message("Component {} deleted".format(comp))
        for el in deleted_comps:
            del self.components[el]
        return deleted_comps

    @aedt_exception_handler
    def delete_component(self, component_name):
        """Delete a component.
        
        Parameters
        ----------
        component_name : str
            Name of the component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        
        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.delete_component("A1") 
        
        """
        edb_cmp = self.get_component_by_name(component_name)
        if edb_cmp is not None:
            edb_cmp.Delete()
            if edb_cmp in list(self.components.keys()):
                del self.components[edb_cmp]
            return True
        return False


    @aedt_exception_handler
    def disable_rlc_component(self, component_name):
        """Disable a RLC component.
        
        Parameters
        ----------
        component_name : str
            Name of the RLC component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.disable_rlc_component("A1")
        
        """
        edb_cmp = self.get_component_by_name(component_name)
        if edb_cmp is not None:
            rlc_property = edb_cmp.GetComponentProperty().Clone()
            pin_pair_model = rlc_property.GetModel().Clone()
            pprlc = pin_pair_model.GetPinPairRlc(list(pin_pair_model.PinPairs)[0])
            pprlc.CEnabled = False
            pprlc.LEnabled = False
            pprlc.REnabled = False
            pin_pair_model.SetPinPairRlc(list(pin_pair_model.PinPairs)[0], pprlc)
            rlc_property.SetModel(pin_pair_model)
            edb_cmp.SetComponentProperty(rlc_property)
            return True
        return False

    @aedt_exception_handler
    def set_component_rlc(self, componentname, res_value=None, ind_value=None, cap_value=None, isparallel=False):
        """Update values for an RLC component.
        
        Parameters
        ----------
        componentname :
            Name of the RLC component.
        res_value : float, optional
            Resistance value. The default is ``None``.
        ind_value : float, optional
            Inductor value.  The default is ``None``.
        cap_value : float optional
            Capacitor value.  The default is ``None``.
        isparallel : bool, optional
            Whether the RLC component is parallel. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        
        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.set_component_rlc("R1", res_value=50, ind_value=1e-9, cap_value=1e-12, isparallel=False)
        
        """
        edbComponent = self.get_component_by_name(componentname)
        componentType = edbComponent.GetComponentType()
        edbRlcComponentProperty = self._edb.Cell.Hierarchy.RLCComponentProperty()
        componentPins = self.get_pin_from_component(componentname)
        pinNumber = len(componentPins)
        if pinNumber == 2:
            fromPin = componentPins[0]
            toPin = componentPins[1]
            if res_value is None and ind_value is None and cap_value is None:
                return False
            rlc = self._edb.Utility.Rlc()
            rlc.IsParallel = isparallel
            if res_value is not None:
                rlc.REnabled = True
                rlc.R = self._edb_value(res_value)
            if ind_value is not None:
                rlc.LEnabled = True
                rlc.L = self._edb_value(ind_value)
            if cap_value is not None:
                rlc.CEnabled = True
                rlc.C = self._edb_value(cap_value)
            pinPair = self._edb.Utility.PinPair(fromPin.GetName(), toPin.GetName())
            rlcModel = self._edb.Cell.Hierarchy.PinPairModel()
            rlcModel.SetPinPairRlc(pinPair, rlc)
            if not edbRlcComponentProperty.SetModel(rlcModel) or not edbComponent.SetComponentProperty(
                    edbRlcComponentProperty):
                self._messenger.add_error_message('Failed to set RLC model on component')
                return False
        else:
            self._messenger.add_warning_message(
                "Component {} has not been assigned because either it is not present in the layout or it contains a number of pins not equal to 2".format(
                    componentname))
            return False
        self._messenger.add_warning_message("RLC properties for Component {} has been assigned.".format(componentname))
        return True

    @aedt_exception_handler
    def update_rlc_from_bom(self, bom_file, delimiter=";", valuefield="Func des", comptype="Prod name",
                            refdes="Pos / Place"):
        """Update the EDC core component values (RLCs) with values coming from a BOM file.
        
        Parameters
        ----------
        bom_file : str
            Full path to the BOM file, which is a delimited text file. 
            Header values needed inside the BOM reader must
            be explicitly set if different from the defaults.
        delimiter : str, optional
            Value to use for the delimiter. The default is ``";"``.
        valuefield : str, optional
            Field header containing the value of the component. The default is ``"Func des"``.
            The value for this parameter must being with the value of the component 
            followed by a space and then the rest of the value. For example, ``"22pF"``.
        comptype : str, optional
            Field header containing the type of component. The default is ``"Prod name"``. For 
            example, you might enter ``"Inductor"``.
        refdes : str, optional
            Field header containing the reference designator of the component. The default is 
            ``"Pos / Place"``. For example, you might enter ``"C100"``. 

        Returns
        -------
        bool
            ``True`` if the file contains the header and it is correctly parsed. ``True`` is
            returned even if no values are assigned.

        """
        with open(bom_file, 'r') as f:
            Lines = f.readlines()
            found = False
            refdescolumn = None
            comptypecolumn = None
            valuecolumn = None
            for line in Lines:
                content_line = [i.strip() for i in line.split(delimiter)]
                if valuefield in content_line:
                    valuecolumn = content_line.index(valuefield)
                if comptype in content_line:
                    comptypecolumn = content_line.index(comptype)
                if refdes in content_line:
                    refdescolumn = content_line.index(refdes)
                elif refdescolumn:
                    found = True
                    new_refdes = content_line[refdescolumn].split(" ")[0]
                    new_value = content_line[valuecolumn].split(" ")[0]
                    new_type = content_line[comptypecolumn]
                    if "resistor" in new_type.lower():
                        self.set_component_rlc(new_refdes, res_value=new_value)
                    elif "capacitor" in new_type.lower():
                        self.set_component_rlc(new_refdes, cap_value=new_value)
                    elif "inductor" in new_type.lower():
                        self.set_component_rlc(new_refdes, ind_value=new_value)
        return found

    @aedt_exception_handler
    def get_pin_from_component(self, cmpName, netName=None, pinName=None):
        """Retrieve the pins of a component.

        Parameters
        ----------
        cmpName : str
            Name of the component.
        netName : str, optional
            Filter on the net name as an alternative to
            ``pinName``. The default is ``None``.
        pinName : str, optional
            Filter on the pin name an an alternative to
            ``netName``. The default is ``None``.

        Returns
        -------
        list
            List of pins when the component is found or ``[]`` otherwise.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_pin_from_component("R1", refdes)
        
        """

        cmp = self._edb.Cell.Hierarchy.Component.FindByName(self._active_layout, cmpName)
        if netName:
            pins = [p for p in cmp.LayoutObjs if
                    p.GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance and
                    p.IsLayoutPin() and
                    p.GetNet().GetName() == netName]
        elif pinName:
            pins = [p for p in cmp.LayoutObjs if
                    p.GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance and
                    p.IsLayoutPin() and
                    (self.get_aedt_pin_name(p) == str(pinName) or p.GetName() == str(pinName))]
        else:
            pins = [p for p in cmp.LayoutObjs if
                    p.GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance and
                    p.IsLayoutPin()]
        return pins


    @aedt_exception_handler
    def get_aedt_pin_name(self, pin):
        """Retrieve the pin name that is shown in AEDT.
        
        .. note::
           To obtain the EDB core pin name, use `pin.GetName()`.

        Parameters
        ----------
        pin : str
            Name of the pin in EDB core.

        Returns
        -------
        str
            Name of the pin in AEDT.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_aedt_pin_name(pin)
        
        """
        if "IronPython" in sys.version or ".NETFramework" in sys.version:
            name = clr.Reference[String]()
            response = pin.GetProductProperty(0, 11, name)
        else:
            val = String("")
            response, name = pin.GetProductProperty(0, 11, val)
        name = str(name).strip("'")
        return name

    @aedt_exception_handler
    def get_pin_position(self, pin):
        """Retrieve the pin position in meters.

        Parameters
        ----------
        pin :str
            Name of the pin.

        Returns
        -------
        list
            Pin position as a list of float values in the form ``[x, y]``.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_pin_position(pin)
        
        """ 
        if is_ironpython:
            res, pt_pos, rot_pos = pin.GetPositionAndRotation()
        else:
            res, pt_pos, rot_pos = pin.GetPositionAndRotation(
                self._edb.Geometry.PointData(self._edb_value(0.0), self._edb_value(0.0)), .0)
        if pin.GetComponent().IsNull():
            transformed_pt_pos = pt_pos
        else:
            transformed_pt_pos = pin.GetComponent().GetTransform().TransformPoint(pt_pos)
        pin_xy = self._edb.Geometry.PointData(self._edb_value(str(transformed_pt_pos.X.ToDouble())),
                                             self._edb_value(str(transformed_pt_pos.Y.ToDouble())))
        return [pin_xy.X.ToDouble(), pin_xy.Y.ToDouble()]

    @aedt_exception_handler
    def get_pins_name_from_net(self, pin_list, net_name):
        """Retrieve pins belonging to a net.

        Parameters
        ----------
        pin_list : list
            List of pins to check.
        net_name : str
            Name of the net.
        
        Returns
        -------
        list
            List of pins belong to the net.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_pins_name_from_net(pin_list, net_name)      
        
        """
        pinlist = []
        for pin in pin_list:
            if pin.GetNet().GetName() == net_name:
                pinlist.append(pin.GetName())
        return pinlist

    @aedt_exception_handler
    def get_nets_from_pin_list(self, PinList):
        """Retrieve nets with one or more pins.

        Parameters
        ----------
        PinList : list
            List of pins.

        Returns
        -------
        list
            List of nets with one or more pins.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_nets_from_pin_list(pinlist)
        
        """
        netlist = []
        for pin in PinList:
            netlist.append(pin.GetNet().GetName())
        return list(set(netlist))

    @aedt_exception_handler
    def get_component_net_connection_info(self, refdes):
        """Retrieve net connection information.
     
        Parameters
        ----------
        refdes :
            Reference designator for the net.

        Returns
        -------
        dict
            Dictionary of the net connection information for the reference designator.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_component_net_connection_info(refdes)
        
        """
        component_pins = self.get_pin_from_component(refdes)
        data = {"refdes":[], "pin_name":[], "net_name":[]}
        for pin_obj in component_pins:
            pin_name = pin_obj.GetName()
            net_name = pin_obj.GetNet().GetName()
            if pin_name is not None:
                data["refdes"].append(refdes)
                data["pin_name"].append(pin_name)
                data["net_name"].append(net_name)
        return data

    def get_rats(self):
        """Retrieve a list of dictionaries of the reference designator, pin names, and net names.
        
        Returns
        -------
        list
            List of dictionaries of the reference designator, pin names, 
            and net names.
        
        Examples
        --------
        
        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_rats()
        
        """
        df_list = []
        for refdes in self.components.keys():
            df = self.get_component_net_connection_info(refdes)
            df_list.append(df)
        return df_list

    def get_through_resistor_list(self, threshold=1):
        """Retrieve through resistors.

        Parameters
        ----------
        threshold : int, optional
            Threshold value. The default is ``1``.

        Returns
        -------
        list
            List of through resistors.

        Examples
        ---------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_through_resistor_list()
       
        """
        through_comp_list = []
        for refdes, comp_obj in self.resistors.items():

            numpins = comp_obj.numpins

            if numpins == 2:

                value = comp_obj.res_value
                value = resistor_value_parser(value)

                if value <= threshold:
                    through_comp_list.append(refdes)

        return through_comp_list
