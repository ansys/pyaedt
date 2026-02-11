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

from ansys.aedt.core import Circuit
from ansys.aedt.core import CircuitNetlist
from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Icepak
from ansys.aedt.core import Maxwell2d
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core import Mechanical
from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from ansys.aedt.core import Rmxprt
from ansys.aedt.core import TwinBuilder
from ansys.aedt.core.generic.aedt_constants import DesignType
from ansys.aedt.core.generic.constants import SolutionsHfss
from ansys.aedt.core.generic.constants import SolutionsIcepak
from ansys.aedt.core.generic.constants import SolutionsMaxwell2D
from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
from ansys.aedt.core.generic.constants import SolutionsMechanical
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.generic.settings import settings

settings.lazy_load = False
settings.wait_for_license = True


def test_run_desktop_mechanical(desktop) -> None:
    aedtapp = Mechanical(solution_type=SolutionsMechanical.SteadyStateThermal)
    assert aedtapp.design_type == DesignType.ICEPAKFEA
    assert aedtapp.solution_type == SolutionsMechanical.SteadyStateThermal

    aedtapp.solution_type = SolutionsMechanical.Modal
    assert aedtapp.solution_type == SolutionsMechanical.Modal

    aedtapp.solution_type = SolutionsMechanical.Thermal
    assert aedtapp.solution_type == SolutionsMechanical.SteadyStateThermal

    aedtapp.solution_type = SolutionsMechanical.Structural
    assert aedtapp.solution_type == SolutionsMechanical.Structural

    aedtapp.solution_type = SolutionsMechanical.TransientThermal
    assert aedtapp.solution_type == SolutionsMechanical.TransientThermal
    aedtapp.close_project(save=False)


def test_run_desktop_circuit(desktop) -> None:
    aedtapp = Circuit()
    assert aedtapp.design_type == "Circuit Design"
    assert aedtapp.solution_type == "NexximLNA"
    aedtapp.close_project(save=False)


def test_run_desktop_icepak(desktop) -> None:
    aedtapp = Icepak(solution_type=SolutionsIcepak.SteadyState)
    assert aedtapp.design_type == "Icepak"
    assert aedtapp.solution_type == SolutionsIcepak.SteadyState

    aedtapp.solution_type = SolutionsIcepak.Transient
    assert aedtapp.solution_type == SolutionsIcepak.Transient
    aedtapp.close_project(save=False)


def test_run_desktop_hfss3dlayout(desktop) -> None:
    aedtapp = Hfss3dLayout(ic_mode=True)
    assert aedtapp.design_type == "HFSS 3D Layout Design"
    assert aedtapp.solution_type == "HFSS3DLayout"
    assert aedtapp.ic_mode
    aedtapp.ic_mode = False
    assert not aedtapp.ic_mode
    aedtapp.close_project(save=False)


@pytest.mark.skipif(is_linux, reason="Not supported in Linux.")
def test_run_desktop_twinbuilder(desktop) -> None:
    aedtapp = TwinBuilder()
    assert aedtapp.design_type == "Twin Builder"
    assert aedtapp.solution_type == "TR"
    aedtapp.close_project(save=False)


def test_run_desktop_q2d(desktop) -> None:
    aedtapp = Q2d()
    assert aedtapp.design_type == "2D Extractor"
    assert aedtapp.solution_type == "Open"
    aedtapp.close_project(save=False)


def test_run_desktop_q3d(desktop) -> None:
    aedtapp = Q3d()
    assert aedtapp.design_type == "Q3D Extractor"
    aedtapp.close_project(save=False)


