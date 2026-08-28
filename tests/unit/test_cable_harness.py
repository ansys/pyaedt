# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Test the explicit cable harness modeling subpackage."""

import copy
import json
import math
from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.advanced_cad.cable_harness import BuildArtifacts
from ansys.aedt.core.modeler.advanced_cad.cable_harness import CableBundleConfig
from ansys.aedt.core.modeler.advanced_cad.cable_harness import MeasuredShield
from ansys.aedt.core.modeler.advanced_cad.cable_harness import RoutedCableBundle
from ansys.aedt.core.modeler.advanced_cad.cable_harness import build_shield_model
from ansys.aedt.core.modeler.advanced_cad.cable_harness import geometry as geo
from ansys.aedt.core.modeler.advanced_cad.cable_harness import transfer_impedance as ti
from ansys.aedt.core.modeler.advanced_cad.cable_harness.shield_models import ShieldModelError

CONFIG = {
    "units": "mm",
    "materials": {
        "copper": {"conductivity": 5.8e7},
        "aluminum": {"conductivity": 3.5e7},
        "pe_foam": {"relative_permittivity": 1.5, "loss_tangent": 0.0005},
        "pvc": {"relative_permittivity": 3.0, "loss_tangent": 0.02},
    },
    "conductors": {
        "w1": {"conductor_equivalent_radius": 0.227, "awg": 25},
        "w2": {"conductor_equivalent_radius": 0.227, "awg": 25},
    },
    "insulation": {"wire_insulation": {"material": "pe_foam", "outer_radius": 0.55}},
    "pairs": {
        "pair1": {
            "members": ["w1", "w2"],
            "twist_pitch": 12.7,
            "shield": {
                "type": "foil",
                "material": "aluminum",
                "thickness": 0.009,
                "construction": {"seam_inductance": 1.0e-9},
            },
        }
    },
    "bundle": {
        "demo_bundle": {
            "members": ["pair1"],
            "jacket": {"material": "pvc", "outer_radius": 4.0},
            "overall_shield": {
                "type": "braid",
                "material": "copper",
                "construction": {
                    "wire_diameter": 0.1,
                    "carriers": 16,
                    "wires_per_carrier": 8,
                    "weave_angle": 30.0,
                },
            },
        }
    },
    "cross_section": {"layout": "quad", "pair_locations": {"pair1": {"center": [0.0, 0.0]}}},
    "routes": {"main": {"points": [[0.0, 0.0, 0.0], [50.0, 0.0, 0.0]]}},
    "simulation": {
        "differential_pairs": [["w1", "w2"]],
        "frequency_range": {"start": 1.0e6, "stop": 1.0e9},
        "characteristic_impedance": {"differential": 100.0},
        "geometry": {
            "facets": 6,
            "samples_per_pitch": 4,
            "pair_wire_center_offset": 0.58,
            "pair_shield_radius": 1.15,
            "overall_shield_radius": 3.6,
            "tube_end_extension": 4.0,
        },
        "ports": {"type": "circuit", "reference": "overall_shield", "impedance": 50.0},
    },
}


@pytest.fixture
def configuration():
    """Return a freshly parsed, valid single-pair cable bundle configuration."""
    return CableBundleConfig.from_dict(copy.deepcopy(CONFIG))


@pytest.fixture(autouse=True)
def propagate_errors():
    """Let PyAEDT exceptions propagate so failure paths can be asserted."""
    initial = settings.enable_error_handler
    settings.enable_error_handler = False
    yield
    settings.enable_error_handler = initial


class FakeObject:
    """Minimal stand-in for a modeler object that keeps a name registry up to date."""

    def __init__(self, name, points, registry):
        self._registry = registry
        self._name = None
        self.points = [np.asarray(p, dtype=float) for p in points]
        self.transparency = None
        self.color = None
        self.material_name = None
        self.name = name
        self._set_terminals(self.points)

    def _set_terminals(self, points):
        """Attach one face and one edge to each end of the object."""
        self.faces = []
        for point in (points[0], points[-1]):
            face = MagicMock()
            face.center = point
            edge = MagicMock()
            edge.midpoint = point
            face.edges = [edge]
            self.faces.append(face)
        self.edges = [face.edges[0] for face in self.faces]

    @property
    def name(self):
        """Name of the object, kept in sync with the modeler registry."""
        return self._name

    @name.setter
    def name(self, value):
        if self._name is not None:
            self._registry.pop(self._name, None)
        self._name = value
        self._registry[value] = self


@pytest.fixture
def mock_hfss():
    """Return a mocked HFSS design that models polyline creation and sweeping."""
    hfss = MagicMock()
    hfss.materials.material_keys = {}
    registry = {}

    def _create_polyline(points, name, **kwargs):
        return FakeObject(name, points, registry)

    def _sweep_along_path(profile, path):
        # The swept solid inherits its end faces from the ends of the sweep path.
        profile._set_terminals(path.points)
        return True

    hfss.modeler.create_polyline.side_effect = _create_polyline
    hfss.modeler.sweep_along_path.side_effect = _sweep_along_path
    hfss.modeler.__getitem__.side_effect = lambda name: registry.get(name)
    return hfss


