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

from contextlib import contextmanager

from ansys.aedt.core.internal.checks import min_aedt_version
from ansys.aedt.core.internal.errors import GrpcApiError


@min_aedt_version("2027.1")
@contextmanager
def _catch_aedt_errors(emit_obj, default_error: str) -> None:
    """Catches grpc exceptions and raises a RuntimeError with the last error message from AEDT if found.

    Parameters
    ----------
    default_error : str
        The default error message to raise if none is found in aedt message manager.
    """
    try:
        yield
    except GrpcApiError as e:
        try:
            errors = emit_obj.logger.aedt_messages.error_level
        except GrpcApiError:  # no messages found (logger bug triggers the exception)
            raise e
        if errors:
            last_message = str(errors[-1])
            if "[error]  " in last_message:
                # Trim the beginning of the error message
                index = last_message.find("[error]  ") + len("[error]  ")
                last_message = last_message[(index):]
                raise RuntimeError(last_message)
            else:
                raise Exception(default_error) from e
        else:
            raise Exception(default_error) from e
