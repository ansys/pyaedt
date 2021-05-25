"""
Components Class
-------------------

This class manages Edb Components and related methods

Disclaimer
==========

**Copyright (c) 1986-2021, ANSYS Inc. unauthorised use, distribution or duplication is prohibited**

**This tool release is unofficial and not covered by standard Ansys Support license.**



"""
import clr
import os
import re
from .general import *
from ..generic.general_methods import get_filename_without_extension, generate_unique_name
clr.AddReference("System")
from System import Convert, String
from System import Double, Array
from System.Collections.Generic import List
import random

def resistor_value_parser(RValue):
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



class Component(object):

    def __init__(self,parent, component, name):
        self.parent = parent
        self.edbcomponent = component
        self.refdes = name
        self.partname = component.PartName
        self.numpins = component.NumPins
        self.type = component.PartType
        self.pinlist = self.parent.get_pin_from_component(self.refdes)
        self.nets = self.parent.get_nets_from_pin_list(self.pinlist)
        self.res_value = None

        try:
            self.res_value = self.parent.edb_value(component.Model.RValue).ToDouble()
        except:
            self.res_value = None
        try:
            self.cap_value = self.parent.edb_value(component.Model.CValue).ToDouble()
        except:
            self.cap_value = None
        try:
            self.ind_value = self.parent.edb_value(component.Model.LValue).ToDouble()
        except:
            self.ind_value = None


