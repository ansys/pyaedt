# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This module contains these classes: ``BoundaryCommon`` and ``BoundaryObject``.
"""

from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.general_methods import PropsManager
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modeler.cad.elements_3d import EdgePrimitive
from ansys.aedt.core.modeler.cad.elements_3d import FacePrimitive
from ansys.aedt.core.modeler.cad.elements_3d import VertexPrimitive


class BoundaryProps(dict):
    """AEDT Boundary Component Internal Parameters."""

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if self._pyaedt_boundary.auto_update:
            if key in ["Edges", "Faces", "Objects"]:
                res = self._pyaedt_boundary.update_assignment()
            else:
                res = self._pyaedt_boundary.update()
            if not res:
                self._pyaedt_boundary._app.logger.warning("Update of %s Failed. Check needed arguments", key)

    def __init__(self, boundary, props):
        dict.__init__(self)
        if props:
            for key, value in props.items():
                if isinstance(value, dict):
                    dict.__setitem__(self, key, BoundaryProps(boundary, value))
                elif isinstance(value, list):
                    list_els = []
                    for el in value:
                        if isinstance(el, dict):
                            list_els.append(BoundaryProps(boundary, el))
                        else:
                            list_els.append(el)
                    dict.__setitem__(self, key, list_els)
                else:
                    dict.__setitem__(self, key, value)
        self._pyaedt_boundary = boundary

    def _setitem_without_update(self, key, value):
        dict.__setitem__(self, key, value)


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
    def _initialize_bynary_tree(self):
        if self._child_object:
            BinaryTreeNode.__init__(self, self._name, self._child_object, False)

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
            if self.name in self._app.excitation_objects.keys():
                self._app.excitation_objects.pop(self.name)
        return True

    def _get_boundary_data(self, ds):
        try:
            if "MaxwellParameterSetup" in self._app.design_properties:
                param = "MaxwellParameters"
                setup = "MaxwellParameterSetup"
                if isinstance(self._app.design_properties[setup][param][ds], dict):
                    return [
                        self._app.design_properties["MaxwellParameterSetup"]["MaxwellParameters"][ds],
                        self._app.design_properties["MaxwellParameterSetup"]["MaxwellParameters"][ds][
                            "MaxwellParameterType"
                        ],
                    ]
        except Exception:
            self._app.logger.debug(
                "An error occurred while getting boundary data for MaxwellParameterSetup."
            )  # pragma: no cover
        try:
            if (
                "ModelSetup" in self._app.design_properties
                and "MotionSetupList" in self._app.design_properties["ModelSetup"]
            ):
                motion_list = "MotionSetupList"
                setup = "ModelSetup"
                # check moving part
                if isinstance(self._app.design_properties[setup][motion_list][ds], dict):
                    return [
                        self._app.design_properties["ModelSetup"]["MotionSetupList"][ds],
                        self._app.design_properties["ModelSetup"]["MotionSetupList"][ds]["MotionType"],
                    ]
        except Exception:
            self._app.logger.debug("An error occurred while getting boundary data for ModelSetup.")  # pragma: no cover
        try:
            if ds in self._app.design_properties["BoundarySetup"]["Boundaries"]:
                if (
                    self._app.design_properties["BoundarySetup"]["Boundaries"][ds]["BoundType"] == "Network"
                    and self._app.design_type == "Icepak"
                ):
                    return [self._app.design_properties["BoundarySetup"]["Boundaries"][ds], ""]
                else:
                    return [
                        self._app.design_properties["BoundarySetup"]["Boundaries"][ds],
                        self._app.design_properties["BoundarySetup"]["Boundaries"][ds]["BoundType"],
                    ]
        except Exception:
            self._app.logger.debug(
                "An error occurred while getting boundary data for BoundarySetup."
            )  # pragma: no cover
            return []


def disable_auto_update(func):
    """Decorator used to disable automatic update."""

    def wrapper(self, *args, **kwargs):
        """Inner wrapper function."""
        obj = self
        if not hasattr(self, "auto_update"):
            obj = self.pcb
        auto_update = obj.auto_update
        obj.auto_update = False
        out = func(self, *args, **kwargs)
        if auto_update:
            obj.update()
        obj.auto_update = auto_update
        return out

    return wrapper


class BoundaryObject(BoundaryCommon, BinaryTreeNode):
    """Manages boundary data and execution.

    Parameters
    ----------
    app : object
        An AEDT application from ``ansys.aedt.core.application``.
    name : str
        Name of the boundary.
    props : dict, optional
        Properties of the boundary.
    boundarytype : str, optional
        Type of the boundary.

    Examples
    --------

    Create a cylinder at the XY working plane and assign a copper coating of 0.2 mm to it. The Coating is a boundary
    operation and coat will return a ``ansys.aedt.core.modules.boundary.common.BoundaryObject``

    >>> from ansys.aedt.core import Hfss
    >>> hfss =Hfss()
    >>> origin = hfss.modeler.Position(0, 0, 0)
    >>> inner = hfss.modeler.create_cylinder(hfss.PLANE.XY,origin,3,200,0,"inner")
    >>> inner_id = hfss.modeler.get_obj_id("inner",)
    >>> coat = hfss.assign_coating([inner_id],"copper",use_thickness=True,thickness="0.2mm")
    """

    def __init__(self, app, name, props=None, boundarytype=None, auto_update=True):
        self.auto_update = False
        self._app = app
        self._name = name
        self.__props = None
        self.__props = BoundaryProps(self, props) if props else {}
        self._type = boundarytype
        self._boundary_name = self.name
        self.auto_update = auto_update
        self._initialize_bynary_tree()

    @property
    def _child_object(self):
        """Object-oriented properties.

        Returns
        -------
        class:`ansys.aedt.core.modeler.cad.elements_3d.BinaryTreeNode`

        """
        child_object = None
        design_childs = self._app.get_oo_name(self._app.odesign)

        if "Thermal" in design_childs:
            cc = self._app.get_oo_object(self._app.odesign, "Thermal")
            cc_names = self._app.get_oo_name(cc)
            if self.name in cc_names:
                child_object = cc.GetChildObject(self.name)
        elif "Boundaries" in design_childs:
            cc = self._app.get_oo_object(self._app.odesign, "Boundaries")
            if self.name in cc.GetChildNames():
                child_object = cc.GetChildObject(self.name)
            elif "Excitations" in design_childs and self.name in self._app.get_oo_name(
                self._app.odesign, "Excitations"
            ):
                child_object = self._app.get_oo_object(self._app.odesign, "Excitations").GetChildObject(self.name)
            elif self._app.design_type in ["Maxwell 3D", "Maxwell 2D"] and "Model" in design_childs:
                model = self._app.get_oo_object(self._app.odesign, "Model")
                if self.name in model.GetChildNames():
                    child_object = model.GetChildObject(self.name)
            elif "Excitations" in design_childs and self._app.get_oo_name(self._app.odesign, "Excitations"):
                for port in self._app.get_oo_name(self._app.odesign, "Excitations"):
                    terminals = self._app.get_oo_name(self._app.odesign, f"Excitations\\{port}")
                    if self.name in terminals:
                        child_object = self._app.get_oo_object(self._app.odesign, f"Excitations\\{port}\\{self.name}")
            elif "Conductors" in design_childs and self._app.get_oo_name(self._app.odesign, "Conductors"):
                for port in self._app.get_oo_name(self._app.odesign, "Conductors"):
                    if self.name == port:
                        child_object = self._app.get_oo_object(self._app.odesign, f"Conductors\\{port}")
        return child_object

    @property
    def props(self):
        """Boundary data.

        Returns
        -------
        :class:BoundaryProps
        """
        if self.__props:
            return self.__props
        props = self._get_boundary_data(self.name)

        if props:
            self.__props = BoundaryProps(self, props[0])
            self._type = props[1]
        return self.__props

    @property
    def type(self):
        """Boundary type.

        Returns
        -------
        str
            Returns the type of the boundary.
        """
        if not self._type:
            if self.available_properties:
                if "Type" in self.available_properties:
                    self._type = self.props["Type"]
                elif "BoundType" in self.available_properties:
                    self._type = self.props["BoundType"]
            elif self.properties and self.properties["Type"]:
                self._type = self.properties["Type"]

        if self._app.design_type == "Icepak" and self._type == "Source":
            return "SourceIcepak"
        else:
            return self._type

    @type.setter
    def type(self, value):
        self._type = value

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
        bound_type = self.type
        if bound_type == "Perfect E":
            self._app.oboundary.AssignPerfectE(self._get_args())
        elif bound_type == "Perfect H":
            self._app.oboundary.AssignPerfectH(self._get_args())
        elif bound_type == "Aperture":
            self._app.oboundary.AssignAperture(self._get_args())
        elif bound_type == "Radiation":
            self._app.oboundary.AssignRadiation(self._get_args())
        elif bound_type == "FE-BI":
            self._app.oboundary.AssignFEBI(self._get_args())
        elif bound_type == "Finite Conductivity":
            self._app.oboundary.AssignFiniteCond(self._get_args())
        elif bound_type == "Lumped RLC":
            self._app.oboundary.AssignLumpedRLC(self._get_args())
        elif bound_type == "Impedance":
            self._app.oboundary.AssignImpedance(self._get_args())
        elif bound_type == "Layered Impedance":
            self._app.oboundary.AssignLayeredImp(self._get_args())
        elif bound_type == "Anisotropic Impedance":
            self._app.oboundary.AssignAnisotropicImpedance(self._get_args())
        elif bound_type == "Primary":
            self._app.oboundary.AssignPrimary(self._get_args())
        elif bound_type == "Secondary":
            self._app.oboundary.AssignSecondary(self._get_args())
        elif bound_type == "Lattice Pair":
            self._app.oboundary.AssignLatticePair(self._get_args())
        elif bound_type == "HalfSpace":
            self._app.oboundary.AssignHalfSpace(self._get_args())
        elif bound_type == "Multipaction SEE":
            self._app.oboundary.AssignMultipactionSEE(self._get_args())
        elif bound_type == "Fresnel":
            self._app.oboundary.AssignFresnel(self._get_args())
        elif bound_type == "Symmetry":
            self._app.oboundary.AssignSymmetry(self._get_args())
        elif bound_type == "Zero Tangential H Field":
            self._app.oboundary.AssignZeroTangentialHField(self._get_args())
        elif bound_type == "Zero Integrated Tangential H Field":
            self._app.oboundary.AssignIntegratedZeroTangentialHField(self._get_args())
        elif bound_type == "Tangential H Field":
            self._app.oboundary.AssignTangentialHField(self._get_args())
        elif bound_type == "Insulating":
            self._app.oboundary.AssignInsulating(self._get_args())
        elif bound_type == "Independent":
            self._app.oboundary.AssignIndependent(self._get_args())
        elif bound_type == "Dependent":
            self._app.oboundary.AssignDependent(self._get_args())
        elif bound_type == "Band":
            self._app.omodelsetup.AssignBand(self._get_args())
        elif bound_type == "InfiniteGround":
            self._app.oboundary.AssignInfiniteGround(self._get_args())
        elif bound_type == "ThinConductor":
            self._app.oboundary.AssignThinConductor(self._get_args())
        elif bound_type == "Stationary Wall":
            self._app.oboundary.AssignStationaryWallBoundary(self._get_args())
        elif bound_type == "Symmetry Wall":
            self._app.oboundary.AssignSymmetryWallBoundary(self._get_args())
        elif bound_type == "Recirculating":
            self._app.oboundary.AssignRecircBoundary(self._get_args())
        elif bound_type == "Resistance":
            self._app.oboundary.AssignResistanceBoundary(self._get_args())
        elif bound_type == "Conducting Plate":
            self._app.oboundary.AssignConductingPlateBoundary(self._get_args())
        elif bound_type == "Adiabatic Plate":
            self._app.oboundary.AssignAdiabaticPlateBoundary(self._get_args())
        elif bound_type == "Network":
            self._app.oboundary.AssignNetworkBoundary(self._get_args())
        elif bound_type == "Grille":
            self._app.oboundary.AssignGrilleBoundary(self._get_args())
        elif bound_type == "Block":
            self._app.oboundary.AssignBlockBoundary(self._get_args())
        elif bound_type == "Blower":
            self._app.oboundary.AssignBlowerBoundary(self._get_args())
        elif bound_type == "SourceIcepak":
            self._app.oboundary.AssignSourceBoundary(self._get_args())
        elif bound_type == "Opening":
            self._app.oboundary.AssignOpeningBoundary(self._get_args())
        elif bound_type == "EMLoss":
            self._app.oboundary.AssignEMLoss(self._get_args())
        elif bound_type == "ThermalCondition":
            self._app.oboundary.AssignThermalCondition(self._get_args())
        elif bound_type == "Convection":
            self._app.oboundary.AssignConvection(self._get_args())
        elif bound_type == "HeatFlux":
            self._app.oboundary.AssignHeatFlux(self._get_args())
        elif bound_type == "HeatGeneration":
            self._app.oboundary.AssignHeatGeneration(self._get_args())
        elif bound_type == "Temperature":
            self._app.oboundary.AssignTemperature(self._get_args())
        elif bound_type == "RotatingFluid":
            self._app.oboundary.AssignRotatingFluid(self._get_args())
        elif bound_type == "Frictionless":
            self._app.oboundary.AssignFrictionlessSupport(self._get_args())
        elif bound_type == "FixedSupport":
            self._app.oboundary.AssignFixedSupport(self._get_args())
        elif bound_type == "Voltage":
            self._app.oboundary.AssignVoltage(self._get_args())
        elif bound_type == "VoltageDrop":
            self._app.oboundary.AssignVoltageDrop(self._get_args())
        elif bound_type == "Floating":
            self._app.oboundary.AssignFloating(self._get_args())
        elif bound_type == "Current":
            self._app.oboundary.AssignCurrent(self._get_args())
        elif bound_type == "CurrentDensity":
            self._app.oboundary.AssignCurrentDensity(self._get_args())
        elif bound_type == "CurrentDensityGroup":
            self._app.oboundary.AssignCurrentDensityGroup(self._get_args()[2], self._get_args()[3])
        elif bound_type == "CurrentDensityTerminal":
            self._app.oboundary.AssignCurrentDensityTerminal(self._get_args())
        elif bound_type == "CurrentDensityTerminalGroup":
            self._app.oboundary.AssignCurrentDensityTerminalGroup(self._get_args()[2], self._get_args()[3])
        elif bound_type == "Balloon":
            self._app.oboundary.AssignBalloon(self._get_args())
        elif bound_type == "Winding" or bound_type == "Winding Group":
            self._app.oboundary.AssignWindingGroup(self._get_args())
        elif bound_type == "Vector Potential":
            self._app.oboundary.AssignVectorPotential(self._get_args())
        elif bound_type == "CoilTerminal" or bound_type == "Coil Terminal":
            self._app.oboundary.AssignCoilTerminal(self._get_args())
        elif bound_type == "Coil":
            self._app.oboundary.AssignCoil(self._get_args())
        elif bound_type == "Source":
            self._app.oboundary.AssignSource(self._get_args())
        elif bound_type == "Sink":
            self._app.oboundary.AssignSink(self._get_args())
        elif bound_type == "SignalNet":
            self._app.oboundary.AssignSignalNet(self._get_args())
        elif bound_type == "GroundNet":
            self._app.oboundary.AssignGroundNet(self._get_args())
        elif bound_type == "FloatingNet":
            self._app.oboundary.AssignFloatingNet(self._get_args())
        elif bound_type == "SignalLine":
            self._app.oboundary.AssignSingleSignalLine(self._get_args())
        elif bound_type == "ReferenceGround":
            self._app.oboundary.AssignSingleReferenceGround(self._get_args())
        elif bound_type == "Circuit Port":
            self._app.oboundary.AssignCircuitPort(self._get_args())
        elif bound_type == "Lumped Port":
            self._app.oboundary.AssignLumpedPort(self._get_args())
        elif bound_type == "Wave Port":
            self._app.oboundary.AssignWavePort(self._get_args())
        elif bound_type == "Floquet Port":
            self._app.oboundary.AssignFloquetPort(self._get_args())
        elif bound_type == "AutoIdentify":
            # Build reference conductor argument as a list of strings
            # ref_cond_arg should be a list.
            ref_cond_arg = ["NAME:ReferenceConductors"] + self.props["ReferenceConductors"]
            self._app.oboundary.AutoIdentifyPorts(
                ["NAME:Faces", self.props["Faces"]],
                self.props["IsWavePort"],
                ref_cond_arg,
                self.name,
                self.props["RenormalizeModes"],
            )
        elif bound_type == "SBRTxRxSettings":
            self._app.oboundary.SetSBRTxRxSettings(self._get_args())
        elif bound_type == "EndConnection":
            self._app.oboundary.AssignEndConnection(self._get_args())
        elif bound_type == "Hybrid":
            self._app.oboundary.AssignHybridRegion(self._get_args())
        elif bound_type == "FluxTangential":
            self._app.oboundary.AssignFluxTangential(self._get_args())
        elif bound_type == "Plane Incident Wave":
            self._app.oboundary.AssignPlaneWave(self._get_args())
        elif bound_type == "ResistiveSheet":
            self._app.oboundary.AssignResistiveSheet(self._get_args())
        else:
            return False
        self._initialize_bynary_tree()

        return True

    @pyaedt_function_handler()
    def update(self):
        """Update the boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        bound_type = self.type
        if bound_type == "Perfect E":
            self._app.oboundary.EditPerfectE(self._boundary_name, self._get_args())
        elif bound_type == "Perfect H":
            self._app.oboundary.EditPerfectH(self._boundary_name, self._get_args())
        elif bound_type == "Aperture":
            self._app.oboundary.EditAperture(self._boundary_name, self._get_args())
        elif bound_type == "Radiation":
            self._app.oboundary.EditRadiation(self._boundary_name, self._get_args())
        elif bound_type == "Finite Conductivity":
            self._app.oboundary.EditFiniteCond(self._boundary_name, self._get_args())
        elif bound_type == "Lumped RLC":
            self._app.oboundary.EditLumpedRLC(self._boundary_name, self._get_args())
        elif bound_type == "Impedance":
            self._app.oboundary.EditImpedance(self._boundary_name, self._get_args())
        elif bound_type == "Layered Impedance":
            self._app.oboundary.EditLayeredImpedance(self._boundary_name, self._get_args())
        elif bound_type == "Anisotropic Impedance":
            self._app.oboundary.EditAssignAnisotropicImpedance(
                self._boundary_name, self._get_args()
            )  # pragma: no cover
        elif bound_type == "Primary":
            self._app.oboundary.EditPrimary(self._boundary_name, self._get_args())
        elif bound_type == "Secondary":
            self._app.oboundary.EditSecondary(self._boundary_name, self._get_args())
        elif bound_type == "Lattice Pair":
            self._app.oboundary.EditLatticePair(self._boundary_name, self._get_args())
        elif bound_type == "HalfSpace":
            self._app.oboundary.EditHalfSpace(self._boundary_name, self._get_args())
        elif bound_type == "Multipaction SEE":
            self._app.oboundary.EditMultipactionSEE(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Fresnel":
            self._app.oboundary.EditFresnel(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Symmetry":
            self._app.oboundary.EditSymmetry(self._boundary_name, self._get_args())
        elif bound_type == "Zero Tangential H Field":
            self._app.oboundary.EditZeroTangentialHField(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Zero Integrated Tangential H Field":
            self._app.oboundary.EditIntegratedZeroTangentialHField(
                self._boundary_name, self._get_args()
            )  # pragma: no cover
        elif bound_type == "Tangential H Field":
            self._app.oboundary.EditTangentialHField(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Insulating":
            self._app.oboundary.EditInsulating(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Independent":
            self._app.oboundary.EditIndependent(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Dependent":
            self._app.oboundary.EditDependent(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Band":
            self._app.omodelsetup.EditMotionSetup(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "InfiniteGround":
            self._app.oboundary.EditInfiniteGround(self._boundary_name, self._get_args())
        elif bound_type == "ThinConductor":
            self._app.oboundary.EditThinConductor(self._boundary_name, self._get_args())
        elif bound_type == "Stationary Wall":
            self._app.oboundary.EditStationaryWallBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Symmetry Wall":
            self._app.oboundary.EditSymmetryWallBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Recirculating":
            self._app.oboundary.EditRecircBoundary(self._boundary_name, self._get_args())
        elif bound_type == "Resistance":
            self._app.oboundary.EditResistanceBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Conducting Plate":
            self._app.oboundary.EditConductingPlateBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Adiabatic Plate":
            self._app.oboundary.EditAdiabaticPlateBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Network":
            self._app.oboundary.EditNetworkBoundary(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Grille":
            self._app.oboundary.EditGrilleBoundary(self._boundary_name, self._get_args())
        elif bound_type == "Opening":
            self._app.oboundary.EditOpeningBoundary(self._boundary_name, self._get_args())
        elif bound_type == "EMLoss":
            self._app.oboundary.EditEMLoss(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Block":
            self._app.oboundary.EditBlockBoundary(self._boundary_name, self._get_args())
        elif bound_type == "Blower":
            self._app.oboundary.EditBlowerBoundary(self._boundary_name, self._get_args())
        elif bound_type == "SourceIcepak":
            self._app.oboundary.EditSourceBoundary(self._boundary_name, self._get_args())
        elif bound_type == "HeatFlux":
            self._app.oboundary.EditHeatFlux(self._boundary_name, self._get_args())
        elif bound_type == "HeatGeneration":
            self._app.oboundary.EditHeatGeneration(self._boundary_name, self._get_args())
        elif bound_type == "Voltage":
            self._app.oboundary.EditVoltage(self._boundary_name, self._get_args())
        elif bound_type == "VoltageDrop":
            self._app.oboundary.EditVoltageDrop(self._boundary_name, self._get_args())
        elif bound_type == "Current":
            self._app.oboundary.EditCurrent(self._boundary_name, self._get_args())
        elif bound_type == "CurrentDensity":
            self._app.oboundary.AssignCurrentDensity(self._get_args())
        elif bound_type == "CurrentDensityGroup":
            self._app.oboundary.AssignCurrentDensityGroup(self._get_args()[2], self._get_args()[3])
        elif bound_type == "CurrentDensityTerminal":
            self._app.oboundary.AssignCurrentDensityTerminal(self._get_args())
        elif bound_type == "CurrentDensityTerminalGroup":
            self._app.oboundary.AssignCurrentDensityTerminalGroup(self._get_args()[2], self._get_args()[3])
        elif bound_type == "Winding" or bound_type == "Winding Group":
            self._app.oboundary.EditWindingGroup(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Vector Potential":
            self._app.oboundary.EditVectorPotential(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "CoilTerminal" or bound_type == "Coil Terminal":
            self._app.oboundary.EditCoilTerminal(self._boundary_name, self._get_args())
        elif bound_type == "Coil":
            self._app.oboundary.EditCoil(self._boundary_name, self._get_args())
        elif bound_type == "Source":
            self._app.oboundary.EditTerminal(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "Sink":
            self._app.oboundary.EditTerminal(self._boundary_name, self._get_args())
        elif bound_type == "SignalNet" or bound_type == "GroundNet" or bound_type == "FloatingNet":
            self._app.oboundary.EditTerminal(self._boundary_name, self._get_args())
        elif bound_type in "Circuit Port":
            self._app.oboundary.EditCircuitPort(self._boundary_name, self._get_args())
        elif bound_type in "Lumped Port":
            self._app.oboundary.EditLumpedPort(self._boundary_name, self._get_args())
        elif bound_type in "Wave Port":
            self._app.oboundary.EditWavePort(self._boundary_name, self._get_args())
        elif bound_type == "SetSBRTxRxSettings":
            self._app.oboundary.SetSBRTxRxSettings(self._get_args())  # pragma: no cover
        elif bound_type == "Floquet Port":
            self._app.oboundary.EditFloquetPort(self._boundary_name, self._get_args())  # pragma: no cover
        elif bound_type == "End Connection":
            self._app.oboundary.EditEndConnection(self._boundary_name, self._get_args())
        elif bound_type == "Hybrid":
            self._app.oboundary.EditHybridRegion(self._boundary_name, self._get_args())
        elif bound_type == "Terminal":
            self._app.oboundary.EditTerminal(self._boundary_name, self._get_args())
        elif bound_type == "Plane Incident Wave":
            self._app.oboundary.EditIncidentWave(self._boundary_name, self._get_args())
        elif bound_type == "ResistiveSheet":
            self._app.oboundary.EditResistiveSheet(self._boundary_name, self._get_args())
        else:
            return False  # pragma: no cover

        self._app._boundaries[self.name] = self._app._boundaries.pop(self._boundary_name)
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

        out = ["Name:" + self.name]

        if "Faces" in self.props:
            faces = self.props["Faces"]
            faces_out = []
            if not isinstance(faces, list):
                faces = [faces]
            for f in faces:
                if isinstance(f, (EdgePrimitive, FacePrimitive, VertexPrimitive)):
                    faces_out.append(f.id)
                else:
                    faces_out.append(f)
            out += ["Faces:=", faces_out]

        if "Objects" in self.props:
            pr = []
            for el in self.props["Objects"]:
                try:
                    pr.append(self._app.modeler[el].name)
                except (KeyError, AttributeError):
                    pass
            out += ["Objects:=", pr]

        if len(out) == 1:
            return False

        self._app.oboundary.ReassignBoundary(out)

        return True