def test_run_desktop_maxwell2d(desktop) -> None:
    solutions_maxwell_2d = SolutionsMaxwell2D

    aedtapp = Maxwell2d(solution_type=solutions_maxwell_2d.MagnetostaticZ)
    assert aedtapp.design_type == "Maxwell 2D"
    assert aedtapp.solution_type == solutions_maxwell_2d.Magnetostatic

    aedtapp.solution_type = solutions_maxwell_2d.MagnetostaticXY
    assert aedtapp.solution_type == solutions_maxwell_2d.Magnetostatic

    aedtapp.solution_type = solutions_maxwell_2d.Magnetostatic
    assert aedtapp.solution_type == solutions_maxwell_2d.Magnetostatic

    aedtapp.solution_type = solutions_maxwell_2d.TransientXY
    assert aedtapp.solution_type == solutions_maxwell_2d.Transient

    aedtapp.solution_type = solutions_maxwell_2d.TransientZ
    assert aedtapp.solution_type == solutions_maxwell_2d.Transient

    aedtapp.solution_type = solutions_maxwell_2d.Transient
    assert aedtapp.solution_type == solutions_maxwell_2d.Transient

    aedtapp.solution_type = solutions_maxwell_2d.ACMagneticXY
    assert aedtapp.solution_type == solutions_maxwell_2d.ACMagnetic

    aedtapp.solution_type = solutions_maxwell_2d.ACMagneticZ
    assert aedtapp.solution_type == solutions_maxwell_2d.ACMagnetic

    aedtapp.solution_type = solutions_maxwell_2d.ACMagnetic
    assert aedtapp.solution_type == solutions_maxwell_2d.ACMagnetic

    # Eddy current deprecated in 2025.2
    aedtapp.solution_type = solutions_maxwell_2d.EddyCurrentXY
    assert aedtapp.solution_type == solutions_maxwell_2d.EddyCurrent

    aedtapp.solution_type = solutions_maxwell_2d.EddyCurrentZ
    assert aedtapp.solution_type == solutions_maxwell_2d.EddyCurrent

    aedtapp.solution_type = solutions_maxwell_2d.EddyCurrent
    assert aedtapp.solution_type == solutions_maxwell_2d.EddyCurrent

    aedtapp.solution_type = solutions_maxwell_2d.ElectroStaticXY
    assert aedtapp.solution_type == solutions_maxwell_2d.ElectroStatic

    aedtapp.solution_type = solutions_maxwell_2d.ElectroStaticZ
    assert aedtapp.solution_type == solutions_maxwell_2d.ElectroStatic

    aedtapp.solution_type = solutions_maxwell_2d.ElectroStatic
    assert aedtapp.solution_type == solutions_maxwell_2d.ElectroStatic

    aedtapp.solution_type = solutions_maxwell_2d.DCConductionXY
    assert aedtapp.solution_type == solutions_maxwell_2d.DCConduction

    aedtapp.solution_type = solutions_maxwell_2d.DCConductionZ
    assert aedtapp.solution_type == solutions_maxwell_2d.DCConduction

    aedtapp.solution_type = solutions_maxwell_2d.DCConduction
    assert aedtapp.solution_type == solutions_maxwell_2d.DCConduction

    aedtapp.solution_type = solutions_maxwell_2d.ACConductionXY
    assert aedtapp.solution_type == solutions_maxwell_2d.ACConduction

    aedtapp.solution_type = solutions_maxwell_2d.ACConductionZ
    assert aedtapp.solution_type == solutions_maxwell_2d.ACConduction

    aedtapp.solution_type = solutions_maxwell_2d.ACConduction
    assert aedtapp.solution_type == solutions_maxwell_2d.ACConduction
    aedtapp.close_project(save=False)


def test_run_desktop_hfss(desktop) -> None:
    aedtapp = Hfss(solution_type=SolutionsHfss.DrivenTerminal)
    assert aedtapp.design_type == "HFSS"
    assert aedtapp.solution_type == SolutionsHfss.DrivenTerminal

    aedtapp.solution_type = SolutionsHfss.DrivenModal
    assert aedtapp.solution_type == SolutionsHfss.DrivenModal

    aedtapp.solution_type = SolutionsHfss.Transient
    assert aedtapp.solution_type == SolutionsHfss.Transient

    aedtapp.solution_type = SolutionsHfss.SBR
    assert aedtapp.solution_type == SolutionsHfss.SBR

    aedtapp.solution_type = SolutionsHfss.EigenMode
    assert aedtapp.solution_type == SolutionsHfss.EigenMode

    aedtapp.solution_type = SolutionsHfss.CharacteristicMode
    assert aedtapp.solution_type == SolutionsHfss.CharacteristicMode
    aedtapp.close_project(save=False)


