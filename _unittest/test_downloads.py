# standard imports
import gc

# Import required modules
from pyaedt.examples import downloads


class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        self.examples = downloads
        pass

    def teardown_class(self):
        gc.collect()

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
        assert self.examples.download_sherlock()
