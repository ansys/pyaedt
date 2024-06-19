# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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

# Generate a pdf report with output of simulation.
import os

import pyaedt
from pyaedt import get_pyaedt_app
from pyaedt.generic.pdf import AnsysReport
from pyaedt.workflows.misc import get_aedt_version
from pyaedt.workflows.misc import get_arguments
from pyaedt.workflows.misc import get_port
from pyaedt.workflows.misc import get_process_id
from pyaedt.workflows.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = None
extension_description = "Create report"


def main(extension_args):
    app = pyaedt.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    design_name = active_design.GetName()

    if active_design.GetDesignType() in ["HFSS 3D Layout Design", "Circuit Design"]:
        design_name = None
    aedtapp = get_pyaedt_app(project_name, design_name)

    report = AnsysReport(
        version=app.aedt_version_id, design_name=aedtapp.design_name, project_name=aedtapp.project_name
    )
    report.create()
    report.add_section()
    report.add_chapter(f"{aedtapp.solution_type} Results")
    report.add_sub_chapter("Plots")
    report.add_text("This section contains all reports results.")
    for plot in aedtapp.post.plots:
        aedtapp.post.export_report_to_jpg(aedtapp.working_directory, plot.plot_name)
        report.add_image(os.path.join(aedtapp.working_directory, plot.plot_name + ".jpg"), plot.plot_name)
        report.add_page_break()
    report.add_toc()
    out = report.save_pdf(aedtapp.working_directory, "AEDT_Results.pdf")
    aedtapp.logger.info(f"Report Generated. {out}")

    if not extension_args["is_test"]:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(extension_arguments, extension_description)
    main(args)
