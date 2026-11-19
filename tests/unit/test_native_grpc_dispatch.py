# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Dispatch between legacy and native gRPC API method names."""

from types import FunctionType
from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import grpc
import pytest

from ansys.aedt.core.application.aedt_objects import AedtObjects
from ansys.aedt.core.application.aedt_objects import _NativeModelerEditor
from ansys.aedt.core.application.design import Design
from ansys.aedt.core.application.variables import Variable
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.icepak import Icepak
from ansys.aedt.core.internal.errors import GrpcApiError
from ansys.aedt.core.internal.grpc_plugin_271 import _patch_native_wrapper_classes
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modeler.cad.primitives import GeometryModeler
from ansys.aedt.core.modules.boundary.common import BoundaryObject
from ansys.aedt.core.modules.boundary.icepak_boundary import NetworkObject
from ansys.aedt.core.modules.mesh import MeshOperation
from ansys.aedt.core.visualization.post.monitor_icepak import Monitor


def _app(native_api: bool) -> MagicMock:
    app = MagicMock()
    app.desktop_class.is_native_grpc_api = native_api
    app.design_type = "HFSS"
    return app


@pytest.fixture(autouse=True)
def no_tree_node():
    with patch.object(BoundaryObject, "_initialize_tree_node"), patch.object(MeshOperation, "_initialize_tree_node"):
        yield


@pytest.mark.parametrize("native_api", [True, False])
@pytest.mark.parametrize(
    ("boundary_type", "legacy_method"),
    [
        ("Finite Conductivity", "EditFiniteCond"),
        ("Circuit Port", "EditCircuitPort"),
        ("Vector Potential", "EditVectorPotential"),
        ("Insulating", "EditInsulating"),
        ("Opening", "EditOpeningBoundary"),
        ("Source", "EditTerminal"),
    ],
)
def test_boundary_update(native_api, boundary_type, legacy_method) -> None:
    app = _app(native_api)
    boundary = BoundaryObject(app, "FC1", boundarytype=boundary_type)
    method = "Edit" if native_api else legacy_method

    with patch.object(BoundaryObject, "_get_args", return_value=["NAME:FC1"]):
        assert boundary.update()

    getattr(app.oboundary, method).assert_called_once_with("FC1", ["NAME:FC1"])
    getattr(app.oboundary, legacy_method if native_api else "Edit").assert_not_called()


@pytest.mark.parametrize(("native_api", "method"), [(True, "Delete"), (False, "DeleteBoundaries")])
def test_boundary_delete(native_api, method) -> None:
    app = _app(native_api)
    app.design_excitations = {}
    boundary = BoundaryObject(app, "FC1", boundarytype="Finite Conductivity")

    assert boundary.delete()

    getattr(app.oboundary, method).assert_called_once_with(["FC1"])


@pytest.mark.parametrize(("native_api", "method"), [(True, "Delete"), (False, "DeleteOp")])
def test_mesh_operation_delete(native_api, method) -> None:
    mesh = MagicMock()
    mesh._app = _app(native_api)
    mesh_op = MeshOperation(mesh, "Length1", None, "LengthBased")
    mesh.meshoperations = [mesh_op]

    assert mesh_op.delete()

    getattr(mesh.omeshmodule, method).assert_called_once_with(["Length1"])
    assert mesh.meshoperations == []


@pytest.mark.parametrize(("native_api", "method"), [(True, "Delete"), (False, "DeleteMonitors")])
def test_monitor_delete(native_api, method) -> None:
    app = _app(native_api)
    app.desktop_class.aedt_version_id = "2027.1"
    app.design_properties = {}
    monitor = Monitor(app)
    monitor._face_monitors["Monitor1"] = object()

    assert monitor.delete_monitor("Monitor1")

    getattr(app.omonitor, method).assert_called_once_with(["Monitor1"])
    assert monitor._face_monitors == {}


@pytest.mark.parametrize(("native_api", "method"), [(True, "Rename"), (False, "RenameBoundary")])
def test_network_rename(native_api, method) -> None:
    app = _app(native_api)
    app.design_type = "Icepak"
    network = NetworkObject(app, "Network1")
    app.boundaries = [network]

    network.name = "Network2"

    getattr(app._oboundary, method).assert_called_once_with("Network1", "Network2")
    assert network.name == "Network2"


@pytest.mark.parametrize(("native_api", "method"), [(True, "CreateSubRegion"), (False, "CreateSubregion")])
def test_create_subregion(native_api, method) -> None:
    modeler = MagicMock()
    modeler._app = _app(native_api)
    modeler._parse_region_args.return_value = (["NAME:SubRegionParameters"], ["NAME:Attributes"])

    GeometryModeler.create_subregion(modeler, 10, "Percentage Offset", ["Box1"], "SubRegion1")

    getattr(modeler.oeditor, method).assert_called_once_with(["NAME:SubRegionParameters"], ["NAME:Attributes"])


