from fspy.attributes import BesselRipplePercentage
from fspy.attributes import GaussianBesselReflection
from fspy.attributes import GaussianTransition
from fspy.attributes import PassbandDefinition
from fspy.attributes import RippleConstrictionBandSelect
from fspy.attributes import SinglePointRippleInfZeros
from fspy.attributes import StopbandDefinition
from fspy.filter_design import FilterClass
from fspy.filter_design import FilterType
from fspy.ideal_design import IdealDesign
import pytest


def test_order():
    design = IdealDesign()
    assert design.attributes.order == 5

    with pytest.raises(RuntimeError) as info:
        design.attributes.order = 0
    assert info.value.args[0] == "The minimum order is 1"

    for i in range(1, 22):
        design.attributes.order = i
        assert design.attributes.order == i

    with pytest.raises(RuntimeError) as info:
        design.attributes.order = 22
    assert info.value.args[0] == "The maximum order is 21"


def test_minimum_order_stop_band_att():
    design = IdealDesign()
    assert design.attributes.minimum_order_stop_band_attenuation_db == "60 dB"
    design.attributes.minimum_order_stop_band_attenuation_db = "40 dB"
    assert design.attributes.minimum_order_stop_band_attenuation_db == "40 dB"


def test_minimum_order_stop_band_freq():
    design = IdealDesign()
    assert design.attributes.minimum_order_stop_band_frequency == "10 GHz"
    design.attributes.minimum_order_stop_band_frequency = "500 MHz"
    assert design.attributes.minimum_order_stop_band_frequency == "500 MHz"


def test_minimum_order():
    design = IdealDesign()
    assert design.attributes.order == 5
    design.attributes.ideal_minimum_order
    assert design.attributes.order == 3


def test_pass_band_definition():
    design = IdealDesign()
    design.filter_class = FilterClass.BAND_PASS
    assert len(PassbandDefinition) == 2
    assert design.attributes.pass_band_definition == PassbandDefinition.CENTER_FREQUENCY
    for pbd in PassbandDefinition:
        design.attributes.pass_band_definition = pbd
        assert design.attributes.pass_band_definition == pbd


def test_pass_band_center_frequency():
    design = IdealDesign()
    assert design.attributes.pass_band_center_frequency == "1G"
    design.attributes.pass_band_center_frequency = "500M"
    assert design.attributes.pass_band_center_frequency == "500M"


def test_pass_band_frequency():
    design = IdealDesign()
    design.filter_class = FilterClass.BAND_PASS
    assert design.attributes.pass_band_width_frequency == "200M"
    design.attributes.pass_band_width_frequency = "500M"
    assert design.attributes.pass_band_width_frequency == "500M"


def test_lower_frequency():
    design = IdealDesign()
    design.filter_class = FilterClass.BAND_PASS
    design.attributes.pass_band_definition = PassbandDefinition.CORNER_FREQUENCIES
    assert design.attributes.lower_frequency == "905 M"
    design.attributes.lower_frequency = "800M"
    assert design.attributes.lower_frequency == "800M"


def test_upper_frequency():
    design = IdealDesign()
    design.filter_class = FilterClass.BAND_PASS
    design.attributes.pass_band_definition = PassbandDefinition.CORNER_FREQUENCIES
    assert design.attributes.upper_frequency == "1.105 G"
    design.attributes.upper_frequency = "1.2 G"
    assert design.attributes.upper_frequency == "1.2 G"


def test_stop_band_definition():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    assert len(StopbandDefinition) == 3
    assert design.attributes.stop_band_definition == StopbandDefinition.RATIO
    for sbd in StopbandDefinition:
        design.attributes.stop_band_definition = sbd
        assert design.attributes.stop_band_definition == sbd


def test_stop_band_ratio():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    assert design.attributes.stop_band_ratio == "1.2"
    design.attributes.stop_band_ratio = "1.5"
    assert design.attributes.stop_band_ratio == "1.5"


def test_stop_band_frequency():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.stop_band_definition = StopbandDefinition.FREQUENCY
    assert design.attributes.stop_band_frequency == "1.2 G"
    design.attributes.stop_band_frequency = "1.5 G"
    assert design.attributes.stop_band_frequency == "1.5 G"


def test_stop_band_attenuation():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.stop_band_definition = StopbandDefinition.ATTENUATION_DB
    assert design.attributes.stop_band_attenuation_db == "60"
    design.attributes.stop_band_attenuation_db = "40 dB"
    assert design.attributes.stop_band_attenuation_db == "40"


def test_standard_pass_band_attenuation():
    design = IdealDesign()
    assert design.attributes.standard_pass_band_attenuation
    design.attributes.standard_pass_band_attenuation = False
    assert design.attributes.standard_pass_band_attenuation is False