class TestConfiguration:
    """Test loading and validating the cable bundle configuration."""

    def test_from_dict_parses_every_section(self, configuration):
        """Test that all configuration sections are parsed with the expected values."""
        assert configuration.units == "mm"
        assert configuration.bundle.name == "demo_bundle"
        assert configuration.bundle.jacket_outer_radius == 4.0
        assert configuration.insulation.material == "pe_foam"
        assert configuration.conductors["w1"].equivalent_radius == 0.227
        assert configuration.pairs["pair1"].members == ["w1", "w2"]
        assert configuration.pairs["pair1"].shield.is_foil
        assert configuration.bundle.overall_shield.is_braid
        assert configuration.cross_section.pair_locations["pair1"] == (0.0, 0.0)
        assert configuration.simulation.differential_pairs == [("w1", "w2")]
        assert configuration.simulation.characteristic_impedance_diff == 100.0
        assert configuration.active_route.points.shape == (2, 3)
        assert configuration.end_extension() == 4.0

    def test_defaults_are_applied(self):
        """Test that omitted optional settings fall back to their documented defaults."""
        data = copy.deepcopy(CONFIG)
        del data["simulation"]["geometry"]
        del data["simulation"]["ports"]
        config = CableBundleConfig.from_dict(data)

        assert config.simulation.geometry.facets == 8
        assert config.simulation.geometry.pair_shield_radius == 1.15
        assert config.simulation.ports.reference == "overall_shield"
        assert config.simulation.ports.impedance == 50.0
        assert config.simulation.geometry.ground_plane.enabled is False

    @pytest.mark.parametrize("suffix", ["json", "yaml", "yml"])
    def test_from_file_round_trip(self, tmp_path, suffix):
        """Test that a configuration loads identically from every supported file format."""
        import yaml

        file_path = tmp_path / f"bundle.{suffix}"
        if suffix == "json":
            file_path.write_text(json.dumps(CONFIG), encoding="utf-8")
        else:
            file_path.write_text(yaml.safe_dump(CONFIG), encoding="utf-8")

        config = CableBundleConfig.from_file(file_path)
        config.validate()

        assert config.bundle.name == "demo_bundle"
        assert config.simulation.frequency_stop == 1.0e9

    def test_validate_accepts_a_correct_configuration(self, configuration):
        """Test that a correct configuration passes validation."""
        assert configuration.validate() is None

    def test_validate_reports_unknown_conductor(self):
        """Test that a pair referencing an undefined conductor is rejected."""
        data = copy.deepcopy(CONFIG)
        data["pairs"]["pair1"]["members"] = ["w1", "missing"]
        with pytest.raises(AEDTRuntimeError, match="unknown conductor 'missing'"):
            CableBundleConfig.from_dict(data).validate()

    def test_validate_reports_missing_pair_location(self):
        """Test that a pair without a cross-section location is rejected."""
        data = copy.deepcopy(CONFIG)
        data["cross_section"]["pair_locations"] = {}
        with pytest.raises(AEDTRuntimeError, match="no entry in cross_section.pair_locations"):
            CableBundleConfig.from_dict(data).validate()

    def test_validate_reports_unknown_material(self):
        """Test that a shield referencing an undefined material is rejected."""
        data = copy.deepcopy(CONFIG)
        data["pairs"]["pair1"]["shield"]["material"] = "unobtainium"
        with pytest.raises(AEDTRuntimeError, match="Material 'unobtainium' is used but not defined"):
            CableBundleConfig.from_dict(data).validate()

    def test_schema_rejects_a_degenerate_route(self):
        """Test that a route with fewer than two points is rejected by the schema."""
        data = copy.deepcopy(CONFIG)
        data["routes"]["main"]["points"] = [[0.0, 0.0, 0.0]]
        with pytest.raises(AEDTRuntimeError, match="does not conform to schema"):
            CableBundleConfig.from_dict(data)

    def test_validate_reports_degenerate_route(self, configuration):
        """Test that a route whose points are not three-dimensional is rejected."""
        configuration.routes["main"].points = np.array([[0.0, 0.0], [1.0, 0.0]])
        with pytest.raises(AEDTRuntimeError, match=r"must be an \(N>=2, 3\) point list"):
            configuration.validate()

    def test_validate_reports_overlapping_pair_shields(self):
        """Test that pair shields placed closer than their diameter are rejected."""
        data = copy.deepcopy(CONFIG)
        data["conductors"]["w3"] = {"conductor_equivalent_radius": 0.227}
        data["conductors"]["w4"] = {"conductor_equivalent_radius": 0.227}
        data["pairs"]["pair2"] = {"members": ["w3", "w4"], "twist_pitch": 12.7}
        data["cross_section"]["pair_locations"]["pair2"] = {"center": [0.5, 0.0]}
        data["bundle"]["demo_bundle"]["members"] = ["pair1", "pair2"]
        with pytest.raises(AEDTRuntimeError, match="overlap"):
            CableBundleConfig.from_dict(data).validate()

    def test_validate_accumulates_every_error(self):
        """Test that all configuration problems are reported in a single exception."""
        data = copy.deepcopy(CONFIG)
        data["pairs"]["pair1"]["members"] = ["w1", "missing"]
        data["cross_section"]["pair_locations"] = {}
        with pytest.raises(AEDTRuntimeError) as excinfo:
            CableBundleConfig.from_dict(data).validate()

        message = str(excinfo.value)
        assert "unknown conductor" in message
        assert "cross_section.pair_locations" in message

    def test_schema_rejects_a_structurally_invalid_configuration(self):
        """Test that a configuration violating the JSON schema is rejected on parse."""
        data = copy.deepcopy(CONFIG)
        data["pairs"]["pair1"]["shield"]["type"] = "chain_mail"
        with pytest.raises(AEDTRuntimeError, match="does not conform to schema"):
            CableBundleConfig.from_dict(data)


