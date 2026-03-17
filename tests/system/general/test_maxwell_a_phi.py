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


import pytest

from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.modules.boundary.maxwell_boundary import GCSourceACMagneticAPhi
from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixACMagneticAPhi
from ansys.aedt.core.modules.boundary.maxwell_boundary import RLSourceACMagneticAPhi


@pytest.fixture
def m3d_app(add_app):
    app = add_app(application=Maxwell3d, solution_type="AC Magnetic APhi")
    yield app
    app.close_project(app.project_name, save=False)


class TestMaxwellAPhiExcitations:
    def test_assign_current(self, m3d_app):
        cyl = m3d_app.modeler.create_cylinder(orientation="XY", origin=[0, 0, 0], radius=10, height=100)

        current1 = m3d_app.assign_current(
            assignment=[cyl.top_face_z],
            amplitude="10A",
            phase="0deg",
        )
        assert current1.props["Current"] == "10A"
        assert current1.props["Phase"] == "0deg"
        assert not current1.props["Point out of terminal"]
        assert current1.props["CurrentExcitationModel"] == "Single Potential"
        assert current1.props["Faces"][0] == cyl.top_face_z.id

    def test_assign_assign_voltage(self, m3d_app):
        cyl = m3d_app.modeler.create_cylinder(orientation="XY", origin=[0, 0, 0], radius=10, height=100)

        m3d_app.modeler.create_region([50, 50, 50, 50, 50, 50])

        voltage = m3d_app.assign_voltage(
            assignment=[cyl.top_face_z], amplitude="10V", excitation_model="Double Potentials with Ground"
        )

        assert voltage.props["Voltage"] == "10V"
        assert voltage.props["Faces"][0] == cyl.top_face_z.id
        assert not voltage.props["VoltageAPhi_Point_out_of_terminal"]
        assert voltage.props["VoltageAPhiExcitationModel"] == "Double Potentials with Ground"


class TestMaxwellAPhiBoundaries:
    def test_assign_flux_tangential(self, m3d_app):
        m3d_app.modeler.create_cylinder(orientation="XY", origin=[0, 0, 0], radius=10, height=100)

        region = m3d_app.modeler.create_region([50, 50, 50, 50, 50, 50])

        flux_tangential = m3d_app.assign_flux_tangential(assignment=region.top_face_z, flux_name="my_bound")

        assert flux_tangential.name == "my_bound"
        assert flux_tangential.props["Faces"][0] == region.top_face_z.id


class TestMaxwellAPhiParameters:
    def test_assign_matrix(self, m3d_app):
        cyl = m3d_app.modeler.create_cylinder(
            orientation="XY", origin=[0, 0, 0], radius=10, height=100, material="copper"
        )
        cyl1 = m3d_app.modeler.create_cylinder(
            orientation="XY", origin=[20, 0, 0], radius=10, height=100, material="copper"
        )

        m3d_app.modeler.create_region([50, 50, 50, 50, 0, 0])

        current = m3d_app.assign_current(assignment=[cyl.top_face_z])
        current1 = m3d_app.assign_current(assignment=[cyl1.top_face_z])
        current2 = m3d_app.assign_current(assignment=[cyl.bottom_face_z], swap_direction=True)
        current3 = m3d_app.assign_current(assignment=[cyl1.bottom_face_z], swap_direction=True)

        rl_source = RLSourceACMagneticAPhi(signal_sources=[current.name], ground_sources=[current2.name])
        gc_source = GCSourceACMagneticAPhi(signal_sources=[current1.name], ground_sources=[current3.name])

        matrix_args = MatrixACMagneticAPhi(
            rl_sources=[rl_source],
            gc_sources=[gc_source],
            matrix_name="test_matrix",
        )
        matrix = m3d_app.assign_matrix(matrix_args)
        assert matrix.props["RLMatrix"]["MatrixEntry"]["MatrixEntry"][0]["Source"] == current.name
        assert matrix.props["GCMatrix"]["MatrixEntry"]["MatrixEntry"][0]["Source"] == current1.name
        assert matrix.name == "test_matrix"

    def test_assign_force(self, m3d_app):
        cyl = m3d_app.modeler.create_cylinder(
            orientation="XY", origin=[0, 0, 0], radius=10, height=100, material="copper"
        )

        force = m3d_app.assign_force(assignment=cyl, is_virtual=True)
        assert force.props["Name"] == force.name
        assert force.props["Objects"][0] == cyl.name
        assert force.props["Reference CS"] == "Global"
        assert force.props["Is Virtual"]

    def test_assign_torque(self, m3d_app):
        cyl = m3d_app.modeler.create_cylinder(
            orientation="XY", origin=[0, 0, 0], radius=10, height=100, material="copper"
        )

        torque = m3d_app.assign_torque(assignment=cyl, is_positive=False, is_virtual=True)
        assert torque.props["Name"] == torque.name
        assert torque.props["Objects"][0] == cyl.name
        assert torque.props["Coordinate System"] == "Global"
        assert torque.props["Is Virtual"]
        assert not torque.props["Is Positive"]
