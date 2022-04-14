from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.GeometryOperators import GeometryOperators


class CommonReport(object):
    """Common Report Class."""

    def __init__(self, app, report_category, setup_name):
        self._post = app
        self.report_category = report_category
        self.setup = setup_name
        self._report_type = "Rectangular Plot"
        self._domain = "Sweep"
        self._primary_sweep = "Freq"
        self._secondary_sweep = None
        self.primary_sweep_range = ["All"]
        self.secondary_sweep_range = ["All"]
        self.variations = {"Freq": ["All"]}
        for el, k in self._post._app.available_variations.nominal_w_values_dict.items():
            self.variations[el] = k
        self.differential_pairs = False
        self.matrix = None
        self.polyline = None
        self.expressions = None
        self._plot_name = None
        self._is_created = True

    @property
    def plot_name(self):
        """Set/Get the Plot Name.

        Returns
        -------
        str
        """
        return self._plot_name

    @plot_name.setter
    def plot_name(self, name):
        self._plot_name = name
        self._is_created = False

    @property
    def primary_sweep(self):
        """Return the Report Primary Sweep.

        Returns
        -------
        str
        """
        return self._primary_sweep

    @primary_sweep.setter
    def primary_sweep(self, val):
        if val == self._secondary_sweep:
            self._secondary_sweep = self._primary_sweep
        self._primary_sweep = val

    @property
    def secondary_sweep(self):
        """Return the Report (optional) Secondary Sweep.

        Returns
        -------
        str
        """
        return self._secondary_sweep

    @secondary_sweep.setter
    def secondary_sweep(self, val):
        if val == self._primary_sweep:
            self._primary_sweep = self._secondary_sweep
        self._secondary_sweep = val

    @property
    def _context(self):
        return []

    @property
    def _trace_info(self):
        if isinstance(self.expressions, list):
            expr = self.expressions
        else:
            expr = [self.expressions]
        arg = ["X Component:=", self.primary_sweep, "Y Component:=", expr]
        if self.report_type in ["3D Polar Plot", "3D Spherical Plot"]:
            arg = [
                "Phi Component:=",
                self.primary_sweep,
                "Theta Component:=",
                self.secondary_sweep,
                "Mag Component:=",
                expr,
            ]
        elif self.report_type == "Radiation Pattern":
            arg = ["Ang Component:=", self.primary_sweep, "Mag Component:=", expr]
        elif self.report_type in ["Smith Chart", "Polar Plot"]:
            arg = ["Polar Component:=", expr]
        elif self.report_type == "Rectangular Contour Plot":
            arg = [
                "X Component:=",
                self.primary_sweep,
                "Y Component:=",
                self.secondary_sweep,
                "Z Component:=",
                expr,
            ]
        return arg

    @property
    def domain(self):
        """Get/Set the Plot Domain.

        Returns
        -------
        str
        """
        return self._domain

    @domain.setter
    def domain(self, domain):
        self._domain = domain
        if self._post._app.design_type in ["Maxwell 3D", "Maxwell 2D"]:
            return
        if self.primary_sweep == "Freq" and domain == "Time":
            self.primary_sweep = "Time"
            self.variations.pop("Freq", None)
            self.variations["Time"] = ["All"]
        elif self.primary_sweep == "Time" and domain == "Sweep":
            self.primary_sweep = "Freq"
            self.variations.pop("Time", None)
            self.variations["Freq"] = ["All"]

    @property
    def report_type(self):
        """Get/Set the report Type. Available values are `"3D Polar Plot"`, `"3D Spherical Plot"`,
        `"Radiation Pattern"`, `"Rectangular Plot"`, `"Data Table"`,
        `"Smith Chart"`, `"Rectangular Contour Plot"`.

        Returns
        -------
        str
        """
        return self._report_type

    @report_type.setter
    def report_type(self, report):
        self._report_type = report
        if not self.primary_sweep:
            if self._report_type in ["3D Polar Plot", "3D Spherical Plot"]:
                self.primary_sweep = "Phi"
                self.secondary_sweep = "Theta"
            elif self._report_type == "Radiation Pattern":
                self.primary_sweep = "Phi"
            elif self.domain == "Sweep":
                self.primary_sweep = "Freq"
            elif self.domain == "Time":
                self.primary_sweep = "Time"

    @pyaedt_function_handler()
    def _convert_dict_to_report_sel(self, sweeps):
        if not sweeps:
            return []
        sweep_list = []
        if self.primary_sweep:
            sweep_list.append(self.primary_sweep + ":=")
            sweep_list.append(self.primary_sweep_range)
        if self.secondary_sweep:
            sweep_list.append(self.secondary_sweep + ":=")
            sweep_list.append(self.secondary_sweep_range)
        for el in sweeps:
            if el in [self.primary_sweep, self.secondary_sweep]:
                continue
            sweep_list.append(el + ":=")
            if type(sweeps[el]) is list:
                sweep_list.append(sweeps[el])
            else:
                sweep_list.append([sweeps[el]])
        for el in list(self._post._app.available_variations.nominal_w_values_dict.keys()):
            if el not in sweeps:
                sweep_list.append(el + ":=")
                sweep_list.append(["Nominal"])
        return sweep_list

    @pyaedt_function_handler()
    def create(self, plot_name=None):
        """Create a new Report.

        Parameters
        ----------
        plot_name : str, optional
            Set optionally the plot name

        Returns
        -------
        Bool
        """
        if not plot_name:
            if self._is_created:
                self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = plot_name
        if self.setup not in self._post._app.existing_analysis_sweeps:
            self._post._app.logger.error("Setup doesn't exist in this design.")
            return False
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

        return True

    @pyaedt_function_handler()
    def get_solution_data(self):
        """Get the Report solution Data.

        Returns
        -------
        :class:`pyaedt.modules.PostProcessor.SolutionData`
            `Solution Data object.
        """
        solution_data = self._post.get_solution_data_per_variation(
            self.report_category, self.setup, self._context, self.variations, self.expressions
        )
        if self.primary_sweep:
            solution_data.primary_sweep = self.primary_sweep
        if not solution_data:
            self._post._app.logger.error("No Data Available. Check inputs")
            return False
        return solution_data

    @pyaedt_function_handler()
    def add_limit_line_from_points(self, x_list, y_list, x_units="", y_units="", y_axis=1):  # pragma: no cover
        """Add a Cartesian Limit Line from point lists. This method works only in graphical mode.

        Parameters
        ----------
        x_list : list
            List of float inputs.
        y_list : list
            List of float y values.
        x_units : str
            x list units.
        y_units : str
            y list units.
        y_axis : int, optional
            Y axis. Default is `"Y1"`.

        Returns
        -------
        bool
        """
        x_list = [GeometryOperators.parse_dim_arg(str(i) + x_units) for i in x_list]
        y_list = [GeometryOperators.parse_dim_arg(str(i) + y_units) for i in y_list]
        if self.plot_name and self._is_created:
            xvals = ["NAME:XValues"]
            xvals.extend(x_list)
            yvals = ["NAME:YValues"]
            yvals.extend(y_list)
            self._post.oreportsetup.AddCartesianLimitLine(
                self.plot_name,
                [
                    "NAME:CartesianLimitLine",
                    xvals,
                    "XUnits:=",
                    x_units,
                    yvals,
                    "YUnits:=",
                    y_units,
                    "YAxis:=",
                    "Y{}".format(y_axis),
                ],
            )
            return True
        return False

    @pyaedt_function_handler()
    def add_limit_line_from_equation(
        self, start_x, stop_x, step, equation="x", units="GHz", y_axis=1
    ):  # pragma: no cover
        """Add a Cartesian Limit Line from point lists. This method works only in graphical mode.

        Parameters
        ----------
        start_x : float
            Start X value.
        stop_x : float
            Stop X value.
        step : float
            X step value.
        equation : str
            Y equation to apply. Default is Y=X.
        units : str
            X axis units. Default is "GHz".
        y_axis : str, optional
            Y axis. Default is `"Y1"`.

        Returns
        -------
        bool
        """
        if self.plot_name and self._is_created:
            self._post.oreportsetup.AddCartesianLimitLineFromEquation(
                self.plot_name,
                [
                    "NAME:CartesianLimitLineFromEquation",
                    "YAxis:=",
                    y_axis,
                    "Start:=",
                    str(start_x) + units,
                    "Stop:=",
                    str(stop_x) + units,
                    "Step:=",
                    str(step) + units,
                    "Equation:=",
                    equation,
                ],
            )
            return True
        return False

    @pyaedt_function_handler()
    def add_cartesian_x_marker(self, val, name=None):  # pragma: no cover
        """Add a cartesian X Marker. This method works only in graphical mode.

        Parameters
        ----------
        val : str
            Value to apply with units.
        name : str, optional
            Marker Name

        Returns
        -------
        str
            Marker name if created.
        """
        if not name:
            name = generate_unique_name("MX")
            self._post.oreportsetup.AddCartesianXMarker(self.plot_name, name, GeometryOperators.parse_dim_arg(val))
            return name
        return ""

    @pyaedt_function_handler()
    def add_cartesian_y_marker(self, val, name=None, y_axis=1):  # pragma: no cover
        """Add a cartesian Y Marker. This method works only in graphical mode.

        Parameters
        ----------
        val : str
            Value to apply with units.
        name : str, optional
            Marker Name
        y_axis : str, optional
            Y axis. Default is `"Y1"`.

        Returns
        -------
        str
            Marker name if created.
        """
        if not name:
            name = generate_unique_name("MY")
            self._post.oreportsetup.AddCartesianYMarker(
                self.plot_name, name, "Y{}".format(y_axis), GeometryOperators.parse_dim_arg(val), ""
            )
            return name
        return ""


