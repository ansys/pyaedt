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

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modules.boundary.hfss_boundary import FarFieldSetup
from ansys.aedt.core.modules.boundary.hfss_boundary import NearFieldSetup


class HFSSReport(object):
    """Provides the HFSS report objects."""

    def __init__(self, post_app):
        self.__post_app = post_app
        self.templates_hfss = self.__post_app._templates
        self.report_type = self.__post_app._app.design_solutions.report_type

    @pyaedt_function_handler()
    def standard(self, expressions=None, setup=None):
        """Create a standard or default report object.

        Parameters
        ----------
        expressions : str or list
            Expression List to add into the report. The expression can be any of the available formula
            you can enter into the Electronics Desktop Report Editor.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Be sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.report_templates.Standard`

        Examples
        --------

        >>> from ansys.aedt.core import HFSS
        >>> hfss = HFSS(my_project)
        >>> report = hfss.post.reports_by_category.standard("dB(S(1,1))")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        >>> report2 = hfss.post.reports_by_category.standard(["dB(S(2,1))", "dB(S(2,2))"])

        """
        if not setup:
            setup = self.__post_app._app.nominal_sweep
        rep = None
        if self.report_type not in ["Eigenmode Parameters"]:
            category = "Standard"
            rep = self.templates_hfss[category](self.__post_app, self.report_type, setup)

            expressions = self.__post_app._retrieve_default_expressions(
                expressions=expressions, report=rep, setup_sweep_name=setup
            )

            if expressions:
                rep.expressions = expressions
            else:
                rep = None

        return rep

    @pyaedt_function_handler(sphere_name="far_field_name")
    def far_field(self, expressions=None, setup=None, far_field_name=None, source_context=None, **variations):
        """Create a far field report object.

        Parameters
        ----------
        expressions : str or list
            Expression List to add into the report. The expression can be any of the available formula
            you can enter into the Electronics Desktop Report Editor.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Be sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.
        far_field_name : str, optional
            Name of the sphere to create the far field on.
        source_context : str, optional
            Name of the active source to create the far field on.

        Returns
        -------
        :class:`ansys.aedt.core.modules.report_templates.FarField`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss(my_project)
        >>> report = hfss.post.reports_by_category.far_field("GainTotal","Setup : LastAdaptive","3D_Sphere")
        >>> report.primary_sweep = "Phi"
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup:
            setup = self.__post_app._app.nominal_sweep
        rep = None
        if self.report_type not in ["Eigenmode Parameters"]:
            setup = self.__post_app._get_setup_from_sweep_name(setup)
            category = "Far Fields"

            if far_field_name is None:
                # If not sphere name in the design, then far_field is not available
                far_field_name = next(
                    (fs.name for fs in self.__post_app._app.field_setups if isinstance(fs, FarFieldSetup)), None
                )
                if far_field_name is None:
                    self.__post_app._app.logger.warning("Not available far field setups.")
                    return

            rep = self.templates_hfss[category](self.__post_app, category, setup, far_field_name, **variations)

            rep.source_context = source_context
            rep.report_type = "Radiation Pattern"
            if expressions:
                if type(expressions) == list:
                    rep.expressions = expressions
                else:
                    rep.expressions = [expressions]
            else:
                expressions = self.__post_app._retrieve_default_expressions(
                    expressions=expressions, report=rep, setup_sweep_name=setup, report_category=category
                )
                if expressions:
                    rep.expressions = expressions
                else:
                    rep = None
        return rep

    @pyaedt_function_handler()
    def fields(self, expressions=None, setup=None, polyline=None):
        """Create a Field Report object.

        Parameters
        ----------
        expressions : str or list
            One or more expressions to add to the report. The expression can be any of the available formula
            you can enter into the Electronics Desktop Report Editor.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Be sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.
        polyline : str, optional
            Name of the polyline to plot the field on.
            If a name is not provided, the report might be incorrect.
            The default value is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.report_templates.Fields`

        Examples
        --------

        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss(my_project)
        >>> report = hfss.post.reports_by_category.fields("Mag_E", "Setup : LastAdaptive", "Polyline1")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup:
            setup = self.__post_app._app.nominal_adaptive

        category = "Fields"
        rep = self.templates_hfss[category](self.__post_app, category, setup)

        rep.polyline = polyline
        if polyline is not None:
            rep.primary_sweep = "Distance"
        else:
            rep.primary_sweep = "Phase"

        expressions = self.__post_app._retrieve_default_expressions(
            expressions=expressions, report=rep, setup_sweep_name=setup, report_category=category
        )
        if expressions:
            rep.expressions = expressions
        else:
            rep = None

        return rep

    @pyaedt_function_handler(infinite_sphere="far_field_name")
    def antenna_parameters(self, expressions=None, setup=None, far_field_name=None):
        """Create an Antenna Parameters Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List to add into the report. The expression can be any of the available formula
            you can enter into the Electronics Desktop Report Editor.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Be sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.
        far_field_name : str, optional
            Name of the sphere to compute antenna parameters on.

        Returns
        -------
        :class:`ansys.aedt.core.modules.report_templates.AntennaParameters`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss(my_project)
        >>> report = hfss.post.reports_by_category.antenna_parameters("GainTotal","Setup : LastAdaptive","3D_Sphere")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup:
            setup = self.__post_app._app.nominal_sweep
        rep = None
        if self.report_type not in ["Eigenmode Parameters"]:
            category = "Antenna Parameters"

            if far_field_name is None:
                # If not sphere name in the design, then far_field is not available
                far_field_name = next(
                    (fs.name for fs in self.__post_app._app.field_setups if isinstance(fs, FarFieldSetup)), None
                )
                if far_field_name is None:
                    self.__post_app._app.logger.warning("Not available far field setups.")
                    return

            rep = self.templates_hfss[category](self.__post_app, category, setup, far_field_name)

            expressions = self.__post_app._retrieve_default_expressions(
                expressions=expressions, report=rep, setup_sweep_name=setup, report_category=category
            )

            if expressions:
                rep.expressions = expressions
            else:
                rep = None
        return rep

    @pyaedt_function_handler()
    def near_field(self, expressions=None, setup=None, near_field_name=None):
        """Create a Field Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List to add into the report. The expression can be any of the available formula
            you can enter into the Electronics Desktop Report Editor.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Be sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.
        near_field_name : str, optional
            Name of the near field setup.

        Returns
        -------
        :class:`ansys.aedt.core.modules.report_templates.NearField`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss(my_project)
        >>> report = hfss.post.reports_by_category.near_field("GainTotal", "Setup : LastAdaptive", "NF_1")
        >>> report.primary_sweep = "Phi"
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup:
            setup = self.__post_app._app.nominal_sweep
        rep = None
        if self.report_type not in ["Eigenmode Parameters"]:
            category = "Near Fields"

            if near_field_name is None:
                # If not near field setup in the design, then far_field is not available
                near_field_name = next(
                    (fs.name for fs in self.__post_app._app.field_setups if isinstance(fs, NearFieldSetup)), None
                )
                if near_field_name is None:
                    self.__post_app._app.logger.warning("Not available near field setups.")
                    return

            rep = self.templates_hfss[category](self.__post_app, category, setup, near_field_name)

            expressions = self.__post_app._retrieve_default_expressions(
                expressions=expressions, report=rep, setup_sweep_name=setup, report_category=category
            )

            if expressions:
                rep.expressions = expressions
            else:
                rep = None

        return rep

    @pyaedt_function_handler()
    def modal_solution(self, expressions=None, setup=None):
        """Create a Standard or Default Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List to add into the report. The expression can be any of the available formula
            you can enter into the Electronics Desktop Report Editor.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Be sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.report_templates.Standard`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss(my_project)
        >>> report = hfss.post.reports_by_category.modal_solution("dB(S(1,1))")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup:
            setup = self.__post_app._app.nominal_sweep
        rep = None
        if self.report_type not in ["Eigenmode Parameters"]:
            category = "Modal Solution Data"
            rep = self.templates_hfss[category](self.__post_app, category, setup)

            expressions = self.__post_app._retrieve_default_expressions(
                expressions=expressions, report=rep, setup_sweep_name=setup, report_category=category
            )

            if expressions:
                rep.expressions = expressions
            else:
                rep = None

        return rep

    @pyaedt_function_handler()
    def terminal_solution(self, expressions=None, setup=None):
        """Create a Standard or Default Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List to add into the report. The expression can be any of the available formula
            you can enter into the Electronics Desktop Report Editor.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Be sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.report_templates.HFSSStandard`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss(my_project)
        >>> report = hfss.post.reports_by_category.terminal_solution("dB(S(1,1))")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup:
            setup = self.__post_app._app.nominal_sweep
        rep = None
        if self.report_type not in ["Eigenmode Parameters", "Modal Solution Data"]:
            category = "Terminal Solution Data"
            rep = self.templates_hfss[category](self.__post_app, category, setup)

            expressions = self.__post_app._retrieve_default_expressions(
                expressions=expressions, report=rep, setup_sweep_name=setup, report_category=category
            )

            if expressions:
                rep.expressions = expressions
            else:
                rep = None

        return rep

    @pyaedt_function_handler()
    def eigenmode(self, expressions=None, setup=None):
        """Create a eigen mode report object.

        Parameters
        ----------
        expressions : str or list
            Expression List to add into the report. The expression can be any of the available formula
            you can enter into the Electronics Desktop Report Editor.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Be sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.report_templates.HFSSStandard`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss(my_project)
        >>> report = hfss.post.reports_by_category.eigenmode("dB(S(1,1))")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup:
            setup = self.__post_app._app.nominal_sweep
        rep = None
        if self.report_type in ["Eigenmode Parameters"]:
            category = "Eigenmode Parameters"
            rep = self.templates_hfss[category](self.__post_app, category, setup)

            expressions = self.__post_app._retrieve_default_expressions(
                expressions=expressions, report=rep, setup_sweep_name=setup, report_category=category
            )

            if expressions:
                rep.expressions = expressions
            else:
                rep = None
        return rep

    @pyaedt_function_handler()
    def emission_test(self, expressions=None, setup=None):
        """Create an emission test report object.

        Parameters
        ----------
        expressions : str or list
            Expression List to add into the report. The expression can be any of the available formula
            you can enter into the Electronics Desktop Report Editor.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Be sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.report_templates.Emission`

        Examples
        --------

        >>> from ansys.aedt.core import HFSS
        >>> hfss = HFSS(my_project)
        >>> report = hfss.post.reports_by_category.standard("dB(S(1,1))")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        >>> report2 = hfss.post.reports_by_category.standard(["dB(S(2,1))", "dB(S(2,2))"])

        """
        if not setup:
            setup = self.__post_app._app.nominal_adaptive
        rep = None
        if self.report_type not in ["Eigenmode Parameters", "SBR+", "Transient"]:
            category = "Emission Test"
            rep = self.templates_hfss[category](self.__post_app, category, setup)
            expressions = self.__post_app._retrieve_default_expressions(
                expressions=expressions, report=rep, setup_sweep_name=setup, report_category=category
            )

            if expressions:
                rep.expressions = expressions
            else:
                rep = None

        return rep
