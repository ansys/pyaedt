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

import multiprocessing
import os
import signal
import socket
import time

import pytest

from ansys.aedt.core import settings
from ansys.aedt.core.common_rpc import create_session
from ansys.aedt.core.common_rpc import pyaedt_service_manager
from ansys.aedt.core.desktop import _find_free_port
from ansys.aedt.core.generic.general_methods import active_sessions
from ansys.aedt.core.hfss import Hfss
from tests.conftest import DESKTOP_VERSION
from tests.conftest import NON_GRAPHICAL
from tests.system.solvers.sequential.test_desktop_grpc_transport import generate_certs

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


@pytest.fixture
def rpc_server():
    """Run the service manager in an isolated process with the configured AEDT version."""
    process = None

    def start():
        nonlocal process
        process = multiprocessing.get_context("spawn").Process(
            target=pyaedt_service_manager,
            kwargs={"host": SERVER_HOST, "port": PORT_SERVER_MANAGER, "aedt_version": DESKTOP_VERSION},
        )
        process.start()
        deadline = time.monotonic() + 30
        while True:
            if not process.is_alive():
                raise RuntimeError(f"RPC service manager exited with code {process.exitcode}.")
            try:
                with socket.create_connection((SERVER_HOST, PORT_SERVER_MANAGER), timeout=1):
                    break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("RPC service manager did not start within 30 seconds.")
                time.sleep(0.1)

    try:
        yield start
    finally:
        if process is not None and process.is_alive():
            process.terminate()
        if process is not None:
            process.join(timeout=10)
            if process.is_alive():
                process.kill()
                process.join()


@pytest.fixture
def rpc_settings(monkeypatch):
    monkeypatch.setattr(settings, "grpc_local", False)
    monkeypatch.setattr(settings, "grpc_secure_mode", True)
    monkeypatch.setattr(settings, "remote_rpc_service_manager_port", PORT_SERVER_MANAGER)
    monkeypatch.setattr(settings, "remote_rpc_session", None)
    monkeypatch.setattr(settings, "remote_rpc_session_temp_folder", settings.remote_rpc_session_temp_folder)
    monkeypatch.setattr(settings, "aedt_version", settings.aedt_version)


def run_remote_hfss_workflow(port_client, port_aedt, secure):
    client = create_session(SERVER_HOST, client_port=port_client, secure=secure)
    hfss = None
    launched = False
    try:
        info = client.aedt(host=SERVER_HOST, port=port_aedt, non_graphical=NON_GRAPHICAL, secure=secure)
        launched = True
        assert info.version == DESKTOP_VERSION
        hfss = Hfss(machine=SERVER_HOST, port=port_aedt, version=DESKTOP_VERSION)
        box = hfss.modeler.create_box([0, 0, 0], [10, 10, 10], name="MyBox")
        assert box is not None
    finally:
        try:
            if hfss is not None:
                hfss.desktop_class.close_desktop()
            elif launched:
                for pid, port in active_sessions(version=DESKTOP_VERSION, non_graphical=NON_GRAPHICAL).items():
                    if port == port_aedt:
                        os.kill(pid, signal.SIGTERM)
        finally:
            try:
                client.close()
            finally:
                client._service_manager_connection.close()


@pytest.mark.skipif(
    DESKTOP_VERSION < "2026.1",
    reason="Not working in versions without grpc patch",
)
def test_remote_hfss_workflow_with_mtls(rpc_server, rpc_settings, tmp_path, monkeypatch):
    # Set up ports, generate certificates, settings and configure environment variables for mTLS
    port_client, port_aedt = find_client_and_aedt_ports()
    generate_certs([SERVER_HOST], tmp_path)
    monkeypatch.setenv("ANSYS_GRPC_CERTIFICATES", str(tmp_path))
    monkeypatch.setenv("AnsysEM_GRPC_Connection_Timeout", f"{GRPC_CONNECTION_TIMEOUT}")
    rpc_server()
    run_remote_hfss_workflow(port_client, port_aedt, secure=True)


@pytest.mark.skipif(
    DESKTOP_VERSION < "2026.1",
    reason="Not working in versions without grpc patch",
)
def test_remote_hfss_workflow_with_insecure(rpc_server, rpc_settings):
    # Set up ports and settings for insecure gRPC connection
    port_client, port_aedt = find_client_and_aedt_ports()
    settings.grpc_secure_mode = False
    rpc_server()
    run_remote_hfss_workflow(port_client, port_aedt, secure=False)
