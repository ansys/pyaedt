import os

from _unittest.conftest import BasisTest
from _unittest.conftest import local_path
from _unittest.conftest import new_thread
from pyaedt import Q2d
from pyaedt import settings


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_export_w_elements_from_sweep(self):
        test_project = self.local_scratch.copyfile(os.path.join(local_path, "example_models", "q2d_solved_sweep.aedtz"))
        with Q2d(test_project, non_graphical=settings.non_graphical, new_desktop_session=new_thread) as q2d:
            try:
                export_folder = os.path.join(self.local_scratch.path, "export_folder")
                files = q2d.export_w_elements(False, export_folder)
                assert len(files) == 3
                for file in files:
                    _, ext = os.path.splitext(file)
                    assert ext == ".sp"
                    assert os.path.isfile(file)
            finally:
                q2d.close_project(saveproject=False)

    def test_02_export_w_elements_from_nominal(self):
        test_project = self.local_scratch.copyfile(
            os.path.join(local_path, "example_models", "q2d_solved_nominal.aedtz")
        )
        with Q2d(test_project, non_graphical=settings.non_graphical, new_desktop_session=new_thread) as q2d:
            try:
                export_folder = os.path.join(self.local_scratch.path, "export_folder")
                files = q2d.export_w_elements(False, export_folder)
                assert len(files) == 1
                for file in files:
                    _, ext = os.path.splitext(file)
                    assert ext == ".sp"
                    assert os.path.isfile(file)
            finally:
                q2d.close_project(saveproject=False)

    def test_03_export_w_elements_to_working_directory(self):
        test_project = self.local_scratch.copyfile(
            os.path.join(local_path, "example_models", "q2d_solved_nominal.aedtz")
        )
        with Q2d(test_project, non_graphical=settings.non_graphical, new_desktop_session=new_thread) as q2d:
            try:
                files = q2d.export_w_elements(False)
                assert len(files) == 1
                for file in files:
                    _, ext = os.path.splitext(file)
                    assert ext == ".sp"
                    assert os.path.isfile(file)
                    file_dir = os.path.abspath(os.path.dirname(file))
                    assert file_dir == os.path.abspath(q2d.working_directory)
            finally:
                q2d.close_project(saveproject=False)
