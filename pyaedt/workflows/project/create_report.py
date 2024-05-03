# Generate pdf report
# ~~~~~~~~~~~~~~~~~~~
# Generate a pdf report with output of simultion.
import os

from pyaedt import Desktop
from pyaedt import get_pyaedt_app
from pyaedt.generic.pdf import AnsysReport

if "PYAEDT_SCRIPT_PORT" in os.environ and "PYAEDT_SCRIPT_VERSION" in os.environ:
    port = os.environ["PYAEDT_SCRIPT_PORT"]
    version = os.environ["PYAEDT_SCRIPT_VERSION"]
else:
    port = 0
    version = "2024.1"

with Desktop(new_desktop_session=False, close_on_exit=False, specified_version=version, port=port) as d:

    proj = d.active_project()
    des = d.active_design()
    projname = proj.GetName()
    desname = des.GetName()
    if des.GetDesignType() in ["HFSS 3D Layout Design", "Circuit Design"]:
        desname = None
    app = get_pyaedt_app(projname, desname)

    report = AnsysReport(version=d.aedt_version_id, design_name=app.design_name, project_name=app.project_name)
    report.create()
    report.add_section()
    report.add_chapter(f"{app.solution_type} Results")
    report.add_sub_chapter("Plots")
    report.add_text("This section contains all reports results.")
    for plot in app.post.plots:
        app.post.export_report_to_jpg(app.working_directory, plot.plot_name)
        report.add_image(os.path.join(app.working_directory, plot.plot_name + ".jpg"), plot.plot_name)
        report.add_page_break()
    report.add_toc()
    out = report.save_pdf(app.working_directory, "AEDT_Results.pdf")
    d.odesktop.AddMessage("", "", 0, f"Report Generated. {out}")
