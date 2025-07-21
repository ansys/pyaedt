# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from importlib import import_module
import os
import sys

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.emit_core.emit_constants import EmiCategoryFilter
from ansys.aedt.core.emit_core.emit_constants import InterfererType
from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.emit_constants import TxRxMode
from ansys.aedt.core.emit_core.emit_constants import UnitType

# TODO: Remove once IronPython compatibility is removed
if sys.version_info < (3, 12):
    import imp
else:  # pragma: no cover
    from importlib.util import find_spec


EMIT_API_PYTHON = None


def emit_api_python():
    """
    Get the EMIT backend API.

    The backend API is available once a ansys.aedt.core.Emit() object has been created.
    An exception is raised if this method is called before a ``ansys.aedt.core.Emit()`` object has been created.
    """
    if not EMIT_API_PYTHON:
        raise Exception("A ansys.aedt.core.Emit() object must be initialized before using the EMIT API.")
    return EMIT_API_PYTHON


def _init_enums(aedt_version):
    numeric_version = int(aedt_version[-3:])

    if numeric_version > 251:
        ResultType.EMI = emit_api_python().result_type().emi
        ResultType.DESENSE = emit_api_python().result_type().desense
        ResultType.SENSITIVITY = emit_api_python().result_type().sensitivity
        ResultType.POWER_AT_RX = emit_api_python().result_type().powerAtRx

        TxRxMode.TX = emit_api_python().tx_rx_mode().tx
        TxRxMode.RX = emit_api_python().tx_rx_mode().rx
        TxRxMode.BOTH = emit_api_python().tx_rx_mode().both

        InterfererType.TRANSMITTERS = emit_api_python().interferer_type().transmitters
        InterfererType.EMITTERS = emit_api_python().interferer_type().emitters
        InterfererType.TRANSMITTERS_AND_EMITTERS = emit_api_python().interferer_type().transmitters_and_emitters

        UnitType.POWER = emit_api_python().unit_type().power
        UnitType.FREQUENCY = emit_api_python().unit_type().frequency
        UnitType.LENGTH = emit_api_python().unit_type().length
        UnitType.TIME = emit_api_python().unit_type().time
        UnitType.VOLTAGE = emit_api_python().unit_type().voltage
        UnitType.DATA_RATE = emit_api_python().unit_type().dataRate
        UnitType.RESISTANCE = emit_api_python().unit_type().resistance

        EmiCategoryFilter.IN_CHANNEL_TX_FUNDAMENTAL = 0
        EmiCategoryFilter.IN_CHANNEL_TX_HARMONIC_SPURIOUS = 1
        EmiCategoryFilter.IN_CHANNEL_TX_INTERMOD = 2
        EmiCategoryFilter.IN_CHANNEL_TX_BROADBAND = 3
        EmiCategoryFilter.OUT_OF_CHANNEL_TX_FUNDAMENTAL = 4
        EmiCategoryFilter.OUT_OF_CHANNEL_TX_HARMONIC_SPURIOUS = 5
        EmiCategoryFilter.OUT_OF_CHANNEL_TX_INTERMOD = 6
    else:
        ResultType.EMI = emit_api_python().result_type().emi
        ResultType.DESENSE = emit_api_python().result_type().desense
        ResultType.SENSITIVITY = emit_api_python().result_type().sensitivity
        ResultType.POWER_AT_RX = emit_api_python().result_type().powerAtRx

        TxRxMode.TX = emit_api_python().tx_rx_mode().tx
        TxRxMode.RX = emit_api_python().tx_rx_mode().rx
        TxRxMode.BOTH = emit_api_python().tx_rx_mode().both

        InterfererType.TRANSMITTERS = emit_api_python().interferer_type().transmitters
        InterfererType.EMITTERS = emit_api_python().interferer_type().emitters
        InterfererType.TRANSMITTERS_AND_EMITTERS = emit_api_python().interferer_type().transmitters_and_emitters

        UnitType.POWER = emit_api_python().unit_type().power
        UnitType.FREQUENCY = emit_api_python().unit_type().frequency
        UnitType.LENGTH = emit_api_python().unit_type().length
        UnitType.TIME = emit_api_python().unit_type().time
        UnitType.VOLTAGE = emit_api_python().unit_type().voltage
        UnitType.DATA_RATE = emit_api_python().unit_type().dataRate
        UnitType.RESISTANCE = emit_api_python().unit_type().resistance

        if numeric_version >= 241:
            emi_cat_filter = emit_api_python().emi_category_filter()
            EmiCategoryFilter.IN_CHANNEL_TX_FUNDAMENTAL = emi_cat_filter.in_channel_tx_fundamental
            EmiCategoryFilter.IN_CHANNEL_TX_HARMONIC_SPURIOUS = emi_cat_filter.in_channel_tx_harmonic_spurious
            EmiCategoryFilter.IN_CHANNEL_TX_INTERMOD = emi_cat_filter.in_channel_tx_intermod
            EmiCategoryFilter.IN_CHANNEL_TX_BROADBAND = emi_cat_filter.in_channel_tx_broadband
            EmiCategoryFilter.OUT_OF_CHANNEL_TX_FUNDAMENTAL = emi_cat_filter.out_of_channel_tx_fundamental
            EmiCategoryFilter.OUT_OF_CHANNEL_TX_HARMONIC_SPURIOUS = emi_cat_filter.out_of_channel_tx_harmonic_spurious
            EmiCategoryFilter.OUT_OF_CHANNEL_TX_INTERMOD = emi_cat_filter.out_of_channel_tx_intermod


# need this as a function so that it can be set
# for the correct aedt version that the user is running
def _set_api(aedt_version):
    numeric_version = int(aedt_version[-3:])
    desktop_path = os.environ.get(aedt_version)
    if desktop_path and numeric_version > 231:
        path = os.path.join(desktop_path, "Delcross")
        override_path_key = "ANSYS_DELCROSS_PYTHON_PATH"
        if override_path_key in os.environ:
            path = os.environ.get(override_path_key)
        sys.path.insert(0, path)
        # TODO: Remove once IronPython compatibility is removed
        if sys.version_info < (3, 12):
            module_path = imp.find_module("EmitApiPython")[1]
            logger.info(f"Importing EmitApiPython from: {module_path}")
        else:  # pragma: no cover
            spec = find_spec("EmitApiPython")
            if spec is None:
                logger.warning(f"Module {'EmitApiPython'} not found")
            else:
                module_path = spec.origin
                logger.info(f"Importing EmitApiPython from: {module_path}")
        global EMIT_API_PYTHON
        EMIT_API_PYTHON = import_module("EmitApiPython")
        logger.info(f"Loaded {EMIT_API_PYTHON.EmitApi().get_version(True)}")
        _init_enums(aedt_version)