def test_reassign_subregion_selects_region() -> None:
    modeler = MagicMock()
    region = MagicMock(padding_types="Percentage Offset")
    region.name = "SubRegion1"
    modeler._parse_region_args.return_value = (["NAME:SubRegionParameters"], ["NAME:Attributes"])

    assert GeometryModeler.reassign_subregion(modeler, region, ["Box1", "Box2"])

    modeler.oeditor.ReassignSubregion.assert_called_once_with(
        ["NAME:Selections", "Selections:=", "SubRegion1"], ["NAME:SubRegionParameters"], ["NAME:Attributes"]
    )


def test_consistent_design_type_ignores_design_name_case() -> None:
    app = MagicMock()
    app.design_list = ["get_fan_op_point"]
    app._design_type = "Icepak"
    app.desktop_class.active_design.return_value.GetDesignType.return_value = "Icepak"

    assert Design._assert_consistent_design_type(app, "get_FAN_OP_POINT") is True

    app.desktop_class.active_design.assert_called_once_with(app.oproject, "get_fan_op_point", app.design_type)


def test_boundary_delete_reads_name_before_deleting() -> None:
    app = _app(True)
    app.design_excitations = {"FC1": object()}
    boundary = BoundaryObject(app, "FC1", boundarytype="Finite Conductivity")
    deleted = []
    app.oboundary.Delete.side_effect = deleted.append

    def name() -> str:
        assert not deleted, "name read from a deleted AEDT object"
        return "FC1"

    with patch.object(BoundaryObject, "name", new_callable=PropertyMock, side_effect=name):
        assert boundary.delete()

    assert deleted == [["FC1"]]
    assert app.design_excitations == {}


@pytest.mark.parametrize("native_api", [True, False])
def test_oeditor_native_wrapping(native_api) -> None:
    app = _app(native_api)
    app._oeditor = None
    editor = app._odesign.SetActiveEditor.return_value

    oeditor = AedtObjects.oeditor.fget(app)

    assert isinstance(oeditor, _NativeModelerEditor) is native_api
    assert (oeditor._editor if native_api else oeditor) is editor


def test_native_modeler_editor_roots_tree_at_modeler() -> None:
    editor = MagicMock()
    native_editor = _NativeModelerEditor(editor)

    native_editor.GetChildObject("b1/CreateBox:1")
    editor.GetChildObject.assert_called_once_with("3D Modeler/b1/CreateBox:1")

    editor.GetChildObject.reset_mock()
    native_editor.GetChildNames("Groups")
    editor.GetChildObject.assert_called_once_with("3D Modeler")
    editor.GetChildObject.return_value.GetChildNames.assert_called_once_with("Groups")

    native_editor.GetObjectsInGroup("Lines")
    editor.GetObjectsInGroup.assert_called_once_with("Lines")


class _RenamableNode(BinaryTreeNode):
    def __init__(self, app, handle, renamed_handle) -> None:
        self._name = "FC1"
        self._renamed_handle = renamed_handle
        BinaryTreeNode.__init__(self, "FC1", handle, app=app)

    @property
    def _child_object(self):
        return self._renamed_handle


@pytest.mark.parametrize("native_api", [True, False])
def test_rename_refreshes_native_handle(native_api) -> None:
    handle = MagicMock()
    handle.SetPropValue.return_value = True
    renamed_handle = MagicMock()
    node = _RenamableNode(_app(native_api), handle, renamed_handle)

    node.update_property("Name", "FC2")

    assert node._name == "FC2"
    assert node.child_object is (renamed_handle if native_api else handle)


def test_properties_skips_data_model_for_invalid_handle(monkeypatch) -> None:
    monkeypatch.setattr(settings, "aedt_version", "2027.1")
    handle = MagicMock()
    handle.GetPropNames.side_effect = RuntimeError("invalid handle")
    node = BinaryTreeNode("FC1", handle)

    with pytest.raises(RuntimeError):
        node.properties

    handle.GetDataModel.assert_not_called()


class _NativeRpcError(grpc.RpcError):
    def details(self):
        return "Error occurred. See message window for details"


class _NativeEditorBase:
    def GetFaceIDs(self, value):
        return value

    def GetPropValue(self, value):
        return value


class _NativeEditor(_NativeEditorBase):
    def GetObjectsByMaterial(self, value):
        return value

    def GetVariables(self):
        return _converter(SimpleNamespace(WhichOneof=lambda _: None))

    def ThickenSheet(self):
        raise _NativeRpcError()


def anvalue2pyvalue(anval_to_copy):
    if anval_to_copy.WhichOneof("kind") == "list_value":
        return [anvalue2pyvalue(value) for value in anval_to_copy.values]
    raise Exception("Programmer error: Unknown type {anvalType} in anvalue_to_pyvalue function")


_converter_globals = {"__name__": "aedt.lib.coreutils"}
_converter = FunctionType(anvalue2pyvalue.__code__, _converter_globals)
_converter_globals["anvalue2pyvalue"] = _converter


@pytest.fixture(scope="module")
def native_editor():
    _patch_native_wrapper_classes([_NativeEditor])
    return _NativeEditor()