def test_run_desktop_maxwell3d(desktop) -> None:
    solutions_maxwell_3d = SolutionsMaxwell3D

    aedtapp = Maxwell3d(solution_type=solutions_maxwell_3d.Magnetostatic)
    assert aedtapp.design_type == "Maxwell 3D"
    assert aedtapp.solution_type == solutions_maxwell_3d.Magnetostatic

    aedtapp.solution_type = solutions_maxwell_3d.Transient
    assert aedtapp.solution_type == solutions_maxwell_3d.Transient

    # Deprecated in 2025.2
    aedtapp.solution_type = solutions_maxwell_3d.EddyCurrent
    assert aedtapp.solution_type == solutions_maxwell_3d.EddyCurrent

    aedtapp.solution_type = solutions_maxwell_3d.ACMagnetic
    assert aedtapp.solution_type == solutions_maxwell_3d.ACMagnetic

    aedtapp.solution_type = solutions_maxwell_3d.ElectroStatic
    assert aedtapp.solution_type == solutions_maxwell_3d.ElectroStatic

    aedtapp.solution_type = solutions_maxwell_3d.DCConduction
    assert aedtapp.solution_type == solutions_maxwell_3d.DCConduction

    aedtapp.solution_type = solutions_maxwell_3d.ElectroDCConduction
    assert aedtapp.solution_type == solutions_maxwell_3d.ElectroDCConduction

    aedtapp.solution_type = solutions_maxwell_3d.ACConduction
    assert aedtapp.solution_type == solutions_maxwell_3d.ACConduction

    aedtapp.solution_type = solutions_maxwell_3d.ElectricTransient
    assert aedtapp.solution_type == solutions_maxwell_3d.ElectricTransient

    aedtapp.solution_type = solutions_maxwell_3d.TransientAPhiFormulation
    assert aedtapp.solution_type == solutions_maxwell_3d.TransientAPhiFormulation

    aedtapp.solution_type = solutions_maxwell_3d.DCBiasedEddyCurrent
    assert aedtapp.solution_type == solutions_maxwell_3d.DCBiasedEddyCurrent

    aedtapp.solution_type = solutions_maxwell_3d.TransientAPhi
    assert aedtapp.solution_type == solutions_maxwell_3d.TransientAPhi

    aedtapp.solution_type = solutions_maxwell_3d.ElectricDCConduction
    assert aedtapp.solution_type == solutions_maxwell_3d.ElectricDCConduction

    aedtapp.solution_type = solutions_maxwell_3d.ACMagneticwithDC
    assert aedtapp.solution_type == solutions_maxwell_3d.ACMagneticwithDC
    aedtapp.close_project(save=False)


def test_run_desktop_circuit_netlist(desktop) -> None:
    aedtapp = CircuitNetlist()
    assert aedtapp.design_type == "Circuit Netlist"
    assert aedtapp.solution_type == ""
    aedtapp.close_project(save=False)


def test_run_desktop_rmxprt(desktop) -> None:
    aedtapp = Rmxprt()
    assert aedtapp.design_type == DesignType.RMXPRT.NAME
    assert aedtapp.solution_type == DesignType.RMXPRT.solution_default
    aedtapp.close_project(save=False)


def test_run_desktop_settings(desktop) -> None:
    aedtapp = Hfss()
    assert aedtapp.desktop_class.disable_optimetrics()
    assert aedtapp.get_registry_key_int("Desktop/Settings/ProjectOptions/EnableLegacyOptimetricsTools") == 0
    assert aedtapp.desktop_class.enable_optimetrics()
    assert aedtapp.get_registry_key_int("Desktop/Settings/ProjectOptions/EnableLegacyOptimetricsTools") == 1
    aedtapp.close_project(save=False)
