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
This module contains the `CircuitNetlistReport` class.

This module provides all functionalities for creating and editing Circuit Netlist reports.
"""

import re

from ansys.aedt.core.generic.aedt_constants import CircuitNetlistConstants
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.visualization.report.common import CommonReport


class CircuitNetlistReport(CommonReport):
    """pass"""

    def __init__(self, app, report_category, expressions):
        CommonReport.__init__(self, app, report_category, expressions)

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
    def maximum_time(self):
        """Value of maximum time for TDR plot.

        Returns
        -------
        float
            Maximum time.
        """
        return self._legacy_props["context"].get("maximum_time", 3.33333333333333e-10) if self.domain == "Time" else 0

    @maximum_time.setter
    def maximum_time(self, val):
        self._legacy_props["context"]["maximum_time"] = val

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
    def thinning(self):
        """Transient windowing.

        Returns
        -------
        int
        """
        return self._legacy_props["context"].get("thinning", 0)

    @thinning.setter
    def thinning(self, value):
        self._legacy_props["context"]["thinning"] = value

    @property
    def thinning_points(self):
        """Transient thinning points.

        Returns
        -------
        int
        """
        return self._legacy_props["context"].get("thinning_points", 500000000)

    @thinning_points.setter
    def thinning_points(self, value):
        self._legacy_props["context"]["thinning_points"] = value

    @property
    def dy_dx_tolerance(self):
        """Transient thinning points.

        Returns
        -------
        int
        """
        return self._legacy_props["context"].get("dy_dx_tolerance", 0.001)

    @dy_dx_tolerance.setter
    def dy_dx_tolerance(self, value):
        self._legacy_props["context"]["dy_dx_tolerance"] = value

    @property
    def time_start(self):
        """Time start value.

        Returns
        -------
        str
            Time start value.
        """
        return self._legacy_props["context"].get("time_start", "0ps")

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
        return self._legacy_props["context"].get("time_stop", "10ns")

    @time_stop.setter
    def time_stop(self, value):
        self._legacy_props["context"]["time_stop"] = value

    @property
    def step_time(self):
        """Value of step time for TDR plot.

        Returns
        -------
        float
            step time.
        """
        return self._legacy_props["context"].get("step_time", 3.33333333333333e-12) if self.domain == "Time" else 0

    @step_time.setter
    def step_time(self, val):
        self._legacy_props["context"]["step_time"] = val

    @property
    def _context(self):
        ctxt = []
        if self._post.post_solution_type in ["NexximLNA", "NexximTransient"]:
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [
                    self._did,
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
                ctxt[2].extend(
                    [
                        "DE",
                        False,
                        str(1 if self.thinning else 0),
                        "DP",
                        False,
                        str(self.thinning_points),
                        "DT",
                        False,
                        str(self.dy_dx_tolerance),
                        "NUMLEVELS",
                        False,
                        "0",
                        "WE",
                        False,
                        self.time_stop,
                        "WM",
                        False,
                        self.time_stop,
                        "WN",
                        False,
                        self.time_start,
                        "WS",
                        False,
                        self.time_start,
                    ]
                )

        elif self._post.post_solution_type in ["NexximAMI"]:
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

        return ctxt

    @pyaedt_function_handler()
    def create(self, name=None, solution=None):
        """Create a report.

        Parameters
        ----------
        name : str, optional
            Name for the plot. The default is ``None``, in which case the
            default name is used.
        solution : str, optional
            Solution type name. If not provided, the first available solution type
            is used. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self._is_created = False
        if not name:
            self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = name
        if not solution:
            if not self._app.post.available_report_solutions()[0]:
                raise IndexError("No solutions available.")
            else:
                solution = self._app.post.available_report_solutions()[0]
        self.setup = CircuitNetlistConstants.solution_types[solution]["name"]
        self._post.oreportsetup.CreateReport(
            self.plot_name,
            self.report_category,
            self.report_type,
            self.setup,
            self._context,
            self._convert_dict_to_report_sel(self.variations),
            self._trace_info,
        )
        self._post.plots.append(self)
        self._is_created = True
        self._initialize_tree_node()
        return True