class TestGeometry:
    """Test the Electronics Desktop independent cable geometry mathematics."""

    def test_unit_normalizes(self):
        """Test that a vector is scaled to unit length."""
        assert np.isclose(np.linalg.norm(geo.unit(np.array([3.0, 4.0, 0.0]))), 1.0)

    def test_normal_basis_is_orthonormal(self):
        """Test that the normal basis is orthonormal and normal to the tangent."""
        tangent = geo.unit(np.array([1.0, 2.0, 3.0]))
        n1, n2 = geo.normal_basis(tangent)

        assert np.isclose(np.linalg.norm(n1), 1.0)
        assert np.isclose(np.linalg.norm(n2), 1.0)
        assert np.isclose(np.dot(n1, n2), 0.0, atol=1e-12)
        assert np.isclose(np.dot(n1, tangent), 0.0, atol=1e-12)

    def test_rotate_about_axis_preserves_length_and_full_turn(self):
        """Test that rotation preserves length and that a full turn is the identity."""
        v = np.array([1.0, 0.0, 0.0])
        axis = np.array([0.0, 0.0, 1.0])

        assert np.allclose(geo.rotate_about_axis(v, axis, math.pi / 2.0), [0.0, 1.0, 0.0], atol=1e-12)
        assert np.allclose(geo.rotate_about_axis(v, axis, 2.0 * math.pi), v, atol=1e-12)

    def test_route_point_frames_stay_orthonormal_around_a_bend(self):
        """Test that transported frames remain orthonormal on a route with a bend."""
        route = np.array([[0.0, 0.0, 0.0], [50.0, 0.0, 0.0], [50.0, 50.0, 0.0], [50.0, 50.0, 50.0]])
        tangents, n1, n2 = geo.route_point_frames(route)

        assert n1.shape == route.shape
        assert n2.shape == route.shape
        for i in range(len(route)):
            assert np.isclose(np.linalg.norm(n1[i]), 1.0)
            assert np.isclose(np.linalg.norm(n2[i]), 1.0)
            assert np.isclose(np.dot(n1[i], n2[i]), 0.0, atol=1e-9)
            assert np.isclose(np.dot(n1[i], tangents[i]), 0.0, atol=1e-9)

    def test_twisted_centerline_has_the_requested_radius_and_pitch(self):
        """Test the helix radius and that one pitch corresponds to one full turn."""
        route = np.array([[0.0, 0.0, 0.0], [25.4, 0.0, 0.0]])
        _, n1, n2 = geo.route_point_frames(route)
        pitch = 12.7
        radius = 0.58

        helix = geo.twisted_centerline(
            route, np.array([0.0, 0.0]), n1, n2, radius=radius, pitch=pitch, phase=0.0, samples_per_pitch=64
        )

        offsets = helix - np.array([[x, 0.0, 0.0] for x in helix[:, 0]])
        assert np.allclose(np.linalg.norm(offsets, axis=1), radius, atol=1e-9)
        # The route is exactly two pitches long, so the helix closes twice.
        assert np.allclose(helix[0][1:], helix[-1][1:], atol=1e-6)

    def test_twisted_centerline_phase_puts_wires_opposite(self):
        """Test that a phase of pi places the two wires of a pair on opposite sides."""
        route = np.array([[0.0, 0.0, 0.0], [25.4, 0.0, 0.0]])
        _, n1, n2 = geo.route_point_frames(route)
        kwargs = {"radius": 0.58, "pitch": 12.7, "samples_per_pitch": 16}

        first = geo.twisted_centerline(route, np.array([0.0, 0.0]), n1, n2, phase=0.0, **kwargs)
        second = geo.twisted_centerline(route, np.array([0.0, 0.0]), n1, n2, phase=math.pi, **kwargs)

        assert np.allclose((first + second) / 2.0, [[x, 0.0, 0.0] for x in first[:, 0]], atol=1e-9)

    def test_extend_route_ends(self):
        """Test that the route is extended along its terminal tangents at both ends."""
        route = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0], [10.0, 10.0, 0.0]])
        extended = geo.extend_route_ends(route, 4.0)

        assert np.allclose(extended[0], [-4.0, 0.0, 0.0])
        assert np.allclose(extended[-1], [10.0, 14.0, 0.0])
        assert np.allclose(extended[1], route[1])

    def test_faceted_profile_points(self):
        """Test the vertex count, circumradius, and planarity of the swept profile."""
        start = np.array([1.0, 2.0, 3.0])
        tangent = np.array([0.0, 0.0, 1.0])
        points = geo.faceted_profile_points(start, tangent, radius=2.0, facets=8)

        assert len(points) == 8
        vertices = np.array(points)
        assert np.allclose(np.linalg.norm(vertices - start, axis=1), 2.0)
        assert np.allclose(vertices[:, 2], 3.0)

    def test_offset_route_points_shifts_in_the_normal_plane(self):
        """Test that a pair offset is applied in the plane normal to the route."""
        route = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]])
        _, n1, n2 = geo.route_point_frames(route)
        offset = geo.offset_route_points(route, np.array([1.0, 2.0]), n1, n2)

        assert offset.shape == route.shape
        assert np.allclose(offset[:, 0], route[:, 0])
        assert np.allclose(np.linalg.norm(offset - route, axis=1), math.sqrt(5.0))


