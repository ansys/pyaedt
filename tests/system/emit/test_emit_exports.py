# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import os
import sys
import tempfile

import pytest

from ansys.aedt.core.generic.general_methods import is_linux
from tests import TESTS_EMIT_PATH
from tests.conftest import DESKTOP_VERSION

import matplotlib.pyplot as plt

if ((3, 8) <= sys.version_info[0:2] <= (3, 11) and DESKTOP_VERSION < "2025.1") or (
    (3, 10) <= sys.version_info[0:2] <= (3, 12) and DESKTOP_VERSION > "2024.2"
):
    from ansys.aedt.core import Emit
    from ansys.aedt.core.emit_core.emit_constants import TxRxMode
    from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
    from ansys.aedt.core.emit_core.nodes.generated import AntennaNode
    from ansys.aedt.core.emit_core.nodes.generated import Band
    from ansys.aedt.core.emit_core.nodes.generated import Amplifier
    from ansys.aedt.core.emit_core.nodes.generated import Cable
    from ansys.aedt.core.emit_core.nodes.generated import Circulator
    from ansys.aedt.core.emit_core.nodes.generated import CouplingsNode
    from ansys.aedt.core.emit_core.nodes.generated import Filter
    from ansys.aedt.core.emit_core.nodes.generated import Isolator
    from ansys.aedt.core.emit_core.nodes.generated import Multiplexer
    from ansys.aedt.core.emit_core.nodes.generated import MultiplexerBand
    from ansys.aedt.core.emit_core.nodes.generated import PowerDivider
    from ansys.aedt.core.emit_core.nodes.generated import PropagationLossCouplingNode
    from ansys.aedt.core.emit_core.nodes.generated import RadioNode
    from ansys.aedt.core.emit_core.nodes.generated import RxMixerProductNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSaturationNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSelectivityNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSpurNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSusceptibilityProfNode
    from ansys.aedt.core.emit_core.nodes.generated import Terminator
    from ansys.aedt.core.emit_core.nodes.generated import TR_Switch
    from ansys.aedt.core.emit_core.nodes.generated import TwoRayPathLossCouplingNode
    from ansys.aedt.core.emit_core.nodes.generated import TxBbEmissionNode
    from ansys.aedt.core.emit_core.nodes.generated import TxHarmonicNode
    from ansys.aedt.core.emit_core.nodes.generated import TxNbEmissionNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpectralProfNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpurNode
    from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
    from ansys.aedt.core.emit_core.results.revision import Revision
    from ansys.aedt.core.emit_core.emit_schematic import EmitSchematic

TEST_SUBFOLDER = TESTS_EMIT_PATH / "example_models/TEMIT"


@pytest.fixture
def emit_app(add_app):
    app = add_app(application=Emit)
    yield app
    app.close_project(app.project_name, save=False)


