import os
import tempfile

import pytest

from pyaedt import downloads
from pyaedt import is_linux
from pyaedt.generic.general_methods import generate_unique_name


@pytest.fixture(scope="module", autouse=True)
def desktop():
    return


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        self.examples = downloads

    def test_00_download_edb(self):
        assert self.examples.download_aedb()

    def test_01_download_touchstone(self):
        assert self.examples.download_touchstone()

    def test_02_download_netlist(self):
        assert self.examples.download_netlist()

    def test_03_download_sbr(self):
        assert self.examples.download_sbr()

    def test_04_download_antenna_array(self):
        assert self.examples.download_antenna_array()

    def test_05_download_antenna_sherlock(self):
        assert self.examples.download_sherlock(destination=os.path.join(tempfile.gettempdir(), "sherlock"))

    @pytest.mark.skipif(is_linux, reason="Crashes on Linux")
    def test_06_download_multiparts(self):
        assert self.examples.download_multiparts(destination=os.path.join(tempfile.gettempdir(), "multi"))

    def test_07_download_wfp(self):
        assert self.examples.download_edb_merge_utility(True)
        assert self.examples.download_edb_merge_utility(True, destination=tempfile.gettempdir())
        out = self.examples.download_edb_merge_utility()
        assert os.path.exists(out)
        new_name = generate_unique_name("test")
        new_path = os.path.split(out)[0] + new_name
        os.rename(os.path.split(out)[0], new_path)
        assert os.path.exists(new_path)

    def test_08_download_leaf(self):
        out = self.examples.download_leaf()
        assert os.path.exists(out[0])
        assert os.path.exists(out[1])
        new_name = generate_unique_name("test")
        new_path = os.path.split(out[0])[0] + new_name
        os.rename(os.path.split(out[0])[0], new_path)
        assert os.path.exists(new_path)

    @pytest.mark.skipif(is_linux, reason="Failing on linux")
    def test_09_download_custom_report(self):
        out = self.examples.download_custom_reports()
        assert os.path.exists(out)

    @pytest.mark.skipif(is_linux, reason="Failing on linux")
    def test_10_download_3dcomp(self):
        out = self.examples.download_3dcomponent()
        assert os.path.exists(out)

    def test_11_download_twin_builder_data(self):
        example_folder = self.examples.download_twin_builder_data("Ex1_Mechanical_DynamicRom.zip", True)
        assert os.path.exists(example_folder)

    def test_12_download_specific_file(self):
        example_folder = self.examples.download_file("motorcad", "IPM_Vweb_Hairpin.mot")
        assert os.path.exists(example_folder)

    @pytest.mark.skipif(is_linux, reason="Failing download files")
    def test_13_download_specific_folder(self):
        example_folder = self.examples.download_file(directory="nissan")
        assert os.path.exists(example_folder)
        example_folder = self.examples.download_file(directory="wpf_edb_merge")
        assert os.path.exists(example_folder)

    @pytest.mark.skipif(is_linux, reason="Failing download files")
    def test_14_download_icepak_3d_component(self):
        assert self.examples.download_icepak_3d_component()

    @pytest.mark.skipif(is_linux, reason="Failing download files")
    def test_15_download_fss_file(self):
        example_folder = self.examples.download_FSS_3dcomponent()
        assert os.path.exists(example_folder)
