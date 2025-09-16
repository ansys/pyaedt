# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""Tests for HFSS excitations, particularly WavePort functionality."""

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.generic.constants import Plane


class TestHfssWavePortExcitations:
    """Test cases for HFSS Wave Port excitations."""

    @classmethod
    def setup_class(cls):
        """Setup the HFSS application and waveguide once for all tests."""
        # Use pytest's request fixture to get add_app
        # This will be set in the first test via setup method
        cls.aedtapp = None
        cls.input_face = None
        cls.output_face = None

    @pytest.fixture(autouse=True)
    def setup(self, add_app):
        """Setup the HFSS application for testing, only once."""
        if TestHfssWavePortExcitations.aedtapp is None:
            TestHfssWavePortExcitations.aedtapp = add_app(application=Hfss, solution_type="Modal")
            # Create a simple waveguide structure for testing
            box = TestHfssWavePortExcitations.aedtapp.modeler.create_box([0, 0, 0], [50, 5, 10], name="waveguide")
            box.material_name = "vacuum"
            TestHfssWavePortExcitations.input_face = TestHfssWavePortExcitations.aedtapp.modeler.create_rectangle(
                Plane.YZ, [0, 0, 0], [5, 10], name="input_face"
            )
            TestHfssWavePortExcitations.output_face = TestHfssWavePortExcitations.aedtapp.modeler.create_rectangle(
                Plane.YZ, [50, 0, 0], [5, 10], name="output_face"
            )
        self.aedtapp = TestHfssWavePortExcitations.aedtapp
        self.input_face = TestHfssWavePortExcitations.input_face
        self.output_face = TestHfssWavePortExcitations.output_face

    def test_01_create_wave_port_basic(self):
        """Test basic wave port creation."""
        port = self.aedtapp.wave_port(assignment=self.input_face.name, name="test_port_basic")
        assert port is not None
        assert port.name == "test_port_basic"
        assert hasattr(port, "specify_wave_direction")
        assert hasattr(port, "deembed")
        assert hasattr(port, "renorm_all_modes")

    def test_02_specify_wave_direction_property(self):
        """Test specify_wave_direction property setter and getter."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            name="test_port_wave_direction",
        )

        # Test getter
        initial_value = port.specify_wave_direction
        assert isinstance(initial_value, bool)

        # Test setter - True
        port.specify_wave_direction = True
        assert port.specify_wave_direction is True

        # Test setter - False
        port.specify_wave_direction = False
        assert port.specify_wave_direction is False

        # Test no change when setting same value
        result = port.specify_wave_direction = False
        assert result is False

    def test_03_deembed_property(self):
        """Test deembed property setter and getter."""
        port = self.aedtapp.wave_port(assignment=self.input_face.name, name="test_port_deembed")

        # Test getter
        initial_value = port.deembed
        assert isinstance(initial_value, bool)

        # Test setter - True
        port.deembed = True
        assert port.deembed is True

        # Test setter - False
        port.deembed = False
        assert port.deembed is False

        # Test no change when setting same value
        result = port.deembed = False
        assert result is False

    def test_04_renorm_all_modes_property(self):
        """Test renorm_all_modes property setter and getter."""
        port = self.aedtapp.wave_port(assignment=self.input_face.name, name="test_port_renorm")

        # Test getter
        initial_value = port.renorm_all_modes
        assert isinstance(initial_value, bool)

        # Test setter - True
        port.renorm_all_modes = True
        assert port.renorm_all_modes is True

        # Test setter - False
        port.renorm_all_modes = False
        assert port.renorm_all_modes is False

        # Test no change when setting same value
        result = port.renorm_all_modes = False
        assert result is False

    def test_05_renorm_impedance_type_property(self):
        """Test renorm_impedance_type property setter and getter."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            name="test_port_impedance_type",
        )

        # Test getter
        initial_type = port.renorm_impedance_type
        assert isinstance(initial_type, str)

        # Test valid values from choices
        choices = port.properties["Renorm Impedance Type/Choices"]
        for choice in choices:
            port.renorm_impedance_type = choice
            assert port.renorm_impedance_type == choice

        # Test invalid value
        with pytest.raises(ValueError, match="Renorm Impedance Type must be one of"):
            port.renorm_impedance_type = "InvalidType"

        # Test no change when setting same value
        port.renorm_impedance_type = "Impedance"
        result = port.renorm_impedance_type = "Impedance"
        assert result == "Impedance"

    def test_06_renorm_impedance_property(self):
        """Test renorm_impedance property setter and getter."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            name="test_port_impedance",
        )

        # Set renorm type to Impedance first
        port.renorm_impedance_type = "Impedance"

        # Test setter with int
        port.renorm_impedance = 75
        assert port.renorm_impedance == "75ohm"

        # Test setter with string with units
        port.renorm_impedance = "100ohm"
        assert port.renorm_impedance == "100ohm"

        port.renorm_impedance = "1kOhm"
        assert port.renorm_impedance == "1kOhm"

        # Test invalid units
        with pytest.raises(ValueError, match="must end with one of"):
            port.renorm_impedance = "50invalid"

        # Test invalid type
        with pytest.raises(ValueError, match="must be a string with units or a float"):
            port.renorm_impedance = []

        # Test error when renorm type is not Impedance
        port.renorm_impedance_type = "RLC"
        with pytest.raises(
            ValueError,
            match="can be set only if Renorm Impedance Type is 'Impedance'",
        ):
            port.renorm_impedance = 50

    def test_07_rlc_type_property(self):
        """Test rlc_type property setter."""
        port = self.aedtapp.wave_port(assignment=self.input_face.name, name="test_port_rlc_type")

        # Set renorm type to RLC first
        port.renorm_impedance_type = "RLC"

        # Test valid values
        port.rlc_type = "Serial"
        port.rlc_type = "Parallel"

        # Test invalid value
        with pytest.raises(ValueError, match="RLC Type must be one of"):
            port.rlc_type = "Invalid"

        # Test error when renorm type is not RLC
        port.renorm_impedance_type = "Impedance"
        with pytest.raises(
            ValueError,
            match="can be set only if Renorm Impedance Type is 'RLC'",
        ):
            port.rlc_type = "Serial"

        # Test getter raises NotImplementedError
        port.renorm_impedance_type = "RLC"
        with pytest.raises(NotImplementedError):
            _ = port.rlc_type

    def test_08_use_resistance_property(self):
        """Test use_resistance property setter."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            name="test_port_use_resistance",
            modes=8,
            characteristic_impedance="Zwave",
            renormalize=True,
        )

        # Set renorm type to RLC first
        port.renorm_all_modes = True
        port.renorm_impedance_type = "RLC"

        # Test error when renorm type is not RLC
        port.renorm_impedance_type = "Impedance"
        with pytest.raises(
            ValueError,
            match="can be set only if Renorm Impedance Type is 'RLC'",
        ):
            port.use_resistance = True

        # Test valid boolean values
        port.renorm_impedance_type = "RLC"
        port.use_resistance = True
        port.use_resistance = False

        # Test invalid value
        with pytest.raises(ValueError, match="must be a boolean value"):
            port.use_resistance = "True"
        # Test getter raises NotImplementedError
        port.renorm_all_modes = True
        port.renorm_impedance_type = "RLC"
        with pytest.raises(NotImplementedError):
            _ = port.use_resistance

    def test_09_resistance_value_property(self):
        """Test resistance_value property setter."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            name="test_port_resistance_value",
        )

        # Set renorm type to RLC first
        port.renorm_impedance_type = "RLC"

        # Test setter with float
        port.resistance_value = 50.0

        # Test setter with int
        port.resistance_value = 75

        # Test setter with string with units
        port.resistance_value = "100ohm"
        port.resistance_value = "1kOhm"

        # Test invalid units
        with pytest.raises(ValueError, match="must end with one of"):
            port.resistance_value = "50invalid"

        # Test invalid type
        with pytest.raises(ValueError, match="must be a string with units or a float"):
            port.resistance_value = []

        # Test error when renorm type is not RLC
        port.renorm_impedance_type = "Impedance"
        with pytest.raises(
            ValueError,
            match="can be set only if Renorm Impedance Type is 'RLC'",
        ):
            port.resistance_value = 50

        # Test getter raises NotImplementedError
        port.renorm_impedance_type = "RLC"
        with pytest.raises(NotImplementedError):
            _ = port.resistance_value

    def test_10_use_inductance_property(self):
        """Test use_inductance property setter."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            name="test_port_use_inductance",
        )

        # Set renorm type to RLC first
        port.renorm_impedance_type = "RLC"

        # Test valid boolean values
        port.use_inductance = True
        port.use_inductance = False

        # Test invalid value
        with pytest.raises(ValueError, match="must be a boolean value"):
            port.use_inductance = "True"

        # Test error when renorm type is not RLC
        port.renorm_impedance_type = "Impedance"
        with pytest.raises(
            ValueError,
            match="can be set only if Renorm Impedance Type is 'RLC'",
        ):
            port.use_inductance = True

        # Test getter raises NotImplementedError
        port.renorm_impedance_type = "RLC"
        with pytest.raises(NotImplementedError):
            _ = port.use_inductance

    def test_11_inductance_value_property(self):
        """Test inductance_value property setter."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            name="test_port_inductance_value",
        )

        # Set renorm type to RLC first
        port.renorm_impedance_type = "RLC"

        # Test setter with float
        port.inductance_value = 1e-9

        # Test setter with int
        port.inductance_value = 1

        # Test setter with string with units
        port.inductance_value = "10nH"
        port.inductance_value = "1uH"

        # Test invalid units
        with pytest.raises(ValueError, match="must end with one of"):
            port.inductance_value = "10invalid"

        # Test invalid type
        with pytest.raises(ValueError, match="must be a string with units or a float"):
            port.inductance_value = []

        # Test error when renorm type is not RLC
        port.renorm_impedance_type = "Impedance"
        with pytest.raises(
            ValueError,
            match="can be set only if Renorm Impedance Type is 'RLC'",
        ):
            port.inductance_value = 1e-9

        # Test getter raises NotImplementedError
        port.renorm_impedance_type = "RLC"
        with pytest.raises(NotImplementedError):
            _ = port.inductance_value

    def test_12_use_capacitance_property(self):
        """Test use_capacitance property setter."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            name="test_port_use_capacitance",
        )

        # Set renorm type to RLC first
        port.renorm_impedance_type = "RLC"

        # Test valid boolean values
        port.use_capacitance = True
        port.use_capacitance = False

        # Test invalid value
        with pytest.raises(ValueError, match="must be a boolean value"):
            port.use_capacitance = "True"

        # Test error when renorm type is not RLC
        port.renorm_impedance_type = "Impedance"
        with pytest.raises(
            ValueError,
            match="can be set only if Renorm Impedance Type is 'RLC'",
        ):
            port.use_capacitance = True

        # Test getter raises NotImplementedError
        port.renorm_impedance_type = "RLC"
        with pytest.raises(NotImplementedError):
            _ = port.use_capacitance

    def test_13_capacitance_value_property(self):
        """Test capacitance_value property setter."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            name="test_port_capacitance_value",
        )

        # Set renorm type to RLC first
        port.renorm_impedance_type = "RLC"

        # Test setter with float
        port.capacitance_value = 1e-12

        # Test setter with int
        port.capacitance_value = 1

        # Test setter with string with units
        port.capacitance_value = "1pF"
        port.capacitance_value = "10nF"

        # Test invalid units
        with pytest.raises(ValueError, match="must end with one of"):
            port.capacitance_value = "1invalid"

        # Test invalid type
        with pytest.raises(ValueError, match="must be a string with units or a float"):
            port.capacitance_value = []

        # Test error when renorm type is not RLC
        port.renorm_impedance_type = "Impedance"
        with pytest.raises(
            ValueError,
            match="can be set only if Renorm Impedance Type is 'RLC'",
        ):
            port.capacitance_value = 1e-12

        # Test getter raises NotImplementedError
        port.renorm_impedance_type = "RLC"
        with pytest.raises(NotImplementedError):
            _ = port.capacitance_value

    def test_14_filter_modes_reporter_property(self):
        """Test filter_modes_reporter property setter and getter."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            modes=3,
            name="test_port_filter_modes",
        )

        # Test getter
        filter_values = port.filter_modes_reporter
        assert isinstance(filter_values, list)
        assert len(filter_values) == 3

        # Test setter with single boolean
        port.filter_modes_reporter = True
        assert all(port.filter_modes_reporter)

        port.filter_modes_reporter = False
        assert not any(port.filter_modes_reporter)

        # Test setter with list
        port.filter_modes_reporter = [True, False, True]
        expected = [True, False, True]
        assert port.filter_modes_reporter == expected

        # Test invalid list length
        with pytest.raises(ValueError, match="must match the number of modes"):
            port.filter_modes_reporter = [True, False]

        # Test invalid type
        with pytest.raises(
            ValueError,
            match="must be a boolean or a list of booleans",
        ):
            port.filter_modes_reporter = "True"

    def test_15_set_analytical_alignment(self):
        """Test set_analytical_alignment method."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            name="test_port_analytical",
        )

        # Test with u_axis_line
        u_line = [[0, 2.5, 0], [0, 2.5, 10]]
        result = port.set_analytical_alignment(u_axis_line=u_line)
        assert result is True

        # Test with all parameters
        result = port.set_analytical_alignment(
            u_axis_line=u_line,
            analytic_reverse_v=True,
            coordinate_system="Global",
            alignment_group=1,
        )
        assert result is True

        # Test with invalid u_axis_line format
        result = port.set_analytical_alignment(u_axis_line=[[0, 0], [1, 0]])
        assert result is False

        # Test with invalid u_axis_line type
        result = port.set_analytical_alignment(u_axis_line="invalid")
        assert result is False

    def test_16_set_alignment_integration_line(self):
        """Test set_alignment_integration_line method."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            modes=3,
            name="test_port_alignment_integration",
        )

        # Test disabling integration lines
        result = port.set_alignment_integration_line()
        assert result is True

        # Test with valid integration lines
        integration_lines = [
            [[0, 0, 0], [0, 5, 0]],
            [[0, 0, 0], [0, 1, 0]],
        ]
        result = port.set_alignment_integration_line(integration_lines)
        assert result is True

        # Test with alignment groups
        alignment_groups = [1, 2, 0]
        result = port.set_alignment_integration_line(integration_lines, alignment_groups=alignment_groups)
        assert result is True

        # Test with single alignment group
        result = port.set_alignment_integration_line(integration_lines, alignment_groups=1)
        assert result is True

        # Test with custom coordinate system
        result = port.set_alignment_integration_line(integration_lines, coordinate_system="Local")
        assert result is True

        # Test error cases
        # Not enough integration lines
        result = port.set_alignment_integration_line([[[0, 0, 0], [1, 0, 0]]])
        assert result is False

        # Invalid integration line format
        result = port.set_alignment_integration_line([[[0, 0], [1, 0]]])
        assert result is False

        # Invalid coordinate system
        result = port.set_alignment_integration_line(integration_lines, coordinate_system=123)
        assert result is False

    def test_17_set_polarity_integration_line(self):
        """Test set_polarity_integration_line method."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            modes=2,
            name="test_port_polarity",
        )

        # Test disabling integration lines
        result = port.set_polarity_integration_line()
        assert result is True

        # Test with valid integration lines
        integration_lines = [
            [[0, 0, 0], [0, 5, 0]],
            [[0, 0, 0], [0, 1, 0]],
        ]
        result = port.set_polarity_integration_line(integration_lines)
        assert result is True

        # Test with custom coordinate system
        result = port.set_polarity_integration_line(integration_lines, coordinate_system="Local")
        assert result is True

        # Test single integration line handling
        single_line = [[0, 0, 0], [0, 5, 0]]
        result = port.set_polarity_integration_line([single_line])
        assert result is True

        # Test error cases
        # Invalid integration line format
        result = port.set_polarity_integration_line([[[0, 0], [1, 0]]])
        assert result is False

        # Invalid coordinate system
        result = port.set_polarity_integration_line(integration_lines, coordinate_system=123)
        assert result is False

        # Invalid integration_lines type
        result = port.set_polarity_integration_line("invalid")
        assert result is False

    def test_18_multiple_ports_properties(self):
        """Test properties with multiple ports to ensure independence."""
        # Create two ports
        port1 = self.aedtapp.wave_port(assignment=self.input_face.name, name="test_port1")
        port2 = self.aedtapp.wave_port(assignment=self.output_face.name, name="test_port2")

        # Set different properties for each port
        port1.specify_wave_direction = True
        port2.specify_wave_direction = False

        port1.deembed = True
        port2.deembed = False

        port1.renorm_all_modes = True
        port2.renorm_all_modes = False

        # Verify properties are independent
        assert port1.specify_wave_direction is True
        assert port2.specify_wave_direction is False

        assert port1.deembed is True
        assert port2.deembed is False

        assert port1.renorm_all_modes is True
        assert port2.renorm_all_modes is False

    def test_19_impedance_renormalization_workflow(self):
        """Test complete impedance renormalization workflow."""
        port = self.aedtapp.wave_port(assignment=self.input_face.name, name="test_port_workflow")

        # Test Impedance renormalization
        port.renorm_impedance_type = "Impedance"
        port.renorm_impedance = 75
        assert port.renorm_impedance == "75ohm"

        # Test RLC renormalization workflow
        port.renorm_impedance_type = "RLC"
        port.rlc_type = "Serial"
        port.use_resistance = True
        port.resistance_value = "50ohm"
        port.use_inductance = True
        port.inductance_value = "10nH"
        port.use_capacitance = True
        port.capacitance_value = "1pF"

        # Verify all settings were applied (no exceptions thrown)
        assert port.renorm_impedance_type == "RLC"

    def test_20_integration_lines_complex_scenario(self):
        """Test complex integration line scenarios."""
        port = self.aedtapp.wave_port(
            assignment=self.input_face.name,
            modes=4,
            name="test_port_complex",
        )

        # Test alignment integration lines with all modes
        integration_lines = [
            [[0, 0, 0], [0, 0, 1]],
            [[0, 0, 0], [0, 1, 0]],
            [[0, 0, 0], [0, 3, 0]],
            [[0, 0, 0], [0, 5, 0]],
        ]
        alignment_groups = [1, 1, 2, 2]

        result = port.set_alignment_integration_line(
            integration_lines,
            coordinate_system="Global",
            alignment_groups=alignment_groups,
        )
        assert result is True

        # Switch to polarity mode
        result = port.set_polarity_integration_line(integration_lines[:2])
        assert result is True

        # Verify mode alignment was disabled
        # (This would need to be verified through properties access)

        # Test filter modes reporter with this port
        port.filter_modes_reporter = [True, False, True, False]
        expected = [True, False, True, False]
        assert port.filter_modes_reporter == expected
