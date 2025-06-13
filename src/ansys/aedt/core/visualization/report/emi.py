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

"""
This module contains this class: `EMIReceiver`.

This module provides all functionalities for creating and editing reports.

"""

from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.visualization.report.common import CommonReport


class EMIReceiver(CommonReport):
    """Provides for managing EMI receiver reports."""

    def __init__(self, app, report_category="EMIReceiver", setup_name=None, expressions=None):
        CommonReport.__init__(self, app, "EMIReceiver", setup_name, expressions)
        self.logger = app.logger
        self.domain = "EMI Receiver"
        self.available_nets = []
        self._net = ""
        for comp in app._app.modeler.components.components.values():
            if comp.name == "CompInst@EMI_RCVR":
                self.available_nets.append(comp.pins[0].net)

        self.time_start = "0ns"
        self.time_stop = "200ns"
        self._emission = "CE"

        self.primary_sweep = "Freq"

    @property
    def net(self):
        """Net attached to the EMI receiver.

        Returns
        -------
        str
            Net name.
        """
        if self._legacy_props["context"].get("net", None):
            self._net = self._legacy_props["context"]["net"]
        elif self._net == "":
            if self.available_nets:
                self._net = self.available_nets[0]
                self._legacy_props["context"]["net"] = self.available_nets[0]
            else:
                self.logger.error("No nets available for EMI receiver.")
        return self._net

    @net.setter
    def net(self, value):
        if value not in self.available_nets:
            self.logger.error("Net not available.")
        else:
            self._legacy_props["context"]["net"] = value
            self._net = value

    @property
    def overlap_rate(self):
        """Overlap rate to the EMI receiver.

        Returns
        -------
        str, int
            Overlap rate.
        """
        return self._legacy_props["context"].get("overlap_rate", 95)

    @overlap_rate.setter
    def overlap_rate(self, value):
        self._legacy_props["context"]["overlap_rate"] = value

    @property
    def band(self):
        """Band attached to the EMI receiver.

        Returns
        -------
        str
            Band name.
        """
        return self._legacy_props["context"].get("band", "0")

    @band.setter
    def band(self, value):
        self._legacy_props["context"]["band"] = value

    @property
    def rbw(self):
        """RBW attached to the EMI receiver.

        Returns
        -------
        str
            RBW setting.
        """
        return self._legacy_props["context"].get("RBW", "0")

    @rbw.setter
    def rbw(self, value):
        self._legacy_props["context"]["RBW"] = value

    @property
    def rbw_factor(self):
        """RBW Factor attached to the EMI receiver.

        Returns
        -------
        str
            RBW Factor setting.
        """
        return self._legacy_props["context"].get("RBW_factor", "0")

    @rbw_factor.setter
    def rbw_factor(self, value):
        self._legacy_props["context"]["RBW_factor"] = value

    @property
    def emission(self):
        """Emission test.

        Options are ``"CE"`` and ``"RE"``.

        Returns
        -------
        str
            Emission.
        """
        return self._emission

    @emission.setter
    def emission(self, value):
        if value == "CE":
            self._emission = value
            self._legacy_props["context"]["emission"] = "CE"
        elif value == "RE":
            self._emission = value
            self._legacy_props["context"]["emission"] = "RE"
        else:
            self.logger.error(f"Emission must be 'CE' or 'RE', value '{value}' is not valid.")

    @property
    def time_start(self):
        """Time start value.

        Returns
        -------
        str
            Time start.
        """
        return self._legacy_props["context"].get("time_start", None)

    @time_start.setter
    def time_start(self, value):
        self._legacy_props["context"]["time_start"] = value

    @property
    def time_stop(self):
        """Time stop value.

        Returns
        -------
        str
            Time stop.
        """
        return self._legacy_props["context"].get("time_stop", None)

    @time_stop.setter
    def time_stop(self, value):
        self._legacy_props["context"]["time_stop"] = value

    @property
    def _context(self):
        if self.emission == "CE":
            em = "0"
        else:
            em = "1"

        arg = [
            "NAME:Context",
            "SimValueContext:=",
            [
                55830,
                0,
                2,
                0,
                False,
                False,
                -1,
                1,
                0,
                1,
                1,
                self.net,
                0,
                0,
                "BAND",
                False,
                str(self.band),
                "CG",
                False,
                "1",
                "EM",
                False,
                em,
                "KP",
                False,
                "0",
                "NUMLEVELS",
                False,
                "0",
                "OR",
                False,
                str(self.overlap_rate),
                "RBW",
                False,
                str(self.rbw),
                "RBWFactor",
                False,
                str(self.rbw_factor),
                "SIG",
                False,
                "0",
                "TCT",
                False,
                "1ms",
                "TDT",
                False,
                "160ms",
                "TE",
                False,
                self.time_stop,
                "TS",
                False,
                self.time_start,
                "WT",
                False,
                "6",
                "WW",
                False,
                "100",
            ],
        ]
        return arg

    @property
    def _trace_info(self):
        if isinstance(self.expressions, list):
            return self.expressions
        else:
            return [self.expressions]

    @pyaedt_function_handler()
    def create(self, name=None):
        """Create an EMI receiver report.

        Parameters
        ----------
        name : str, optional
            Plot name. The default is ``None``, in which case
            the default name is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not name:
            self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = name
        self._post.oreportsetup.CreateReport(
            self.plot_name,
            "Standard",
            self.report_type,
            self.setup,
            self._context,
            self._convert_dict_to_report_sel(self.variations),
            [
                "X Component:=",
                self.primary_sweep,
                "Y Component:=",
                self._trace_info,
            ],
        )
        self._post.plots.append(self)
        self._is_created = True
        return self