def test_standard_pass_band_attenuation_value_db():
    design = IdealDesign()
    design.attributes.standard_pass_band_attenuation = False
    assert design.attributes.standard_pass_band_attenuation_value_db == "3.01"
    design.attributes.standard_pass_band_attenuation_value_db = "4"
    assert design.attributes.standard_pass_band_attenuation_value_db == "4"


def test_bessel_normalized_delay():
    design = IdealDesign()
    design.filter_type = FilterType.BESSEL
    assert design.attributes.bessel_normalized_delay is False
    design.attributes.bessel_normalized_delay = True
    assert design.attributes.bessel_normalized_delay


def test_bessel_normalized_delay_period():
    design = IdealDesign()
    design.filter_type = FilterType.BESSEL
    design.attributes.bessel_normalized_delay = True
    assert design.attributes.bessel_normalized_delay_period == "2"
    design.attributes.bessel_normalized_delay_period = "3"
    assert design.attributes.bessel_normalized_delay_period == "3"


def test_bessel_normalized_delay_percentage():
    design = IdealDesign()
    design.filter_type = FilterType.BESSEL
    design.attributes.bessel_normalized_delay = True
    assert len(BesselRipplePercentage) == 6
    for bessel_normalized_delay_percentage in BesselRipplePercentage:
        design.attributes.bessel_normalized_delay_percentage = bessel_normalized_delay_percentage
        assert design.attributes.bessel_normalized_delay_percentage == bessel_normalized_delay_percentage


def test_pass_band_ripple():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    assert design.attributes.pass_band_ripple == ".05"
    design.attributes.pass_band_ripple = ".03"
    assert design.attributes.pass_band_ripple == ".03"


def test_arith_symmetry():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    design.filter_class = FilterClass.BAND_PASS
    assert design.attributes.arith_symmetry is False
    design.attributes.arith_symmetry = True
    assert design.attributes.arith_symmetry


def test_asymmetric():
    design = IdealDesign()
    design.filter_class = FilterClass.BAND_PASS
    assert design.attributes.asymmetric is False
    design.attributes.asymmetric = True
    assert design.attributes.asymmetric


def test_asymmetric_low_order():
    design = IdealDesign()
    design.filter_class = FilterClass.BAND_PASS
    design.attributes.asymmetric = True
    assert design.attributes.asymmetric_low_order == 5

    with pytest.raises(RuntimeError) as info:
        design.attributes.asymmetric_low_order = 0
    assert info.value.args[0] == "The minimum order is 1"

    for i in range(1, 22):
        design.attributes.asymmetric_low_order = i
        assert design.attributes.asymmetric_low_order == i

    with pytest.raises(RuntimeError) as info:
        design.attributes.asymmetric_low_order = 22
    assert info.value.args[0] == "The maximum order is 21"


def test_asymmetric_high_order():
    design = IdealDesign()
    design.filter_class = FilterClass.BAND_PASS
    design.attributes.asymmetric = True
    assert design.attributes.asymmetric_high_order == 5

    with pytest.raises(RuntimeError) as info:
        design.attributes.asymmetric_high_order = 0
    assert info.value.args[0] == "The minimum order is 1"

    for i in range(1, 22):
        design.attributes.asymmetric_high_order = i
        assert design.attributes.asymmetric_high_order == i

    with pytest.raises(RuntimeError) as info:
        design.attributes.asymmetric_high_order = 22
    assert info.value.args[0] == "The maximum order is 21"


def test_asymmetric_low_stop_band_ratio():
    design = IdealDesign()
    design.filter_class = FilterClass.BAND_PASS
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.asymmetric = True
    assert design.attributes.asymmetric_low_stop_band_ratio == "1.2"
    design.attributes.asymmetric_low_stop_band_ratio = "1.5"
    assert design.attributes.asymmetric_low_stop_band_ratio == "1.5"


def test_asymmetric_high_stop_band_ratio():
    design = IdealDesign()
    design.filter_class = FilterClass.BAND_PASS
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.asymmetric = True
    assert design.attributes.asymmetric_high_stop_band_ratio == "1.2"
    design.attributes.asymmetric_high_stop_band_ratio = "1.5"
    assert design.attributes.asymmetric_high_stop_band_ratio == "1.5"


def test_asymmetric_low_stop_band_attenuation_db():
    design = IdealDesign()
    design.filter_class = FilterClass.BAND_PASS
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.asymmetric = True
    assert design.attributes.asymmetric_low_stop_band_attenuation_db == "60"
    design.attributes.asymmetric_low_stop_band_attenuation_db = "40"
    assert design.attributes.asymmetric_low_stop_band_attenuation_db == "40"