class TestTransferImpedance:
    """Test the closed-form foil and braid transfer-impedance models."""

    def test_foil_transfer_impedance_tends_to_dc_resistance(self):
        """Test that the foil transfer impedance tends to the DC resistance at low frequency."""
        foil = ti.FoilShield(sigma=3.5e7, thickness_m=9e-6, cable_radius_m=1.15e-3, seam_inductance_h_per_m=0.0)
        dc_resistance = 1.0 / (foil.sigma * 2.0 * math.pi * foil.cable_radius_m * foil.thickness_m)

        value = foil.transfer_impedance(np.array([1.0]))[0]

        assert np.isclose(value.real, dc_resistance, rtol=1e-3)

    def test_foil_transfer_impedance_rolls_off_with_frequency(self):
        """Test that the diffusion term attenuates the transfer impedance as frequency rises."""
        foil = ti.FoilShield(sigma=3.5e7, thickness_m=9e-6, cable_radius_m=1.15e-3, seam_inductance_h_per_m=0.0)
        magnitudes = np.abs(foil.transfer_impedance(np.array([1e3, 1e6, 1e8, 1e9])))

        assert np.all(np.diff(magnitudes) < 0.0)

    def test_foil_seam_inductance_raises_high_frequency_impedance(self):
        """Test that a seam inductance increases the high-frequency transfer impedance."""
        common = {"sigma": 3.5e7, "thickness_m": 9e-6, "cable_radius_m": 1.15e-3}
        without = ti.FoilShield(seam_inductance_h_per_m=0.0, **common)
        with_seam = ti.FoilShield(seam_inductance_h_per_m=1e-9, **common)
        frequencies = np.array([1e9])

        assert abs(with_seam.transfer_impedance(frequencies)[0]) > abs(without.transfer_impedance(frequencies)[0])

    def test_braid_optical_coverage_matches_hand_calculation(self):
        """Test the braid fill factor and optical coverage against a hand calculation."""
        braid = ti.BraidShield(
            sigma=5.8e7,
            wire_diameter_m=0.1e-3,
            carriers=16,
            wires_per_carrier=8,
            weave_angle_deg=30.0,
            cable_radius_m=3.6e-3,
        )
        expected_fill = (16 * 8 * 0.1e-3) / (2.0 * math.pi * 3.6e-3 * math.cos(math.radians(30.0)))

        assert np.isclose(braid.fill_factor, expected_fill, rtol=1e-9)
        assert np.isclose(braid.optical_coverage, 2.0 * expected_fill - expected_fill**2, rtol=1e-9)
        assert 0.0 < braid.optical_coverage <= 1.0

    def test_braid_dc_resistance_is_positive_and_decreases_with_more_wires(self):
        """Test that adding carriers lowers the braid DC resistance."""
        common = {
            "sigma": 5.8e7,
            "wire_diameter_m": 0.1e-3,
            "wires_per_carrier": 8,
            "weave_angle_deg": 30.0,
            "cable_radius_m": 3.6e-3,
        }
        sparse = ti.BraidShield(carriers=16, **common)
        dense = ti.BraidShield(carriers=24, **common)

        assert sparse.dc_resistance_per_m > 0.0
        assert dense.dc_resistance_per_m < sparse.dc_resistance_per_m

    def test_braid_transfer_impedance_rises_at_high_frequency(self):
        """Test that aperture coupling dominates the braid transfer impedance at high frequency."""
        braid = ti.BraidShield(
            sigma=5.8e7,
            wire_diameter_m=0.1e-3,
            carriers=16,
            wires_per_carrier=8,
            weave_angle_deg=30.0,
            cable_radius_m=3.6e-3,
        )
        magnitudes = np.abs(braid.transfer_impedance(np.array([1e3, 1e9])))

        assert np.isclose(magnitudes[0], braid.dc_resistance_per_m, rtol=1e-2)
        assert magnitudes[1] > magnitudes[0]


