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

# -*- coding: utf-8 -*-
import os
import sys
import tempfile

import pytest

from tests.conftest import DESKTOP_VERSION

# Prior to 2025R1, the Emit API supported Python 3.8,3.9,3.10,3.11
# Starting with 2025R1, the Emit API supports Python 3.10,3.11,3.12
if ((3, 8) <= sys.version_info[0:2] <= (3, 11) and DESKTOP_VERSION < "2025.1") or (
    (3, 10) <= sys.version_info[0:2] <= (3, 12) and DESKTOP_VERSION > "2024.2"
):
    from ansys.aedt.core import Emit
    from ansys.aedt.core.emit_core.nodes.generated import CouplingsNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSaturationNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSusceptibilityProfNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpectralProfNode


@pytest.fixture
def emit_app(add_app):
    app = add_app(application=Emit)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(not DESKTOP_VERSION or DESKTOP_VERSION < "2027.1", reason="Regression test for defect 1442338.")
def test_defect_1442338_pyaedt_importcsvfile_should_be_csvfile_not_csv(emit_app) -> None:
    """Regression test for TFS defect 1442338.

    [PyAedt] import_csv_file should be 'CsvFile', not 'Csv'
    https://tfs.ansys.com:8443/tfs/ANSYS_Development/Portfolio/_workitems/edit/1442338

    Severity: Class 2 - Minor Problem
    """
    # Step 1: Add a radio
    radio = emit_app.schematic.create_component("New Radio")

    # Step 2: Navigate to the Rx Susceptibility Profile and add a Rx Saturation node
    rev = emit_app.results.analyze()
    radio_node = rev.get_component_node(radio.name)
    band = radio_node.children[0]
    rx_susceptibility = band.children[1]
    assert isinstance(rx_susceptibility, RxSusceptibilityProfNode)
    rx_saturation = rx_susceptibility.add_rx_saturation()
    assert isinstance(rx_saturation, RxSaturationNode)

    # Step 3: Create a temporary CSV file and import it via import_csv_file.
    # The defect was that import_type was "Csv" instead of "CsvFile", causing the API call to fail.
    csv_content = "1e9,-10\n2e9,-20\n"
    csv_path = os.path.join(tempfile.gettempdir(), "test_defect_1442338.csv")
    try:
        with open(csv_path, "w") as f:
            f.write(csv_content)
        imported_node = rx_saturation.import_csv_file(csv_path)
        assert imported_node is not None
        assert imported_node.table_data == [(1e9, -10.0), (2e9, -20.0)]
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)


