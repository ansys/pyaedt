import os

from pyaedt.generic import ibis_reader
from pyaedt import Circuit
from _unittest.conftest import local_path

from pyaedt.generic.general_methods import is_ironpython


class TestClass:
    def setup_class(self):
        self.aedtapp = Circuit()

    def teardown_class(self):
        self.aedtapp.close_project(self.aedtapp.project_name, saveproject=False)

    def test_01_read_ibis(self):
        if is_ironpython:
            ibis = ibis_reader.IbisReader.__new__(
                ibis_reader.IbisReader,
                os.path.join(local_path, "example_models", "u26a_800_modified.ibs"),
                self.aedtapp,
            )
        else:
            ibis = ibis_reader.IbisReader(
                os.path.join(local_path, "example_models", "u26a_800_modified.ibs"), self.aedtapp
            )

        ibis_components = ibis.components
        assert len(ibis_components) == 6
        assert ibis_components["MT47H64M4BP-3_25"].name == "MT47H64M4BP-3_25"
        assert ibis_components["MT47H64M4BP_CLP-3_25"].name == "MT47H64M4BP_CLP-3_25"
        assert ibis_components["MT47H32M8BP-3_25"].name == "MT47H32M8BP-3_25"
        assert ibis_components["MT47H16M16BG_CLP-3_25"].name == "MT47H16M16BG_CLP-3_25"

        ibis_models = ibis.models
        assert len(ibis_models) == 17
        assert ibis_models[0].name == "DQ_FULL_800"
        assert ibis_models[1].name == "DQ_FULL_ODT50_800"
        assert ibis_models[16].name == "NF_IN_800"

        # Test pin caracteristics
        assert (
            ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].name
            == "A1_MT47H64M4BP-3_25_u26a_800_modified"
        )
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].short_name == "A1"
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].signal == "VDD"
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].model == "POWER"
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].r_value == "44.3m"
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].l_value == "1.99nH"
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].c_value == "0.59pF"
