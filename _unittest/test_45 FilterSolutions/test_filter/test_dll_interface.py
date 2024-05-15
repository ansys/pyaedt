import fspy
import pytest
from fspy.filter_design import FilterType
from fspy.ideal_design import IdealDesign


def test_string_to_enum():
    assert fspy._dll_interface().string_to_enum(FilterType, "gaussian") == FilterType.GAUSSIAN


def test_enum_to_string():
    assert fspy._dll_interface().enum_to_string(FilterType.GAUSSIAN) == "gaussian"


def test_raise_error():
    design = IdealDesign()
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_ratio.row(0)
    assert info.value.args[0] == "This filter has no transmission zero at row 0"
