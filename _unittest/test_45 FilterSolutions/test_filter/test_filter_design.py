import fspy
from fspy.filter_design import DiplexerType
from fspy.filter_design import FilterClass
from fspy.filter_design import FilterDesign
from fspy.filter_design import FilterImplementation
from fspy.filter_design import FilterType


def test_version():
    assert fspy.api_version() == "FilterSolutions API Version 2024 R1 (Beta)"


def test_filter_type():
    design = FilterDesign()
    assert design.filter_type == FilterType.BUTTERWORTH

    assert len(FilterType) == 8

    for fimp in [FilterImplementation.LUMPED]:
        design.filter_implementation = fimp
        for ftype in FilterType:
            design.filter_type = ftype
            assert design.filter_type == ftype


def test_filter_class():
    design = FilterDesign()
    assert design.filter_implementation == FilterImplementation.LUMPED

    # Only lumped supports all classes
    # TODO: Confirm proper exceptions are raised when setting unsupported filter class for each implementation.

    assert len(FilterClass) == 10
    for index, fclass in enumerate(FilterClass):
        if index > 5:
            design.filter_multiple_bands_enabled = True
        design.filter_class = fclass
        assert design.filter_class == fclass


def test_filter_multiple_bands_enabled():
    design = FilterDesign()
    assert design.filter_multiple_bands_enabled is False
    design.filter_multiple_bands_enabled = True
    assert design.filter_multiple_bands_enabled


def test_filter_multiple_bands_low_pass_frequency():
    design = FilterDesign()
    design.filter_multiple_bands_enabled = True
    design.filter_class = FilterClass.LOW_BAND
    assert design.filter_multiple_bands_low_pass_frequency == "1G"
    design.filter_multiple_bands_low_pass_frequency = "500M"
    assert design.filter_multiple_bands_low_pass_frequency == "500M"


def test_filter_multiple_bands_high_pass_frequency():
    design = FilterDesign()
    design.filter_multiple_bands_enabled = True
    design.filter_class = FilterClass.BAND_HIGH
    assert design.filter_multiple_bands_high_pass_frequency == "1G"
    design.filter_multiple_bands_high_pass_frequency = "500M"
    assert design.filter_multiple_bands_high_pass_frequency == "500M"


def test_filter_implementation():
    design = FilterDesign()
    assert len(FilterImplementation) == 5
    for fimplementation in FilterImplementation:
        design.filter_implementation = fimplementation
        assert design.filter_implementation == fimplementation


def test_diplexer_type():
    design = FilterDesign()
    assert len(DiplexerType) == 6
    for index, diplexer_type in enumerate(DiplexerType):
        if index < 3:
            design.filter_class = FilterClass.DIPLEXER_1
        elif index > 2:
            design.filter_class = FilterClass.DIPLEXER_2
        design.diplexer_type = diplexer_type
        assert design.diplexer_type == diplexer_type
