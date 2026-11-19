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

import functools
import inspect
from pathlib import Path
import sys

from ansys.aedt.core.generic.protocols import _ODesktop
from ansys.aedt.core.internal.errors import GrpcApiError

# AEDT methods whose result is always an array in the legacy API. The native API returns a
# one-element array as a bare scalar and fails to convert an empty array, so the results of these
# methods are normalized back to lists.
_ARRAY_RESULT_METHODS = frozenset(
    {
        # 3D modeler
        "CreateObjectFromEdges",
        "CreateObjectFromFaces",
        "CreateObjectsFromFaceGroups",
        "DetachEdges",
        "DetachFaces",
        "DuplicateAlongLine",
        "DuplicateAroundAxis",
        "DuplicateMirror",
        "Get3DComponentDefinitionNames",
        "Get3DComponentInstanceNames",
        "Get3DComponentMaterialNames",
        "Get3DComponentParameters",
        "Get3DComponentPartNames",
        "GetBodyNamesByPosition",
        "GetCoordinateSystems",
        "GetEdgeIDsFromFace",
        "GetEdgeIDsFromObject",
        "GetEntityIDsContainedByEntityList",
        "GetEntityIDsContainedByNamedSelection",
        "GetFaceIDs",
        "GetFaceIDsOfSheet",
        "GetGroupSubmodelNames",
        "GetMatchedObjectName",
        "GetObjectsByMaterial",
        "GetObjectsInGroup",
        "GetPartsForUserDefinedModel",
        "GetRelativeCoordinateSystems",
        "GetSelections",
        "GetSubGroupsInGroup",
        "GetVertexIDsFromEdge",
        "GetVertexIDsFromFace",
        "GetVertexIDsFromObject",
        "GetWireBodyNames",
        "Section",
        "SeparateBody",
        "Split",
        "SweepFacesAlongNormal",
        "SweepFacesAlongNormalWithAttributes",
        # Layout and schematic editors
        "FilterObjectList",
        "FindObjects",
        "FindObjectsByPoint",
        "FindObjectsByPolygon",
        "GetAllComponents",
        "GetAllElements",
        "GetAllGraphics",
        "GetAllLayerNames",
        "GetAllNets",
        "GetComponentPins",
        "GetComponentPorts",
        "GetNetClassNets",
        "GetStackupLayerNames",
        # Object tree, definition managers, and desktop
        "GetChildNames",
        "GetChildTypes",
        "GetDesigns",
        "GetInUseProjectMaterialNames",
        "GetMessages",
        "GetNames",
        "GetProjectList",
        "GetProjectMaterialNames",
        "GetProjects",
        "GetPropNames",
        "GetTopDesignList",
        # Variables
        "GetArrayNames",
        "GetArrayVariables",
        "GetDerivativeVariables",
        "GetOutputVariables",
        "GetPostProcessingVariables",
        "GetVariables",
        # Boundaries, mesh, motion, and analysis modules
        "GetAllBoundariesList",
        "GetAllPorts",
        "GetAllPortsList",
        "GetAllSolutionNames",
        "GetAllSolutionSetups",
        "GetAllSources",
        "GetAssignment",
        "GetBoundaries",
        "GetConductionPathObjects",
        "GetConductionPaths",
        "GetDiffPairs",
        "GetExcitations",
        "GetHybridRegions",
        "GetMeshOps",
        "GetMotions",
        "GetSetups",
        "GetSweepNames",
        "GetSweeps",
        "ListReduceMatrixes",
        "ListReduceMatrixOperations",
        "ListReduceMatrixReducedSources",
        # Solutions and reports
        "GetAllCategories",
        "GetAllQuantities",
        "GetAllReportNames",
        "GetAvailableDisplayTypes",
        "GetAvailableReportTypes",
        "GetAvailableSolutions",
        "GetAvailableVariations",
        "GetDataExpressions",
        "GetFieldsCalculatorExpressions",
        "GetImagDataValues",
        "GetRealDataValues",
        "GetSweepValues",
        "GetValidISolutionList",
        "ListVariations",
    }
)

# Array methods that return entity IDs as strings, which the native API returns as an integer for a single ID.
_STRING_ID_RESULT_METHODS = frozenset(
    {
        "GetAssignment",
        "GetEdgeIDsFromFace",
        "GetEdgeIDsFromObject",
        "GetEntityIDsContainedByEntityList",
        "GetEntityIDsContainedByNamedSelection",
        "GetFaceIDs",
        "GetFaceIDsOfSheet",
        "GetVertexIDsFromEdge",
        "GetVertexIDsFromFace",
        "GetVertexIDsFromObject",
    }
)