class Standard(CommonReport):
    """Standard Report Class that fits most of the application standard reports."""

    def __init__(self, app, report_category, setup_name):
        CommonReport.__init__(self, app, report_category, setup_name)
        self.expressions = None
        self.sub_design_id = None
        self.time_start = None
        self.time_stop = None

    @property
    def _did(self):
        if self.domain == "Sweep":
            return 3
        else:
            return 1

    @property
    def _context(self):
        ctxt = []
        if self._post.post_solution_type in ["TR", "AC", "DC"]:
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [self._did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0],
            ]
        elif self._post._app.design_type in ["Q3D Extractor", "2D Extractor"]:
            if not self.matrix:
                ctxt = ["Context:=", "Original"]
            else:
                ctxt = ["Context:=", self.matrix]
        elif self._post.post_solution_type in ["HFSS3DLayout"]:
            if self.differential_pairs:
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
                        "EnsDiffPairKey",
                        False,
                        "1",
                        "IDIID",
                        False,
                        "1",
                    ],
                ]
            else:
                ctxt = [
                    "NAME:Context",
                    "SimValueContext:=",
                    [self._did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"],
                ]
        elif self._post.post_solution_type in ["NexximLNA", "NexximTransient"]:
            ctxt = ["NAME:Context", "SimValueContext:=", [self._did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0]]
            if self.sub_design_id:
                ctxt_temp = ["NUMLEVELS", False, "1", "SUBDESIGNID", False, str(self.sub_design_id)]
                for el in ctxt_temp:
                    ctxt[2].append(el)
            if self.differential_pairs:
                ctxt_temp = ["USE_DIFF_PAIRS", False, "1"]
                for el in ctxt_temp:
                    ctxt[2].append(el)
            if self.domain == "Time":
                if self.time_start:
                    ctxt[2].extend(["WS", False, self.time_start])
                if self.time_stop:
                    ctxt[2].extend(["WE", False, self.time_stop])
        elif self.differential_pairs:
            ctxt = ["Diff:=", "Differential Pairs", "Domain:=", self.domain]
        else:
            ctxt = ["Domain:=", self.domain]
        return ctxt


class Fields(CommonReport):
    """General Fields Class."""

    def __init__(self, app, report_type, setup_name):
        CommonReport.__init__(self, app, report_type, setup_name)
        self.domain = "Sweep"
        self.polyline = None
        self.point_number = 1001
        self.primary_sweep = "Distance"

    @property
    def _context(self):
        ctxt = ["Context:=", self.polyline]
        ctxt.append("PointCount:=")
        ctxt.append(self.point_number)
        return ctxt


class NearField(CommonReport):
    """Near Field Report Class."""

    def __init__(self, app, report_type, setup_name):
        CommonReport.__init__(self, app, report_type, setup_name)
        self.domain = "Sweep"
        self.near_field = None

    @property
    def _context(self):
        return ["Context:=", self.near_field]


class FarField(CommonReport):
    """FarField Report Class."""

    def __init__(self, app, report_type, setup_name):
        CommonReport.__init__(self, app, report_type, setup_name)
        self.domain = "Sweep"
        self.primary_sweep = "Phi"
        self.secondary_sweep = "Theta"
        self.far_field_sphere = None
        if not "Phi" in self.variations:
            self.variations["Phi"] = ["All"]
        if not "Theta" in self.variations:
            self.variations["Theta"] = ["All"]
        if not "Freq" in self.variations:
            self.variations["Freq"] = ["Nominal"]

    @property
    def _context(self):
        return ["Context:=", self.far_field_sphere]


class EyeDiagram(CommonReport):
    """Eye Diagram Report Class."""

    def __init__(self, app, report_type, setup_name):
        CommonReport.__init__(self, app, report_type, setup_name)
        self.domain = "Time"
        self.time_start = "0ns"
        self.time_stop = "200ns"
        self.unit_interval = "0s"
        self.offset = "0ms"
        self.auto_delay = True
        self.manual_delay = "0ps"
        self.auto_cross_amplitude = True
        self.cross_amplitude = "0mV"
        self.auto_compute_eye_meas = True
        self.eye_meas_pont = "5e-10s"
        self.thinning = False
        self.dy_dx_tolerance = 0.001
        self.thinning_points = 500000000

    @property
    def _context(self):
        if self.thinning:
            val = "1"
        else:
            val = "0"
        arg = [
            "NAME:Context",
            "SimValueContext:=",
            [
                1,
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
                "DE",
                False,
                val,
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
                "200ns",
                "WN",
                False,
                "0ps",
                "WS",
                False,
                self.time_start,
            ],
        ]
        return arg

    @property
    def _trace_info(self):
        if isinstance(self.expressions, list):
            return ["Component:=", self.expressions]
        else:
            return ["Component:=", [self.expressions]]

    @pyaedt_function_handler()
    def create(self, plot_name=None):
        """Create a new Eye Diagram Report.

        Parameters
        ----------
        plot_name : str, optional
            Optional Plot name.

        Returns
        -------
        bool
        """
        if not plot_name:
            if self._is_created:
                self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = plot_name
        self._post.oreportsetup.CreateReport(
            self.plot_name,
            self.report_category,
            self.report_type,
            self.setup,
            self._context,
            self._convert_dict_to_report_sel(self.variations),
            self._trace_info,
            [
                "Unit Interval:=",
                self.unit_interval,
                "Offset:=",
                self.offset,
                "Auto Delay:=",
                self.auto_delay,
                "Manual Delay:=",
                self.manual_delay,
                "AutoCompCrossAmplitude:=",
                self.auto_cross_amplitude,
                "CrossingAmplitude:=",
                self.cross_amplitude,
                "AutoCompEyeMeasurementPoint:=",
                self.auto_compute_eye_meas,
                "EyeMeasurementPoint:=",
                self.eye_meas_pont,
            ],
        )
        self._post.plots.append(self)
        self._is_created = True
        return True


class Emission(CommonReport):
    """Emission Report Class."""

    def __init__(self, app, report_type, setup_name):
        CommonReport.__init__(self, app, report_type, setup_name)
        self.domain = "Sweep"
