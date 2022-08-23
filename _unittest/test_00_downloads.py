# Import required modules
import os
import tempfile

from _unittest.conftest import BasisTest
from pyaedt.examples import downloads


class TestClass(BasisTest, object):
    def setup_class(self):
        # set a scratch directory and the environment / test data
        self.examples = downloads
        pass

    def teardown_class(self):
        del self.examples

    def test_download_edb(self):
        assert self.examples.download_aedb()

    def test_download_touchstone(self):
        assert self.examples.download_touchstone()

    def test_download_netlist(self):
        assert self.examples.download_netlist()

    def test_download_sbr(self):
        assert self.examples.download_sbr()

    def test_download_antenna_array(self):
        assert self.examples.download_antenna_array()

    def test_download_antenna_sherlock(self):
        assert self.examples.download_sherlock(destination=os.path.join(tempfile.gettempdir(), "sherlock"))

    def test_download_multiparts(self):
        assert self.examples.download_multiparts(destination=os.path.join(tempfile.gettempdir(), "multi"))

    def test_download_wfp(self):
        assert self.examples.download_edb_merge_utility()
        assert self.examples.download_edb_merge_utility(True)
        out = self.examples.download_edb_merge_utility(True, destination=tempfile.gettempdir())
        assert os.path.exists(out)

    def test_download_leaf(self):
        out = self.examples.download_leaf()
        assert os.path.exists(out[0])
        assert os.path.exists(out[1])

    def test_download_custom_report(self):
        out = self.examples.download_custom_reports()
        assert os.path.exists(out)

    def test_download_3dcomp(self):
        out = self.examples.download_3dcomponent()
        assert os.path.exists(out)

    def test_download_twin_builder_data(self):
        example_folder = self.examples.download_twin_builder_data("Ex1_Mechanical_DynamicRom.zip", True)
        assert os.path.exists(example_folder)
