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

"""Entry point to spawn a per-client RPyC GlobalService worker.

This script is called by `ServiceManager.start_service()` as a subprocess.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ansys.aedt.core.common_rpc import launch_server


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch a PyAEDT RPyC worker server.")
    parser.add_argument("--ansysem-path", required=True, help="Full path to the ANSYS EM installation directory.")
    parser.add_argument("--host", default=None, help="Host name or IP address to be forwarded when launching AEDT.")
    parser.add_argument("--port", type=int, default=18000, help="Port the RPyC server listens on (default: 18000).")
    parser.add_argument(
        "--non-graphical",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Start AEDT in non-graphical mode.",
    )
    parser.add_argument("--no-threaded", action="store_true", help="Use a one-shot server instead of a threaded one.")
    parser.add_argument(
        "--listen-all", action=argparse.BooleanOptionalAction, default=False, help="Listen on all network interfaces."
    )
    parser.add_argument(
        "--secure", action=argparse.BooleanOptionalAction, default=True, help="Use a secure connection."
    )

    args = parser.parse_args()
    launch_server(
        host=args.host,
        ansysem_path=args.ansysem_path,
        port=args.port,
        non_graphical=args.non_graphical,
        threaded=not args.no_threaded,
        listen_all=args.listen_all,
        secure=args.secure,
    )


if __name__ == "__main__":
    main()
