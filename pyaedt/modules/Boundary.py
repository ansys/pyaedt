"""
This module contains these classes: `BoundaryCommon` and `BoundaryObject`.
"""
from collections import OrderedDict
from pyaedt.generic.general_methods import aedt_exception_handler
from pyaedt.generic.DataHandlers import _dict2arg
from pyaedt.modeler.Object3d import EdgePrimitive, FacePrimitive, VertexPrimitive
from pyaedt.generic.DataHandlers import random_string


class BoundaryCommon(object):
    """ """

    @aedt_exception_handler
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

    @aedt_exception_handler
    def delete(self):
        """Delete the boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
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
        self._app = app
        self.name = "InsertNativeComponentData"
        self.component_name = component_name
        self.props = OrderedDict(
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
        )
        if props:
            self._update_props(self.props, props)
        self.native_properties = self.props["NativeComponentDefinitionProvider"]

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

    @aedt_exception_handler
    def _get_args(self, props=None):
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    @aedt_exception_handler
    def create(self):
        """Create a Native Component in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.name = "InsertNativeComponentData"
        try:
            names = [i for i in self._app.modeler.get_excitations_name()]
        except Exception as e:
            names = []
        self.antennaname = self._app.modeler.oeditor.InsertNativeComponent(self._get_args())
        try:
            a = [i for i in self._app.modeler.get_excitations_name() if i not in names]
            self.excitation_name = a[0].split(":")[0]
        except Exception as e:
            self.excitation_name = self.antennaname
        return True

    @aedt_exception_handler
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

    @aedt_exception_handler
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
    >>> inner = hfss.modeler.primitives.create_cylinder(hfss.PLANE.XY, origin, 3, 200, 0, "inner")
    >>> inner_id = hfss.modeler.primitives.get_obj_id("inner")
    >>> coat = hfss.assign_coating([inner_id], "copper", usethickness=True, thickness="0.2mm")
    """

    def __init__(self, app, name, props, boundarytype):
        self._app = app
        self.name = name
        self.props = props
        self.type = boundarytype

    @aedt_exception_handler
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

    @aedt_exception_handler
    def create(self):
        """Create a boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.type == "PerfectE":
            self._app.oboundary.AssignPerfectE(self._get_args())
        elif self.type == "PerfectH":
            self._app.oboundary.AssignPerfectH(self._get_args())
        elif self.type == "Aperture":
            self._app.oboundary.AssignAperture(self._get_args())
        elif self.type == "Radiation":
            self._app.oboundary.AssignRadiation(self._get_args())
        elif self.type == "FiniteCond":
            self._app.oboundary.AssignFiniteCond(self._get_args())
        elif self.type == "LumpedRLC":
            self._app.oboundary.AssignLumpedRLC(self._get_args())
        elif self.type == "Impedance":
            self._app.oboundary.AssignImpedance(self._get_args())
        elif self.type == "Anisotropic Impedance":
            self._app.oboundary.AssignAssignAnisotropicImpedance(self._get_args())
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
        elif self.type == "VectorPotential":
            self._app.oboundary.AssignVectorPotential(self._get_args())
        elif self.type == "CoilTerminal":
            self._app.oboundary.AssignCoilTerminal(self._get_args())
        elif self.type == "Coil":
            self._app.oboundary.AssignCoil(self._get_args())
        elif self.type == "Source":
            self._app.oboundary.AssignSource(self._get_args())
        elif self.type == "Sink":
            self._app.oboundary.AssignSink(self._get_args())
        elif self.type == "CircuitPort":
            self._app.oboundary.AssignCircuitPort(self._get_args())
        elif self.type == "LumpedPort":
            self._app.oboundary.AssignLumpedPort(self._get_args())
        elif self.type == "WavePort":
            self._app.oboundary.AssignWavePort(self._get_args())
        elif self.type == "FloquetPort":
            self._app.oboundary.AssignFloquetPort(self._get_args())
        elif self.type == "AutoIdentify":
            self._app.oboundary.AutoIdentifyPorts(
                ["NAME:Faces", self.props["Faces"]],
                self.props["IsWavePort"],
                ["NAME:ReferenceConductors", self.props["ReferenceConductors"]],
                self.name,
                self.props["RenormalizeModes"],
            )
        elif self.type == "SBRTxRxSettings":
            self._app.oboundary.SetSBRTxRxSettings(self._get_args())
        else:
            return False
        return True

    @aedt_exception_handler
    def update(self):
        """Update the boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.type == "PerfectE":
            self._app.oboundary.EditPerfectE(self.name, self._get_args())
        elif self.type == "PerfectH":
            self._app.oboundary.EditPerfectH(self.name, self._get_args())
        elif self.type == "Aperture":
            self._app.oboundary.EditAperture(self.name, self._get_args())
        elif self.type == "Radiation":
            self._app.oboundary.EditRadiation(self.name, self._get_args())
        elif self.type == "FiniteCond":
            self._app.oboundary.EditFiniteCond(self.name, self._get_args())
        elif self.type == "LumpedRLC":
            self._app.oboundary.EditLumpedRLC(self.name, self._get_args())
        elif self.type == "Impedance":
            self._app.oboundary.EditImpedance(self.name, self._get_args())
        elif self.type == "Anisotropic Impedance":
            self._app.oboundary.EditAssignAnisotropicImpedance(self.name, self._get_args())
        elif self.type == "Primary":
            self._app.oboundary.EditPrimary(self.name, self._get_args())
        elif self.type == "Secondary":
            self._app.oboundary.EditSecondary(self.name, self._get_args())
        elif self.type == "Lattice Pair":
            self._app.oboundary.EditLatticePair(self.name, self._get_args())
        elif self.type == "HalfSpace":
            self._app.oboundary.EditHalfSpace(self.name, self._get_args())
        elif self.type == "Multipaction SEE":
            self._app.oboundary.EditMultipactionSEE(self.name, self._get_args())
        elif self.type == "Fresnel":
            self._app.oboundary.EditFresnel(self.name, self._get_args())
        elif self.type == "Symmetry":
            self._app.oboundary.EditSymmetry(self.name, self._get_args())
        elif self.type == "Zero Tangential H Field":
            self._app.oboundary.EditZeroTangentialHField(self.name, self._get_args())
        elif self.type == "Zero Integrated Tangential H Field":
            self._app.oboundary.EditIntegratedZeroTangentialHField(self.name, self._get_args())
        elif self.type == "Tangential H Field":
            self._app.oboundary.EditTangentialHField(self.name, self._get_args())
        elif self.type == "Insulating":
            self._app.oboundary.EditInsulating(self.name, self._get_args())
        elif self.type == "Independent":
            self._app.oboundary.EditIndependent(self.name, self._get_args())
        elif self.type == "Dependent":
            self._app.oboundary.EditDependent(self.name, self._get_args())
        elif self.type == "Band":
            self._app.omodelsetup.EditMotionSetup(self.name, self._get_args())
        elif self.type == "InfiniteGround":
            self._app.oboundary.EditInfiniteGround(self.name, self._get_args())
        elif self.type == "ThinConductor":
            self._app.oboundary.EditThinConductor(self.name, self._get_args())
        elif self.type == "Stationary Wall":
            self._app.oboundary.EditStationaryWallBoundary(self.name, self._get_args())
        elif self.type == "Symmetry Wall":
            self._app.oboundary.EditSymmetryWallBoundary(self.name, self._get_args())
        elif self.type == "Resistance":
            self._app.oboundary.EditResistanceBoundary(self.name, self._get_args())
        elif self.type == "Conducting Plate":
            self._app.oboundary.EditConductingPlateBoundary(self.name, self._get_args())
        elif self.type == "Adiabatic Plate":
            self._app.oboundary.EditAdiabaticPlateBoundary(self.name, self._get_args())
        elif self.type == "Network":
            self._app.oboundary.EditNetworkBoundary(self.name, self._get_args())
        elif self.type == "Grille":
            self._app.oboundary.EditGrilleBoundary(self.name, self._get_args())
        elif self.type == "Opening":
            self._app.oboundary.EditOpeningBoundary(self.name, self._get_args())
        elif self.type == "EMLoss":
            self._app.oboundary.EditEMLoss(self.name, self._get_args())
        elif self.type == "Block":
            self._app.oboundary.EditBlockBoundary(self.name, self._get_args())
        elif self.type == "SourceIcepak":
            self._app.oboundary.EditSourceBoundary(self._get_args())
        elif self.type == "Voltage":
            self._app.oboundary.EditVoltage(self.name, self._get_args())
        elif self.type == "VoltageDrop":
            self._app.oboundary.EditVoltageDrop(self.name, self._get_args())
        elif self.type == "Current":
            self._app.oboundary.Current(self.name, self._get_args())
        elif self.type == "Winding" or self.type == "Winding Group":
            self._app.oboundary.EditWindingGroup(self.name, self._get_args())
        elif self.type == "VectorPotential":
            self._app.oboundary.EditVectorPotential(self.name, self._get_args())
        elif self.type == "CoilTerminal":
            self._app.oboundary.EditCoilTerminal(self.name, self._get_args())
        elif self.type == "Coil":
            self._app.oboundary.EditCoil(self.name, self._get_args())
        elif self.type == "Source":
            self._app.oboundary.EditTerminal(self.name, self._get_args())
        elif self.type == "Sink":
            self._app.oboundary.EditSink(self.name, self._get_args())
        elif self.type in ["CircuitPort", "Circuit Port"]:
            self._app.oboundary.EditCircuitPort(self.name, self._get_args())
        elif self.type in ["LumpedPort", "Lumped Port"]:
            self._app.oboundary.EditLumpedPort(self.name, self._get_args())
        elif self.type in ["WavePort", "Wave Port"]:
            self._app.oboundary.EditWavePort(self.name, self._get_args())
        elif self.type == "SetSBRTxRxSettings":
            self._app.oboundary.SetSBRTxRxSettings(self._get_args())
        elif self.type == "FloquetPort":
            self._app.oboundary.EditFloquetPort(self.name, self._get_args())
        else:
            return False
        return True

    @aedt_exception_handler
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

            self._app.oboundary.ReassignBoundary(["Name:" + self.name, "Objects:=", self.props["Objects"]])
        else:
            return False
        return True
