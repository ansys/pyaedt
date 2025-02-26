from ..EmitNode import *

class ReadOnlyAmplifier(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        val = self._get_property('Filename')
        return val

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property('Noise Temperature')
        return val

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

    class AmplifierTypeOption(Enum):
            TRANSMIT_AMPLIFIER = "Transmit Amplifier"
            RECEIVE_AMPLIFIER = "Receive Amplifier"

    @property
    def amplifier_type(self) -> AmplifierTypeOption:
        """Amplifier Type
        "Configures the amplifier as a Tx or Rx amplifier."
        "        """
        val = self._get_property('Amplifier Type')
        val = self.AmplifierTypeOption[val]
        return val

    @property
    def gain(self) -> float:
        """Gain
        "Amplifier in-band gain."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Gain')
        return val

    @property
    def center_frequency(self) -> float:
        """Center Frequency
        "Center frequency of amplifiers operational bandwidth."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Center Frequency')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @property
    def bandwidth(self) -> float:
        """Bandwidth
        "Frequency region where the gain applies."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Bandwidth')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @property
    def noise_figure(self) -> float:
        """Noise Figure
        "Amplifier noise figure."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Noise Figure')
        return val

    @property
    def saturation_level(self) -> float:
        """Saturation Level
        "Saturation level."
        "Units options: fW, pW, nW, uW, mW, W, kW, megW, gW, dBm, dBW."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Saturation Level')
        val = self._convert_from_default_units(float(val), "Power Unit")
        return val

    @property
    def _1_db_point_ref_input(self) -> float:
        """1-dB Point, Ref. Input
        "Incoming signals > this value saturate the amplifier."
        "Units options: fW, pW, nW, uW, mW, W, kW, megW, gW, dBm, dBW."
        "Value should be between -200 and 200."
        """
        val = self._get_property('1-dB Point, Ref. Input')
        val = self._convert_from_default_units(float(val), "Power Unit")
        return val

    @property
    def ip3_ref_input(self) -> float:
        """IP3, Ref. Input
        "3rd order intercept point."
        "Units options: fW, pW, nW, uW, mW, W, kW, megW, gW, dBm, dBW."
        "Value should be between -200 and 200."
        """
        val = self._get_property('IP3, Ref. Input')
        val = self._convert_from_default_units(float(val), "Power Unit")
        return val

    @property
    def shape_factor(self) -> float:
        """Shape Factor
        "Ratio defining the selectivity of the amplifier."
        "Value should be between 1 and 100."
        """
        val = self._get_property('Shape Factor')
        return val

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        "Amplifier reverse isolation."
        "Value should be between 0 and 200."
        """
        val = self._get_property('Reverse Isolation')
        return val

    @property
    def max_intermod_order(self) -> int:
        """Max Intermod Order
        "Maximum order of intermods to compute."
        "Value should be between 3 and 20."
        """
        val = self._get_property('Max Intermod Order')
        return val

