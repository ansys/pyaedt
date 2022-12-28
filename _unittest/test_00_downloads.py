# Import required modules
import os
import tempfile

from _unittest.conftest import BasisTest
from _unittest.conftest import is_ironpython
from pyaedt import downloads
from pyaedt.generic.general_methods import generate_unique_name


class TestClass(BasisTest, object):
    def setup_class(self):
        # set a scratch directory and the environment / test data
        self.examples = downloads
        pass

    def teardown_class(self):
        del self.examples

    def test_00_download_edb(self):
        assert self.downloads.download_aedb()

    def test_01_download_touchstone(self):
        assert self.downloads.download_touchstone()

    def test_02_download_netlist(self):
        assert self.downloads.download_netlist()

    def test_03_download_sbr(self):
        assert self.downloads.download_sbr()

    def test_04_download_antenna_array(self):
        assert self.downloads.download_antenna_array()

    def test_05_download_antenna_sherlock(self):
        assert self.downloads.download_sherlock(destination=os.path.join(tempfile.gettempdir(), "sherlock"))

    def test_06_download_multiparts(self):
        assert self.downloads.download_multiparts(destination=os.path.join(tempfile.gettempdir(), "multi"))

    def test_07_download_wfp(self):
        assert self.downloads.download_edb_merge_utility(True)
        assert self.downloads.download_edb_merge_utility(True, destination=tempfile.gettempdir())
        out = self.downloads.download_edb_merge_utility()
        assert os.path.exists(out)
        new_name = generate_unique_name("test")
        new_path = os.path.split(out)[0] + new_name
        os.rename(os.path.split(out)[0], new_path)
        assert os.path.exists(new_path)

    def test_08_download_leaf(self):
        out = self.downloads.download_leaf()
        assert os.path.exists(out[0])
        assert os.path.exists(out[1])
        new_name = generate_unique_name("test")
        new_path = os.path.split(out[0])[0] + new_name
        os.rename(os.path.split(out[0])[0], new_path)
        assert os.path.exists(new_path)

    def test_09_download_custom_report(self):
        out = self.downloads.download_custom_reports()
        assert os.path.exists(out)

    def test_10_download_3dcomp(self):
        out = self.downloads.download_3dcomponent()
        assert os.path.exists(out)

    def test_11_download_twin_builder_data(self):
        example_folder = self.downloads.download_twin_builder_data("Ex1_Mechanical_DynamicRom.zip", True)
        assert os.path.exists(example_folder)

    def test_12_download_specific_file(self):
        example_folder = self.downloads.download_file("motorcad", "IPM_Vweb_Hairpin.mot")
        assert os.path.exists(example_folder)

    def test_13_download_specific_folder(self):
        if is_ironpython:
            assert not self.downloads.download_file(directory="nissan")
        else:
            example_folder = self.downloads.download_file(directory="nissan")
            assert os.path.exists(example_folder)
        if is_ironpython:
            assert not self.downloads.download_file(directory="wpf_edb_merge")
        else:
            example_folder = self.downloads.download_file(directory="wpf_edb_merge")
            assert os.path.exists(example_folder)
