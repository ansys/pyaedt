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
        if port == 0:
            self.port = self._odesktop.GetGrpcServerPort()
        else:
            self.port = port

        return self.aedt

    @property
    def odesktop(self) -> "_ODesktop":
        """Retrieve odesktop."""
        return self._odesktop

    def recreate_application(self):
        self.CreateAedtApplication(self.machine, self.port)
        return self.odesktop

    def Release(self) -> None:
        from ScriptEnv import Release

        Release()

    def Shutdown(self) -> None:
        from ScriptEnv import Shutdown

        Shutdown()
