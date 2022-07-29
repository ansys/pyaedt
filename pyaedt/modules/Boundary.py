"""
This module contains these classes: `BoundaryCommon` and `BoundaryObject`.
"""
from collections import OrderedDict

from pyaedt.generic.constants import CATEGORIESQ3D
from pyaedt.generic.DataHandlers import _dict2arg
from pyaedt.generic.DataHandlers import random_string
from pyaedt.generic.general_methods import PropsManager
from pyaedt.generic.general_methods import filter_tuple
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.Object3d import EdgePrimitive
from pyaedt.modeler.Object3d import FacePrimitive
from pyaedt.modeler.Object3d import VertexPrimitive
from pyaedt.modeler.Object3d import _dim_arg


class BoundaryProps(OrderedDict):
    """AEDT Boundary Component Internal Parameters."""

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        if self._pyaedt_boundary.auto_update:
            if key in ["Edges", "Faces", "Objects"]:
                res = self._pyaedt_boundary.update_assignment()
            else:
                res = self._pyaedt_boundary.update()
            if not res:
                self._pyaedt_boundary._app.logger.warning("Update of %s Failed. Check needed arguments", key)

    def __init__(self, boundary, props):
        OrderedDict.__init__(self)
        if props:
            for key, value in props.items():
                if isinstance(value, (OrderedDict, dict)):
                    OrderedDict.__setitem__(self, key, BoundaryProps(boundary, value))
                elif isinstance(value, list):
                    list_els = []
                    for el in value:
                        if isinstance(el, (OrderedDict, dict)):
                            list_els.append(BoundaryProps(boundary, el))
                        else:
                            list_els.append(el)
                    OrderedDict.__setitem__(self, key, list_els)
                else:
                    OrderedDict.__setitem__(self, key, value)
        self._pyaedt_boundary = boundary

    def _setitem_without_update(self, key, value):
        OrderedDict.__setitem__(self, key, value)


class BoundaryCommon(PropsManager):
    """ """

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Retrieve boundary properties.

        Parameters
        ----------
        props : dict, optional
             The default is ``None``.

        Returns
        -------
        dict
            Dictionary of boundary properties.

        """
        if not props:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    @pyaedt_function_handler()
    def delete(self):
        """Delete the boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.type == "Matrix" or self.type == "Force" or self.type == "Torque":
            self._app.o_maxwell_parameters.DeleteParameters([self.name])
        else:
            self._app.oboundary.DeleteBoundaries([self.name])
        for el in self._app.boundaries:
            if el.name == self.name:
                self._app.boundaries.remove(el)
        return True


class NativeComponentObject(BoundaryCommon, object):
    """Manages Native Component data and execution.

    Examples
    --------
    in this example the par_beam returned object is a ``pyaedt.modules.Boundary.NativeComponentObject``
    >>> from pyaedt import Hfss
    >>> hfss = Hfss(solution_type="SBR+")
    >>> ffd_file ="path/to/ffdfile.ffd"
    >>> par_beam = hfss.create_sbr_file_based_antenna(ffd_file)
    >>> par_beam.native_properties["Size"] = "0.1mm"
    >>> par_beam.update()
    >>> par_beam.delete()
    """

    def __init__(self, app, component_type, component_name, props):
        self.auto_update = False
        self._app = app
        self.name = "InsertNativeComponentData"
        self.component_name = component_name
        self.props = BoundaryProps(
            self,
            OrderedDict(
                {
                    "TargetCS": "Global",
                    "SubmodelDefinitionName": self.component_name,
                    "ComponentPriorityLists": OrderedDict({}),
                    "NextUniqueID": 0,
                    "MoveBackwards": False,
                    "DatasetType": "ComponentDatasetType",
                    "DatasetDefinitions": OrderedDict({}),
                    "BasicComponentInfo": OrderedDict(
                        {
                            "ComponentName": self.component_name,
                            "Company": "",
                            "Company URL": "",
                            "Model Number": "",
                            "Help URL": "",
                            "Version": "1.0",
                            "Notes": "",
                            "IconType": "",
                        }
                    ),
                    "GeometryDefinitionParameters": OrderedDict({"VariableOrders": OrderedDict({})}),
                    "DesignDefinitionParameters": OrderedDict({"VariableOrders": OrderedDict({})}),
                    "MaterialDefinitionParameters": OrderedDict({"VariableOrders": OrderedDict({})}),
                    "MapInstanceParameters": "DesignVariable",
                    "UniqueDefinitionIdentifier": "89d26167-fb77-480e-a7ab-"
                    + random_string(12, char_set="abcdef0123456789"),
                    "OriginFilePath": "",
                    "IsLocal": False,
                    "ChecksumString": "",
                    "ChecksumHistory": [],
                    "VersionHistory": [],
                    "NativeComponentDefinitionProvider": OrderedDict({"Type": component_type}),
                    "InstanceParameters": OrderedDict(
                        {"GeometryParameters": "", "MaterialParameters": "", "DesignParameters": ""}
                    ),
                }
            ),
        )
        if props:
            self._update_props(self.props, props)
        self.native_properties = self.props["NativeComponentDefinitionProvider"]
        self.auto_update = True

    @property
    def targetcs(self):
        """Native Component Coordinate System.

        Returns
        -------
        str
            Native Component Coordinate System
        """
        if "TargetCS" in list(self.props.keys()):
            return self.props["TargetCS"]
        else:
            return "Global"

    @targetcs.setter
    def targetcs(self, cs):
        self.props["TargetCS"] = cs

    def _update_props(self, d, u):
        for k, v in u.items():
            if isinstance(v, (dict, OrderedDict)):
                if k not in d:
                    d[k] = OrderedDict({})
                d[k] = self._update_props(d[k], v)
            else:
                d[k] = v
        return d

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    @pyaedt_function_handler()
    def create(self):
        """Create a Native Component in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.name = "InsertNativeComponentData"
        try:
            names = [i for i in self._app.excitations]
        except Exception as e:
            names = []
        self.antennaname = self._app.modeler.oeditor.InsertNativeComponent(self._get_args())
        try:
            a = [i for i in self._app.excitations if i not in names]
            self.excitation_name = a[0].split(":")[0]
        except Exception as e:
            self.excitation_name = self.antennaname
        return True

    @pyaedt_function_handler()
    def update(self):
        """Update the Native Component in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        self.name = "EditNativeComponentDefinitionData"
        self.update_props = OrderedDict({})
        self.update_props["DefinitionName"] = self.props["SubmodelDefinitionName"]
        self.update_props["GeometryDefinitionParameters"] = self.props["GeometryDefinitionParameters"]
        self.update_props["DesignDefinitionParameters"] = self.props["DesignDefinitionParameters"]
        self.update_props["MaterialDefinitionParameters"] = self.props["MaterialDefinitionParameters"]
        self.update_props["NextUniqueID"] = self.props["NextUniqueID"]
        self.update_props["MoveBackwards"] = self.props["MoveBackwards"]
        self.update_props["DatasetType"] = self.props["DatasetType"]
        self.update_props["DatasetDefinitions"] = self.props["DatasetDefinitions"]
        self.update_props["NativeComponentDefinitionProvider"] = self.props["NativeComponentDefinitionProvider"]
        self.update_props["ComponentName"] = self.props["BasicComponentInfo"]["ComponentName"]
        self.update_props["Company"] = self.props["BasicComponentInfo"]["Company"]
        self.update_props["Model Number"] = self.props["BasicComponentInfo"]["Model Number"]
        self.update_props["Help URL"] = self.props["BasicComponentInfo"]["Help URL"]
        self.update_props["Version"] = self.props["BasicComponentInfo"]["Version"]
        self.update_props["Notes"] = self.props["BasicComponentInfo"]["Notes"]
        self.update_props["IconType"] = self.props["BasicComponentInfo"]["IconType"]
        self._app.modeler.oeditor.EditNativeComponentDefinition(self._get_args(self.update_props))

        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete the Native Component in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._app.modeler.oeditor.Delete(["NAME:Selections", "Selections:=", self.antennaname])
        for el in self._app.native_components:
            if el.component_name == self.component_name:
                self._app.native_components.remove(el)
        return True