def _setup_two_radio_project(emit_app):
    """Create a project with two radios and antennas, run analysis, and return the revision."""
    radio1, ant1 = emit_app.schematic.create_radio_antenna("New Radio")
    radio2, ant2 = emit_app.schematic.create_radio_antenna("New Radio")

    ant1.position_defined = True
    ant1.position = "0 0 5"
    
    ant2.position_defined = True
    ant2.position = "10 0 10"

    revision = emit_app.results.analyze()
    return revision


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="export_to_csv requires 2027 R1 or later.")
class TestEmitExports:
    """Tests for the export_to_csv method on various EMIT node types."""

    def test_cable_export(self, emit_app):
        """Test export_to_csv on a Cable node (SelectedInputPort|SelectedOutputPort keys)."""
        cable_node: Cable = emit_app.schematic.create_component("Cable", name="Cable")
        assert cable_node is not None

        # configure some parameters
        cable_node.cable_type = Cable.CableTypeOption.CONSTANT_LOSS
        cable_node.length = "2.0"
        cable_node.loss_per_length = "0.5"
        data = cable_node.export_to_csv("")
        assert data is not None
        assert len(data) > 0, "Inline ExportTraceData should return non-empty CSV data."

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "cable_export.csv")
            cable_node.export_to_csv(csv_path)
            assert os.path.isfile(csv_path)
            with open(csv_path, "r") as f:
                content = f.read()
            lines = [l for l in content.strip().split("\n") if l.strip()]
            assert len(lines) > 0, "Cable CSV export should contain data rows."

        # test cable plot
        fig = cable_node.plot()
        assert fig is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "cable_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path), "Cable plot figure was not saved."
            assert os.path.getsize(png_path) > 0, "Cable plot file is empty."

    def test_filter_export(self, emit_app):
        """Test export_to_csv on a Filter node (SelectedInputPort|SelectedOutputPort keys)."""
        filter_node: Filter = emit_app.schematic.create_component("Band Pass", name="BPF")
        assert filter_node is not None

        # configure some parameters
        filter_node.insertion_loss = "1.0"
        filter_node.stop_band_attenuation = "60.0"
        filter_node.bp_lower_stop_band_frequency = 100e6
        filter_node.bp_lower_cutoff_frequency = 200e6
        filter_node.bp_higher_cutoff_frequency = 300e6
        filter_node.bp_higher_stop_band_frequency = 400e6

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "filter_export.csv")
            filter_node.export_to_csv(csv_path)
            assert os.path.isfile(csv_path)
            with open(csv_path, "r") as f:
                content = f.read()
            lines = [l for l in content.strip().split("\n") if l.strip()]
            assert len(lines) > 0, "Filter CSV export should contain data rows."

        # Change the filter to a tunable filter and test export
        filter_node.filter_type = Filter.FilterTypeOption.TUNABLE_BANDPASS
        filter_node.lowest_tuned_frequency = 100e6
        filter_node.highest_tuned_frequency = 400e6
        filter_node.percent_bandwidth = 20.0
        filter_node.shape_factor = 3.0
        data = filter_node.export_to_csv(channel_freq=200e6)
        assert data is not None
        assert len(data) > 0, "Tunable Filter CSV export should return non-empty CSV data."

        fig = filter_node.plot(channel_freq=200e6)
        assert fig is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "filter_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path), "Filter plot figure was not saved."
            assert os.path.getsize(png_path) > 0, "Filter plot file is empty."

    def test_amplifier_export(self, emit_app):
        """Test export_to_csv on an Amplifier node."""
        amp_node: Amplifier = emit_app.schematic.create_component("Amplifier", name="Amp1")
        assert amp_node is not None

        amp_node.gain = "20.0"
        amp_node.noise_figure = "3.0"

        data = amp_node.export_to_csv("")
        assert data is not None
        assert len(data) > 0, "Amplifier inline CSV export should return non-empty data."

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "amplifier_export.csv")
            amp_node.export_to_csv(csv_path)
            assert os.path.isfile(csv_path)
            with open(csv_path, "r") as f:
                content = f.read()
            lines = [l for l in content.strip().split("\n") if l.strip()]
            assert len(lines) > 0, "Amplifier CSV export should contain data rows."

        # test amplifier plot props
        amp_props = Amplifier.AmplifierPlotProps(90e6, -10, 10e3, 110e6, -10, 10e3, -170.0)
        data2 = amp_node.export_to_csv("", amp_props)
        assert data2 is not None
        assert len(data2) > 0, "Amplifier CSV export with plot props should return non-empty data."

        fig = amp_node.plot(amp_props)
        assert fig is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "amplifier_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path), "Amplifier plot figure was not saved."
            assert os.path.getsize(png_path) > 0, "Amplifier plot file is empty."

    def test_circulator_export(self, emit_app):
        """Test export_to_csv on a Circulator node."""
        circ_node: Circulator = emit_app.schematic.create_component("Circulator", name="Circ1")
        assert circ_node is not None

        circ_node.insertion_loss = "0.5"
        circ_node.isolation = "20.0"

        data = circ_node.export_to_csv(ports="1|2")
        assert data is not None
        assert len(data) > 0, "Circulator inline CSV export should return non-empty data."

        # try to export ports 1 and 3, should fail
        data = None
        with pytest.raises(Exception):
            data = circ_node.export_to_csv(ports="1|3")
            
        assert data is None
        err_msg = emit_app._odesktop.GetMessages("", "", 2)[0]
        assert "The reverse isolation is infinite." in err_msg, "Expected error message to contain 'The reverse isolation is infinite.'"
        emit_app._odesktop.ClearMessages("", "", 2, 2)

        # set reverse isolation to a finite value and try again
        circ_node.finite_reverse_isolation = True
        circ_node.reverse_isolation = "20.0"
        data = circ_node.export_to_csv(ports="1|3")
        assert data is not None
        assert len(data) > 0, "Circulator CSV export should return non-empty data."

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "circulator_export.csv")
            circ_node.export_to_csv(csv_path)
            assert os.path.isfile(csv_path)
            with open(csv_path, "r") as f:
                content = f.read()
            lines = [l for l in content.strip().split("\n") if l.strip()]
            assert len(lines) > 0, "Circulator CSV export should contain data rows."

        fig = circ_node.plot()
        assert fig is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "circulator_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path), "Circulator plot figure was not saved."
            assert os.path.getsize(png_path) > 0, "Circulator plot file is empty."

    def test_isolator_export(self, emit_app):
        """Test export_to_csv on an Isolator node."""
        iso_node: Isolator = emit_app.schematic.create_component("Isolator", name="Iso1")
        assert iso_node is not None

        iso_node.insertion_loss = "0.5"
        iso_node.isolation = "25.0"

        data = iso_node.export_to_csv(ports="1|2")
        assert data is not None
        assert len(data) > 0, "Isolator inline CSV export should return non-empty data."

        # reverse direction should fail when reverse isolation is infinite
        data = None
        with pytest.raises(Exception):
            data = iso_node.export_to_csv(ports="2|1")

        assert data is None
        err_msg = emit_app._odesktop.GetMessages("", "", 2)[0]
        assert "reverse isolation is infinite" in err_msg, "Expected reverse isolation error message."
        emit_app._odesktop.ClearMessages("", "", 2, 2)

        # enable finite reverse isolation and retry
        iso_node.finite_reverse_isolation = True
        iso_node.reverse_isolation = "20.0"
        data = iso_node.export_to_csv(ports="2|1")
        assert data is not None
        assert len(data) > 0, "Isolator reverse direction CSV export should return non-empty data."

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "isolator_export.csv")
            iso_node.export_to_csv(csv_path)
            assert os.path.isfile(csv_path)
            with open(csv_path, "r") as f:
                content = f.read()
            lines = [l for l in content.strip().split("\n") if l.strip()]
            assert len(lines) > 0, "Isolator CSV export should contain data rows."

        fig = iso_node.plot()
        assert fig is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "isolator_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path), "Isolator plot figure was not saved."
            assert os.path.getsize(png_path) > 0, "Isolator plot file is empty."

    def test_power_divider_export(self, emit_app):
        """Test export_to_csv on a PowerDivider node."""
        div_node: PowerDivider = emit_app.schematic.create_component("Divider", name="Div1")
        assert div_node is not None

        div_node.insertion_loss = "3.5"

        data = div_node.export_to_csv(ports="1|2")
        assert data is not None
        assert len(data) > 0, "PowerDivider inline CSV export should return non-empty data."

        # output-to-output direction should fail when isolation is infinite
        data = None
        with pytest.raises(Exception):
            data = div_node.export_to_csv(ports="2|3")

        assert data is None
        err_msg = emit_app._odesktop.GetMessages("", "", 2)[0]
        assert "isolation between output ports is infinite" in err_msg, "Expected isolation error message."
        emit_app._odesktop.ClearMessages("", "", 2, 2)

        # enable finite isolation and retry
        div_node.finite_isolation = True
        div_node.isolation = "20.0"
        data = div_node.export_to_csv(ports="2|3")
        assert data is not None
        assert len(data) > 0, "PowerDivider port 2-3 CSV export should return non-empty data."

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "divider_export.csv")
            div_node.export_to_csv(csv_path)
            assert os.path.isfile(csv_path)
            with open(csv_path, "r") as f:
                content = f.read()
            lines = [l for l in content.strip().split("\n") if l.strip()]
            assert len(lines) > 0, "PowerDivider CSV export should contain data rows."

        fig = div_node.plot()
        assert fig is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "divider_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path), "PowerDivider plot figure was not saved."
            assert os.path.getsize(png_path) > 0, "PowerDivider plot file is empty."

    def test_tr_switch_export(self, emit_app):
        """Test export_to_csv on a TR Switch node."""
        sw_node: TR_Switch = emit_app.schematic.create_component("TR Switch", name="SW1")
        assert sw_node is not None

        sw_node.insertion_loss = "1.0"

        data = sw_node.export_to_csv(ports="1|2")
        assert data is not None
        assert len(data) > 0, "TR Switch inline CSV export should return non-empty data."

        # reverse direction should fail when isolation is infinite
        sw_node.finite_isolation = False
        data = None
        with pytest.raises(Exception):
            data = sw_node.export_to_csv(ports="2|1")

        assert data is None
        err_msg = emit_app._odesktop.GetMessages("", "", 2)[0]
        assert "isolation is infinite" in err_msg, "Expected isolation error message."
        emit_app._odesktop.ClearMessages("", "", 2, 2)

        # enable finite isolation and retry
        sw_node.finite_isolation = True
        sw_node.isolation = "30.0"
        data = sw_node.export_to_csv(ports="2|1")
        assert data is not None
        assert len(data) > 0, "TR Switch reverse direction CSV export should return non-empty data."

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "tr_switch_export.csv")
            sw_node.export_to_csv(csv_path)
            assert os.path.isfile(csv_path)
            with open(csv_path, "r") as f:
                content = f.read()
            lines = [l for l in content.strip().split("\n") if l.strip()]
            assert len(lines) > 0, "TR Switch CSV export should contain data rows."

        fig = sw_node.plot()
        assert fig is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "tr_switch_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path), "TR Switch plot figure was not saved."
            assert os.path.getsize(png_path) > 0, "TR Switch plot file is empty."

    def test_terminator_export(self, emit_app):
        """Test export_to_csv on a Terminator node."""
        term_node: Terminator = emit_app.schematic.create_component("Terminator", name="Term1")
        assert term_node is not None

        data = term_node.export_to_csv("")
        assert data is not None
        assert len(data) > 0, "Terminator inline CSV export should return non-empty data."

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "terminator_export.csv")
            term_node.export_to_csv(csv_path)
            assert os.path.isfile(csv_path)
            with open(csv_path, "r") as f:
                content = f.read()
            lines = [l for l in content.strip().split("\n") if l.strip()]
            assert len(lines) > 0, "Terminator CSV export should contain data rows."

        fig = term_node.plot()
        assert fig is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "terminator_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path), "Terminator plot figure was not saved."
            assert os.path.getsize(png_path) > 0, "Terminator plot file is empty."

    def test_multiplexer_export(self, emit_app):
        """Test export_to_csv on a Multiplexer node."""
        mux_node: Multiplexer = emit_app.schematic.create_component("3 Port", name="Mux1")
        assert mux_node is not None

        mux_node.insertion_loss = "1.0"

        data = mux_node.export_to_csv(ports="1|2")
        assert data is not None
        assert len(data) > 0, "Multiplexer port 1-2 CSV export should return non-empty data."

        # test a different port combination
        data = mux_node.export_to_csv(ports="1|3")
        assert data is not None
        assert len(data) > 0, "Multiplexer port 1-3 CSV export should return non-empty data."

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "multiplexer_export.csv")
            mux_node.export_to_csv(csv_path)
            assert os.path.isfile(csv_path)
            with open(csv_path, "r") as f:
                content = f.read()
            lines = [l for l in content.strip().split("\n") if l.strip()]
            assert len(lines) > 0, "Multiplexer CSV export should contain data rows."

        # test multiplexer band export
        mb1 = mux_node.children[0]
        assert mb1 is not None
        data = mb1.export_to_csv("")
        assert data is not None
        assert len(data) > 0, "MultiplexerBand CSV export should return non-empty data."

        mb2 = mux_node.children[1]
        assert mb2 is not None
        data = mb2.export_to_csv("")
        assert data is not None
        assert len(data) > 0, "MultiplexerBand CSV export should return non-empty data."

        fig = mux_node.plot()
        assert fig is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "multiplexer_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path), "Multiplexer plot figure was not saved."
            assert os.path.getsize(png_path) > 0, "Multiplexer plot file is empty."

    def test_coupling_node_export(self, emit_app):
        """Test export_to_csv on a parametric coupling node (SelectedRxAntenna|SelectedTxAntenna)."""
        revision = _setup_two_radio_project(emit_app)

        # test parametric coupling node export
        coupling_data: CouplingsNode = revision.get_coupling_data_node()
        assert coupling_data is not None

        scene_node = revision.get_scene_node()
        ant_children = scene_node.children
        ant_short_names = [c.name for c in ant_children if isinstance(c, AntennaNode)]  
        ant_full_names = [c._full_node_name for c in ant_children if isinstance(c, AntennaNode)]
        assert len(ant_short_names) >= 2, "Expected at least 2 antennas in the scene."

        data = coupling_data.export_to_csv("", ports=f"{ant_full_names[0]}|{ant_full_names[1]}")
        assert data is not None
        assert len(data) > 0, "Coupling CSV export should return non-empty data."

        data2 = coupling_data.export_to_csv("", antennas=(ant_children[0], ant_children[1]))
        assert data2 is not None
        assert len(data2) > 0, "Coupling CSV export should return non-empty data."
        assert data == data2, "Coupling CSV export should return the same data."    

        # test path loss coupling node export
        path_loss: PropagationLossCouplingNode = coupling_data._add_child_node("Path Loss Coupling")
        assert path_loss is not None
        path_loss.antenna_a = ant_short_names[0]
        path_loss.antenna_b = ant_short_names[1]

        data = path_loss.export_to_csv("", ports=f"{ant_short_names[0]}|{ant_short_names[1]}")
        assert data is not None
        assert len(data) > 0, "Path Loss Coupling CSV export should return non-empty data."

        data2 = path_loss.export_to_csv("", antennas=(ant_children[0], ant_children[1]))
        assert data2 is not None
        assert len(data2) > 0, "Path Loss Coupling CSV export should return non-empty data."
        assert data == data2, "Path Loss Coupling CSV export should return the same data."

        # test two ray path loss coupling node export
        two_ray_path_loss: TwoRayPathLossCouplingNode = coupling_data._add_child_node("Two Ray Path Loss Coupling")
        assert two_ray_path_loss is not None
        two_ray_path_loss.antenna_a = ant_short_names[0]
        two_ray_path_loss.antenna_b = ant_short_names[1]

        data = two_ray_path_loss.export_to_csv("", ports=f"{ant_short_names[0]}|{ant_short_names[1]}")
        assert data is not None
        assert len(data) > 0, "Two Ray Path Loss Coupling CSV export should return non-empty data."

        fig = coupling_data.plot(ports=f"{ant_full_names[0]}|{ant_full_names[1]}")
        assert fig is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "coupling_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path), "Coupling plot figure was not saved."
            assert os.path.getsize(png_path) > 0, "Coupling plot file is empty."

    def test_band_export(self, emit_app):
        """Test export_to_csv on a Band node."""
        radio: RadioNode = emit_app.schematic.create_component("New Radio")
        band: Band = radio.children[0]
        assert band is not None
        band.stop_frequency = 200e6
        
        data = band.export_to_csv("", channel_freq=150e6, channel_type=Band.ChannelType.TX)
        assert data is not None
        assert len(data) > 0, "Band CSV export should return non-empty data."

        data = band.export_to_csv("", channel_freq=150e6, channel_type=Band.ChannelType.RX)
        assert data is not None
        assert len(data) > 0, "Band CSV export should return non-empty data."

        fig = band.plot(channel_freq=150e6, channel_type=Band.ChannelType.TX)
        assert fig is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "band_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path), "Band plot figure was not saved."
            assert os.path.getsize(png_path) > 0, "Band plot file is empty."

        with tempfile.TemporaryDirectory() as export_dir:
            # --- Tx Spectral Profile ---
            tx_spec: TxSpectralProfNode = band.children[0]
            assert tx_spec is not None

            data = tx_spec.export_to_csv("", channel_freq=150e6)
            assert data is not None
            assert len(data) > 0, "Tx Spectral Profile CSV export should return non-empty data."

            fig = tx_spec.plot(channel_freq=150e6)
            assert fig is not None
            png_path = os.path.join(export_dir, "tx_spectral_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path) and os.path.getsize(png_path) > 0

            # --- Tx Broadband Emissions ---
            tx_bb: TxBbEmissionNode = tx_spec.add_tx_broadband_noise_profile()
            assert tx_bb is not None

            data = tx_bb.export_to_csv("")
            assert data is not None
            assert len(data) > 0, "Tx BB Emission CSV export should return non-empty data."

            fig = tx_bb.plot()
            assert fig is not None
            png_path = os.path.join(export_dir, "tx_bb_emission_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path) and os.path.getsize(png_path) > 0

            # --- Tx Harmonics ---
            tx_harm: TxHarmonicNode = tx_spec.add_custom_tx_harmonics()
            assert tx_harm is not None

            data = tx_harm.export_to_csv("")
            assert data is not None
            assert len(data) > 0, "Tx Harmonics CSV export should return non-empty data."

            fig = tx_harm.plot()
            assert fig is not None
            png_path = os.path.join(export_dir, "tx_harmonics_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path) and os.path.getsize(png_path) > 0

            # --- Tx Spurs ---
            tx_spur: TxSpurNode = tx_spec.add_spurious_emissions()
            assert tx_spur is not None

            data = tx_spur.export_to_csv("")
            assert data is not None
            assert len(data) > 0, "Tx Spurs CSV export should return non-empty data."

            fig = tx_spur.plot()
            assert fig is not None
            png_path = os.path.join(export_dir, "tx_spurs_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path) and os.path.getsize(png_path) > 0

            # --- Tx Narrowband Emissions ---
            tx_nb: TxNbEmissionNode = tx_spec.add_narrowband_emissions_mask()
            assert tx_nb is not None
            tx_nb.table_data = [(150e6, 0.0), (160e6, 0.5)]

            data = tx_nb.export_to_csv("")
            assert data is not None
            assert len(data) > 0, "Tx NB Emission CSV export should return non-empty data."

            fig = tx_nb.plot()
            assert fig is not None
            png_path = os.path.join(export_dir, "tx_nb_emission_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path) and os.path.getsize(png_path) > 0

            # --- Rx Susceptibility Profile ---
            rx_spec: RxSusceptibilityProfNode = band.children[1]
            assert rx_spec is not None

            data = rx_spec.export_to_csv("", channel_freq=150e6)
            assert data is not None
            assert len(data) > 0, "Rx Susceptibility Profile CSV export should return non-empty data."

            fig = rx_spec.plot(channel_freq=150e6)
            assert fig is not None
            png_path = os.path.join(export_dir, "rx_susceptibility_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path) and os.path.getsize(png_path) > 0

            # --- Rx Mixer Products ---
            rx_mixer: RxMixerProductNode = rx_spec.add_mixer_products()
            assert rx_mixer is not None

            data = rx_mixer.export_to_csv("")
            assert data is not None
            assert len(data) > 0, "Rx Mixer Products CSV export should return non-empty data."

            fig = rx_mixer.plot()
            assert fig is not None
            png_path = os.path.join(export_dir, "rx_mixer_products_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path) and os.path.getsize(png_path) > 0

            # --- Rx Saturation ---
            rx_sat: RxSaturationNode = rx_spec.add_rx_saturation()
            assert rx_sat is not None

            data = rx_sat.export_to_csv("")
            assert data is not None
            assert len(data) > 0, "Rx Saturation CSV export should return non-empty data."

            fig = rx_sat.plot()
            assert fig is not None
            png_path = os.path.join(export_dir, "rx_saturation_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path) and os.path.getsize(png_path) > 0

            # --- Rx Selectivity ---
            rx_sel: RxSelectivityNode = rx_spec.add_rx_selectivity()
            assert rx_sel is not None
            rx_sel.table_data = [(150e6, -90.0), (160e6, -70.5)]

            data = rx_sel.export_to_csv("")
            assert data is not None
            assert len(data) > 0, "Rx Selectivity CSV export should return non-empty data."

            fig = rx_sel.plot()
            assert fig is not None
            png_path = os.path.join(export_dir, "rx_selectivity_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path) and os.path.getsize(png_path) > 0

            # --- Rx Spurs ---
            rx_spur: RxSpurNode = rx_spec.add_spurious_responses()
            assert rx_spur is not None

            data = rx_spur.export_to_csv("")
            assert data is not None
            assert len(data) > 0, "Rx Spurs CSV export should return non-empty data."

            fig = rx_spur.plot()
            assert fig is not None
            png_path = os.path.join(export_dir, "rx_spurs_plot.png")
            fig.savefig(png_path)
            assert os.path.isfile(png_path) and os.path.getsize(png_path) > 0