class TestShieldModels:
    """Test the adapter that turns a shield definition into a transfer-impedance model."""

    def test_factory_builds_a_foil_model(self, configuration):
        """Test that a foil shield definition produces a foil model with converted units."""
        model = build_shield_model(
            configuration.pairs["pair1"].shield, radius_mm=1.15, materials=configuration.materials
        )

        assert isinstance(model, ti.FoilShield)
        assert np.isclose(model.thickness_m, 9e-6)
        assert np.isclose(model.cable_radius_m, 1.15e-3)
        assert np.isclose(model.sigma, 3.5e7)

    def test_factory_builds_a_braid_model(self, configuration):
        """Test that a braid shield definition produces a braid model with converted units."""
        model = build_shield_model(
            configuration.bundle.overall_shield, radius_mm=3.6, materials=configuration.materials
        )

        assert isinstance(model, ti.BraidShield)
        assert model.carriers == 16
        assert model.wires_per_carrier == 8
        assert np.isclose(model.wire_diameter_m, 1e-4)

    def test_factory_rejects_an_undefined_material(self, configuration):
        """Test that a shield whose material is absent from the material table is rejected."""
        shield = configuration.pairs["pair1"].shield
        with pytest.raises(ShieldModelError, match="is not defined in 'materials'"):
            build_shield_model(shield, radius_mm=1.15, materials={})

    def test_factory_rejects_a_material_without_conductivity(self, configuration):
        """Test that a shield material with no conductivity is rejected."""
        shield = configuration.pairs["pair1"].shield
        materials = dict(configuration.materials)
        materials["aluminum"].conductivity = None
        with pytest.raises(ShieldModelError, match="has no 'conductivity'"):
            build_shield_model(shield, radius_mm=1.15, materials=materials)

    def test_factory_rejects_a_foil_without_thickness(self, configuration):
        """Test that a foil shield with no thickness is rejected."""
        shield = configuration.pairs["pair1"].shield
        shield.thickness = None
        with pytest.raises(ShieldModelError, match="requires a 'thickness'"):
            build_shield_model(shield, radius_mm=1.15, materials=configuration.materials)

    def test_measured_shield_interpolates(self):
        """Test that measured data is interpolated on a logarithmic frequency axis."""
        frequencies = np.array([1e3, 1e6, 1e9])
        values = np.array([1.0 + 0.0j, 2.0 + 0.0j, 4.0 + 0.0j])
        model = MeasuredShield(frequencies, values)

        assert np.allclose(model.transfer_impedance(frequencies), values)
        # 10^4.5 Hz is the geometric midpoint between 1 kHz and 1 MHz.
        assert np.isclose(model.transfer_impedance(np.array([10**4.5]))[0].real, 1.5)

    def test_measured_shield_rejects_mismatched_lengths(self):
        """Test that mismatched frequency and impedance arrays are rejected."""
        with pytest.raises(ValueError, match="equal length"):
            MeasuredShield(np.array([1e3, 1e6]), np.array([1.0 + 0.0j]))


