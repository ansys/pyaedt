# Import required modules
import tempfile
import os

from pyaedt.examples import downloads
from _unittest.conftest import BasisTest


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