class BoundaryObject(BoundaryCommon, object):
    """Manages boundary data and execution.

    Examples
    --------

    Create a cylinder at the XY working plane and assign a copper coating of 0.2 mm to it. The Coating is a boundary
    operation and coat will return a ``pyaedt.modules.Boundary.BoundaryObject``

    >>> from pyaedt import Hfss
    >>> hfss =Hfss()
    >>> origin = hfss.modeler.Position(0, 0, 0)
    >>> inner = hfss.modeler.create_cylinder(hfss.PLANE.XY, origin, 3, 200, 0, "inner")
    >>> inner_id = hfss.modeler.get_obj_id("inner")
    >>> coat = hfss.assign_coating([inner_id], "copper", usethickness=True, thickness="0.2mm")
    """

    def __init__(self, app, name, props, boundarytype):
        self.auto_update = False
        self._app = app
        self._name = name
        self.props = BoundaryProps(self, OrderedDict(props))
        self.type = boundarytype
        self._boundary_name = self.name
        self.auto_update = True

    @property
    def name(self):
        """Boundary Name."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.update()

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Retrieve arguments.

        Parameters
        ----------
        props :
            The default is ``None``.

        Returns
        -------
        list
            List of boundary properties.

        """
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    @pyaedt_function_handler()
    def create(self):
        """Create a boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.type == "Perfect E":
            self._app.oboundary.AssignPerfectE(self._get_args())
        elif self.type == "Perfect H":
            self._app.oboundary.AssignPerfectH(self._get_args())
        elif self.type == "Aperture":
            self._app.oboundary.AssignAperture(self._get_args())
        elif self.type == "Radiation":
            self._app.oboundary.AssignRadiation(self._get_args())
        elif self.type == "Finite Conductivity":
            self._app.oboundary.AssignFiniteCond(self._get_args())
        elif self.type == "Lumped RLC":
            self._app.oboundary.AssignLumpedRLC(self._get_args())
        elif self.type == "Impedance":
            self._app.oboundary.AssignImpedance(self._get_args())
        elif self.type == "Layered Impedance":
            self._app.oboundary.AssignLayeredImp(self._get_args())
        elif self.type == "Anisotropic Impedance":
            self._app.oboundary.AssignAnisotropicImpedance(self._get_args())
        elif self.type == "Primary":
            self._app.oboundary.AssignPrimary(self._get_args())
        elif self.type == "Secondary":
            self._app.oboundary.AssignSecondary(self._get_args())
        elif self.type == "Lattice Pair":
            self._app.oboundary.AssignLatticePair(self._get_args())
        elif self.type == "HalfSpace":
            self._app.oboundary.AssignHalfSpace(self._get_args())
        elif self.type == "Multipaction SEE":
            self._app.oboundary.AssignMultipactionSEE(self._get_args())
        elif self.type == "Fresnel":
            self._app.oboundary.AssignFresnel(self._get_args())
        elif self.type == "Symmetry":
            self._app.oboundary.AssignSymmetry(self._get_args())
        elif self.type == "Zero Tangential H Field":
            self._app.oboundary.AssignZeroTangentialHField(self._get_args())
        elif self.type == "Zero Integrated Tangential H Field":
            self._app.oboundary.AssignIntegratedZeroTangentialHField(self._get_args())
        elif self.type == "Tangential H Field":
            self._app.oboundary.AssignTangentialHField(self._get_args())
        elif self.type == "Insulating":
            self._app.oboundary.AssignInsulating(self._get_args())
        elif self.type == "Independent":
            self._app.oboundary.AssignIndependent(self._get_args())
        elif self.type == "Dependent":
            self._app.oboundary.AssignDependent(self._get_args())
        elif self.type == "Band":
            self._app.omodelsetup.AssignBand(self._get_args())
        elif self.type == "InfiniteGround":
            self._app.oboundary.AssignInfiniteGround(self._get_args())
        elif self.type == "ThinConductor":
            self._app.oboundary.AssignThinConductor(self._get_args())
        elif self.type == "Stationary Wall":
            self._app.oboundary.AssignStationaryWallBoundary(self._get_args())
        elif self.type == "Symmetry Wall":
            self._app.oboundary.AssignSymmetryWallBoundary(self._get_args())
        elif self.type == "Resistance":
            self._app.oboundary.AssignResistanceBoundary(self._get_args())
        elif self.type == "Conducting Plate":
            self._app.oboundary.AssignConductingPlateBoundary(self._get_args())
        elif self.type == "Adiabatic Plate":
            self._app.oboundary.AssignAdiabaticPlateBoundary(self._get_args())
        elif self.type == "Network":
            self._app.oboundary.AssignNetworkBoundary(self._get_args())
        elif self.type == "Grille":
            self._app.oboundary.AssignGrilleBoundary(self._get_args())
        elif self.type == "Block":
            self._app.oboundary.AssignBlockBoundary(self._get_args())
        elif self.type == "SourceIcepak":
            self._app.oboundary.AssignSourceBoundary(self._get_args())
        elif self.type == "Opening":
            self._app.oboundary.AssignOpeningBoundary(self._get_args())
        elif self.type == "EMLoss":
            self._app.oboundary.AssignEMLoss(self._get_args())
        elif self.type == "ThermalCondition":
            self._app.oboundary.AssignThermalCondition(self._get_args())
        elif self.type == "Convection":
            self._app.oboundary.AssignConvection(self._get_args())
        elif self.type == "Temperature":
            self._app.oboundary.AssignTemperature(self._get_args())
        elif self.type == "RotatingFluid":
            self._app.oboundary.AssignRotatingFluid(self._get_args())
        elif self.type == "Frictionless":
            self._app.oboundary.AssignFrictionlessSupport(self._get_args())
        elif self.type == "FixedSupport":
            self._app.oboundary.AssignFixedSupport(self._get_args())
        elif self.type == "Voltage":
            self._app.oboundary.AssignVoltage(self._get_args())
        elif self.type == "VoltageDrop":
            self._app.oboundary.AssignVoltageDrop(self._get_args())
        elif self.type == "Current":
            self._app.oboundary.AssignCurrent(self._get_args())
        elif self.type == "Balloon":
            self._app.oboundary.AssignBalloon(self._get_args())
        elif self.type == "Winding" or self.type == "Winding Group":
            self._app.oboundary.AssignWindingGroup(self._get_args())
        elif self.type == "Vector Potential":
            self._app.oboundary.AssignVectorPotential(self._get_args())
        elif self.type == "CoilTerminal" or self.type == "Coil Terminal":
            self._app.oboundary.AssignCoilTerminal(self._get_args())
        elif self.type == "Coil":
            self._app.oboundary.AssignCoil(self._get_args())
        elif self.type == "Source":
            self._app.oboundary.AssignSource(self._get_args())
        elif self.type == "Sink":
            self._app.oboundary.AssignSink(self._get_args())
        elif self.type == "SignalNet":
            self._app.oboundary.AssignSignalNet(self._get_args())
        elif self.type == "GroundNet":
            self._app.oboundary.AssignGroundNet(self._get_args())
        elif self.type == "FloatingNet":
            self._app.oboundary.AssignFloatingNet(self._get_args())
        elif self.type == "SignalLine":
            self._app.oboundary.AssignSingleSignalLine(self._get_args())
        elif self.type == "ReferenceGround":
            self._app.oboundary.AssignSingleReferenceGround(self._get_args())
        elif self.type == "Circuit Port":
            self._app.oboundary.AssignCircuitPort(self._get_args())
        elif self.type == "Lumped Port":
            self._app.oboundary.AssignLumpedPort(self._get_args())
        elif self.type == "Wave Port":
            self._app.oboundary.AssignWavePort(self._get_args())
        elif self.type == "Floquet Port":
            self._app.oboundary.AssignFloquetPort(self._get_args())
        elif self.type == "AutoIdentify":
            self._app.oboundary.AutoIdentifyPorts(
                ["NAME:Faces", self.props["Faces"]],
                self.props["IsWavePort"],
                ["NAME:ReferenceConductors"] + self.props["ReferenceConductors"],
                self.name,
                self.props["RenormalizeModes"],
            )
        elif self.type == "SBRTxRxSettings":
            self._app.oboundary.SetSBRTxRxSettings(self._get_args())
        elif self.type == "EndConnection":
            self._app.oboundary.AssignEndConnection(self._get_args())
        else:
            return False
        return True

    @pyaedt_function_handler()
    def update(self):
        """Update the boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.type == "Perfect E":
            self._app.oboundary.EditPerfectE(self._boundary_name, self._get_args())
        elif self.type == "Perfect H":
            self._app.oboundary.EditPerfectH(self._boundary_name, self._get_args())
        elif self.type == "Aperture":
            self._app.oboundary.EditAperture(self._boundary_name, self._get_args())
        elif self.type == "Radiation":
            self._app.oboundary.EditRadiation(self._boundary_name, self._get_args())
        elif self.type == "Finite Conductivity":
            self._app.oboundary.EditFiniteCond(self._boundary_name, self._get_args())
        elif self.type == "Lumped RLC":
            self._app.oboundary.EditLumpedRLC(self._boundary_name, self._get_args())
        elif self.type == "Impedance":
            self._app.oboundary.EditImpedance(self._boundary_name, self._get_args())
        elif self.type == "Layered Impedance":
            self._app.oboundary.EditLayeredImpedance(self._boundary_name, self._get_args())
        elif self.type == "Anisotropic Impedance":
            self._app.oboundary.EditAssignAnisotropicImpedance(
                self._boundary_name, self._get_args()
            )  # pragma: no cover
        elif self.type == "Primary":
            self._app.oboundary.EditPrimary(self._boundary_name, self._get_args())
        elif self.type == "Secondary":
            self._app.oboundary.EditSecondary(self._boundary_name, self._get_args())
        elif self.type == "Lattice Pair":
            self._app.oboundary.EditLatticePair(self._boundary_name, self._get_args())
        elif self.type == "HalfSpace":
            self._app.oboundary.EditHalfSpace(self._boundary_name, self._get_args())
        elif self.type == "Multipaction SEE":
            self._app.oboundary.EditMultipactionSEE(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Fresnel":
            self._app.oboundary.EditFresnel(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Symmetry":
            self._app.oboundary.EditSymmetry(self._boundary_name, self._get_args())
        elif self.type == "Zero Tangential H Field":
            self._app.oboundary.EditZeroTangentialHField(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Zero Integrated Tangential H Field":
            self._app.oboundary.EditIntegratedZeroTangentialHField(
                self._boundary_name, self._get_args()
            )  # pragma: no cover
        elif self.type == "Tangential H Field":
            self._app.oboundary.EditTangentialHField(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Insulating":
            self._app.oboundary.EditInsulating(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Independent":
            self._app.oboundary.EditIndependent(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Dependent":
            self._app.oboundary.EditDependent(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Band":
            self._app.omodelsetup.EditMotionSetup(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "InfiniteGround":
            self._app.oboundary.EditInfiniteGround(self._boundary_name, self._get_args())
        elif self.type == "ThinConductor":
            self._app.oboundary.EditThinConductor(self._boundary_name, self._get_args())
        elif self.type == "Stationary Wall":
            self._app.oboundary.EditStationaryWallBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Symmetry Wall":
            self._app.oboundary.EditSymmetryWallBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Resistance":
            self._app.oboundary.EditResistanceBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Conducting Plate":
            self._app.oboundary.EditConductingPlateBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Adiabatic Plate":
            self._app.oboundary.EditAdiabaticPlateBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Network":
            self._app.oboundary.EditNetworkBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Grille":
            self._app.oboundary.EditGrilleBoundary(self._boundary_name, self._get_args())
        elif self.type == "Opening":
            self._app.oboundary.EditOpeningBoundary(self._boundary_name, self._get_args())
        elif self.type == "EMLoss":
            self._app.oboundary.EditEMLoss(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Block":
            self._app.oboundary.EditBlockBoundary(self._boundary_name, self._get_args())
        elif self.type == "SourceIcepak":
            self._app.oboundary.EditSourceBoundary(self._get_args())
        elif self.type == "Voltage":
            self._app.oboundary.EditVoltage(self._boundary_name, self._get_args())
        elif self.type == "VoltageDrop":
            self._app.oboundary.EditVoltageDrop(self._boundary_name, self._get_args())
        elif self.type == "Current":
            self._app.oboundary.EditCurrent(self._boundary_name, self._get_args())
        elif self.type == "Winding" or self.type == "Winding Group":
            self._app.oboundary.EditWindingGroup(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Vector Potential":
            self._app.oboundary.EditVectorPotential(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "CoilTerminal" or self.type == "Coil Terminal":
            self._app.oboundary.EditCoilTerminal(self._boundary_name, self._get_args())
        elif self.type == "Coil":
            self._app.oboundary.EditCoil(self._boundary_name, self._get_args())
        elif self.type == "Source":
            self._app.oboundary.EditTerminal(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "Sink":
            self._app.oboundary.EditTerminal(self._boundary_name, self._get_args())
        elif self.type == "SignalNet" or self.type == "GroundNet" or self.type == "FloatingNet":
            self._app.oboundary.EditTerminal(self._boundary_name, self._get_args())
        elif self.type in "Circuit Port":
            self._app.oboundary.EditCircuitPort(self._boundary_name, self._get_args())
        elif self.type in "Lumped Port":
            self._app.oboundary.EditLumpedPort(self._boundary_name, self._get_args())
        elif self.type in "Wave Port":
            self._app.oboundary.EditWavePort(self._boundary_name, self._get_args())
        elif self.type == "SetSBRTxRxSettings":
            self._app.oboundary.SetSBRTxRxSettings(self._get_args())  # pragma: no cover
        elif self.type == "Floquet Port":
            self._app.oboundary.EditFloquetPort(self._boundary_name, self._get_args())  # pragma: no cover
        elif self.type == "End Connection":
            self._app.oboundary.EditEndConnection(self._boundary_name, self._get_args())
        else:
            return False  # pragma: no cover
        self._boundary_name = self.name
        return True

    @pyaedt_function_handler()
    def update_assignment(self):
        """Update the boundary assignment.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if "Faces" in self.props:
            faces = self.props["Faces"]
            faces_out = []
            if type(faces) is not list:
                faces = [faces]
            for f in faces:
                if type(f) is EdgePrimitive or type(f) is FacePrimitive or type(f) is VertexPrimitive:
                    faces_out.append(f.id)
                else:
                    faces_out.append(f)
            self._app.oboundary.ReassignBoundary(["Name:" + self.name, "Faces:=", faces_out])
        elif "Objects" in self.props:
            pr = []
            for el in self.props["Objects"]:
                try:
                    pr.append(self._app.modeler[el].name)
                except (KeyError, AttributeError):
                    pass

            self._app.oboundary.ReassignBoundary(["Name:" + self.name, "Objects:=", pr])
        else:
            return False
        return True


class MaxwellParameters(BoundaryCommon, object):
    """Manages parameter data and execution.

    Examples
    --------

    Create a matrix in Maxwell3D return a ``pyaedt.modules.Boundary.BoundaryObject``

    >>> from pyaedt import Maxwell2d
    >>> maxwell_2d = Maxwell2d()
    >>> coil1 = maxwell_2d.modeler.create_rectangle([8.5,1.5, 0], [8, 3], True, "Coil_1", "vacuum")
    >>> coil2 = maxwell_2d.modeler.create_rectangle([8.5,1.5, 0], [8, 3], True, "Coil_2", "vacuum")
    >>> maxwell_2d.assign_matrix(["Coil_1", "Coil_2"])
    """

    def __init__(self, app, name, props, boundarytype):
        self.auto_update = False
        self._app = app
        self._name = name
        self.props = BoundaryProps(self, OrderedDict(props))
        self.type = boundarytype
        self._boundary_name = self.name
        self.auto_update = True

    @property
    def name(self):
        """Boundary Name."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.update()

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Retrieve arguments.

        Parameters
        ----------
        props :
            The default is ``None``.

        Returns
        -------
        list
            List of boundary properties.

        """
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    @pyaedt_function_handler()
    def create(self):
        """Create a boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.type == "Matrix":
            self._app.o_maxwell_parameters.AssignMatrix(self._get_args())
        elif self.type == "Torque":
            self._app.o_maxwell_parameters.AssignTorque(self._get_args())
        elif self.type == "Force":
            self._app.o_maxwell_parameters.AssignForce(self._get_args())
        else:
            return False
        return True

    @pyaedt_function_handler()
    def update(self):
        """Update the boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.type == "Matrix":
            self._app.o_maxwell_parameters.EditMatrix(self._boundary_name, self._get_args())
        elif self.type == "Force":
            self._app.o_maxwell_parameters.EditForce(self._boundary_name, self._get_args())
        elif self.type == "Torque":
            self._app.o_maxwell_parameters.EditTorque(self._boundary_name, self._get_args())
        else:
            return False
        self._boundary_name = self.name
        return True

    @pyaedt_function_handler()
    def _create_matrix_reduction(self, red_type, sources, matrix_name=None, join_name=None):
        if not matrix_name:
            matrix_name = generate_unique_name("ReducedMatrix", n=3)
        if not join_name:
            join_name = generate_unique_name("Join" + red_type, n=3)
        try:
            self._app.o_maxwell_parameters.AddReduceOp(
                self.name,
                matrix_name,
                ["NAME:" + join_name, "Type:=", "Join in " + red_type, "Sources:=", ",".join(sources)],
            )
            return matrix_name, join_name
        except:
            self._app.logger.error("Failed to create Matrix Reduction")
            return False, False

    @pyaedt_function_handler()
    def join_series(self, sources, matrix_name=None, join_name=None):
        """

        Parameters
        ----------
        sources : list
            Sources to be included in matrix reduction.
        matrix_name :  str, optional
            name of the string to create.
        join_name : str, optional
            Name of the Join operation.

        Returns
        -------
        (str, str)
            Matrix name and Joint name.

        """
        return self._create_matrix_reduction(
            red_type="Series", sources=sources, matrix_name=matrix_name, join_name=join_name
        )

    @pyaedt_function_handler()
    def join_parallel(self, sources, matrix_name=None, join_name=None):
        """

        Parameters
        ----------
        sources : list
            Sources to be included in matrix reduction.
        matrix_name :  str, optional
            name of the string to create.
        join_name : str, optional
            Name of the Join operation.

        Returns
        -------
        (str, str)
            Matrix name and Joint name.

        """
        return self._create_matrix_reduction(
            red_type="Parallel", sources=sources, matrix_name=matrix_name, join_name=join_name
        )


class FieldSetup(BoundaryCommon, object):
    """Manages Far Field and Near Field Component data and execution.

    Examples
    --------
    In this example the sphere1 returned object is a ``pyaedt.modules.Boundary.FarFieldSetup``
    >>> from pyaedt import Hfss
    >>> hfss = Hfss()
    >>> sphere1 = hfss.insert_infinite_sphere()
    >>> sphere1.props["ThetaStart"] = "-90deg"
    >>> sphere1.props["ThetaStop"] = "90deg"
    >>> sphere1.props["ThetaStep"] = "2deg"
    >>> sphere1.delete()
    """

    def __init__(self, app, component_name, props, component_type):
        self.auto_update = False
        self._app = app
        self.type = component_type
        self.name = component_name
        self.props = BoundaryProps(self, OrderedDict(props))
        self.auto_update = True

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    @pyaedt_function_handler()
    def create(self):
        """Create a Field Setup Component in HFSS.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        if self.type == "FarFieldSphere":
            self._app.oradfield.InsertInfiniteSphereSetup(self._get_args())
        elif self.type == "NearFieldBox":
            self._app.oradfield.InsertBoxSetup(self._get_args())
        elif self.type == "NearFieldSphere":
            self._app.oradfield.InsertSphereSetup(self._get_args())
        elif self.type == "NearFieldRectangle":
            self._app.oradfield.InsertRectangleSetup(self._get_args())
        elif self.type == "NearFieldLine":
            self._app.oradfield.InsertLineSetup(self._get_args())
        elif self.type == "AntennaOverlay":
            self._app.oradfield.AddAntennaOverlay(self._get_args())
        elif self.type == "FieldSourceGroup":
            self._app.oradfield.AddRadFieldSourceGroup(self._get_args())
        return True

    @pyaedt_function_handler()
    def update(self):
        """Update the Field Setup in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        if self.type == "FarFieldSphere":
            self._app.oradfield.EditInfiniteSphereSetup(self.name, self._get_args())
        elif self.type == "NearFieldBox":
            self._app.oradfield.EditBoxSetup(self.name, self._get_args())
        elif self.type == "NearFieldSphere":
            self._app.oradfield.EditSphereSetup(self.name, self._get_args())
        elif self.type == "NearFieldRectangle":
            self._app.oradfield.EditRectangleSetup(self.name, self._get_args())
        elif self.type == "NearFieldLine":
            self._app.oradfield.EditLineSetup(self.name, self._get_args())
        elif self.type == "AntennaOverlay":
            self._app.oradfield.EditAntennaOverlay(self.name, self._get_args())
        elif self.type == "FieldSourceGroup":
            self._app.oradfield.EditRadFieldSourceGroup(self._get_args())
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete the Field Setup in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._app.oradfield.DeleteSetup([self.name])
        for el in self._app.field_setups:
            if el.name == self.name:
                self._app.field_setups.remove(el)
        return True


class FarFieldSetup(FieldSetup, object):
    """Manages Far Field Component data and execution.

    Examples
    --------
    in this example the sphere1 returned object is a ``pyaedt.modules.Boundary.FarFieldSetup``
    >>> from pyaedt import Hfss
    >>> hfss = Hfss()
    >>> sphere1 = hfss.insert_infinite_sphere()
    >>> sphere1.props["ThetaStart"] = "-90deg"
    >>> sphere1.props["ThetaStop"] = "90deg"
    >>> sphere1.props["ThetaStep"] = "2deg"
    >>> sphere1.delete()
    """

    def __init__(self, app, component_name, props, component_type, units="deg"):
        FieldSetup.__init__(self, app, component_name, props, component_type)
        self.units = units

    @property
    def definition(self):
        """Set/Get the Far Field Angle Definition."""
        return self.props["CSDefinition"]

    @definition.setter
    def definition(self, value):
        actual_value = self.props["CSDefinition"]
        self.props["CSDefinition"] = value
        actual_defs = None
        defs = None
        if actual_value != value and value == "Theta-Phi":
            defs = ["ThetaStart", "ThetaStop", "ThetaStep", "PhiStart", "PhiStop", "PhiStep"]
            actual_defs = [
                "AzimuthStart",
                "AzimuthStop",
                "AzimuthStep",
                "ElevationStart",
                "ElevationStop",
                "ElevationStep",
            ]
        elif actual_value != value and value == "El Over Az":
            defs = ["AzimuthStart", "AzimuthStop", "AzimuthStep", "ElevationStart", "ElevationStop", "ElevationStep"]
            if actual_value == "Theta-Phi":
                actual_defs = ["ThetaStart", "ThetaStop", "ThetaStep", "PhiStart", "PhiStop", "PhiStep"]
            else:
                actual_defs = [
                    "AzimuthStart",
                    "AzimuthStop",
                    "AzimuthStep",
                    "ElevationStart",
                    "ElevationStop",
                    "ElevationStep",
                ]
        elif actual_value != value:
            defs = ["ElevationStart", "ElevationStop", "ElevationStep", "AzimuthStart", "AzimuthStop", "AzimuthStep"]
            if actual_value == "Theta-Phi":
                actual_defs = ["ThetaStart", "ThetaStop", "ThetaStep", "PhiStart", "PhiStop", "PhiStep"]
            else:
                actual_defs = [
                    "ElevationStart",
                    "ElevationStop",
                    "ElevationStep",
                    "AzimuthStart",
                    "AzimuthStop",
                    "AzimuthStep",
                ]
        if actual_defs != defs:
            self.props[defs[0]] = self.props[actual_defs[0]]
            self.props[defs[1]] = self.props[actual_defs[1]]
            self.props[defs[2]] = self.props[actual_defs[2]]
            self.props[defs[3]] = self.props[actual_defs[3]]
            self.props[defs[4]] = self.props[actual_defs[4]]
            self.props[defs[5]] = self.props[actual_defs[5]]
            del self.props[actual_defs[0]]
            del self.props[actual_defs[1]]
            del self.props[actual_defs[2]]
            del self.props[actual_defs[3]]
            del self.props[actual_defs[4]]
            del self.props[actual_defs[5]]
        self.update()

    @property
    def use_custom_radiation_surface(self):
        """Set/Get the Far Field Radiation Surface Enable."""
        return self.props["UseCustomRadiationSurface"]

    @use_custom_radiation_surface.setter
    def use_custom_radiation_surface(self, value):
        self.props["UseCustomRadiationSurface"] = value
        self.update()

    @property
    def custom_radiation_surface(self):
        """Set/Get the Far Field Radiation Surface FaceList."""
        return self.props["CustomRadiationSurface"]

    @custom_radiation_surface.setter
    def custom_radiation_surface(self, value):
        if value:
            self.props["UseCustomRadiationSurface"] = True
            self.props["CustomRadiationSurface"] = value
        else:
            self.props["UseCustomRadiationSurface"] = False
            self.props["CustomRadiationSurface"] = ""
        self.update()

    @property
    def use_local_coordinate_system(self):
        """Set/Get the usage of a custom Coordinate System."""
        return self.props["UseLocalCS"]

    @use_local_coordinate_system.setter
    def use_local_coordinate_system(self, value):
        self.props["UseLocalCS"] = value
        self.update()

    @property
    def local_coordinate_system(self):
        """Set/Get the custom Coordinate System name."""
        return self.props["CoordSystem"]

    @local_coordinate_system.setter
    def local_coordinate_system(self, value):
        if value:
            self.props["UseLocalCS"] = True
            self.props["CoordSystem"] = value
        else:
            self.props["UseLocalCS"] = False
            self.props["CoordSystem"] = ""
        self.update()

    @property
    def polarization(self):
        """Set/Get the Far Field Polarization."""
        return self.props["Polarization"]

    @polarization.setter
    def polarization(self, value):
        self.props["Polarization"] = value
        self.update()

    @property
    def slant_angle(self):
        """Set/Get the Far Field Slant Angle if Polarization is Set to `Slant`."""

        if self.props["Polarization"] == "Slant":
            return self.props["SlantAngle"]
        else:
            return

    @slant_angle.setter
    def slant_angle(self, value):
        self.props["Polarization"] = "Slant"
        self.props["SlantAngle"] = value
        self.update()

    @property
    def theta_start(self):
        """Set/Get the Far Field Theta Start Angle if Definition is Set to `Theta-Phi`."""

        if "ThetaStart" in self.props:
            return self.props["ThetaStart"]
        else:
            return

    @property
    def theta_stop(self):
        """Set/Get the Far Field Theta Stop Angle if Definition is Set to `Theta-Phi`."""

        if "ThetaStop" in self.props:
            return self.props["ThetaStop"]
        else:
            return

    @property
    def theta_step(self):
        """Set/Get the Far Field Theta Step Angle if Definition is Set to `Theta-Phi`."""

        if "ThetaStep" in self.props:
            return self.props["ThetaStep"]
        else:
            return

    @property
    def phi_start(self):
        """Set/Get the Far Field Phi Start Angle if Definition is Set to `Theta-Phi`."""

        if "PhiStart" in self.props:
            return self.props["PhiStart"]
        else:
            return

    @property
    def phi_stop(self):
        """Set/Get the Far Field Phi Stop Angle if Definition is Set to `Theta-Phi`."""

        if "PhiStop" in self.props:
            return self.props["PhiStop"]
        else:
            return

    @property
    def phi_step(self):
        """Set/Get the Far Field Phi Step Angle if Definition is Set to `Theta-Phi`."""

        if "PhiStep" in self.props:
            return self.props["PhiStep"]
        else:
            return

    @property
    def azimuth_start(self):
        """Set/Get the Far Field Azimuth Start Angle if Definition is Set to `Az Over El` or `El Over Az`."""

        if "AzimuthStart" in self.props:
            return self.props["AzimuthStart"]
        else:
            return

    @property
    def azimuth_stop(self):
        """Set/Get the Far Field Azimuth Stop Angle if Definition is Set to `Az Over El` or `El Over Az`."""

        if "AzimuthStop" in self.props:
            return self.props["AzimuthStop"]
        else:
            return

    @property
    def azimuth_step(self):
        """Set/Get the Far Field Azimuth Step Angle if Definition is Set to `Az Over El` or `El Over Az`."""

        if "AzimuthStep" in self.props:
            return self.props["AzimuthStep"]
        else:
            return

    @property
    def elevation_start(self):
        """Set/Get the Far Field Elevation Start Angle if Definition is Set to `Az Over El` or `El Over Az`."""

        if "ElevationStart" in self.props:
            return self.props["ElevationStart"]
        else:
            return

    @property
    def elevation_stop(self):
        """Set/Get the Far Field Elevation Stop Angle if Definition is Set to `Az Over El` or `El Over Az`."""

        if "ElevationStop" in self.props:
            return self.props["ElevationStop"]
        else:
            return

    @property
    def elevation_step(self):
        """Set/Get the Far Field Elevation Step Angle if Definition is Set to `Az Over El` or `El Over Az`."""

        if "ElevationStep" in self.props:
            return self.props["ElevationStep"]
        else:
            return

    @theta_start.setter
    def theta_start(self, value):
        if "ThetaStart" in self.props:
            self.props["ThetaStart"] = _dim_arg(value, self.units)
            self.update()

    @theta_stop.setter
    def theta_stop(self, value):
        if "ThetaStop" in self.props:
            self.props["ThetaStop"] = _dim_arg(value, self.units)
            self.update()

    @theta_step.setter
    def theta_step(self, value):
        if "ThetaStep" in self.props:
            self.props["ThetaStep"] = _dim_arg(value, self.units)
            self.update()

    @phi_start.setter
    def phi_start(self, value):
        if "PhiStart" in self.props:
            self.props["PhiStart"] = _dim_arg(value, self.units)
            self.update()

    @phi_stop.setter
    def phi_stop(self, value):
        if "PhiStop" in self.props:
            self.props["PhiStop"] = _dim_arg(value, self.units)
            self.update()

    @phi_step.setter
    def phi_step(self, value):
        if "PhiStep" in self.props:
            self.props["PhiStep"] = _dim_arg(value, self.units)
            self.update()

    @azimuth_start.setter
    def azimuth_start(self, value):
        if "AzimuthStart" in self.props:
            self.props["AzimuthStart"] = _dim_arg(value, self.units)
            self.update()

    @azimuth_stop.setter
    def azimuth_stop(self, value):
        if "AzimuthStop" in self.props:
            self.props["AzimuthStop"] = _dim_arg(value, self.units)
            self.update()

    @azimuth_step.setter
    def azimuth_step(self, value):
        if "AzimuthStep" in self.props:
            self.props["AzimuthStep"] = _dim_arg(value, self.units)
            self.update()

    @elevation_start.setter
    def elevation_start(self, value):
        if "ElevationStart" in self.props:
            self.props["ElevationStart"] = _dim_arg(value, self.units)
            self.update()

    @elevation_stop.setter
    def elevation_stop(self, value):
        if "ElevationStop" in self.props:
            self.props["ElevationStop"] = _dim_arg(value, self.units)
            self.update()

    @elevation_step.setter
    def elevation_step(self, value):
        if "ElevationStep" in self.props:
            self.props["ElevationStep"] = _dim_arg(value, self.units)
            self.update()


class Matrix(object):
    """Manages Matrix in Q3d and Q2d Projects.

    Examples
    --------


    """

    def __init__(self, app, name, operations=None):
        self._app = app
        self.omatrix = self._app.omatrix
        self.name = name
        self._sources = []
        if operations:
            if isinstance(operations, list):
                self._operations = operations
            else:
                self._operations = [operations]
        self.CATEGORIES = CATEGORIESQ3D()

    @pyaedt_function_handler()
    def sources(self, is_gc_sources=True):
        """List of matrix sources.

        Parameters
        ----------
        is_gc_sources : bool,
            In Q3d, define if to return GC sources or RL sources. Default `True`.

        Returns
        -------
        List
        """
        if self.name in list(self._app.omatrix.ListReduceMatrixes()):
            if self._app.design_type == "Q3D Extractor":
                self._sources = list(self._app.omatrix.ListReduceMatrixReducedSources(self.name, is_gc_sources))
            else:
                self._sources = list(self._app.omatrix.ListReduceMatrixReducedSources(self.name))
        return self._sources

    @pyaedt_function_handler()
    def get_sources_for_plot(
        self,
        get_self_terms=True,
        get_mutual_terms=True,
        first_element_filter=None,
        second_element_filter=None,
        category="C",
    ):
        """Return a list of source of specified matrix ready to be used in plot reports.

        Parameters
        ----------
        get_self_terms : bool
            Either if self terms have to be returned or not.
        get_mutual_terms : bool
            Either if mutual terms have to be returned or not.
        first_element_filter : str, optional
            Filter to apply to first element of equation. It accepts `*` and `?` as special characters.
        second_element_filter : str, optional
            Filter to apply to second element of equation. It accepts `*` and `?` as special characters.
        category : str
            Plot category name as in the report. Eg. "C" is category Capacitance.
            Matrix `CATEGORIES` property can be used to map available categories.

        Returns
        -------
        list

        Examples
        --------
        >>> from pyaedt import Q3d
        >>> q3d = Q3d(project_path)
        >>> q3d.matrices[0].get_sources_for_plot(first_element_filter="Bo?1",
        ...                                      second_element_filter="GND*", category="DCL")
        """
        if not first_element_filter:
            first_element_filter = "*"
        if not second_element_filter:
            second_element_filter = "*"
        is_cg = False
        if category in [self.CATEGORIES.Q3D.C, self.CATEGORIES.Q3D.G]:
            is_cg = True
        list_output = []
        if get_self_terms:
            for el in self.sources(is_gc_sources=is_cg):
                value = "{}({},{})".format(category, el, el)
                if filter_tuple(value, first_element_filter, second_element_filter):
                    list_output.append(value)
        if get_mutual_terms:
            for el1 in self.sources(is_gc_sources=is_cg):
                for el2 in self.sources(is_gc_sources=is_cg):
                    if el1 != el2:
                        value = "{}({},{})".format(category, el1, el2)
                        if filter_tuple(value, first_element_filter, second_element_filter):
                            list_output.append(value)
        return list_output

    @property
    def operations(self):
        """List of matrix operations.

        Returns
        -------
        List
        """
        if self.name in list(self._app.omatrix.ListReduceMatrixes()):
            self._operations = self._app.omatrix.ListReduceMatrixOperations(self.name)
        return self._operations

    @pyaedt_function_handler()
    def create(self, source_names=None):
        """Create a new matrix.

        Parameters
        ----------
        source_names : str, list
            List or str containing the content of the matrix reduction (eg. source name).

        Returns
        -------
        bool
            `True` if succeeded.
        """
        if not isinstance(source_names, list) and source_names:
            source_names = [source_names]
        command = self._write_command(source_names)
        self.omatrix.InsertRM(self.name, command)
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete current matrix.

        Returns
        -------
        bool
            `True` if succeeded.
        """
        self.omatrix.DeleteRM(self.name)
        for el in self._app.matrices:
            if el.name == self.name:
                self._app.matrices.remove(el)
        return True

    @pyaedt_function_handler()
    def add_operation(self, operation_type, source_names=None):
        """Add a new operation to existing matrix.

        Parameters
        ----------
        operation_type : str
            Operation to perform
        source_names : str, list
            List or str containing the content of the matrix reduction (eg. source name).

        Returns
        -------
        bool
            `True` if succeeded.
        """
        self._operations.append(operation_type)
        if not isinstance(source_names, list) and source_names:
            source_names = [source_names]
        command = self._write_command(source_names)
        self.omatrix.RMAddOp(self.name, command)
        return True

    @pyaedt_function_handler()
    def _write_command(self, source_names):
        command = ""
        if self._operations[-1] == "JoinSeries":
            new_name = generate_unique_name(source_names[0])
            for el in self._app.boundaries:
                if el.name == source_names[0]:
                    new_name = el.props["Net"]
            command = "{}('{}', '{}')".format(self._operations[-1], new_name, "', '".join(source_names))
        elif self._operations[-1] == "JoinParallel":
            new_name = generate_unique_name(source_names[0])
            for el in self._app.boundaries:
                if el.name == source_names[0]:
                    new_name = el.props["Net"]
            new_source = source_names[0]
            new_sink = generate_unique_name("Sink")
            command = "{}('{}', '{}', '{}', '{}')".format(
                self._operations[-1], new_name, new_source, new_sink, "', '".join(source_names)
            )
        elif self._operations[-1] == "JoinSelectedTerminals":
            command = "{}('', '{}')".format(self._operations[-1], "', '".join(source_names))
        elif self._operations[-1] == "FloatInfinity":
            command = "FloatInfinity()"
        elif self._operations[-1] == "AddGround":
            command = "{}(SelectionArray[{}: '{}'], OverrideInfo())".format(
                self._operations[-1], len(source_names), "', '".join(source_names)
            )
        elif (
            self._operations[-1] == "SetReferenceGround"
            or self._operations[-1] == "SetReferenceGround"
            or self._operations[-1] == "Float"
        ):
            command = "{}(SelectionArray[{}: '{}'], OverrideInfo())".format(
                self._operations[-1], len(source_names), "', '".join(source_names)
            )
        elif self._operations[-1] == "Parallel" or self._operations[-1] == "DiffPair":
            pair_name = generate_unique_name("Pair")
            id = 0
            for el in self._app.boundaries:
                if el.name == source_names[0]:
                    id = self._app.modeler[el.props["Objects"][0]].id
            command = "{}(SelectionArray[{}: '{}'], OverrideInfo({}, '{}'))".format(
                self._operations[-1], len(source_names), "', '".join(source_names), id, pair_name
            )
        else:
            command = "{}('{}')".format(self._operations[-1], "', '".join(source_names))
        return command
