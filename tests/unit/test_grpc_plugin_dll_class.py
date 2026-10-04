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

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.internal.errors import GrpcApiError
from ansys.aedt.core.internal.grpc_plugin_dll_class import AedtObjWrapper
from ansys.aedt.core.internal.grpc_plugin_dll_class import AedtPropServer


@pytest.fixture
def dll_api():
    api = MagicMock()
    return MagicMock(AedtAPI=api)


def test_aedt_object_exposes_only_registered_methods(dll_api):
    wrapper = AedtObjWrapper(1, ["RegisteredMethod"], dll_api)

    assert callable(wrapper.RegisteredMethod)
    assert wrapper.ScopeID == 1
    assert not hasattr(wrapper, "MissingMethod")


def test_aedt_object_invokes_registered_method(dll_api):
    dll_api.AedtAPI.InvokeAedtObjMethod.return_value = "result"
    wrapper = AedtObjWrapper(1, ["RegisteredMethod"], dll_api)

    with patch(
        "ansys.aedt.core.internal.grpc_plugin_dll_class._retry_ntimes",
        side_effect=lambda retries, method, *args: method(*args),
    ):
        assert wrapper.RegisteredMethod("argument") == "result"

    dll_api.AedtAPI.InvokeAedtObjMethod.assert_called_once_with(1, "RegisteredMethod", ("argument",))


def test_aedt_object_propagates_dll_api_to_returned_wrappers(dll_api):
    child = AedtObjWrapper(2, [], None)
    dll_api.AedtAPI.InvokeAedtObjMethod.return_value = child
    wrapper = AedtObjWrapper(1, ["GetChild"], dll_api)

    with patch(
        "ansys.aedt.core.internal.grpc_plugin_dll_class._retry_ntimes",
        side_effect=lambda retries, method, *args: method(*args),
    ):
        assert wrapper.GetChild() is child

    assert child.dllapi is dll_api


def test_aedt_property_server_falls_back_to_properties(dll_api):
    def invoke_method(object_id, method_name, arguments):
        if method_name == "GetPropNames":
            return ["Property Name"]
        if method_name == "GetPropValue":
            return f"value of {arguments[0]}"
        raise AssertionError(f"Unexpected method: {method_name}")

    dll_api.AedtAPI.InvokeAedtObjMethod.side_effect = invoke_method
    prop_server = AedtPropServer(2, ["GetPropNames", "GetPropValue"], dll_api)

    with patch(
        "ansys.aedt.core.internal.grpc_plugin_dll_class._retry_ntimes",
        side_effect=lambda retries, method, *args: method(*args),
    ):
        assert "Property_Name" in dir(prop_server)
        assert prop_server.Property_Name == "value of Property Name"
        with pytest.raises(GrpcApiError, match="MissingProperty"):
            prop_server.MissingProperty
