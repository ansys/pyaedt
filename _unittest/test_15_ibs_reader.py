import os
from pyaedt.generic import ibs_reader
try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

from pyaedt.generic.general_methods import is_ironpython


class TestClass:

    def test_01_read_ibis(self):
        ibs_reader.read_project(os.path.join(os.getcwd(), "_unittest", "example_models", "u26a_800_modified.ibs" ))

        assert len(ibs_reader.Components) == 3
        
        assert ibs_reader.Components[0].name == "MT47H64M4BP-3_25"
        assert ibs_reader.Components[1].name == "MT47H32M8BP-3_25"
        assert ibs_reader.Components[2].name == "MT47H16M16BG-3_25"

        assert len(ibs_reader.Models) == 17
        assert ibs_reader.Models[0].name == 'DQ_FULL_800'
        assert ibs_reader.Models[1].name == 'DQ_FULL_ODT50_800'
        assert ibs_reader.Models[16].name == "NF_IN_800"