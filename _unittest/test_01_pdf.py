import os

from _unittest.conftest import desktop_version
from _unittest.conftest import local_path
import pytest

from pyaedt import pyaedt_path
from pyaedt.generic.pdf import AnsysReport

# from _unittest.conftest import scratch_path


# try:
#     import pytest  # noqa: F401
# except ImportError:
#     import _unittest_ironpython.conf_unittest as pytest  # noqa: F401

tol = 1e-12


@pytest.fixture(scope="module", autouse=True)
def desktop():
    return


class TestClass(object):
    # def setup_class(self):
    #     pass
    #
    # def teardown_class(self):
    #     pass

    def test_create_pdf(self, local_scratch):
        template_path = os.path.join(pyaedt_path, "dlls", "PDFReport", "AnsysTemplate.json")
        report = AnsysReport(project_name="Coaxial", design_name="Design1", tempplate_json_file=template_path)
        report.aedt_version = desktop_version
        assert "AnsysTemplate" in report.template_name
        report.template_name = "AnsysTemplate"
        assert report.project_name == "Coaxial"
        report.project_name = "Coaxial1"
        assert report.project_name == "Coaxial1"
        assert report.design_name == "Design1"
        report.design_name = "Design2"
        assert report.design_name == "Design2"
        report.create()
        report.add_section()
        report.add_chapter("Chapter 1")
        report.add_sub_chapter("C1")
        report.add_text("ciao")
        report.add_text("ciao2", True, True)
        report.add_empty_line(2)
        report.add_page_break()
        report.add_image(os.path.join(local_path, "example_models", "Coax_HFSS.jpg"), "Coaxial Cable")
        report.add_section("L")
        report.add_table("MyTable", [["x", "y"], ["0", "1"], ["2", "3"], ["10", "20"]])
        report.add_section()
        report.add_chart([0, 1, 2, 3, 4, 5], [10, 20, 4, 30, 40, 12], "Freq", "Val", "MyTable")
        report.add_toc()
        assert os.path.exists(report.save_pdf(local_scratch.path, "my_firstpdf.pdf"))
