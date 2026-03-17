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

import threading
import time

import pytest

from ansys.aedt.core import settings
from ansys.aedt.core.common_rpc import create_session
from ansys.aedt.core.common_rpc import pyaedt_service_manager
from ansys.aedt.core.desktop import _find_free_port
from ansys.aedt.core.hfss import Hfss
from tests.conftest import DESKTOP_VERSION
from tests.system.general.test_desktop_grpc_transport import generate_certs

GRPC_CONNECTION_TIMEOUT = 30

# # NOTE: Activating this environment variable forces PyAEDT to use the
# # old grpc connection arguments. This is useful for testing backward
# # compatibility with previous SP of AEDT.
# os.environ["PYAEDT_USE_PRE_GRPC_ARGS"] = "True"

SERVER_HOST = "127.0.0.1"
PORT_SERVER_MANAGER = _find_free_port()


def find_client_and_aedt_ports():
    """Find distinct free ports for the client and AEDT.

    These ports should not conflict with the server manager port.
    """
    while True:
        port_client = _find_free_port()
        port_aedt = _find_free_port()
        if len({PORT_SERVER_MANAGER, port_client, port_aedt}) == 3:
            return port_client, port_aedt


@pytest.fixture(scope="module")
def rpc_server():
    """Fixture to start the PyAEDT service manager in a separate thread for testing."""

    def run_server():
        pyaedt_service_manager(host=SERVER_HOST, port=PORT_SERVER_MANAGER)

    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(5)

    yield


@pytest.mark.skipif(
    DESKTOP_VERSION < "2026.1",
    reason="Not working in versions without grpc patch",
)
def test_remote_hfss_workflow_with_mtls(rpc_server, tmp_path, monkeypatch):
    # Set up ports, generate certificates, settings and configure environment variables for mTLS
    port_client, port_aedt = find_client_and_aedt_ports()
    generate_certs([SERVER_HOST], tmp_path)
    monkeypatch.setenv("ANSYS_GRPC_CERTIFICATES", str(tmp_path))
    monkeypatch.setenv("AnsysEM_GRPC_Connection_Timeout", f"{GRPC_CONNECTION_TIMEOUT}")
    settings.grpc_local = False
    settings.remote_rpc_service_manager_port = PORT_SERVER_MANAGER

    cl1 = create_session(SERVER_HOST, client_port=port_client)
    cl1.aedt(host=SERVER_HOST, port=port_aedt, non_graphical=False)
    hfss = Hfss(machine=SERVER_HOST, port=port_aedt)
    box = hfss.modeler.create_box([0, 0, 0], [10, 10, 10], name="MyBox")

    assert box is not None

    # NOTE: This is required as each test creates a new desktop session.
    hfss.desktop_class.close_desktop()
    cl1.close()


# NOTE: Uncomment this test to test insecure gRPC connection.
# @pytest.mark.skipif(
#     DESKTOP_VERSION < "2026.1",
#     reason="Not working in versions without grpc patch",
# )
# def test_remote_hfss_workflow_with_insecure(rpc_server, tmp_path, monkeypatch):
#     # Set up ports and settings for insecure gRPC connection
#     port_client, port_aedt = find_client_and_aedt_ports()
#     settings.grpc_local = False
#     settings.grpc_secure_mode = False
#     settings.remote_rpc_service_manager_port = PORT_SERVER_MANAGER

#     cl1 = create_session(SERVER_HOST, client_port=port_client)
#     cl1.aedt(host=SERVER_HOST, port=port_aedt, non_graphical=False, secure=False)
#     hfss = Hfss(machine=SERVER_HOST, port=port_aedt)
#     box = hfss.modeler.create_box([0, 0, 0], [10, 10, 10], name="MyBox")

#     assert box is not None

#     # NOTE: This is required as each test creates a new desktop session.
#     hfss.desktop_class.close_desktop()
#     cl1.close()
