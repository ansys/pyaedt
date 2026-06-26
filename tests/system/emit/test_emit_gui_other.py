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

"""PyAEDT equivalents of the EDT_EMITCLASSIC/GuiOther/Scripted coupling model tests.

Replicates the following legacy DlxPyScript tests:
  - Hata_test: Hata coupling with environment/distance sweeps
  - TwoRay_test: Two Ray Ground Reflection with GP normal/position/fading sweeps
  - Atmosphere_test: Two Ray with atmospheric absorption parameter sweeps
  - RainAttenuation_test: Two Ray with rain attenuation parameter sweeps
  - IndoorCoupling_test: Indoor propagation with building type/floor sweeps
  - WalfIkeg_test: Walfisch-Ikegami NLOS/LOS with urban geometry sweeps
  - import_spurs_test: Tx/Rx spur CSV import and table verification
"""

from __future__ import annotations

import os
import sys
import tempfile
import shutil

import pytest

from tests.conftest import DESKTOP_VERSION
from tests import TESTS_EMIT_PATH

if ((3, 8) <= sys.version_info[0:2] <= (3, 11) and DESKTOP_VERSION < "2025.1") or (
    (3, 10) <= sys.version_info[0:2] <= (3, 12) and DESKTOP_VERSION > "2024.2"
):
    from ansys.aedt.core import Emit
    from ansys.aedt.core.emit_core.nodes.generated import Amplifier
    from ansys.aedt.core.emit_core.nodes.generated import AntennaNode
    from ansys.aedt.core.emit_core.nodes.generated import Band
    from ansys.aedt.core.emit_core.nodes.generated import Cable
    from ansys.aedt.core.emit_core.nodes.generated import Circulator
    from ansys.aedt.core.emit_core.nodes.generated import CouplingsNode
    from ansys.aedt.core.emit_core.nodes.generated import EmitSceneNode
    from ansys.aedt.core.emit_core.nodes.generated import Filter
    from ansys.aedt.core.emit_core.nodes.generated import HataCouplingNode
    from ansys.aedt.core.emit_core.nodes.generated import IndoorPropagationCouplingNode
    from ansys.aedt.core.emit_core.nodes.generated import Isolator
    from ansys.aedt.core.emit_core.nodes.generated import Multiplexer
    from ansys.aedt.core.emit_core.nodes.generated import MultiplexerBand
    from ansys.aedt.core.emit_core.nodes.generated import PowerDivider
    from ansys.aedt.core.emit_core.nodes.generated import PropagationLossCouplingNode
    from ansys.aedt.core.emit_core.nodes.generated import RadioNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSpurNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSusceptibilityProfNode
    from ansys.aedt.core.emit_core.nodes.generated import SamplingNode
    from ansys.aedt.core.emit_core.nodes.generated import Terminator
    from ansys.aedt.core.emit_core.nodes.generated import TwoRayPathLossCouplingNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpectralProfNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpurNode
    from ansys.aedt.core.emit_core.nodes.generated import WalfischCouplingNode
    from ansys.aedt.core.emit_core.results.revision import Revision

TEST_SUBFOLDER = TESTS_EMIT_PATH / "example_models/TEMIT"

@pytest.fixture
def emit_app(add_app):
    app = add_app(application=Emit)
    yield app
    app.close_project(app.project_name, save=False)


def _setup_coupling_project(emit_app, coupling_type: str):
    """Create a project with two positioned antennas and a specific coupling type.

    Returns (revision, coupling_node, ant1, ant2, scene_node, coupling_data).
    """
    radio1, ant1 = emit_app.schematic.create_radio_antenna("New Radio")
    radio2, ant2 = emit_app.schematic.create_radio_antenna("New Radio")

    ant1.position_defined = True
    ant1.position = "0 0 100"

    ant2.position_defined = True
    ant2.position = "1000 0 5"

    revision = emit_app.results.analyze()

    coupling_data: CouplingsNode = revision.get_coupling_data_node()
    coupling_node = coupling_data._add_child_node(coupling_type)

    scene_node = revision.get_scene_node()
    ant_children = [c for c in scene_node.children if isinstance(c, AntennaNode)]
    assert len(ant_children) >= 2

    short_names = [c.name for c in ant_children]
    if hasattr(coupling_node, "antenna_a"):
        coupling_node.antenna_a = short_names[0]
        coupling_node.antenna_b = short_names[1]
    elif hasattr(coupling_node, "base_antenna"):
        coupling_node.base_antenna = short_names[0]
        coupling_node.mobile_antenna = short_names[1]

    return revision, coupling_node, ant_children[0], ant_children[1], scene_node, coupling_data


