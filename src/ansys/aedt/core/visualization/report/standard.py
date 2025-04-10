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
This module contains these classes: `Standard`, and `HFSSStandard`.

This module provides all functionalities for creating and editing reports.

"""
import re

from ansys.aedt.core.visualization.report.common import CommonReport
from ansys.aedt.core.visualization.report.common import CommonReportNew


class HFSSStandard(CommonReportNew):
    """Provides a reporting class that fits HFSS standard reports."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReportNew.__init__(self, app, report_category, setup_name, expressions)
        if report_category == "Eigenmode Parameters":
            self._legacy_props["context"]["domain"] = []
            variations = self._app.available_variations.get_independent_nominal_values()
            primary_sweep = "X"
            if variations:
                primary_sweep = list(variations.keys())[0]
            self.primary_sweep = primary_sweep
            self._legacy_props["context"]["variations"].pop("Freq", None)
            self._legacy_props["context"]["variations"][primary_sweep] = ["All"]

    @property
    def domain(self):
        """Plot domain.

        Returns
        -------
        str
            Plot domain.
        """
        if self._is_created:
            try:
                return self.traces[0].properties["Domain"]
            except Exception:
                self._app.logger.debug("Something went wrong while accessing trace's Domain property.")
        return self._legacy_props["context"]["domain"]

    @domain.setter
    def domain(self, domain):
        self._legacy_props["context"]["domain"] = domain

        if self.primary_sweep == "Freq" and domain == "Time":
            self.primary_sweep = "Time"
            if isinstance(self._legacy_props["context"]["variations"], dict):
                self._legacy_props["context"]["variations"].pop("Freq", None)
                self._legacy_props["context"]["variations"]["Time"] = ["All"]
            else:  # pragma: no cover
                self._legacy_props["context"]["variations"] = {"Time": "All"}

        elif self.primary_sweep == "Time" and domain == "Sweep":
            self.primary_sweep = "Freq"
            if isinstance(self._legacy_props["context"]["variations"], dict):
                self._legacy_props["context"]["variations"].pop("Time", None)
                self._legacy_props["context"]["variations"]["Freq"] = ["All"]
            else:  # pragma: no cover
                self._legacy_props["context"]["variations"] = {"Freq": "All"}

    @property
    def pulse_rise_time(self):
        """Value of Pulse rise time for TDR plot.

        Returns
        -------
        float
            Pulse rise time.
        """
        return self._legacy_props["context"].get("pulse_rise_time", 0) if self.domain == "Time" else 0

    @pulse_rise_time.setter
    def pulse_rise_time(self, val):
        self._legacy_props["context"]["pulse_rise_time"] = val

    @property
    def use_pulse_in_tdr(self):
        """Value of Pulse rise time for TDR plot.

        Returns
        -------
        float
            Pulse rise time.
        """
        return self._legacy_props["context"].get("use_pulse_in_tdr", False) if self.domain == "Time" else False

    @use_pulse_in_tdr.setter
    def use_pulse_in_tdr(self, val):
        self._legacy_props["context"]["use_pulse_in_tdr"] = val

    @property
    def maximum_time(self):
        """Value of maximum time for TDR plot.

        Returns
        -------
        float
            Maximum time.
        """
        return self._legacy_props["context"].get("maximum_time", 0) if self.domain == "Time" else 0

    @maximum_time.setter
    def maximum_time(self, val):
        self._legacy_props["context"]["maximum_time"] = val

    @property
    def step_time(self):
        """Value of step time for TDR plot.

        Returns
        -------
        float
            step time.
        """
        return self._legacy_props["context"].get("step_time", 0) if self.domain == "Time" else 0

    @step_time.setter
    def step_time(self, val):
        self._legacy_props["context"]["step_time"] = val

    @property
    def time_windowing(self):
        """Returns the TDR time windowing.

        Options are:
            * ``0`` : Rectangular
            * ``1`` : Bartlett
            * ``2`` : Blackman
            * ``3`` : Hamming
            * ``4`` : Hanning
            * ``5`` : Kaiser
            * ``6`` : Welch
            * ``7`` : Weber
            * ``8`` : Lanzcos.

        Returns
        -------
        int
            Time windowing.
        """
        _time_windowing = self._legacy_props["context"].get("time_windowing", 0)
        return _time_windowing if self.domain == "Time" and self.pulse_rise_time != 0 else 0

    @time_windowing.setter
    def time_windowing(self, val):
        available_values = {
            "rectangular": 0,
            "bartlett": 1,
            "blackman": 2,
            "hamming": 3,
            "hanning": 4,
            "kaiser": 5,
            "welch": 6,
            "weber": 7,
            "lanzcos": 8,
        }
        if isinstance(val, int):
            self._legacy_props["context"]["time_windowing"] = val
        elif isinstance(val, str) and val.lower in available_values:
            self._legacy_props["context"]["time_windowing"] = available_values[val.lower()]

    @property
    def window_width(self):
        """Window width from 0 to 1.

        Returns
        -------
        float
            Window width.
        """
        _window_width = self._legacy_props["context"].get("window_width", 1.0)
        return _window_width if self.domain == "Time" and self.pulse_rise_time != 0 else 1.0

    @window_width.setter
    def window_width(self, val):
        self._legacy_props["context"]["window_width"] = val

    @property
    def _context(self):
        if self.domain == "Time" and self._app.solution_type in ["Modal", "Terminal"]:
            ctxt = [
                "Domain:=",
                self.domain,
                "HoldTime:=",
                1,
                "RiseTime:=",
                self.pulse_rise_time,
                "StepTime:=",
                self.step_time,
                "Step:=",
                not self.use_pulse_in_tdr,
                "WindowWidth:=",
                self.window_width,
                "WindowType:=",
                self.time_windowing,
                "KaiserParameter:=",
                1,
                "MaximumTime:=",
                self.maximum_time,
            ]
        else:
            ctxt = ["Domain:=", self.domain]

        return ctxt