@pytest.mark.parametrize(
    ("method", "value", "expected"),
    [
        ("GetObjectsByMaterial", "Box1", ["Box1"]),
        ("GetObjectsByMaterial", ["Box1", "Box2"], ["Box1", "Box2"]),
        ("GetFaceIDs", 10, ["10"]),
        ("GetPropValue", "Box1", "Box1"),
    ],
)
def test_native_array_results_match_legacy(native_editor, method, value, expected) -> None:
    assert getattr(native_editor, method)(value) == expected


def test_native_empty_array_result(native_editor) -> None:
    assert native_editor.GetVariables() == []


@pytest.mark.parametrize("nested", [True, False])
def test_native_array_conversion_does_not_hide_invalid_results(nested) -> None:
    class InvalidResult:
        def GetVariables(self):
            if nested:
                return _converter(
                    SimpleNamespace(
                        WhichOneof=lambda _: "list_value",
                        values=[SimpleNamespace(WhichOneof=lambda _: None)],
                    )
                )
            raise Exception("Programmer error: Unknown type {anvalType} in anvalue_to_pyvalue function")

    _patch_native_wrapper_classes([InvalidResult])
    with pytest.raises(Exception, match="Unknown type"):
        InvalidResult().GetVariables()


@pytest.mark.parametrize("native_api", [True, False])
def test_mesh_assignment_uses_native_integer_id(native_api) -> None:
    mesh = MagicMock()
    mesh._app = _app(native_api)
    mesh._app.modeler.objects = {12: object()}
    mesh.omeshmodule.GetAssignment.return_value = ["12"]
    mesh.omeshmodule.GetMeshOpAssignment.return_value = ["12"]
    operation = MeshOperation(mesh, "Length1", None, "LengthBased")

    with patch.object(MeshOperation, "properties", new_callable=PropertyMock, return_value={}):
        assert operation.props["Objects"] == [mesh._app.oeditor.GetObjectNameByID.return_value]

    mesh._app.oeditor.GetObjectNameByID.assert_called_once_with(12 if native_api else "12")
    getattr(mesh.omeshmodule, "GetAssignment" if native_api else "GetMeshOpAssignment").assert_called_once_with(
        "Length1"
    )


def test_native_rpc_error_raises_grpc_api_error(native_editor) -> None:
    with pytest.raises(GrpcApiError, match="ThickenSheet"):
        native_editor.ThickenSheet()


def test_native_tuple_arguments_converted_to_lists(native_editor) -> None:
    args = ["NAME:Props", "Temperature:=", ("20cel",), ["Nested:=", ("0mm", 1)]]

    assert native_editor.GetPropValue(args) == ["NAME:Props", "Temperature:=", ["20cel"], ["Nested:=", ["0mm", 1]]]
    assert native_editor.GetPropValue(value=("Box1",)) == ["Box1"]


def test_native_wrapper_classes_patched_once(native_editor) -> None:
    method = _NativeEditor.__dict__["GetObjectsByMaterial"]
    _patch_native_wrapper_classes([_NativeEditor])

    assert _NativeEditor.__dict__["GetObjectsByMaterial"] is method


def _variable(native_api: bool) -> tuple[Variable, MagicMock]:
    app = _app(native_api)
    app._aedt_version = "2027.1"
    app.get_oo_name.return_value = ["a"]
    var = Variable("3mm", name="a")
    var._app = app
    return var, app.get_oo_object.return_value


@pytest.mark.parametrize(
    ("native_api", "method", "args"),
    [(True, "GetPropValue", ("EvaluatedValue",)), (False, "GetPropEvaluatedValue", ())],
)
def test_variable_evaluated_value(native_api, method, args) -> None:
    var, var_obj = _variable(native_api)
    getattr(var_obj, method).return_value = "3mm"

    assert var.numeric_value == 3.0
    getattr(var_obj, method).assert_called_once_with(*args)


def test_variable_numeric_value_falls_back_on_aedt_error() -> None:
    var, var_obj = _variable(False)
    var_obj.GetPropEvaluatedValue.side_effect = GrpcApiError("GetPropEvaluatedValue")

    assert var.numeric_value == 3.0


class _ProjectSwitchingApp:
    def __init__(self, native_api: bool) -> None:
        self.desktop_class = MagicMock(is_native_grpc_api=native_api, project_list=["ipk"])
        self.project_name = "ipk"
        self.modeler = MagicMock()
        self.materials = MagicMock()
        self._oproject = MagicMock(name="ipk")

    @property
    def oproject(self):
        return self._oproject

    @oproject.setter
    def oproject(self, value) -> None:
        self._oproject = MagicMock(name=value)


@pytest.mark.parametrize(("native_api", "method"), [(True, "Close"), (False, "close")])
def test_copy_group_from_restores_project(native_api, method) -> None:
    app = _ProjectSwitchingApp(native_api)
    original_project = app._oproject

    assert Icepak.copy_group_from(app, "Group1", "uUSB", "USBConnector_HFSS", "USBConnector_HFSS.aedtz")

    assert app._oproject is original_project
    getattr(app.desktop_class.active_project.return_value, method).assert_called_once_with()
