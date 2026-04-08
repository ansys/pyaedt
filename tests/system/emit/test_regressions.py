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
    from ansys.aedt.core.emit_core.nodes.generated import CustomCouplingNode
    from ansys.aedt.core.emit_core.nodes.generated import RxMixerProductNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSaturationNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSelectivityNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSpurNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSusceptibilityProfNode
    from ansys.aedt.core.emit_core.nodes.generated import TxBbEmissionNode
    from ansys.aedt.core.emit_core.nodes.generated import TxHarmonicNode
    from ansys.aedt.core.emit_core.nodes.generated import TxNbEmissionNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpectralProfNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpurNode


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
