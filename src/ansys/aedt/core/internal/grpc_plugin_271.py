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

from pathlib import Path
import sys

from ansys.aedt.core.generic.protocols import _ODesktop
from ansys.aedt.core.internal.errors import GrpcApiError

def _rpc_error_types() -> tuple:
    try:
        import grpc
    except ImportError:  # pragma: no cover
        return ()
    return (grpc.RpcError,)

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