@pytest.mark.skipif(not DESKTOP_VERSION or DESKTOP_VERSION < "2027.1", reason="Requires 2027 R1 or later.")
def test_import_csv_file_all_node_types(emit_app) -> None:
    """Verify import_csv_file works for every generated node class that supports it.

    Tests all 9 node types that define import_csv_file:
    - Rx: RxSaturationNode, RxSelectivityNode, RxMixerProductNode, RxSpurNode
    - Tx: TxHarmonicNode, TxNbEmissionNode, TxBbEmissionNode, TxSpurNode
    - Coupling: CustomCouplingNode
    """
    radio = emit_app.schematic.create_component("New Radio")
    rev = emit_app.results.analyze()
    radio_node = rev.get_component_node(radio.name)
    band = radio_node.children[0]

    # Rx susceptibility child nodes
    rx_susceptibility = band.children[1]
    assert isinstance(rx_susceptibility, RxSusceptibilityProfNode)
    rx_nodes = {
        "RxSaturationNode": rx_susceptibility.add_rx_saturation(),
        "RxSelectivityNode": rx_susceptibility.add_rx_selectivity(),
        "RxMixerProductNode": rx_susceptibility.add_mixer_products(),
        "RxSpurNode": rx_susceptibility.add_spurious_responses(),
    }

    # Tx spectral profile child nodes
    tx_spectral = band.children[0]
    assert isinstance(tx_spectral, TxSpectralProfNode)
    tx_nodes = {
        "TxHarmonicNode": tx_spectral.add_custom_tx_harmonics(),
        "TxNbEmissionNode": tx_spectral.add_narrowband_emissions_mask(),
        "TxBbEmissionNode": tx_spectral.add_tx_broadband_noise_profile(),
        "TxSpurNode": tx_spectral.add_spurious_emissions(),
    }

    # Custom coupling node
    couplings_node: CouplingsNode = rev.get_coupling_data_node()
    custom_coupling = couplings_node.add_custom_coupling()

    all_nodes = {**rx_nodes, **tx_nodes, "CustomCouplingNode": custom_coupling}

    # CSV data per node type, matching the column layout from each class's table_data docstring.
    # 2-column nodes: Frequency/Amplitude, Bandwidth/Attenuation, etc.
    # 3-column nodes: RxMixerProductNode, RxSpurNode, TxSpurNode
    csv_data = {
        # Frequency (1–100e9), Amplitude (-1000–1000)
        "RxSaturationNode": "1e9,-10\n2e9,-20\n",
        # Bandwidth (0–100e9), Attenuation (-200–1000)
        "RxSelectivityNode": "1e6,-3\n10e6,-20\n",
        # RF Harmonic Order (-100–100), LO Harmonic Order (1–100), Power (-1000–1000)
        "RxMixerProductNode": "1,1,-30\n2,1,-60\n",
        # Frequency MHz (expression), Bandwidth (>1), Power (-200–150)
        "RxSpurNode": "100,2,-50\n200,5,-80\n",
        # Harmonic (2–1000), Power (-1000–1000)
        "TxHarmonicNode": "2,-30\n3,-60\n",
        # Bandwidth or Frequency (1–100e9), Attenuation or Power (-1000–1000)
        "TxNbEmissionNode": "1e9,-10\n2e9,-20\n",
        # Frequency/Bandwidth/Offset (-100e9–100e9), Amplitude (-1000–200)
        "TxBbEmissionNode": "1e6,-100\n10e6,-120\n",
        # Frequency MHz (expression), Bandwidth (>1), Power (-200–150)
        "TxSpurNode": "100,2,-50\n200,5,-80\n",
        # Frequency (1–100e9), Value dB (-1000–0)
        "CustomCouplingNode": "1e9,-10\n2e9,-20\n",
    }

    csv_dir = tempfile.gettempdir()
    csv_paths = []
    try:
        for node_type_name, node in all_nodes.items():
            assert node is not None, f"Failed to create {node_type_name}"
            csv_path = os.path.join(csv_dir, f"test_import_{node_type_name}.csv")
            csv_paths.append(csv_path)
            with open(csv_path, "w") as f:
                f.write(csv_data[node_type_name])
            imported = node.import_csv_file(csv_path)
            assert imported is not None, f"import_csv_file returned None for {node_type_name}"
    finally:
        for p in csv_paths:
            if os.path.exists(p):
                os.remove(p)

