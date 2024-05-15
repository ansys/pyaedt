import pytest
from fspy.ideal_design import IdealDesign


def test_raise_error():
    design = IdealDesign()
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_ratio.row(0)
    assert info.value.args[0] == "This filter has no transmission zero at row 0"
