import os

from _unittest.conftest import local_path
import pytest

from pyaedt import Hfss3dLayout

test_subfolder = "T44"
test_T44_dir = os.path.join(local_path, "example_models", test_subfolder)

test_project_name = "hfss_design"
aedt_proj_name = "differential_microstrip"


@pytest.fixture(scope="class")
def hfss3dl(add_app):
    app = add_app(project_name=aedt_proj_name, application=Hfss3dLayout, subfolder=test_subfolder)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, hfss3dl, local_scratch):
        self.hfss3dl = hfss3dl
        self.local_scratch = local_scratch

    def test_01_get_touchstone_data(self):
        assert isinstance(self.hfss3dl.get_touchstone_data("Setup1"), list)
        ts_data = self.hfss3dl.get_touchstone_data("Setup1")[0]
        assert ts_data.get_return_loss_index()
        assert ts_data.get_insertion_loss_index_from_prefix("diff1", "diff2")
        assert ts_data.get_next_xtalk_index()
        assert ts_data.get_fext_xtalk_index_from_prefix("diff1", "diff2")

    def test_02_read_ts_file(self):
        from pyaedt.generic.touchstone_parser import TouchstoneData

        ts1 = TouchstoneData(touchstone_file=os.path.join(test_T44_dir, "port_order_1234.s8p"))
        assert ts1.get_mixed_mode_touchstone_data()
        ts2 = TouchstoneData(touchstone_file=os.path.join(test_T44_dir, "port_order_1324.s8p"))
        assert ts2.get_mixed_mode_touchstone_data(port_ordering="1324")

        assert ts1.plot_insertion_losses(plot=False)
        assert ts1.get_worst_curve(curve_list=ts1.get_return_loss_index(), plot=False)