@pytest.mark.skipif(not DESKTOP_VERSION or DESKTOP_VERSION < "2027.1", reason="Regression test for defect 1442777.")
def test_defect_1442777_csv_import_bounds_validation(emit_app) -> None:
    """Regression test for TFS defect 1442777.

    [Scripting] Unable to get node id after reopening a project with scripting
    https://tfs.ansys.com:8443/tfs/ANSYS_Development/Portfolio/_workitems/edit/1442777

    Severity: Class 2 - Minor Problem

    Verifies that:
    - Each of the 9 node types can successfully import a valid CSV file
    - Out-of-bounds values in each column raise an appropriate error
    """
    radio = emit_app.schematic.create_component("New Radio")
    rev = emit_app.results.analyze()
    radio_node = rev.get_component_node(radio.name)
    band = radio_node.children[0]

    rx_susceptibility = band.children[1]
    assert isinstance(rx_susceptibility, RxSusceptibilityProfNode)

    tx_spectral = band.children[0]
    assert isinstance(tx_spectral, TxSpectralProfNode)

    couplings_node: CouplingsNode = rev.get_coupling_data_node()

    def _write_csv(name, content):
        path = os.path.join(tempfile.gettempdir(), f"test_1442777_{name}.csv")
        with open(path, "w") as f:
            f.write(content)
        return path

    csv_paths = []

    def _assert_import_fails(node, csv_path):
        """Assert that importing the CSV raises an Exception."""
        with pytest.raises(Exception):
            node.import_csv_file(csv_path)

    try:
        # ---------------------------------------------------------------
        # RxSaturationNode: 2 cols - Frequency [1, 100e9], Amplitude [-1000, 1000]
        # ---------------------------------------------------------------
        rx_sat = rx_susceptibility.add_rx_saturation()
        assert isinstance(rx_sat, RxSaturationNode)

        # Valid data
        valid_csv = _write_csv("rx_sat_valid", "\n".join(
            [f"{f},{a}" for f, a in
             [(1, -500), (10, -200), (1e3, -100), (1e6, -50), (1e9, 0),
              (5e9, 100), (10e9, 200), (50e9, 500), (80e9, 800), (100e9, 1000)]]
        ))
        csv_paths.append(valid_csv)
        result = rx_sat.import_csv_file(valid_csv)
        assert result is not None

        # Frequency too low (< 1)
        bad_csv = _write_csv("rx_sat_freq_low", "0.5,-10\n1e9,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_sat, bad_csv)

        # Frequency too high (> 100e9)
        bad_csv = _write_csv("rx_sat_freq_high", "1e9,-10\n200e9,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_sat, bad_csv)

        # Amplitude too low (< -1000)
        bad_csv = _write_csv("rx_sat_amp_low", "1e9,-1001\n2e9,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_sat, bad_csv)

        # Amplitude too high (> 1000)
        bad_csv = _write_csv("rx_sat_amp_high", "1e9,1001\n2e9,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_sat, bad_csv)

        # ---------------------------------------------------------------
        # RxSelectivityNode: 2 cols - Bandwidth [channelBw, 100e9], Attenuation [-1000, 1000]
        # ---------------------------------------------------------------
        rx_sel = rx_susceptibility.add_rx_selectivity()
        assert isinstance(rx_sel, RxSelectivityNode)

        valid_csv = _write_csv("rx_sel_valid", "\n".join(
            [f"{bw},{att}" for bw, att in
             [(25e3, -3), (50e3, -6), (100e3, -10), (500e3, -20), (1e6, -30),
              (5e6, -40), (10e6, -50), (50e6, -60), (100e6, -70), (1e9, -80)]]
        ))
        csv_paths.append(valid_csv)
        result = rx_sel.import_csv_file(valid_csv)
        assert result is not None

        # Attenuation too low (< -1000)
        bad_csv = _write_csv("rx_sel_att_low", "1e6,-1001\n2e6,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_sel, bad_csv)

        # Attenuation too high (> 1000)
        bad_csv = _write_csv("rx_sel_att_high", "1e6,1001\n2e6,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_sel, bad_csv)

        # Bandwidth too high (> 100e9)
        bad_csv = _write_csv("rx_sel_bw_high", "200e9,-10\n1e6,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_sel, bad_csv)

        # ---------------------------------------------------------------
        # RxMixerProductNode: 3 cols - RF Order [-100, 100], LO Order [1, 100], Power [-1000, 1000]
        # ---------------------------------------------------------------
        rx_mixer = rx_susceptibility.add_mixer_products()
        assert isinstance(rx_mixer, RxMixerProductNode)

        valid_csv = _write_csv("rx_mixer_valid", "\n".join(
            [f"{rf},{lo},{p}" for rf, lo, p in
             [(-5, 1, -30), (-3, 2, -40), (-1, 1, -50), (0, 1, -60), (1, 1, -30),
              (2, 1, -60), (3, 2, -45), (5, 3, -55), (7, 1, -70), (10, 5, -80)]]
        ))
        csv_paths.append(valid_csv)
        result = rx_mixer.import_csv_file(valid_csv)
        assert result is not None

        # RF Order too low (< -100)
        bad_csv = _write_csv("rx_mixer_rf_low", "-101,1,-30\n2,1,-60\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_mixer, bad_csv)

        # RF Order too high (> 100)
        bad_csv = _write_csv("rx_mixer_rf_high", "101,1,-30\n2,1,-60\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_mixer, bad_csv)

        # LO Order too low (< 1)
        bad_csv = _write_csv("rx_mixer_lo_low", "1,0,-30\n2,1,-60\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_mixer, bad_csv)

        # LO Order too high (> 100)
        bad_csv = _write_csv("rx_mixer_lo_high", "1,101,-30\n2,1,-60\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_mixer, bad_csv)

        # Power too low (< -1000)
        bad_csv = _write_csv("rx_mixer_pow_low", "1,1,-1001\n2,1,-60\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_mixer, bad_csv)

        # Power too high (> 1000)
        bad_csv = _write_csv("rx_mixer_pow_high", "1,1,1001\n2,1,-60\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_mixer, bad_csv)

        # ---------------------------------------------------------------
        # TxHarmonicNode: 2 cols - Harmonic [2, 1000], Power [-1000, 1000]
        # ---------------------------------------------------------------
        tx_harm = tx_spectral.add_custom_tx_harmonics()
        assert isinstance(tx_harm, TxHarmonicNode)

        valid_csv = _write_csv("tx_harm_valid", "\n".join(
            [f"{h},{p}" for h, p in
             [(2, -10), (3, -20), (5, -30), (7, -40), (10, -50),
              (15, -60), (20, -70), (50, -80), (100, -90), (500, -100)]]
        ))
        csv_paths.append(valid_csv)
        result = tx_harm.import_csv_file(valid_csv)
        assert result is not None

        # Harmonic too low (< 2)
        bad_csv = _write_csv("tx_harm_order_low", "1,-30\n3,-60\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_harm, bad_csv)

        # Harmonic too high (> 1000)
        bad_csv = _write_csv("tx_harm_order_high", "1001,-30\n3,-60\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_harm, bad_csv)

        # Power too low (< -1000)
        bad_csv = _write_csv("tx_harm_pow_low", "2,-1001\n3,-60\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_harm, bad_csv)

        # Power too high (> 1000)
        bad_csv = _write_csv("tx_harm_pow_high", "2,1001\n3,-60\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_harm, bad_csv)

        # ---------------------------------------------------------------
        # TxNbEmissionNode: 2 cols - Frequency/Bandwidth, Attenuation [-1000, 1000]
        #   Absolute mode: freq range [-100e9, 100e9]
        #   Relative mode: min freq = BandNode channel_bandwidth (dynamic)
        # ---------------------------------------------------------------
        tx_nb = tx_spectral.add_narrowband_emissions_mask()
        assert isinstance(tx_nb, TxNbEmissionNode)

        # Use absolute mode for the valid import — default may be relative which
        # constrains min frequency to channel_bandwidth.
        tx_nb.narrowband_behavior = TxNbEmissionNode.NarrowbandBehaviorOption.ABSOLUTE_FREQS_AND_POWER
        valid_csv = _write_csv("tx_nb_valid", "\n".join(
            [f"{f},{a}" for f, a in
             [(1e3, -10), (5e3, -15), (1e4, -20), (5e4, -30), (1e5, -40),
              (5e5, -50), (1e6, -60), (5e6, -70), (1e7, -80), (1e8, -90)]]
        ))
        csv_paths.append(valid_csv)
        result = tx_nb.import_csv_file(valid_csv)
        assert result is not None

        # Frequency too high (> 100e9)
        bad_csv = _write_csv("tx_nb_freq_high", "200e9,-10\n1e6,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_nb, bad_csv)

        # Frequency too low in relative-bandwidth mode (< channel bandwidth)
        tx_nb.narrowband_behavior = TxNbEmissionNode.NarrowbandBehaviorOption.RELATIVE_FREQS_AND_ATTENUATION
        ch_bw = band.channel_bandwidth
        bad_csv = _write_csv("tx_nb_freq_low_rel", f"{ch_bw * 0.5},-10\n{ch_bw * 2},-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_nb, bad_csv)
        tx_nb.narrowband_behavior = TxNbEmissionNode.NarrowbandBehaviorOption.ABSOLUTE_FREQS_AND_POWER

        # Attenuation too low (< -1000)
        bad_csv = _write_csv("tx_nb_att_low", "1e6,-1001\n2e6,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_nb, bad_csv)

        # Attenuation too high (> 1000)
        bad_csv = _write_csv("tx_nb_att_high", "1e6,1001\n2e6,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_nb, bad_csv)

        # ---------------------------------------------------------------
        # TxBbEmissionNode: 2 cols - Frequency [-100e9, 100e9], Amplitude [-1000, 1000]
        # ---------------------------------------------------------------
        tx_bb = tx_spectral.add_tx_broadband_noise_profile()
        assert isinstance(tx_bb, TxBbEmissionNode)

        valid_csv = _write_csv("tx_bb_valid", "\n".join(
            [f"{f},{a}" for f, a in
             [(1e3, -100), (5e3, -105), (1e4, -110), (5e4, -115), (1e5, -120),
              (5e5, -125), (1e6, -130), (5e6, -135), (1e7, -140), (1e8, -145)]]
        ))
        csv_paths.append(valid_csv)
        result = tx_bb.import_csv_file(valid_csv)
        assert result is not None

        # Frequency too low (< -100e9)
        bad_csv = _write_csv("tx_bb_freq_low", "-200e9,-100\n1e6,-120\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_bb, bad_csv)

        # Frequency too high (> 100e9)
        bad_csv = _write_csv("tx_bb_freq_high", "200e9,-100\n1e6,-120\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_bb, bad_csv)

        # Attenuation too low (< -1000)
        bad_csv = _write_csv("tx_bb_att_low", "1e6,-1001\n10e6,-120\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_bb, bad_csv)

        # Attenuation too high (> 1000)
        bad_csv = _write_csv("tx_bb_att_high", "1e6,1001\n10e6,-120\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_bb, bad_csv)

        # ---------------------------------------------------------------
        # TxSpurNode: 3 cols - Frequency [1, 100e9] Hz, Bandwidth [1, 100e9] Hz, Power [-1000, 1000]
        # Input CSV: col0=freq in Hz, col1=bandwidth in kHz, col2=power
        # ---------------------------------------------------------------
        tx_spur = tx_spectral.add_spurious_emissions()
        assert isinstance(tx_spur, TxSpurNode)

        valid_csv = _write_csv("tx_spur_valid", "\n".join(
            [f"{f},{bw},{p}" for f, bw, p in
             [(1e6, 1, -30), (2e6, 2, -40), (5e6, 5, -50), (1e7, 10, -60), (2e7, 20, -70),
              (5e7, 50, -55), (1e8, 100, -45), (2e8, 200, -65), (5e8, 500, -75), (1e9, 1000, -85)]]
        ))
        csv_paths.append(valid_csv)
        result = tx_spur.import_csv_file(valid_csv)
        assert result is not None

        # Frequency too low (< 1)
        bad_csv = _write_csv("tx_spur_freq_low", "0,2,-50\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_spur, bad_csv)

        # Frequency too high (> 100e9)
        bad_csv = _write_csv("tx_spur_freq_high", "200e9,2,-50\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_spur, bad_csv)

        # Bandwidth too low (< 1)
        bad_csv = _write_csv("tx_spur_bw_low", "100,0,-50\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_spur, bad_csv)

        # Bandwidth too high (> 100e9)
        bad_csv = _write_csv("tx_spur_bw_high", "100,200e9,-50\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_spur, bad_csv)

        # Power too low (< -1000)
        bad_csv = _write_csv("tx_spur_pow_low", "100,2,-1001\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_spur, bad_csv)

        # Power too high (> 1000)
        bad_csv = _write_csv("tx_spur_pow_high", "100,2,1001\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(tx_spur, bad_csv)

        # ---------------------------------------------------------------
        # RxSpurNode: 3 cols - Frequency [1, 100e9] Hz, Bandwidth [1, 100e9] Hz, Power [-1000, 1000]
        # Input CSV: col0=freq in Hz, col1=bandwidth in kHz, col2=power
        # ---------------------------------------------------------------
        rx_spur = rx_susceptibility.add_spurious_responses()
        assert isinstance(rx_spur, RxSpurNode)

        valid_csv = _write_csv("rx_spur_valid", "\n".join(
            [f"{f},{bw},{p}" for f, bw, p in
             [(1e6, 1, -30), (2e6, 2, -40), (5e6, 5, -50), (1e7, 10, -60), (2e7, 20, -70),
              (5e7, 50, -55), (1e8, 100, -45), (2e8, 200, -65), (5e8, 500, -75), (1e9, 1000, -85)]]
        ))
        csv_paths.append(valid_csv)
        result = rx_spur.import_csv_file(valid_csv)
        assert result is not None

        # Frequency too low (< 1)
        bad_csv = _write_csv("rx_spur_freq_low", "0,2,-50\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_spur, bad_csv)

        # Frequency too high (> 100e9)
        bad_csv = _write_csv("rx_spur_freq_high", "200e9,2,-50\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_spur, bad_csv)

        # Bandwidth too low (< 1)
        bad_csv = _write_csv("rx_spur_bw_low", "100,0,-50\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_spur, bad_csv)

        # Bandwidth too high (> 100e9)
        bad_csv = _write_csv("rx_spur_bw_high", "100,200e9,-50\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_spur, bad_csv)

        # Power too low (< -1000)
        bad_csv = _write_csv("rx_spur_pow_low", "100,2,-1001\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_spur, bad_csv)

        # Power too high (> 1000)
        bad_csv = _write_csv("rx_spur_pow_high", "100,2,1001\n200,5,-80\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(rx_spur, bad_csv)

        # ---------------------------------------------------------------
        # CustomCouplingNode: 2 cols - Frequency [1e-6, 100000] MHz, Value [-1000, 0] dB
        # Input CSV: col0=freq in Hz, col1=value in dB
        # ---------------------------------------------------------------
        custom_coupling = couplings_node.add_custom_coupling()
        assert isinstance(custom_coupling, CustomCouplingNode)

        valid_csv = _write_csv("custom_coupling_valid", "\n".join(
            [f"{f},{v}" for f, v in
             [(1e-6, -5), (10e-6, -10), (50e-6, -15), (100e-6, -20), (500e-6, -30),
              (1e3, -40), (5e3, -50), (10e3, -60), (50e3, -70), (100e3, -80)]]
        ))  
        csv_paths.append(valid_csv)
        result = custom_coupling.import_csv_file(valid_csv)
        assert result is not None

        # Frequency too low (< 1 Hz)
        bad_csv = _write_csv("cc_freq_low", "0,-10\n1e9,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(custom_coupling, bad_csv)

        # Frequency too high (> 100 GHz)
        bad_csv = _write_csv("cc_freq_high", "200e9,-10\n1e9,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(custom_coupling, bad_csv)

        # Value too low (< -1000)
        bad_csv = _write_csv("cc_val_low", "1e9,-1001\n2e9,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(custom_coupling, bad_csv)

        # Value too high (> 0)
        bad_csv = _write_csv("cc_val_high", "1e9,1\n2e9,-20\n")
        csv_paths.append(bad_csv)
        _assert_import_fails(custom_coupling, bad_csv)

    finally:
        for p in csv_paths:
            if os.path.exists(p):
                os.remove(p)