class TestRoutedCableBundle:
    """Test the HFSS builder against a mocked design."""

    def test_build_creates_the_expected_objects(self, configuration, mock_hfss):
        """Test that a full build creates every conductor, shield, boundary, and port."""
        bundle = RoutedCableBundle(configuration, mock_hfss, name_prefix="cbl")
        artifacts = bundle.build()

        assert artifacts.conductors == ["cbl_w1_cu", "cbl_w2_cu"]
        assert artifacts.insulation == ["cbl_w1_ins", "cbl_w2_ins"]
        assert artifacts.pair_shields == ["cbl_pair1_foil_shield"]
        assert artifacts.overall_shield == ["cbl_overall_braid"]
        assert artifacts.jacket == ["cbl_pvc_jacket"]
        assert artifacts.ports == ["cbl_P_w1_in", "cbl_P_w1_out", "cbl_P_w2_in", "cbl_P_w2_out"]
        assert artifacts.datasets == [
            "cbl_ZT_pair1_re",
            "cbl_ZT_pair1_im",
            "cbl_ZT_overall_braid_re",
            "cbl_ZT_overall_braid_im",
        ]
        assert set(artifacts.as_dict()) == set(BuildArtifacts().as_dict())

    def test_ensure_materials_creates_and_assigns_properties(self, configuration, mock_hfss):
        """Test that every configured material is created with its physical properties."""
        material = MagicMock()
        mock_hfss.materials.add_material.return_value = material

        RoutedCableBundle(configuration, mock_hfss).ensure_materials()

        created = [call.args[0] for call in mock_hfss.materials.add_material.call_args_list]
        assert created == ["copper", "aluminum", "pe_foam", "pvc"]
        assert material.conductivity == 3.5e7
        assert material.permittivity == 3.0
        assert material.dielectric_loss_tangent == 0.02

    def test_existing_materials_are_reused(self, configuration, mock_hfss):
        """Test that a material already present in the design is updated instead of recreated."""
        mock_hfss.materials.material_keys = {"copper": MagicMock()}

        RoutedCableBundle(configuration, mock_hfss).ensure_materials()

        created = [call.args[0] for call in mock_hfss.materials.add_material.call_args_list]
        assert "copper" not in created

    def test_shield_boundaries_use_a_frequency_dependent_dataset(self, configuration, mock_hfss):
        """Test that a transfer-impedance dataset drives each shield impedance boundary."""
        frequencies = np.array([1e3, 1e6, 1e9])
        bundle = RoutedCableBundle(configuration, mock_hfss, frequencies=frequencies)
        bundle.build_geometry()
        bundle.assign_shield_boundaries()

        dataset_call = mock_hfss.create_dataset.call_args_list[0]
        assert dataset_call.args[0] == "cbl_ZT_pair1_re"
        assert dataset_call.args[1] == frequencies.tolist()
        assert len(dataset_call.args[2]) == 3
        assert all(np.isfinite(value) for value in dataset_call.args[2])
        assert dataset_call.kwargs["x_unit"] == "Hz"
        assert dataset_call.kwargs["y_unit"] == "ohm"

        boundary_call = mock_hfss.assign_impedance_to_sheet.call_args_list[0]
        assert boundary_call.args[0] == "cbl_pair1_foil_shield"
        assert boundary_call.kwargs["resistance"] == "pwl(cbl_ZT_pair1_re, Freq)"
        assert boundary_call.kwargs["reactance"] == "pwl(cbl_ZT_pair1_im, Freq)"

    def test_shield_model_factory_can_be_injected(self, configuration, mock_hfss):
        """Test that a custom shield model factory overrides the analytic models."""
        measured = MeasuredShield(np.array([1e3, 1e9]), np.array([1.0 + 0.0j, 2.0 + 0.0j]))
        bundle = RoutedCableBundle(
            configuration,
            mock_hfss,
            frequencies=np.array([1e3, 1e9]),
            shield_model_factory=lambda shield, **kwargs: measured,
        )
        bundle.build_geometry()
        bundle.assign_shield_boundaries()

        circ = 2.0 * math.pi * 1.15e-3
        expected = [pytest.approx(1.0 * circ), pytest.approx(2.0 * circ)]
        assert mock_hfss.create_dataset.call_args_list[0].args[2] == expected

    def test_create_ports_uses_the_overall_shield_as_reference(self, configuration, mock_hfss):
        """Test that a port is created at each conductor end against the shield reference."""
        bundle = RoutedCableBundle(configuration, mock_hfss)
        bundle.build_geometry()
        bundle.create_ports()

        assert mock_hfss.circuit_port.call_count == 4
        first = mock_hfss.circuit_port.call_args_list[0]
        assert first.kwargs["name"] == "cbl_P_w1_in"
        assert first.kwargs["impedance"] == 50.0
        assert first.kwargs["renorm_impedance"] == "50.0"
        assert bundle.port_pairs["w1"] == ("cbl_P_w1_in", "cbl_P_w1_out")

    def test_create_ports_before_geometry_raises(self, configuration, mock_hfss):
        """Test that creating ports before the geometry exists reports a clear error."""
        bundle = RoutedCableBundle(configuration, mock_hfss)
        with pytest.raises(AEDTRuntimeError, match="before the geometry is built"):
            bundle.create_ports()

    def test_unsupported_port_reference_raises(self, configuration, mock_hfss):
        """Test that a ground plane port reference reports a clear error."""
        configuration.simulation.ports.reference = "ground_plane"
        bundle = RoutedCableBundle(configuration, mock_hfss)
        bundle.build_geometry()
        with pytest.raises(AEDTRuntimeError, match="is not supported"):
            bundle.create_ports()

    def test_define_differential_pairs(self, configuration, mock_hfss):
        """Test that the configured differential pairs are registered on both ends."""
        bundle = RoutedCableBundle(configuration, mock_hfss)
        bundle.build_geometry()
        bundle.create_ports()
        assert bundle.define_differential_pairs() is True

        assert mock_hfss.set_differential_pair.call_count == 2
        first = mock_hfss.set_differential_pair.call_args_list[0]
        assert first.kwargs["assignment"] == "cbl_P_w1_in"
        assert first.kwargs["reference"] == "cbl_P_w2_in"
        assert first.kwargs["common_mode"] == "cbl_CM0"
        assert first.kwargs["differential_mode"] == "cbl_DM0"
        assert first.kwargs["differential_reference"] == 100.0
        assert first.kwargs["common_reference"] == 25.0

    def test_define_differential_pairs_without_ports(self, configuration, mock_hfss):
        """Test that no differential pair is registered when no port exists."""
        bundle = RoutedCableBundle(configuration, mock_hfss)

        assert bundle.define_differential_pairs() is False
        mock_hfss.set_differential_pair.assert_not_called()

    def test_create_setup_uses_the_configured_frequency_range(self, configuration, mock_hfss):
        """Test that the setup and sweep span the configured frequency range."""
        bundle = RoutedCableBundle(configuration, mock_hfss)
        setup = bundle.create_setup(name="Sparam", num_points=101)

        assert mock_hfss.create_setup.call_args.kwargs["name"] == "Sparam"
        assert mock_hfss.create_setup.call_args.kwargs["Frequency"] == "5.000e+08Hz"
        sweep = setup.create_frequency_sweep.call_args.kwargs
        assert sweep["start_frequency"] == 1.0e6
        assert sweep["stop_frequency"] == 1.0e9
        assert sweep["num_of_freq_points"] == 101
        assert sweep["sweep_type"] == "Interpolating"

    def test_create_setup_raises_when_hfss_fails(self, configuration, mock_hfss):
        """Test that a failed setup creation is surfaced as an error."""
        mock_hfss.create_setup.return_value = False
        bundle = RoutedCableBundle(configuration, mock_hfss)

        with pytest.raises(AEDTRuntimeError, match="Failed to create the HFSS setup 'Sparam'"):
            bundle.create_setup(name="Sparam")

    def test_build_can_skip_optional_steps(self, configuration, mock_hfss):
        """Test that ports, boundaries, and differential pairs can be skipped."""
        bundle = RoutedCableBundle(configuration, mock_hfss)
        artifacts = bundle.build(create_ports=False, assign_shield_boundaries=False, define_differential_pairs=False)

        assert artifacts.conductors
        assert artifacts.ports == []
        assert artifacts.boundaries == []
        mock_hfss.circuit_port.assert_not_called()
        mock_hfss.assign_impedance_to_sheet.assert_not_called()

    def test_from_file(self, tmp_path, mock_hfss):
        """Test that the builder can be created directly from a configuration file."""
        file_path = tmp_path / "bundle.json"
        file_path.write_text(json.dumps(CONFIG), encoding="utf-8")

        bundle = RoutedCableBundle.from_file(file_path, mock_hfss)

        assert bundle.configuration.bundle.name == "demo_bundle"
        assert bundle.frequencies.shape == (71,)

    def test_missing_impedance_boundary_raises(self, configuration, mock_hfss):
        """Test that a failed impedance boundary assignment reports a clear error."""
        mock_hfss.assign_impedance_to_sheet.return_value = None
        bundle = RoutedCableBundle(configuration, mock_hfss)
        bundle.build_geometry()

        with pytest.raises(AEDTRuntimeError, match="could not be assigned"):
            bundle.assign_shield_boundaries()

    def test_transfer_impedance_unit_conversion_is_pinned(self, configuration, mock_hfss):
        """Test that ohm/m values from the shield model are correctly converted to ohm/square in the dataset.

        With a fake shield model returning 3+4j ohm/m, the _re dataset must equal
        3 * 2*pi*r and the _im dataset must equal 4 * 2*pi*r, where r is the shield
        radius in metres. The pair and overall shields use their respective radii.
        """
        fake_zt = 3.0 + 4.0j  # ohm/m — constant at every frequency
        fake_model = MeasuredShield(np.array([1e6]), np.array([fake_zt]))
        bundle = RoutedCableBundle(
            configuration,
            mock_hfss,
            frequencies=np.array([1e6]),
            shield_model_factory=lambda shield, **kw: fake_model,
        )
        bundle.build_geometry()
        bundle.assign_shield_boundaries()

        r_pair = 1.15e-3  # m — pair_shield_radius from CONFIG
        r_overall = 3.6e-3  # m — overall_shield_radius from CONFIG
        calls = mock_hfss.create_dataset.call_args_list
        # Order: pair_re, pair_im, overall_re, overall_im
        re_pair = calls[0].args[2][0]
        im_pair = calls[1].args[2][0]
        re_overall = calls[2].args[2][0]
        im_overall = calls[3].args[2][0]

        assert re_pair == pytest.approx(3.0 * 2.0 * math.pi * r_pair, rel=1e-9)
        assert im_pair == pytest.approx(4.0 * 2.0 * math.pi * r_pair, rel=1e-9)
        assert re_overall == pytest.approx(3.0 * 2.0 * math.pi * r_overall, rel=1e-9)
        assert im_overall == pytest.approx(4.0 * 2.0 * math.pi * r_overall, rel=1e-9)

    def test_build_raises_on_second_call(self, configuration, mock_hfss):
        """Test that calling build() twice on the same instance raises AEDTRuntimeError."""
        bundle = RoutedCableBundle(configuration, mock_hfss)
        bundle.build(create_ports=False, assign_shield_boundaries=False, define_differential_pairs=False)
        with pytest.raises(AEDTRuntimeError, match="already been built"):
            bundle.build(create_ports=False, assign_shield_boundaries=False, define_differential_pairs=False)

    def test_build_geometry_raises_on_second_call(self, configuration, mock_hfss):
        """Test that calling build_geometry() twice on the same instance raises AEDTRuntimeError."""
        bundle = RoutedCableBundle(configuration, mock_hfss)
        bundle.build_geometry()
        with pytest.raises(AEDTRuntimeError, match="already exists"):
            bundle.build_geometry()

    def test_lumped_port_type_warns_once_and_creates_circuit_ports(self, configuration, mock_hfss):
        """Test that a lumped port type logs exactly one warning and still creates circuit ports."""
        configuration.simulation.ports.kind = "lumped"
        bundle = RoutedCableBundle(configuration, mock_hfss)
        bundle.build_geometry()
        bundle.create_ports()

        bundle.logger.warning.assert_called_once()
        assert mock_hfss.circuit_port.call_count == 4  # 2 conductors × 2 ends

    def test_create_dataset_failure_raises(self, configuration, mock_hfss):
        """Test that a False return from create_dataset is surfaced as AEDTRuntimeError naming the dataset."""
        mock_hfss.create_dataset.return_value = False
        bundle = RoutedCableBundle(configuration, mock_hfss, frequencies=np.array([1e6]))
        bundle.build_geometry()
        with pytest.raises(AEDTRuntimeError, match="cbl_ZT_pair1_re"):
            bundle.assign_shield_boundaries()

    def test_ensure_materials_sets_per_material_properties(self, configuration, mock_hfss):
        """Test that distinct mock objects per material receive the correct physical properties.

        A side_effect that returns a separate MagicMock per material name allows asserting
        that the conductor (copper) gets conductivity and the dielectric (pe_foam) gets
        permittivity and loss_tangent independently.
        """
        material_mocks = {name: MagicMock() for name in ["copper", "aluminum", "pe_foam", "pvc"]}
        mock_hfss.materials.add_material.side_effect = lambda name: material_mocks[name]

        RoutedCableBundle(configuration, mock_hfss).ensure_materials()

        assert material_mocks["copper"].conductivity == 5.8e7
        assert material_mocks["aluminum"].conductivity == 3.5e7
        assert material_mocks["pe_foam"].permittivity == 1.5
        assert material_mocks["pe_foam"].dielectric_loss_tangent == 0.0005
        assert material_mocks["pvc"].permittivity == 3.0
        assert material_mocks["pvc"].dielectric_loss_tangent == 0.02


