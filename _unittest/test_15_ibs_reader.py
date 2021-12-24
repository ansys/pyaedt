import os
from pyaedt.generic import ibis_reader


class TestClass:

    def test_01_read_ibis(self):
        reader = ibis_reader.IbisReader()
        ibis = reader.read_project(os.path.join(os.getcwd(), "_unittest", "example_models", "u26a_800_modified.ibs" ))

        ibis_components = ibis.components
        assert len(ibis_components) == 6
        assert ibis_components[0].name == "MT47H64M4BP-3_25"
        assert ibis_components[1].name == "MT47H64M4BP_CLP-3_25"
        assert ibis_components[2].name == "MT47H32M8BP-3_25"
        assert ibis_components[5].name == "MT47H16M16BG_CLP-3_25"

        ibis_models = ibis.models
        assert len(ibis_models) == 17
        assert ibis_models[0].name == 'DQ_FULL_800'
        assert ibis_models[1].name == 'DQ_FULL_ODT50_800'
        assert ibis_models[16].name == "NF_IN_800"