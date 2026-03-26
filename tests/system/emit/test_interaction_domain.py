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

import sys

# Import required modules
import pytest

from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
from tests import TESTS_EMIT_PATH
from tests.conftest import DESKTOP_VERSION

# Prior to 2025R1, the Emit API supported Python 3.8,3.9,3.10,3.11
# Starting with 2025R1, the Emit API supports Python 3.10,3.11,3.12
if ((3, 8) <= sys.version_info[0:2] <= (3, 11) and DESKTOP_VERSION < "2025.1") or (
    (3, 10) <= sys.version_info[0:2] <= (3, 12) and DESKTOP_VERSION > "2024.2"
):
    from ansys.aedt.core import Emit

TEST_SUBFOLDER = TESTS_EMIT_PATH / "example_models/TEMIT"

RXNAME = "GSM Mobile Station"
RXBANDNAME = "Rx GSM-850 - Other Modulations"
TX1NAME = "WiFi - 802.11-2012"
TX1BANDNAME = "Tx OFDM - 54 Mbps"


@pytest.fixture
def emit_app(add_app):
    app = add_app(application=Emit)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def cell_phone(add_app_example):
    app = add_app_example(
        project="Cell Phone",
        application=Emit,
        subfolder=TEST_SUBFOLDER,
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_interaction_domain(cell_phone):
    # Test domain get/set, isSingleInstance, errors
    domain = InteractionDomain(cell_phone)
    assert domain is not None
    assert domain.receiver_name == ""
    assert domain.receiver_band_name == ""
    assert domain.receiver_channel_frequency == 0
    assert domain.interferer_names == []
    assert domain.interferer_band_names == []
    assert domain.interferer_channel_frequencies == []

    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()

    domain.set_receiver(name="", band_name=RXBANDNAME)
    assert sim.is_domain_valid(domain) == f"No receiver defined for band '{RXBANDNAME}'."

    domain.set_receiver(name=RXNAME, band_name="", freq=20, units="Hz")
    assert sim.is_domain_valid(domain) == "Receiver frequency defined without a band."

    domain.set_receiver(name="Bad Rx")
    assert sim.is_domain_valid(domain) == "Receiver 'Bad Rx' not found."

    domain.set_receiver(name=RXNAME, band_name="Bad Rx Band")
    assert sim.is_domain_valid(domain) == f"Receiver band 'Bad Rx Band' not found in '{RXNAME}'."

    domain.set_receiver(name="")
    assert sim.is_domain_valid(domain) == ""

    # set_interferers validation warnings
    with pytest.warns(UserWarning, match="When assigning bands you must assign one band per interferer."):
        domain.set_interferers(names=[], band_names=["band"])

    with pytest.warns(UserWarning, match="When assigning channels you must assign one channel per band."):
        domain.set_interferers(names=[TX1NAME], band_names=[], freqs=[50])

    domain.set_interferers(names=["bad tx"])
    assert sim.is_domain_valid(domain) == "Interferer 'bad tx' not found."

    domain.set_interferers(names=[""], band_names=[TX1BANDNAME])
    assert sim.is_domain_valid(domain) == f"No interferer defined for band '{TX1BANDNAME}'."

    domain.set_interferers(names=[TX1NAME], band_names=["bad band"])
    assert sim.is_domain_valid(domain) == f"Interferer band 'bad band' not found in '{TX1NAME}'."

    domain.set_interferers(names=[TX1NAME], band_names=[""], freqs=[50])
    assert sim.is_domain_valid(domain) == "Interferer frequency defined without a band."

    domain.set_interferers(names=[], band_names=[], freqs=[])
    domain.set_receiver(name=RXNAME, band_name=RXBANDNAME, freq=2, units="Hz")
    assert (
        sim.is_domain_valid(domain) == f"Receiver channel 2.000000 Hz not found in band '{RXBANDNAME}' of '{RXNAME}'."
    )

    domain.set_receiver(name=RXNAME, band_name=RXBANDNAME, freq=869000000, units="Hz")
    domain.set_interferers(names=[TX1NAME], band_names=[TX1BANDNAME], freqs=[50], units="Hz")
    assert (
        sim.is_domain_valid(domain)
        == f"Interferer channel 50.000000 Hz not found in band '{TX1BANDNAME}' of '{TX1NAME}'."
    )

    domain.set_interferers(names=["GPS Receiver"], band_names=["L1"])
    assert sim.is_domain_valid(domain) == "Interferer band 'L1' disabled."

    domain.set_interferers(names=[], band_names=[], freqs=[])
    domain.set_receiver(name="GPS Receiver", band_name="L1", freq=-1)
    assert sim.is_domain_valid(domain) == "Receiver band 'L1' disabled."

    # check is_single_instance
    domain.set_interferers(names=[TX1NAME], band_names=[TX1BANDNAME])
    domain.set_receiver(name=RXNAME, band_name=RXBANDNAME, freq=869000000, units="Hz")
    assert domain.is_single_instance() is False

    domain.set_interferers(names=[TX1NAME], band_names=[TX1BANDNAME], freqs=[2422000000], units="Hz")
    assert domain.is_single_instance() is True

    # check property getters
    assert domain.receiver_name == RXNAME
    assert domain.receiver_band_name == RXBANDNAME
    assert domain.get_receiver_channel_frequency("Hz") == 869000000
    assert domain.interferer_names == [TX1NAME]
    assert len(domain.interferer_names) == 1
    assert domain.interferer_band_names == [TX1BANDNAME]
    assert len(domain.interferer_band_names) == 1
    freqs = domain.get_interferer_channel_frequencies("Hz")
    assert len(freqs) == 1
    assert freqs[0] == 2422000000

    # check unit conversions for receiver frequency
    domain.set_receiver(name=RXNAME, band_name=RXBANDNAME, freq=869.2, units="MHz")
    assert domain.get_receiver_channel_frequency() == 869200000
    assert domain.get_receiver_channel_frequency("Hz") == 869200000
    assert domain.get_receiver_channel_frequency("kHz") == 869200
    assert domain.get_receiver_channel_frequency("MHz") == 869.2
    assert domain.get_receiver_channel_frequency("GHz") == 0.8692
    assert domain.get_receiver_channel_frequency("THz") == 0.0008692

    domain.set_receiver(name=RXNAME, band_name=RXBANDNAME, freq=869400000, units="Hz")
    assert domain.get_receiver_channel_frequency("MHz") == 869.4

    domain.set_receiver(name=RXNAME, band_name=RXBANDNAME, freq=869600, units="kHz")
    assert domain.get_receiver_channel_frequency("MHz") == 869.6

    domain.set_receiver(name=RXNAME, band_name=RXBANDNAME, freq=869.8, units="MHz")
    assert domain.get_receiver_channel_frequency("MHz") == 869.8

    domain.set_receiver(name=RXNAME, band_name=RXBANDNAME, freq=0.87, units="GHz")
    assert domain.get_receiver_channel_frequency("MHz") == 870.0

    domain.set_receiver(name=RXNAME, band_name=RXBANDNAME, freq=0.0008702, units="THz")
    assert domain.get_receiver_channel_frequency("MHz") == 870.2
