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

import warnings

from ansys.aedt.core.emit_core.emit_constants import EMIT_INTERNAL_UNITS
from ansys.aedt.core.emit_core.nodes import emit_node
import ansys.aedt.core.generic.constants as consts

class InteractionDomain:
    def __init__(self, emit_obj):
        self.emit_project = emit_obj
        """EMIT project."""

        self.current_revision = None
        """Current active Revision."""

        self.revisions = []
        """List of all result revisions. Only one loaded at a time"""

        self.design = emit_obj.desktop_class.active_design(emit_obj.odesktop.GetActiveProject())
        """Active design for the EMIT project."""

        self.aedt_version = int(self.emit_project.aedt_version_id[-3:])

        self.interferer_band_names = []
        """List of interferer band names."""

        self.interferer_channel_frequencies = []
        """List of interferer channel frequencies."""

        self.interferer_names = []
        """List of interferer names."""

        self.receiver_band_name = ""
        """Receiver band name."""

        self.receiver_channel_frequency = 0
        """Receiver channel frequency."""

        self.receiver_name = ""
        """Receiver name."""
    
    def set_reciever(self, name : str, band_name : str, freq : float, units : str):
        
        self.receiver_name = name
        self.receiver_band_name = band_name

        if units not in EMIT_INTERNAL_UNITS["Freq"]:
            err_msg = (f"Unit {units} is not valid for frequency. "
                       f"Valid units are: {EMIT_INTERNAL_UNITS["Freq"]}")
            warnings.warn(err_msg)
            return False 

        converted_freq = consts.unit_converter(freq, 'Freq', units, EMIT_INTERNAL_UNITS['Freq']) 
        self.receiver_channel_frequency = converted_freq
        return True
    
    def set_interferer(self, name : str, band_name : str, freq : float, units : str):
        self.interferer_names = []
        self.interferer_names.append(name)
        self.interferer_band_names = []
        self.interferer_band_names.append(band_name)
        self.interferer_channel_frequencies = []

        return