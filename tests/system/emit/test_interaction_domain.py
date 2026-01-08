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

from enum import Enum
import inspect
import os
from pathlib import Path
import random
import shutil
import sys
import tempfile
import types

# Import required modules
from typing import cast
from typing import get_args
from unittest.mock import MagicMock
import warnings

import pytest

from ansys.aedt.core.generic import constants as consts
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.internal.errors import GrpcApiError
from tests import TESTS_EMIT_PATH
from tests.conftest import DESKTOP_VERSION

# Prior to 2025R1, the Emit API supported Python 3.8,3.9,3.10,3.11
# Starting with 2025R1, the Emit API supports Python 3.10,3.11,3.12
if ((3, 8) <= sys.version_info[0:2] <= (3, 11) and DESKTOP_VERSION < "2025.1") or (
    (3, 10) <= sys.version_info[0:2] <= (3, 12) and DESKTOP_VERSION > "2024.2"
):
    from ansys.aedt.core import Emit
    from ansys.aedt.core.emit_core.emit_constants import EmiCategoryFilter
    from ansys.aedt.core.emit_core.emit_constants import InterfererType
    from ansys.aedt.core.emit_core.emit_constants import ResultType
    from ansys.aedt.core.emit_core.emit_constants import TxRxMode
    from ansys.aedt.core.emit_core.nodes import generated
    from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
    from ansys.aedt.core.emit_core.nodes.emitter_node import EmitterNode
    from ansys.aedt.core.emit_core.nodes.generated import Amplifier
    from ansys.aedt.core.emit_core.nodes.generated import AntennaNode
    from ansys.aedt.core.emit_core.nodes.generated import Band
    from ansys.aedt.core.emit_core.nodes.generated import CouplingsNode
    from ansys.aedt.core.emit_core.nodes.generated import EmitSceneNode
    from ansys.aedt.core.emit_core.nodes.generated import Filter
    from ansys.aedt.core.emit_core.nodes.generated import RadioNode
    from ansys.aedt.core.emit_core.nodes.generated import RxMixerProductNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSaturationNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSelectivityNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSpurNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSusceptibilityProfNode
    from ansys.aedt.core.emit_core.nodes.generated import SamplingNode
    from ansys.aedt.core.emit_core.nodes.generated import Terminator
    from ansys.aedt.core.emit_core.nodes.generated import TouchstoneCouplingNode
    from ansys.aedt.core.emit_core.nodes.generated import TxBbEmissionNode
    from ansys.aedt.core.emit_core.nodes.generated import TxHarmonicNode
    from ansys.aedt.core.emit_core.nodes.generated import TxNbEmissionNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpectralProfEmitterNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpectralProfNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpurNode
    from ansys.aedt.core.emit_core.nodes.generated import Waveform
    from ansys.aedt.core.modeler.circuits.primitives_emit import EmitAntennaComponent
    from ansys.aedt.core.modeler.circuits.primitives_emit import EmitComponent
    from ansys.aedt.core.modeler.circuits.primitives_emit import EmitComponents

TEST_SUBFOLDER = TESTS_EMIT_PATH / "example_models/TEMIT"

@pytest.mark.skipif(DESKTOP_VERSION <= "2022.1", reason="Skipped on versions earlier than 2021.2")
def test_interaction_domain(emit_app):
    engine = emit_app._emit_api.get_engine()
    
    domain = emit_app.interaction_domain()