def _is_empty_array_conversion_error(error: Exception) -> bool:
    """Recognize an unset top-level AnValue, not malformed elements in an array."""
    if str(error) != "Programmer error: Unknown type {anvalType} in anvalue_to_pyvalue function":
        return False
    conversions = []
    traceback = error.__traceback__
    while traceback is not None:
        frame = traceback.tb_frame
        if frame.f_globals.get("__name__") == "aedt.lib.coreutils" and frame.f_code.co_name == "anvalue2pyvalue":
            conversions.append(frame.f_locals["anval_to_copy"])
        traceback = traceback.tb_next
    # The native converter also raises this message for malformed nested values.
    return len(conversions) == 1 and conversions[0].WhichOneof("kind") is None


def _rpc_error_types() -> tuple:
    try:
        import grpc
    except ImportError:  # pragma: no cover
        return ()
    return (grpc.RpcError,)


def _native_argument(value):
    """Convert tuples, which the native API cannot serialize unlike the legacy API, to lists."""
    if isinstance(value, (list, tuple)):
        converted = [_native_argument(item) for item in value]
        if isinstance(value, tuple) or any(new is not old for new, old in zip(converted, value)):
            return converted
    return value


def _native_method(method, rpc_errors: tuple = (), array_result: bool = False, string_ids: bool = False):
    """Wrap a native API method to match the legacy API argument, error, and array result contracts."""
    name = method.__name__

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        args = tuple(_native_argument(arg) for arg in args)
        kwargs = {key: _native_argument(value) for key, value in kwargs.items()}
        try:
            result = method(*args, **kwargs)
        except rpc_errors as e:
            details = e.details() if callable(getattr(e, "details", None)) else str(e)
            raise GrpcApiError(f"Failed to execute gRPC AEDT command: {name}. {details}") from e
        except Exception as e:
            if array_result and _is_empty_array_conversion_error(e):
                return []
            raise
        if not array_result or result is None or isinstance(result, (list, tuple)):
            return result
        if string_ids and isinstance(result, int) and not isinstance(result, bool):
            result = str(result)
        return [result]

    wrapper._pyaedt_native_method = True
    return wrapper


def _patch_native_wrapper_classes(classes) -> None:
    """Patch the public methods of the native API wrapper classes to follow the legacy API contracts."""
    rpc_errors = _rpc_error_types()
    for cls in classes:
        for klass in getattr(cls, "__mro__", ()):
            if klass is object:
                continue
            for name, member in list(vars(klass).items()):
                if name.startswith("_") or not inspect.isfunction(member):
                    continue
                if getattr(member, "_pyaedt_native_method", False):
                    continue
                setattr(
                    klass,
                    name,
                    _native_method(
                        member,
                        rpc_errors,
                        array_result=name in _ARRAY_RESULT_METHODS,
                        string_ids=name in _STRING_ID_RESULT_METHODS,
                    ),
                )


def _native_wrapper_classes(*instances) -> list:
    """Return the native API wrapper classes, including those of the given instances."""
    classes = [type(instance) for instance in instances if instance is not None]
    try:
        from aedt.lib import coreutils

        classes.extend((coreutils.gServiceName2ClassMap or {}).values())
    except ImportError:  # pragma: no cover
        pass
    for module_name, module in list(sys.modules.items()):
        class_name = getattr(module, "PYWRAPPERCLASS_NAME", None) if module_name.startswith("aedt.") else None
        if class_name and isinstance(getattr(module, class_name, None), type):
            classes.append(getattr(module, class_name))
    return classes


class AEDT:
    def __init__(self, installer_path):

        self.installer_path = installer_path
        sys.path.append(str(Path(self.installer_path) / "gRPCFiles" / "API"))
        self._oDesktop = None

    def CreateAedtApplication(self, machine, port: int | None = 0, NGmode: bool = False, alwaysNew: bool = True):
        from ScriptEnv import Initialize

        Initialize(name=None, ngMode=NGmode, machine=machine, port=port, ngApp=None)
        Module = sys.modules["__main__"]
        self.aedt = Module.oAnsoftApplication if "oAnsoftApplication" in dir(Module) else None
        if not self.aedt:
            raise GrpcApiError("Failed to connect to Desktop Session")
        self.machine = machine
        self.non_graphical = NGmode
        self._odesktop = Module.oDesktop
        _patch_native_wrapper_classes(_native_wrapper_classes(self.aedt, self._odesktop))
        if port == 0:
            self.port = self._odesktop.GetGrpcServerPort()
        else:
            self.port = port

        return self.aedt

    @property
    def odesktop(self) -> "_ODesktop":
        """Retrieve odesktop."""
        return self._odesktop

    def recreate_application(self, force: bool = False) -> None:
        self.CreateAedtApplication(machine=self.machine, port=self.port)
        return self.odesktop

    def Release(self) -> None:
        import ScriptEnv

        try:
            ScriptEnv.Release()
        finally:
            channel = ScriptEnv.gChannel
            ScriptEnv.gChannel = None
            ScriptEnv.gDesktop = None
            ScriptEnv.gSSLClientCredentials = None
            self._odesktop = None
            if channel is not None:
                channel.close()

    def Shutdown(self) -> None:
        from ScriptEnv import Shutdown

        Shutdown()
