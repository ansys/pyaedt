# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

# Toolkit template if the user does not pass any valid script in the toolkit manager

import pyaedt
from pyaedt import get_pyaedt_app
from pyaedt.workflows.misc import get_aedt_version
from pyaedt.workflows.misc import get_port
from pyaedt.workflows.misc import get_process_id
from pyaedt.workflows.misc import is_test

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
test_dict = is_test()


def main():
    app = pyaedt.Desktop(
        new_desktop_session=False, specified_version=version, port=port, aedt_process_id=aedt_process_id
    )

    active_project = app.active_project()
    active_design = app.active_design()

    aedtapp = get_pyaedt_app(design_name=active_design.GetName(), desktop=app)

    # Your PyAEDT script
    aedtapp.modeler.create_sphere([0, 0, 0], 3)

    if not test_dict["is_test"]:  # pragma: no cover
        app.release_desktop(False, False)


if __name__ == "__main__":
    main()