def test_asymmetric_high_stop_band_attenuation_db():
    design = IdealDesign()
    design.filter_class = FilterClass.BAND_PASS
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.asymmetric = True
    assert design.attributes.asymmetric_high_stop_band_attenuation_db == "60"
    design.attributes.asymmetric_high_stop_band_attenuation_db = "40"
    assert design.attributes.asymmetric_high_stop_band_attenuation_db == "40"


def test_gaussian_transition():
    design = IdealDesign()
    design.filter_type = FilterType.GAUSSIAN
    assert len(GaussianTransition) == 6
    for gaussian_transition in GaussianTransition:
        design.attributes.gaussian_transition = gaussian_transition
        assert design.attributes.gaussian_transition == gaussian_transition


def test_gaussian_bessel_reflection():
    design = IdealDesign()
    design.filter_type = FilterType.BESSEL
    assert len(GaussianBesselReflection) == 3
    for gaussian_bessel_reflection in GaussianBesselReflection:
        design.attributes.gaussian_bessel_reflection = gaussian_bessel_reflection
        assert design.attributes.gaussian_bessel_reflection == gaussian_bessel_reflection


def test_even_order():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.order = 4
    assert design.attributes.even_order
    design.attributes.even_order = False
    assert design.attributes.even_order is False


def test_even_order_refl_zero():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.order = 4
    assert design.attributes.even_order_refl_zero
    design.attributes.even_order_refl_zero = False
    assert design.attributes.even_order_refl_zero is False


def test_even_order_trn_zero():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.order = 4
    assert design.attributes.even_order_trn_zero
    design.attributes.even_order_trn_zero = False
    assert design.attributes.even_order_trn_zero is False


def test_constrict_ripple():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    assert design.attributes.constrict_ripple is False
    design.attributes.constrict_ripple = True
    assert design.attributes.constrict_ripple


def test_single_point_ripple():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    assert design.attributes.single_point_ripple is False
    design.attributes.single_point_ripple = True
    assert design.attributes.single_point_ripple


def test_half_band_ripple():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    assert design.attributes.half_band_ripple is False
    design.attributes.half_band_ripple = True
    assert design.attributes.half_band_ripple


def test_constrict_ripple_percent():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.constrict_ripple = True
    assert design.attributes.constrict_ripple_percent == "50%"
    design.attributes.constrict_ripple_percent = "40%"
    assert design.attributes.constrict_ripple_percent == "40%"


def test_ripple_constriction_band():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.constrict_ripple = True
    assert len(RippleConstrictionBandSelect) == 3
    for ripple_constriction_band in RippleConstrictionBandSelect:
        design.attributes.ripple_constriction_band = ripple_constriction_band
        assert design.attributes.ripple_constriction_band == ripple_constriction_band


def test_single_point_ripple_inf_zeros():
    design = IdealDesign()
    design.filter_type = FilterType.ELLIPTIC
    design.attributes.single_point_ripple = True
    assert len(SinglePointRippleInfZeros) == 2
    for single_point_ripple_inf_zeros in SinglePointRippleInfZeros:
        design.attributes.single_point_ripple_inf_zeros = single_point_ripple_inf_zeros
        assert design.attributes.single_point_ripple_inf_zeros == single_point_ripple_inf_zeros


def test_delay_equalizer():
    design = IdealDesign()
    assert design.attributes.delay_equalizer is False
    design.attributes.delay_equalizer = True
    assert design.attributes.delay_equalizer


def test_delay_equalizer_order():
    design = IdealDesign()
    design.attributes.delay_equalizer = True
    assert design.attributes.delay_equalizer_order == 2

    for i in range(0, 21):
        design.attributes.delay_equalizer_order = i
        assert design.attributes.delay_equalizer_order == i

    with pytest.raises(RuntimeError) as info:
        design.attributes.delay_equalizer_order = 21
    assert info.value.args[0] == "The maximum order is 20"


def test_standard_delay_equ_pass_band_attenuation():
    design = IdealDesign()
    design.attributes.delay_equalizer = True
    assert design.attributes.standard_delay_equ_pass_band_attenuation
    design.attributes.standard_delay_equ_pass_band_attenuation = False
    assert design.attributes.standard_delay_equ_pass_band_attenuation is False


def test_standard_delay_equ_pass_band_attenuation_value_db():
    design = IdealDesign()
    design.attributes.delay_equalizer = True
    design.attributes.standard_delay_equ_pass_band_attenuation = False
    assert design.attributes.standard_delay_equ_pass_band_attenuation_value_db == "3.01"
    design.attributes.standard_delay_equ_pass_band_attenuation_value_db = "4"
    assert design.attributes.standard_delay_equ_pass_band_attenuation_value_db == "4"