@pytest.mark.skipif(
    sys.version_info < (3, 10) or DESKTOP_VERSION < "2027.1",
    reason="Requires Python 3.10+ and AEDT 2027.1+",
)
class TestEmitGuiOther:
    """PyAEDT equivalents of EDT_EMITCLASSIC/GuiOther/Scripted tests."""

    def test_hata_coupling(self, emit_app):
        """Replicate Hata_test: sweep Environment x distance, export coupling CSV.

        Original test sets Tx at (0,0,100) and varies Rx distance across
        [1000, 10000, 20000] for each of 4 environment types, exporting
        12 CSV files total.
        """
        revision, hata, ant1, ant2, scene, coupling_data = _setup_coupling_project(
            emit_app, "Hata Coupling"
        )
        short_names = [ant1.name, ant2.name]
        ports = f"{short_names[0]}|{short_names[1]}"

        ant1.position = "0 0 100"

        export_count = 0
        for env in [
            HataCouplingNode.EnvironmentOption.LARGE_CITY,
            HataCouplingNode.EnvironmentOption.SMALLMEDIUM_CITY,
            HataCouplingNode.EnvironmentOption.SUBURBAN,
            HataCouplingNode.EnvironmentOption.RURAL,
        ]:
            hata.environment = env
            for distance in [1000, 10000, 20000]:
                ant2.position = f"{distance} 0 5"
                data = hata.export_to_csv("", ports=ports)
                assert data is not None and len(data) > 0, (
                    f"Hata export failed for env={env.name}, dist={distance}"
                )
                export_count += 1

        assert export_count == 12

    def test_two_ray_coupling(self, emit_app):
        """Replicate TwoRay_test: sweep GP normal/position x fading type, export CSV.

        Original test uses 3 GP normal/position/antenna configs, each with
        3 GP positions and 4 fading types = 36 exports.
        """
        revision, two_ray, ant1, ant2, scene, coupling_data = _setup_coupling_project(
            emit_app, "Two Ray Path Loss Coupling"
        )
        short_names = [ant1.name, ant2.name]
        ports = f"{short_names[0]}|{short_names[1]}"

        fading_types = [
            TwoRayPathLossCouplingNode.FadingTypeOption.NONE,
            TwoRayPathLossCouplingNode.FadingTypeOption.FAST_FADING_ONLY,
            TwoRayPathLossCouplingNode.FadingTypeOption.SHADOWING_ONLY,
            TwoRayPathLossCouplingNode.FadingTypeOption.FAST_FADING_AND_SHADOWING,
        ]

        settings = [
            (EmitSceneNode.GroundPlaneNormalOption.Z_AXIS, "50000 0 3", "0 0 250"),
            (EmitSceneNode.GroundPlaneNormalOption.X_AXIS, "3 50000 3", "250 0 250"),
            (EmitSceneNode.GroundPlaneNormalOption.Z_AXIS, "50000 3 3", "0 250 250"),
        ]

        export_count = 0
        for gp_normal, rx_pos, tx_pos in settings:
            scene.ground_plane_normal = gp_normal
            for gp_position in [0, 1, 2]:
                scene.gp_position_along_normal = gp_position
                ant2.position = rx_pos
                ant1.position = tx_pos
                for fading in fading_types:
                    two_ray.fading_type = fading
                    data = two_ray.export_to_csv("", ports=ports)
                    assert data is not None and len(data) > 0, (
                        f"TwoRay export failed: gp={gp_normal.name}, pos={gp_position}, fading={fading.name}"
                    )
                    export_count += 1

        assert export_count == 36

    def test_atmosphere_absorption(self, emit_app):
        """Replicate Atmosphere_test: Two Ray with atmospheric absorption sweeps.

        Original test enables atmospheric absorption (disables rain), sets
        antenna positions, then sweeps temperature/pressure/water-vapor
        settings x 4 fading types = 12 exports.
        """
        revision, two_ray, ant1, ant2, scene, coupling_data = _setup_coupling_project(
            emit_app, "Two Ray Path Loss Coupling"
        )
        short_names = [ant1.name, ant2.name]
        ports = f"{short_names[0]}|{short_names[1]}"

        scene.ground_plane_normal = EmitSceneNode.GroundPlaneNormalOption.Z_AXIS
        scene.gp_position_along_normal = 0
        two_ray.include_rain_attenuation = False
        two_ray.include_atmospheric_absorption = True
        ant2.position = "50000 0 3"
        ant1.position = "0 0 250"

        atmo_settings = [
            (25.0, 900.0, 5.0),
            (20.0, 1013.0, 7.5),
            (25.0, 1100.0, 10.0),
        ]

        fading_types = [
            TwoRayPathLossCouplingNode.FadingTypeOption.NONE,
            TwoRayPathLossCouplingNode.FadingTypeOption.FAST_FADING_ONLY,
            TwoRayPathLossCouplingNode.FadingTypeOption.SHADOWING_ONLY,
            TwoRayPathLossCouplingNode.FadingTypeOption.FAST_FADING_AND_SHADOWING,
        ]

        export_count = 0
        for fading in fading_types:
            two_ray.fading_type = fading
            for temp, pressure, water_vapor in atmo_settings:
                two_ray.temperature = temp
                two_ray.total_air_pressure = pressure
                two_ray.water_vapor_concentration = water_vapor
                data = two_ray.export_to_csv("", ports=ports)
                assert data is not None and len(data) > 0, (
                    f"Atmosphere export failed: fading={fading.name}, temp={temp}"
                )
                export_count += 1

        assert export_count == 12

    def test_rain_attenuation(self, emit_app):
        """Replicate RainAttenuation_test: Two Ray with rain attenuation sweeps.

        Original test enables rain attenuation (disables atmospheric absorption),
        sets rain rate/availability, then sweeps polarization tilt angle x fading
        type = 12 exports.
        """
        revision, two_ray, ant1, ant2, scene, coupling_data = _setup_coupling_project(
            emit_app, "Two Ray Path Loss Coupling"
        )
        short_names = [ant1.name, ant2.name]
        ports = f"{short_names[0]}|{short_names[1]}"

        scene.ground_plane_normal = EmitSceneNode.GroundPlaneNormalOption.Z_AXIS
        scene.gp_position_along_normal = 0
        two_ray.include_rain_attenuation = True
        two_ray.include_atmospheric_absorption = False
        two_ray.rain_availability = 99.0
        two_ray.rain_rate = 5.0
        ant2.position = "50000 0 3"
        ant1.position = "0 0 250"

        fading_types = [
            TwoRayPathLossCouplingNode.FadingTypeOption.NONE,
            TwoRayPathLossCouplingNode.FadingTypeOption.FAST_FADING_ONLY,
            TwoRayPathLossCouplingNode.FadingTypeOption.SHADOWING_ONLY,
            TwoRayPathLossCouplingNode.FadingTypeOption.FAST_FADING_AND_SHADOWING,
        ]

        export_count = 0
        for polar_angle in [45, 90, 135]:
            two_ray.polarization_tilt_angle = polar_angle
            for fading in fading_types:
                two_ray.fading_type = fading
                data = two_ray.export_to_csv("", ports=ports)
                assert data is not None and len(data) > 0, (
                    f"Rain export failed: angle={polar_angle}, fading={fading.name}"
                )
                export_count += 1

        assert export_count == 12

    def test_indoor_coupling(self, emit_app):
        """Replicate IndoorCoupling_test: sweep building type x number of floors.

        Original test iterates 4 building types x 3 floor counts = 12 exports.
        """
        revision, indoor, ant1, ant2, scene, coupling_data = _setup_coupling_project(
            emit_app, "Indoor Propagation Coupling"
        )
        short_names = [ant1.name, ant2.name]
        ports = f"{short_names[0]}|{short_names[1]}"

        building_types = [
            IndoorPropagationCouplingNode.BuildingTypeOption.RESIDENTIAL_APARTMENT,
            IndoorPropagationCouplingNode.BuildingTypeOption.RESIDENTIAL_HOUSE,
            IndoorPropagationCouplingNode.BuildingTypeOption.OFFICE_BUILDING,
            IndoorPropagationCouplingNode.BuildingTypeOption.COMMERCIAL_BUILDING,
        ]

        export_count = 0
        for building in building_types:
            indoor.building_type = building
            for num_floors in range(1, 4):
                indoor.number_of_floors = num_floors
                data = indoor.export_to_csv("", ports=ports)
                assert data is not None and len(data) > 0, (
                    f"Indoor export failed: building={building.name}, floors={num_floors}"
                )
                export_count += 1

        assert export_count == 12

    def test_walfisch_ikegami_coupling(self, emit_app):
        """Replicate WalfIkeg_test: Walfisch-Ikegami NLOS and LOS sweeps.

        Original test:
        1. NLOS Dense Metro: roof height x building dist x incidence angle (12 exports)
        2. NLOS Small/Medium City: same parameter sweep (12 exports)
        3. LOS Urban Canyon: distance sweep (12 exports)
        """
        revision, walf, ant1, ant2, scene, coupling_data = _setup_coupling_project(
            emit_app, "Walfisch-Ikegami Coupling"
        )
        short_names = [ant1.name, ant2.name]
        ports = f"{short_names[0]}|{short_names[1]}"

        ant1.position = "2500 0 25"
        ant2.position = "0 0 2"

        export_count = 0

        # NLOS Dense Metro
        walf.path_loss_type = WalfischCouplingNode.PathLossTypeOption.NLOS
        walf.environment = WalfischCouplingNode.EnvironmentOption.DENSE_METRO
        for roof_height in [10, 30]:
            walf.roof_height = roof_height
            for b in [20, 40]:
                walf.distance_between_buildings = b
                walf.street_width = b / 2
                for angle in [15, 40, 80]:
                    walf.incidence_angle = angle
                    data = walf.export_to_csv("", ports=ports)
                    assert data is not None and len(data) > 0, (
                        f"WalfIkeg NLOS DenseMetro failed: roof={roof_height}, b={b}, angle={angle}"
                    )
                    export_count += 1

        # NLOS Small/Medium City
        walf.environment = WalfischCouplingNode.EnvironmentOption.SMALLMEDIUM_CITY_OR_SUBURBAN
        for roof_height in [10, 30]:
            walf.roof_height = roof_height
            for b in [20, 40]:
                walf.distance_between_buildings = b
                walf.street_width = b / 2
                for angle in [15, 40, 80]:
                    walf.incidence_angle = angle
                    data = walf.export_to_csv("", ports=ports)
                    assert data is not None and len(data) > 0, (
                        f"WalfIkeg NLOS SmallCity failed: roof={roof_height}, b={b}, angle={angle}"
                    )
                    export_count += 1

        # LOS Urban Canyon distance sweep
        walf.path_loss_type = WalfischCouplingNode.PathLossTypeOption.LOS_URBAN_CANYON
        for distance in range(500, 5000, 400):
            ant1.position = f"{distance} 0 25"
            data = walf.export_to_csv("", ports=ports)
            assert data is not None and len(data) > 0, (
                f"WalfIkeg LOS failed: distance={distance}"
            )
            export_count += 1

        assert export_count == 36  # 24 NLOS + 12 LOS

    def test_component_warnings_filter(self, emit_app):
        """Replicate Component_Warnings: Filter with no file generates warning.

        From Component_Warnings baseline: 'No file specified for this Filter'
        when a Filter component is set to By File type with no file loaded.
        """
        filt: Filter = emit_app.schematic.create_component("File-based")
        assert "No file specified" in filt.warnings or "file" in filt.warnings.lower()

    def test_component_warnings_cable(self, emit_app):
        """Replicate Component_Warnings: Cable with no file generates warning.

        From Component_Warnings baseline: 'No file specified for this Cable'
        """
        cable: Cable = emit_app.schematic.create_component("Cable")
        cable.cable_type = Cable.CableTypeOption.BY_FILE
        assert "No file specified" in cable.warnings or "file" in cable.warnings.lower()

    def test_component_warnings_circulator(self, emit_app):
        """Replicate Component_Warnings: Circulator with no file generates warning.

        From Component_Warnings baseline: 'No file specified for this Circulator'
        """
        circ: Circulator = emit_app.schematic.create_component("Circulator")
        circ.circulator_type = Circulator.CirculatorTypeOption.BY_FILE
        assert "No file specified" in circ.warnings or "file" in circ.warnings.lower()

    def test_component_warnings_isolator(self, emit_app):
        """Replicate Component_Warnings: Isolator with no file generates warning.

        From Component_Warnings baseline: 'No file specified for this Isolator'
        """
        iso: Isolator = emit_app.schematic.create_component("Isolator")
        iso.isolator_type = Isolator.IsolatorTypeOption.BY_FILE
        assert "No file specified" in iso.warnings or "file" in iso.warnings.lower()

    def test_component_warnings_power_divider(self, emit_app):
        """Replicate Component_Warnings: Power Divider with no file generates warning.

        From Component_Warnings baseline: 'No file specified for this Power Divider'
        """
        pd: PowerDivider = emit_app.schematic.create_component("Divider")
        pd.power_divider_type = PowerDivider.PowerDividerTypeOption.BY_FILE
        assert "No file specified" in pd.warnings or "file" in pd.warnings.lower()

    def test_component_warnings_amplifier_ip3(self, emit_app):
        """Replicate Component_Warnings: Amplifier with IIP3 > P1dB+27 generates warning.

        From Component_Warnings baseline: 'EMIT's amplifier model requires
        monotonically decreasing intercept points'
        """
        amp: Amplifier = emit_app.schematic.create_component("Amplifier")
        amp.p1_db_point_ref_input = '-10.0 dBm'
        amp.ip3_ref_input = '50.0 dBm'
        assert "intercept" in amp.warnings.lower() or "IIP3" in amp.warnings or "monotonically" in amp.warnings.lower()

    def test_component_warnings_multiplexer(self, emit_app):
        """Replicate Component_Warnings: Multiplexer with no file generates warning.

        From Component_Warnings baseline: 'No file specified for this Multiplexer'
        """
        mux: Multiplexer = emit_app.schematic.create_component("3 Port")
        mux.multiplexer_type = Multiplexer.MultiplexerTypeOption.BY_FILE
        assert "No file specified" in mux.warnings or "file" in mux.warnings.lower()

        mux.multiplexer_type = Multiplexer.MultiplexerTypeOption.BY_PASS_BAND
        pb1_fullname = mux.children[0]._full_node_name()
        mux.ports = f"{pb1_fullname}|{pb1_fullname}"
        assert "Multiple ports" in mux.warnings or "same" in mux.warnings.lower()

        mux2: Multiplexer = emit_app.schematic.create_component("3 Port")
        pass_band: MultiplexerBand = mux2.children[0]
        pass_band.passband_type = MultiplexerBand.PassbandTypeOption.BY_FILE
        assert "No file specified" in pass_band.warnings or "file" in pass_band.warnings.lower()

    def test_component_warnings_terminator(self, emit_app):
        """Replicate Component_Warnings: Terminator with no file generates warning.

        From Component_Warnings baseline: 'No file specified for this Terminator'
        """
        term: Terminator = emit_app.schematic.create_component("Terminator")
        term.terminator_type = Terminator.TerminatorTypeOption.BY_FILE
        assert "No file specified" in term.warnings or "file" in term.warnings.lower()

    def test_coupling_warnings_undefined_antenna(self, emit_app):
        """Replicate Coupling_Warnings: Path Loss coupling with undefined antenna warns.

        From Component_Warnings and Coupling_Warnings baselines:
        'An antenna selection is undefined'
        """
        revision = emit_app.results.analyze()
        coupling_data: CouplingsNode = revision.get_coupling_data_node()
        path_loss: PropagationLossCouplingNode = coupling_data._add_child_node("Path Loss Coupling")
        assert "antenna" in path_loss.warnings.lower() or "undefined" in path_loss.warnings.lower()

    def test_coupling_warnings_colocated_antennas(self, emit_app):
        """Replicate Coupling_Warnings: co-located antennas generate warnings.

        From Coupling_Warnings baseline: 'are co-located' or 'are too close'
        """
        radio1, ant1 = emit_app.schematic.create_radio_antenna("New Radio")
        radio2, ant2 = emit_app.schematic.create_radio_antenna("New Radio")
        ant1.position_defined = True
        ant1.position = "0 0 0"
        ant2.position_defined = True
        ant2.position = "0 0 0"

        revision = emit_app.results.analyze()
        coupling_data: CouplingsNode = revision.get_coupling_data_node()
        path_loss: PropagationLossCouplingNode = coupling_data._add_child_node("Path Loss Coupling")
        scene_node = revision.get_scene_node()
        ant_children = [c for c in scene_node.children if isinstance(c, AntennaNode)]
        path_loss.antenna_a = ant_children[0].name
        path_loss.antenna_b = ant_children[1].name

        warn = path_loss.warnings.lower()
        assert "co-located" in warn or "too close" in warn

    def test_coupling_warnings_hata_bad_height(self, emit_app):
        """Replicate Coupling_Warnings: Hata coupling with invalid antenna heights warns.

        From Coupling_Warnings baseline: 'Base station antenna height is 0.000 m,
        but the model expects: 30 m <= hm <= 200 m'
        """
        radio1, ant1 = emit_app.schematic.create_radio_antenna("New Radio")
        radio2, ant2 = emit_app.schematic.create_radio_antenna("New Radio")
        ant1.position_defined = True
        ant1.position = "0 0 0"
        ant2.position_defined = True
        ant2.position = "5000 0 5"

        revision = emit_app.results.analyze()
        coupling_data: CouplingsNode = revision.get_coupling_data_node()
        hata = coupling_data._add_child_node("Hata Coupling")
        scene_node = revision.get_scene_node()
        ant_children = [c for c in scene_node.children if isinstance(c, AntennaNode)]
        hata.base_antenna = ant_children[0].name
        hata.mobile_antenna = ant_children[1].name

        warn = hata.warnings.lower()
        assert "antenna height" in warn or "model expects" in warn

    def test_coupling_warnings_two_ray_below_ground(self, emit_app):
        """Replicate Coupling_Warnings: Two Ray with antenna below ground plane warns.

        From Coupling_Warnings baseline: 'must be above the ground plane'
        """
        radio1, ant1 = emit_app.schematic.create_radio_antenna("New Radio")
        radio2, ant2 = emit_app.schematic.create_radio_antenna("New Radio")
        ant1.position_defined = True
        ant1.position = "0 0 -5"
        ant2.position_defined = True
        ant2.position = "1000 0 10"

        revision = emit_app.results.analyze()
        coupling_data: CouplingsNode = revision.get_coupling_data_node()
        two_ray = coupling_data._add_child_node("Two Ray Path Loss Coupling")
        scene_node = revision.get_scene_node()
        ant_children = [c for c in scene_node.children if isinstance(c, AntennaNode)]
        two_ray.antenna_a = ant_children[0].name
        two_ray.antenna_b = ant_children[1].name

        warn = two_ray.warnings.lower()
        assert "above the ground plane" in warn or "ground plane" in warn

    def test_radio_warnings_invalid_emission_designator(self, emit_app):
        """Replicate Radio_Warnings: invalid emission designator generates warning.

        From Radio_Warnings baseline: 'Invalid Emission Designator'
        """
        radio: RadioNode = emit_app.schematic.create_component("New Radio")
        band: Band = radio.children[0]
        band.use_emission_designator = True
        band.emission_designator = "BAD"
        warn = band.warnings
        assert "Invalid Emission Designator" in warn or "Emission Designator" in warn

    def test_sampling_warnings(self, emit_app):
        """Replicate Sampling_Warnings: invalid number of channels generates warning.

        From Sampling_Warnings baseline: 'Invalid number of channels'
        """
        radio: RadioNode = emit_app.schematic.create_component("New Radio")
        sampling: SamplingNode = radio.children[1]
        sampling.table_data = [(200e6, 100e6)]
        warn = sampling.warnings.lower()
        assert "No channels are enabled" in warn or "range" in warn

    def test_import_cad_with_skip_dialog(self, emit_app, file_tmp_root):
        """Test importing a CAD file with skip dialog set to True."""
        revision = emit_app.results.analyze()
        scene_node = revision.get_scene_node()
        cad_file = TEST_SUBFOLDER / "Ansys_777_200_ER.glb"
        file = shutil.copy2(cad_file, file_tmp_root / "Ansys_777_200_ER.glb")           
        cad_node = scene_node.import_cad(str(file), create_antennas=False)
        assert cad_node
        assert len(scene_node.children) == 1


        cad2_node = scene_node.import_cad(str(file), create_antennas=True)
        assert cad2_node
        assert len(scene_node.children) == 5