class TestConfigurationHardeningRegression:
    """Regression tests for the hardening fixes applied to CableBundleConfig.validate()."""

    def test_validate_rejects_zero_twist_pitch(self, configuration):
        """Test that twist_pitch == 0 is rejected with a clear message."""
        configuration.pairs["pair1"].twist_pitch = 0.0
        with pytest.raises(AEDTRuntimeError, match="twist_pitch"):
            configuration.validate()

    def test_validate_rejects_negative_twist_pitch(self, configuration):
        """Test that a negative twist pitch is rejected by validate()."""
        configuration.pairs["pair1"].twist_pitch = -5.0
        with pytest.raises(AEDTRuntimeError, match="twist_pitch"):
            configuration.validate()

    def test_validate_rejects_pair_shield_nesting_violation(self, configuration):
        """Test that pair_shield_radius < insulation.outer_radius + pair_wire_center_offset is rejected."""
        # insulation.outer_radius=0.55, pair_wire_center_offset=0.58 → sum=1.13 > 0.5
        configuration.simulation.geometry.pair_shield_radius = 0.5
        with pytest.raises(AEDTRuntimeError, match="insulated wire extends outside pair shield"):
            configuration.validate()

    def test_validate_rejects_zero_conductor_radius(self, configuration):
        """Test that conductor_equivalent_radius of zero is rejected by the positivity check."""
        configuration.conductors["w1"].equivalent_radius = 0.0
        with pytest.raises(AEDTRuntimeError, match="equivalent_radius"):
            configuration.validate()


