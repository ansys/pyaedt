# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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


class LicenseSession:
    """Manage an EMIT solver license session for AEDT 2027.1+."""

    def __init__(self, emit_com_module, result_index: int):
        self._emit_com_module = emit_com_module
        self._result_index = result_index
        self._active = False
        self.checkout()

    def checkout(self) -> None:
        """Check out a solver license and start a session."""
        if self._active:
            return
        self._emit_com_module.CheckoutLicenseSession(self._result_index)
        self._active = True

    def check_in(self) -> None:
        """Check in the solver license and end the session."""
        if not self._active:
            return
        self._emit_com_module.CheckinLicenseSession(self._result_index)
        self._active = False

    def close(self) -> None:
        """End the current license session."""
        self.check_in()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.check_in()
        return False

    def __del__(self):
        # Destructor timing is implementation-dependent, so this is best-effort.
        try:
            self.check_in()
        except Exception:
            pass
