# Generate pdf report
# ~~~~~~~~~~~~~~~~~~~
# Generate a pdf report with output of simulation.
import os

import pyaedt
from pyaedt import get_pyaedt_app
from pyaedt.generic.pdf import AnsysReport
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

    if not test_dict["is_test"]:  # pragma: no cover
        app.release_desktop(False, False)


if __name__ == "__main__":
    main()