class TestTransferImpedanceHardeningRegression:
    """Regression tests for the hardening fixes applied to BraidShield and MeasuredShield."""

    def test_braid_diffusion_term_is_grid_independent(self):
        """Test that the diffusion term value at 1 GHz is identical regardless of the surrounding frequency grid."""
        braid = ti.BraidShield(
            sigma=5.8e7,
            wire_diameter_m=0.1e-3,
            carriers=16,
            wires_per_carrier=8,
            weave_angle_deg=30.0,
            cable_radius_m=3.6e-3,
        )
        value_single = braid._diffusion_term(np.array([1e9]))[0]
        value_grid = braid._diffusion_term(np.array([1e3, 1e6, 1e9]))[2]
        assert value_single == pytest.approx(value_grid)

        # An empty frequency array must not raise IndexError.
        result = braid._diffusion_term(np.array([]))
        assert result.shape == (0,)

        # DC limit: as f -> 0 the diffusion term approaches dc_resistance_per_m.
        # At 1 mHz the where-branch in _diffusion_impedance fires (|gamma_t| << 1e-6),
        # so the DC limit is exact.
        dc_value = braid._diffusion_term(np.array([1e-3]))[0].real
        assert dc_value == pytest.approx(braid.dc_resistance_per_m, rel=1e-9)

    def test_braid_optical_coverage_clips_to_one_for_dense_braid(self):
        """Test that fill_factor > 1 clamps optical_coverage to 1.0 and emits a warning."""
        braid = ti.BraidShield(
            sigma=5.8e7,
            wire_diameter_m=1.0e-3,  # deliberately large → fill_factor >> 1
            carriers=16,
            wires_per_carrier=8,
            weave_angle_deg=30.0,
            cable_radius_m=3.6e-3,
        )
        assert braid.fill_factor > 1.0  # raw value is unclipped
        with patch("ansys.aedt.core.aedt_logger.pyaedt_logger") as mock_log:
            cov = braid.optical_coverage
        assert cov == 1.0
        mock_log.warning.assert_called_once()

    def test_report_zt_logs_at_spot_frequencies(self):
        """Test that report_zt emits one header line plus one line per checkpoint frequency."""
        freqs = np.array([1e3, 1e6, 1e8, 1e9])
        zt = np.array([1.0, 2.0, 3.0, 4.0]) * 1e-3  # ohm/m — simple real values
        with patch("ansys.aedt.core.aedt_logger.pyaedt_logger") as mock_log:
            ti.report_zt("test_shield", zt, freqs)
        # 1 header + 4 checkpoints = 5 info calls
        assert mock_log.info.call_count == 5
        # Second call: f_actual=1e3 Hz, mag = 1e-3 * 1e3 = 1.0 mOhm/m
        second = mock_log.info.call_args_list[1]
        assert second.args[2] == pytest.approx(1.0)  # mag argument

    def test_measured_shield_clamps_out_of_range_frequencies(self):
        """Test that MeasuredShield clamps to boundary values rather than extrapolating."""
        frequencies = np.array([1e3, 1e6, 1e9])
        values = np.array([1.0 + 0.0j, 2.0 + 0.0j, 4.0 + 0.0j])
        model = MeasuredShield(frequencies, values)

        below = model.transfer_impedance(np.array([1.0]))  # below lowest tabulated frequency
        above = model.transfer_impedance(np.array([1e12]))  # above highest tabulated frequency

        assert below[0].real == pytest.approx(1.0)  # clamped to first tabulated value
        assert above[0].real == pytest.approx(4.0)  # clamped to last tabulated value


class TestShieldModelsHardeningRegression:
    """Regression tests for hardening fixes in shield_models.build_shield_model."""

    def test_factory_raises_for_braid_missing_required_key(self, configuration):
        """Test that build_shield_model raises ShieldModelError naming the missing key for a braid shield."""
        shield = configuration.bundle.overall_shield  # braid
        # Omit wires_per_carrier and weave_angle
        shield.construction = {"wire_diameter": 0.1, "carriers": 16}
        with pytest.raises(ShieldModelError, match="missing required key"):
            build_shield_model(shield, radius_mm=3.6, materials=configuration.materials)