class Components(object):
    """HFSS 3DLayout object


    """
    @property
    def edb(self):
        return self.parent.edb

    @property
    def messenger(self):
        return self.parent.messenger

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
        self.init_parts()


    @aedt_exception_handler
    def init_parts(self):
        a = self.components
        a = self.resistors
        a = self.ICs
        a = self.Others
        a = self.inductors
        a = self.IOs
        a = self.components_by_partname
        return True

    @property
    def builder(self):
        return self.parent.builder

    @property
    def edb(self):
        return self.parent.edb

    @property
    def edb_value(self):
        return self.parent.edb_value

    @property
    def edbutils(self):
        return self.parent.edbutils

    @property
    def active_layout(self):
        return self.parent.active_layout

    @property
    def cell(self):
        return self.parent.cell

    @property
    def db(self):
        return self.parent.db

    @property
    def components_methods(self):
        return self.parent.edblib.Layout.ComponentsMethods

    @property
    def components(self):
        """
        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.components

        :return:Dictionary of EDB ComponentSetupInfo
        """
        try:
            cmplist = self.get_component_list()
            self._cmp = {}
            for cmp in cmplist:
                self._cmp[cmp.RefDes] = Component(self,cmp, cmp.RefDes)
        except:
            pass
        return self._cmp

    @property
    def resistors(self):
        """
        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.resistors

        :return: Dictionary of Resistors
        """
        try:
            comps = self.edbutils.ComponentSetupInfo.GetFromLayout(self.active_layout)
            self._res = {}
            for cmp in self.edbutils.ComponentSetupInfo.GetFromLayout(self.active_layout):
                if cmp.PartType == 'Resistor':
                    self._res[cmp.RefDes] = Component(self,cmp, cmp.RefDes)
        except:
            pass

        return self._res

    @property
    def capacitors(self):
        """
        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.capacitors

        :return: Dictionary of capacitors
        """
        try:
            comps = self.edbutils.ComponentSetupInfo.GetFromLayout(self.active_layout)
            self._cap = {}
            for cmp in comps:
                if cmp.PartType == 'Capacitor':
                    self._cap[cmp.RefDes] = Component(self,cmp, cmp.RefDes)
        except:
            pass

        return self._cap

    @property
    def inductors(self):
        """

        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.inductors

        :return: Dictionary of inductors
        """
        try:
            comps = self.edbutils.ComponentSetupInfo.GetFromLayout(self.active_layout)
            self._ind = {}
            for cmp in comps:
                if cmp.PartType == 'Inductor':
                    self._ind[cmp.RefDes] = Component(self,cmp, cmp.RefDes)
        except:
            pass
        return self._ind

    @property
    def ICs(self):
        """

        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.ICs

        :return: Dictionary of capacitors
        """
        try:
            comps = self.edbutils.ComponentSetupInfo.GetFromLayout(self.active_layout)
            self._ics = {}
            for cmp in comps:
                if cmp.PartType == 'IC':
                    self._ics[cmp.RefDes] = Component(self,cmp, cmp.RefDes)
        except:
            pass
        return self._ics

    @property
    def IOs(self):
        """
        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.IOs

        :return: Dictionary of capacitors
        """
        try:
            comps = self.edbutils.ComponentSetupInfo.GetFromLayout(self.active_layout)
            self._ios = {}
            for cmp in comps:
                if cmp.PartType == 'IO':
                    self._ios[cmp.RefDes] = Component(self,cmp, cmp.RefDes)
        except:
            pass

        return self._ios

    @property
    def Others(self):
        """
        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.others


        :return: Dictionary of capacitors
        """
        try:
            comps = self.edbutils.ComponentSetupInfo.GetFromLayout(self.active_layout)
            self._others = {}
            for cmp in comps:
                if cmp.PartType == 'Other':
                    self._others[cmp.RefDes] = Component(self,cmp, cmp.RefDes)
        except:
            pass
        return self._others

    @property
    def components_by_partname(self):
        """
        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.components_by_partname


        :return: Components Dictionary grouped by PartName
        """

        try:
            comps = self.edbutils.ComponentSetupInfo.GetFromLayout(self.active_layout)
            self._comps_by_part = {}
            for comp in comps:
                if comp.PartName in self._comps_by_part.keys():
                    self._comps_by_part[comp.PartName].append(Component(self,comp, comp.RefDes))
                else:
                    self._comps_by_part[comp.PartName] = [Component(self,comp, comp.RefDes)]
        except:
            pass
        return self._comps_by_part

    @aedt_exception_handler
    def get_component_list(self):
        """
        Return the list of all components

        :return: List of component Setup Info
        """
        cmp_setup_info_list = self.parent.edbutils.ComponentSetupInfo.GetFromLayout(
            self.parent.builder.EdbHandler.layout)
        cmp_list = []
        for comp in cmp_setup_info_list:
            cmp_list.append(comp)
        return cmp_list

    @aedt_exception_handler
    def get_component_by_name(self, name):
        """
        return the component object by name

        :param name: name of the component
        :return: Edb component (Edb.Cell.Hierarchy.Component) object if exists
        """
        edbcmp = self.edb.Cell.Hierarchy.Component.FindByName(self.active_layout, name)
        if edbcmp is not None:
            return edbcmp
        else:
            pass

    @aedt_exception_handler
    def get_components_from_nets(self, netlist=None):
        """
        Get Components from Net List

        :param netlist: netlist string.
        :return: list of component names that belongs to signal nets
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
        """

        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> pins = edbapp.core_components.get_pin_from_component("A1")
        >>> edbapp.core_components.create_component_from_pins(pins, "A1New")

        :param pins: list of edb_core pins
        :param component_name: the component RefDes name
        :return: python tuple<bool,the Edb.Cell.Hierarchy.Component> With Item1 = True when component has successfully been created and False if not
        """
        try:
            new_cmp = self.parent.edb.Cell.Hierarchy.Component.Create(self.parent.builder.EdbHandler, component_name)
            new_group = self.parent.edb.Cell.Hierarchy.Group.Create(self.parent.builder.EdbHandler.layout,
                                                                    component_name)
            for pin in pins:
                new_group.AddMember(pin)
            new_cmp.SetGroup(new_group)
            new_cmp_layer_name = pins[0].GetPadstackDef().GetData().GetLayerNames().First()
            new_cmp_placement_layer = self.parent.edb.Cell.Layer.FindByName(
                self.parent.builder.EdbHandler.layout.GetLayerCollection(), new_cmp_layer_name)
            new_cmp.SetPlacementLayer(new_cmp_placement_layer)
            return (True, new_cmp)
        except:
            return (False, None)

    @aedt_exception_handler
    def set_component_model(self, componentname, model_type="Spice", modelpath=None, modelname=None):
        """Assign a model (spice or Touchstone to a component)

        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.set_component_model("A1", model_type="Spice", modelpath="pathtospfile", modelname="spicemodelname")

        :param componentname: Name of the component to update
        :param model_type: Type of the model. Spice (default) | Touchstone
        :param modelpath: full path to the model file
        :param modelname: name of the model. None ->filename
        :return: True if succeded | False if failed
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
                spiceMod = self.edb.Cell.Hierarchy.SPICEModel()
                spiceMod.SetModelPath(modelpath)
                spiceMod.SetModelName(modelname)
                terminal = 1
                for pn in pinNames:
                    spiceMod.AddTerminalPinPair(pn, str(terminal))
                    terminal+=1

                edbRlcComponentProperty.SetModel(spiceMod)
                if not edbComponent.SetComponentProperty(edbRlcComponentProperty):
                    self.messenger.add_error_message("Error Assigning the Touchstone model")
                    return False
            else:
                self.messenger.add_error_message("Wrong number of Pins")
                return False

        elif model_type=="Touchstone":

            nPortModelName = modelname
            edbComponentDef = edbComponent.GetComponentDef()
            nPortModel = self.edb.Definition.NPortComponentModel.FindByName(edbComponentDef, nPortModelName)
            if nPortModel.IsNull():
                nPortModel = self.edb.Definition.NPortComponentModel.Create(nPortModelName)
                nPortModel.SetReferenceFile(modelpath)
                edbComponentDef.AddComponentModel(nPortModel)

            sParameterMod = self.edb.Cell.Hierarchy.SParameterModel()
            sParameterMod.SetComponentModelName(nPortModel)
            gndnets=filter(lambda x: 'gnd' in x.lower(), componentNets)
            if len(gndnets)>0:

                net = gndnets[0]
            else:
                net = componentNets[len(componentNets)-1]
            sParameterMod.SetReferenceNet(net)
            edbRlcComponentProperty.SetModel(sParameterMod)
            if not edbComponent.SetComponentProperty(edbRlcComponentProperty):
                self.messenger.add_error_message("Error Assigning the Touchstone model")
                return False
        return True

    @aedt_exception_handler
    def create_pingroup_from_pins(self, pins, group_name=None):
        """
        Create a pin group on a component

         :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.create_pingroup_from_pins(gndpinlist, "MyGNDPingroup")

        :param pins: python list of edb_core pins o
        :param group_name: Optional the name for the group. If None a default name will be applied with [component Name] [NetName]
        """
        if len(pins) < 1:
            self.messenger.add_error_message('No pins specified for pin group {}'.format(group_name))
            return (False, None)
        if group_name is None:
            cmp_name = pins[0].GetComponent().GetName()
            net_name = pins[0].GetNet().GetName()
            group_name = "{}_{}_{}".format(cmp_name, net_name, random.randint(0, 100))
        pingroup = self.parent.edb.Cell.Hierarchy.PinGroup.Create(self.builder.EdbHandler.layout, group_name, pins)
        if pingroup.IsNull():
            return (False, None)
        else:
            return (True, pingroup)


    @aedt_exception_handler
    def delete_single_pin_rlc(self):
        """
        Delete all RLC Components with less than 2 Pins

        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> list_of_deleted_rlcs = edbapp.core_components.delete_single_pin_rlc()
        >>> print(list_of_deleted_rlcs)

        :return: list of deleted components
        """
        deleted_comps = []
        for comp,val  in self.components.items():
            if val.numpins<2 and (val.type == "Resistor" or val.type == "Capacitor" or val.type == "Inductor"):
                edb_cmp = self.get_component_by_name(comp)
                if edb_cmp is not None:
                    edb_cmp.Delete()
                    deleted_comps.append(comp)
                    self.parent.messenger.add_info_message("Component {} deleted".format(comp))
        return deleted_comps

    @aedt_exception_handler
    def delete_component(self, component_name):
        """
        Delete Component

        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.delete_component("A1")

        :param component_name: str name of component to delete
        :return: Bool
        """
        edb_cmp = self.get_component_by_name(component_name)
        if edb_cmp is not None:
            edb_cmp.Delete()
            return True
        return False


    @aedt_exception_handler
    def disable_rlc_component(self, component_name):
        """
        Disable Given Component

        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.disable_rlc_component("A1")

        :param component_name: str component name
        :return: Bool
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
        """Set RLC Component Values

        :example:

        >>> from pyaedt import EDB
        >>> edbapp = EDB("myaedbfolder")
        >>> edbapp.core_components.set_component_rlc("R1", res_value=50, ind_value=1e-9, cap_value=1e-12, isparallel=False)

        :param componentname: name of component to update
        :param res_value:  Resistance value
        :param ind_value: Inductor value
        :param cap_value: Capacitor Value
        :param isparallel: boolean
        :return: bool
        """
        edbComponent = self.get_component_by_name(componentname)
        componentType = edbComponent.GetComponentType()
        edbRlcComponentProperty = self.edb.Cell.Hierarchy.RLCComponentProperty()
        componentPins = self.get_pin_from_component(componentname)
        pinNumber = len(componentPins)
        if pinNumber == 2:
            fromPin = componentPins[0]
            toPin = componentPins[1]
            if res_value is None and ind_value is None and cap_value is None:
                return False
            rlc = self.edb.Utility.Rlc()
            rlc.IsParallel = isparallel
            if res_value is not None:
                rlc.REnabled = True
                rlc.R = self.edb_value(res_value)
            if ind_value is not None:
                rlc.LEnabled = True
                rlc.L = self.edb_value(ind_value)
            if cap_value is not None:
                rlc.CEnabled = True
                rlc.C = self.edb_value(cap_value)
            pinPair = self.edb.Utility.PinPair(fromPin.GetName(), toPin.GetName())
            rlcModel = self.edb.Cell.Hierarchy.PinPairModel()
            rlcModel.SetPinPairRlc(pinPair, rlc)
            if not edbRlcComponentProperty.SetModel(rlcModel) or not edbComponent.SetComponentProperty(
                    edbRlcComponentProperty):
                self.messenger.add_error_message('Failed to set RLC model on component')
                return False
        else:
            self.messenger.add_warning_message(
                "Component {} has been not assigned because it is not present in layout or it contains a number of pins  not equal to 2".format(
                    componentname))
            return False
        self.messenger.add_warning_message("RLC Properties for Component {} has been assigned".format(componentname))
        return True

    @aedt_exception_handler
    def update_rlc_from_bom(self, bom_file, delimiter=";", valuefield="Func des", comptype="Prod name",
                            refdes="Pos / Place"):
        """
        Function to update the edb_core components values (RLCs) with values coming from BOM.
        Files is a text file delimited and header values needed inside the bom reader have to be explicitily set if different from the defaults
        valuefield has to contain the value of the Component (eg. 22pF) at beginning of the value followed by a space and then the rest of the value

        :param bom_file: full path to the bom file
        :param delimiter: delimiter default value ;
        :param valuefield: Field Header containing the value of component
        :param comptype: Field Header containing the type of component.eg "Inductor"
        :param refdes: Field Header containing the RefDes of Component. eg "C100"
        :return: True if the file contains the header and it is correctly parsed. the function returns True even if no values are assigned
        """
        with open(bom_file, 'r') as f:
            Lines = f.readlines()
            found = False
            refdescolumn = None
            comptypecolumn = None
            valuecolumn = None
            for line in Lines:
                content_line = line.split(delimiter)
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
        """
        get the pins of a specified component name


        :param cmpName: component name
        :param netName: filter on net name, optional and alternative to pinName
        :param pinName: filter on pin name, optional and alternative to netName
        :return: the list of pin. [] if component not found
        """

        cmp = self.edb.Cell.Hierarchy.Component.FindByName(self.active_layout, cmpName)
        if netName:
            pins = [p for p in cmp.LayoutObjs if
                    p.GetObjType() == self.edb.Cell.LayoutObjType.PadstackInstance and
                    p.IsLayoutPin() and
                    p.GetNet().GetName() == netName]
        elif pinName:
            pins = [p for p in cmp.LayoutObjs if
                    p.GetObjType() == self.edb.Cell.LayoutObjType.PadstackInstance and
                    p.IsLayoutPin() and
                    (self.get_aedt_pin_name(p) == str(pinName) or p.GetName()==str(pinName))]
        else:
            pins = [p for p in cmp.LayoutObjs if
                    p.GetObjType() == self.edb.Cell.LayoutObjType.PadstackInstance and
                    p.IsLayoutPin()]
        return pins


    @aedt_exception_handler
    def get_aedt_pin_name(self, pin):
        """
        get the pin name as shown in aedt
        Note: to obtain the edb_core pin name simply use pin.GetName()
        :param pin: the pin
        :return: name as string
        """
        if "IronPython" in sys.version or ".NETFramework" in sys.version:
                name = clr.Reference[String]()
        else:
                name = String("")
        response = pin.GetProductProperty(0, 11, name)
        name = str(name).strip("'")
        return name

    @aedt_exception_handler
    def get_pin_position(self, pin):
        """
        get the pin position x, y in meter
        :param pin: the pin
        :return: [x, y] as list of float
        """
        if is_ironpython:
            res, pt_pos, rot_pos = pin.GetPositionAndRotation()
        else:
            res, pt_pos, rot_pos = pin.GetPositionAndRotation(
                self.edb.Geometry.PointData(self.edb_value(0.0), self.edb_value(0.0)), .0)
        if pin.GetComponent().IsNull():
            transformed_pt_pos = pt_pos
        else:
            transformed_pt_pos = pin.GetComponent().GetTransform().TransformPoint(pt_pos)
        pin_xy = self.edb.Geometry.PointData(self.edb_value(str(transformed_pt_pos.X.ToDouble())),
                                             self.edb_value(str(transformed_pt_pos.Y.ToDouble())))
        return [pin_xy.X.ToDouble(), pin_xy.Y.ToDouble()]

    @aedt_exception_handler
    def get_pins_name_from_net(self, pin_list, net_name):
        """
        Return the list of pins belonging to a specific net

        :param net_name: string of netname
        :param pin_list: list of pins to check
        :return: pinlist
        """
        pinlist = []
        for pin in pin_list:
            if pin.GetNet().GetName() == net_name:
                pinlist.append(pin.GetName())
        return pinlist

    @aedt_exception_handler
    def get_nets_from_pin_list(self, PinList):
        """
        returns the list of nets of specified pin or pin list

        :param PinList: list of pins objects
        :return: list of nets
        """
        netlist = []
        for pin in PinList:
            netlist.append(pin.GetNet().GetName())
        return list(set(netlist))

    @aedt_exception_handler
    def get_component_net_connection_info(self, refdes):
        """
        return dictionary of RefDes, PinNames and NetNames for specified ref des
        :param refdes: reference designator
        :return: dicti
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
        """

        :return:
        """
        df_list = []
        for refdes in self.components.keys():
            df = self.get_component_net_connection_info(refdes)
            df_list.append(df)
        return df_list



    def get_through_resistor_list(self, threshold=1):
        """

        :param threshold:
        :return:
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