class Standard(CommonReport):
    """Provides a reporting class that fits most of the app's standard reports."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)

    @property
    def sub_design_id(self):
        """Sub design ID for a Circuit or HFSS 3D Layout sub design.

        Returns
        -------
        int
            Number of the sub design ID.
        """
        return self._legacy_props["context"].get("Sub Design ID", None)

    @sub_design_id.setter
    def sub_design_id(self, value):
        self._legacy_props["context"]["Sub Design ID"] = value

    @property
    def time_start(self):
        """Time start value.

        Returns
        -------
        str
            Time start value.
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
            Time stop value.
        """
        return self._legacy_props["context"].get("time_stop", None)

    @time_stop.setter
    def time_stop(self, value):
        self._legacy_props["context"]["time_stop"] = value

    @property
    def _did(self):
        if self.domain == "Sweep":
            return 3
        elif self.domain == "Clock Times":
            return 55827
        elif self.domain in [
            "UI",
        ]:
            return 55819
        elif self.domain in ["Initial Response"]:
            return 55824
        else:
            return 1

    @property
    def pulse_rise_time(self):
        """Value of Pulse rise time for TDR plot.

        Returns
        -------
        float
            Pulse rise time.
        """
        return self._legacy_props["context"].get("pulse_rise_time", 0) if self.domain == "Time" else 0

    @pulse_rise_time.setter
    def pulse_rise_time(self, val):
        self._legacy_props["context"]["pulse_rise_time"] = val

    @property
    def maximum_time(self):
        """Value of maximum time for TDR plot.

        Returns
        -------
        float
            Maximum time.
        """
        return self._legacy_props["context"].get("maximum_time", 0) if self.domain == "Time" else 0

    @maximum_time.setter
    def maximum_time(self, val):
        self._legacy_props["context"]["maximum_time"] = val

    @property
    def step_time(self):
        """Value of step time for TDR plot.

        Returns
        -------
        float
            step time.
        """
        return self._legacy_props["context"].get("step_time", 0) if self.domain == "Time" else 0

    @step_time.setter
    def step_time(self, val):
        self._legacy_props["context"]["step_time"] = val

    @property
    def time_windowing(self):
        """Returns the TDR time windowing.

        Options are:
            * ``0`` : Rectangular
            * ``1`` : Bartlett
            * ``2`` : Blackman
            * ``3`` : Hamming
            * ``4`` : Hanning
            * ``5`` : Kaiser
            * ``6`` : Welch
            * ``7`` : Weber
            * ``8`` : Lanzcos.

        Returns
        -------
        int
            Time windowing.
        """
        _time_windowing = self._legacy_props["context"].get("time_windowing", 0)
        return _time_windowing if self.domain == "Time" and self.pulse_rise_time != 0 else 0

    @time_windowing.setter
    def time_windowing(self, val):
        available_values = {
            "rectangular": 0,
            "bartlett": 1,
            "blackman": 2,
            "hamming": 3,
            "hanning": 4,
            "kaiser": 5,
            "welch": 6,
            "weber": 7,
            "lanzcos": 8,
        }
        if isinstance(val, int):
            self._legacy_props["context"]["time_windowing"] = val
        elif isinstance(val, str) and val.lower in available_values:
            self._legacy_props["context"]["time_windowing"] = available_values[val.lower()]

    @property
    def _context(self):
        ctxt = []
        if self._app.solution_type in ["TR", "AC", "DC"]:
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [self._did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0],
            ]
        elif self._app.design_type in ["Q3D Extractor", "2D Extractor"]:
            if not self.matrix:
                ctxt = ["Context:=", "Original"]
            else:
                ctxt = ["Context:=", self.matrix]
        elif self._app.design_type in ["Maxwell 2D", "Maxwell 3D"] and self._app.solution_type in [
            "EddyCurrent",
            "Electrostatic",
        ]:
            if not self.matrix:
                ctxt = ["Context:=", "Original"]
            elif self.matrix and not self.reduced_matrix:
                ctxt = ["Context:=", self.matrix]
            elif self.reduced_matrix:
                ctxt = ["Context:=", self.matrix, "Matrix:=", self.reduced_matrix]
        elif self._app.solution_type in ["HFSS3DLayout"]:
            if self.domain == "DCIR":
                ctxt = [
                    "NAME:Context",
                    "SimValueContext:=",
                    [
                        37010,
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
                        "",
                        0,
                        0,
                        "DCIRID",
                        False,
                        str(self.siwave_dc_category),
                        "IDIID",
                        False,
                        "1",
                    ],
                ]
            elif self.differential_pairs:
                ctxt = [
                    "NAME:Context",
                    "SimValueContext:=",
                    [
                        self._did,
                        0,
                        2,
                        self.pulse_rise_time,
                        self.use_pulse_in_tdr if self.pulse_rise_time else False,
                        False,
                        -1,
                        1,
                        self.time_windowing,
                        1,
                        1,
                        "",
                        (self.pulse_rise_time / 5) if not self.step_time else self.step_time,
                        (self.pulse_rise_time * 100) if not self.maximum_time else self.maximum_time,
                        "EnsDiffPairKey",
                        False,
                        "1",
                        "IDIID",
                        False,
                        "1" if not self.pulse_rise_time else "3",
                    ],
                ]
            else:
                ctxt = [
                    "NAME:Context",
                    "SimValueContext:=",
                    [
                        self._did,
                        0,
                        2,
                        self.pulse_rise_time,
                        self.use_pulse_in_tdr if self.pulse_rise_time else False,
                        False,
                        -1,
                        1,
                        self.time_windowing,
                        1,
                        1,
                        "",
                        (self.pulse_rise_time / 5) if not self.step_time else self.step_time,
                        (self.pulse_rise_time * 100) if not self.maximum_time else self.maximum_time,
                        "EnsDiffPairKey",
                        False,
                        "0",
                        "IDIID",
                        False,
                        "1" if not self.pulse_rise_time else "3",
                    ],
                ]
        elif self._app.solution_type in ["NexximLNA", "NexximTransient"]:
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [
                    self._did,
                    0,
                    2,
                    self.pulse_rise_time,
                    self.use_pulse_in_tdr if self.pulse_rise_time else False,
                    False,
                    -1,
                    1,
                    self.time_windowing,
                    1,
                    1,
                    "",
                    (self.pulse_rise_time / 5) if not self.step_time else self.step_time,
                    (self.pulse_rise_time * 100) if not self.maximum_time else self.maximum_time,
                ],
            ]
            if self.sub_design_id:
                # BUG in AEDT. Trace only created when the plot is manually created one time
                ctxt_temp = ["NUMLEVELS", False, "1", "SUBDESIGNID", False, str(self.sub_design_id)]
                for el in ctxt_temp:
                    ctxt[2].append(el)
            if self.differential_pairs:
                ctxt_temp = ["USE_DIFF_PAIRS", False, "1"]
                for el in ctxt_temp:
                    ctxt[2].append(el)

            elif self.domain == "UI":
                if self.report_type == "Rectangular Contour Plot":
                    ctxt[2].extend(
                        [
                            "MLO",
                            False,
                            "0",
                            "NF",
                            False,
                            "1e-16",
                            "NUMLEVELS",
                            False,
                            "1",
                            "PCID",
                            False,
                            "-1",
                            "PID",
                            False,
                            "0",
                            "PRIDIST",
                            False,
                            "-1",
                            "USE_PRI_DIST",
                            False,
                            "0",
                        ]
                    )
                else:
                    ctxt[2].extend(
                        [
                            "AMPUI",
                            False,
                            "1",
                            "AMPUIVAL",
                            False,
                            "0",
                            "MLO",
                            False,
                            "0",
                            "NF",
                            False,
                            "1e-16",
                            "NUMLEVELS",
                            False,
                            "1",
                            "PCID",
                            False,
                            "-1",
                            "PID",
                            False,
                            "0",
                            "PRIDIST",
                            False,
                            "-1",
                            "USE_PRI_DIST",
                            False,
                        ]
                    )
            elif self.domain == "Initial Response":
                ctxt[2].extend(["IRID", False, "0", "NUMLEVELS", False, "1", "SCID", False, "-1", "SID", False, "0"])
            if self.domain == "Time":
                if self.time_start:
                    ctxt[2].extend(["WS", False, self.time_start])
                if self.time_stop:
                    ctxt[2].extend(["WE", False, self.time_stop])
        elif self._app.solution_type in ["NexximAMI"]:
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [self._did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "NUMLEVELS", False, "1"],
            ]
            qty = re.sub("<[^>]+>", "", self.expressions[0])
            if qty == "InitialWave":
                ctxt_temp = ["QTID", False, "0", "SCID", False, "-1", "SID", False, "0"]
            elif qty == "WaveAfterSource":
                ctxt_temp = ["QTID", False, "1", "SCID", False, "-1", "SID", False, "0"]
            elif qty == "WaveAfterChannel":
                ctxt_temp = [
                    "PCID",
                    False,
                    "-1",
                    "PID",
                    False,
                    "0",
                    "QTID",
                    False,
                    "2",
                    "SCID",
                    False,
                    "-1",
                    "SID",
                    False,
                    "0",
                ]
            elif qty == "WaveAfterProbe":
                ctxt_temp = [
                    "PCID",
                    False,
                    "-1",
                    "PID",
                    False,
                    "0",
                    "QTID",
                    False,
                    "3",
                    "SCID",
                    False,
                    "-1",
                    "SID",
                    False,
                    "0",
                ]
            elif qty == "ClockTics":
                ctxt_temp = ["PCID", False, "-1", "PID", False, "0"]
            else:
                return None
            for el in ctxt_temp:
                ctxt[2].append(el)

        elif self.differential_pairs:
            ctxt = ["Diff:=", "differential_pairs", "Domain:=", self.domain]
        else:
            if self.domain == "Time" and self._app.solution_type in ["Modal", "Terminal"]:
                ctxt = [
                    "Domain:=",
                    self.domain,
                    "HoldTime:=",
                    1,
                    "RiseTime:=",
                    self.pulse_rise_time,
                    "StepTime:=",
                    self.step_time,
                    "Step:=",
                    True,
                    "WindowWidth:=",
                    1,
                    "WindowType:=",
                    self.time_windowing,
                    "KaiserParameter:=",
                    1,
                    "MaximumTime:=",
                    self.maximum_time,
                ]
            else:
                ctxt = ["Domain:=", self.domain]

        return ctxt
