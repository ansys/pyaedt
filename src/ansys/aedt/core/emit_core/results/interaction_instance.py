# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.figure import Figure

from ansys.aedt.core.emit_core.emit_constants import EMI_CATEGORY_TO_INTERFERER_TYPE
from ansys.aedt.core.emit_core.emit_constants import EMIInterfererType
from ansys.aedt.core.emit_core.emit_constants import PowerType
from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.checks import min_aedt_version

if TYPE_CHECKING:
    from ansys.aedt.core.emit_core.results.interaction import Interaction
    from ansys.aedt.core.emit_core.results.revision import Revision


class InteractionInstance:
    def __init__(
        self, emit_obj, domain: InteractionDomain, revision: Revision, parent_interaction: "Interaction | None" = None
    ):
        self.emit_project = emit_obj
        self.odesktop = self.emit_project.odesktop

        self.domain = domain
        self.revision = revision
        self.parent_interaction = parent_interaction
        """Reference to parent Interaction for invalidation tracking."""

    @min_aedt_version("2027.1")
    @pyaedt_function_handler()
    def get_result_warning(self) -> str:
        """Get the result warning for this interaction.

        Returns
        -------
        str
            The warning message if values are invalid, empty string otherwise.
        """
        error = self._check_validity()
        if error:
            raise ValueError(f"Interaction instance is not valid: {error}")

        warning = self.emit_project._emit_com_module.GetResultWarning(
            self.revision.results_index,
            self.domain.receiver_name,
            self.domain.receiver_band_name,
            self.domain.receiver_channel_frequency,
            self.domain.interferer_names,
            self.domain.interferer_band_names,
            self.domain.interferer_channel_frequencies,
        )
        return str(warning) if warning else ""

    @min_aedt_version("2027.1")
    @pyaedt_function_handler()
    def has_valid_values(self) -> bool:
        """
        Check if this interaction instance has valid values.

        Returns ``True`` if at least one of the EMI or desense values
        is a valid numeric result.

        Returns
        -------
        bool
            True if at least one result value is valid, False otherwise.
        """
        error = self._check_validity()
        if error:
            raise ValueError(f"Interaction instance is not valid: {error}")

        valid_values = self.emit_project._emit_com_module.HasValidResultValues(
            self.revision.results_index,
            self.domain.receiver_name,
            self.domain.receiver_band_name,
            self.domain.receiver_channel_frequency,
            self.domain.interferer_names,
            self.domain.interferer_band_names,
            self.domain.interferer_channel_frequencies,
        )
        return bool(valid_values)

    @min_aedt_version("2027.1")
    @pyaedt_function_handler()
    def get_value(self, result_type: ResultType) -> float:
        """
        Get the value of this interaction.

        Parameters
        ----------
        result_type : ResultType
            The type of result to get (EMI, DESENSE, SENSITIVITY, or POWER_AT_RX).

        Returns
        -------
        float
            The value of the interaction, rounded to 2 decimal places.

        Raises
        ------
        ValueError
            If the interaction is invalid or values are not available.
        """
        error = self._check_validity()
        if error:
            raise ValueError(f"Interaction instance is not valid: {error}")

        # Check if the requested result type is valid
        if result_type not in (ResultType.EMI, ResultType.DESENSE, ResultType.SENSITIVITY, ResultType.POWER_AT_RX):
            raise ValueError(
                f"Invalid result type: {result_type}. Must be one of: EMI, DESENSE, SENSITIVITY, POWER_AT_RX."
            )

        # For worst-case instances, check if the requested result type is available locally
        # (a worst-case EMI instance has _encoded_desense=30201 meaning "not available")
        if result_type == ResultType.EMI and self._encoded_emi == 30201:
            raise ValueError("EMI value not available.")
        elif result_type in (ResultType.DESENSE, ResultType.SENSITIVITY) and self._encoded_desense == 30201:
            raise ValueError("Desense and sensitivity values not available.")

        value = self.emit_project._emit_com_module.GetResultValue(
            self.revision.results_index,
            self.domain.receiver_name,
            self.domain.receiver_band_name,
            self.domain.receiver_channel_frequency,
            self.domain.interferer_names,
            self.domain.interferer_band_names,
            self.domain.interferer_channel_frequencies,
            result_type,
        )
        if float(value) < -30000 or float(value) > 30000:
            warning = self.get_result_warning()
            raise ValueError(f"Value not valid: {warning}")
        return float(value)

    @min_aedt_version("2027.1")
    @pyaedt_function_handler()
    def get_largest_emi_problem_type(self) -> EMIInterfererType:
        """
        Return the largest EMI problem type for this interaction.

        Returns
        -------
        EMIInterfererType
            The largest EMI problem type for this interaction.
            Example: IN_CHANNEL_TX_FUNDAMENTAL, OUT_OF_CHANNEL_TX_HARMONIC_SPURIOUS, etc.

        Raises
        ------
        ValueError
            If the interaction is invalid or values are not available.
        """
        error = self._check_validity()
        if error:
            raise ValueError(f"Interaction instance is not valid: {error}")

        if self._encoded_emi == 30201:
            raise ValueError("An EMI value is not available so the largest EMI problem type is undefined.")

        if not self.has_valid_values():
            raise ValueError("An EMI value is not available so the largest EMI problem type is undefined.")

        category = self.emit_project._emit_com_module.GetLargestEmiProblemType(
            self.revision.results_index,
            self.domain.receiver_name,
            self.domain.receiver_band_name,
            self.domain.receiver_channel_frequency,
            self.domain.interferer_names,
            self.domain.interferer_band_names,
            self.domain.interferer_channel_frequencies,
        )

        # Map the category to the enum
        result = EMI_CATEGORY_TO_INTERFERER_TYPE.get(int(category))
        if result is None:
            raise ValueError(f"Error: category {category} not found")
        return result

    @min_aedt_version("2027.2")
    def export_emi_spectrum_to_csv(self, file_name: str = "") -> str:
        """Exports the emi trace data for this instance to a CSV file.

        Parameters
        ----------
        file_name: str, optional
            full path to the file to export to.

        Returns
        -------
        csv_data: str
            stringified data for the node returned if file_name not specified
        """
        self.validate()
        keys = ["EmiType", "UseDomain"]
        vals = ["Point", "true"]
        self.domain._populate_result_trace_properties(keys, vals)
        sim_node: EmitNode = self.revision.get_simulation_node()
        return sim_node._export_to_csv(file_name, "|".join(keys), "|".join(vals))

    @min_aedt_version("2027.2")
    @pyaedt_function_handler()
    def plot_emi_spectrum(self) -> Figure:
        """Plots point EMI margin using matplotlib.

        Returns
        -------
        matplotlib.pyplot.Figure
            The plot figure with frequency in MHz.
        """
        self.validate()
        keys = ["EmiType", "UseDomain"]
        vals = ["Point", "true"]
        self.domain._populate_result_trace_properties(keys, vals)
        sim_node: EmitNode = self.revision.get_simulation_node()
        return sim_node._plot("|".join(keys), "|".join(vals))

    @min_aedt_version("2027.2")
    def export_power_at_port_to_csv(
        self,
        power_type: PowerType,
        component: str | EmitNode,
        port_name: str,
        toward_tx: bool = False,
        file_name: str = "",
    ) -> str | None:
        """Exports the power trace data output at a given rx side port to a CSV file.

        Parameters
        ----------
        power_type: PowerType
            The type of power to export (NARROWBAND or BROADBAND).
        component: str | EmitNode
            The component node or name to export the power trace from.
        port_name: str
            The rx side port name to export the power trace from.
        toward_tx: bool, optional, default False
            If True, export the trace for power going toward the tx radio.
        file_name: str, optional
            full path to the file to export to.

        Returns
        -------
        csv_data: str
            stringified data for the node returned if file_name not specified
        """
        self.validate()
        keys = ["UseDomain"]
        vals = ["true"]
        keys.append("EmiType")
        vals.append("NBPowerTrace" if power_type == PowerType.NARROWBAND else "BBPowerTrace")
        full_port_name = ""
        if isinstance(component, EmitNode):
            full_port_name = f"{component._full_node_name}:{port_name}"
        else:
            comp_node = self.revision.get_component_node(component)
            if not isinstance(comp_node, EmitNode):
                raise ValueError(f"{component} does not exist.")
            full_port_name = f"{comp_node._full_node_name()}:{port_name}"
        keys.append("RxSidePortSelection") if toward_tx else keys.append("TxSidePortSelection")
        vals.append(full_port_name)
        keys.append("Direction")
        vals.append("Toward" if toward_tx else "Away")
        self.domain._populate_result_trace_properties(keys, vals)
        sim_node: EmitNode = self.revision.get_simulation_node()
        return sim_node._export_to_csv(file_name, "|".join(keys), "|".join(vals))

    @min_aedt_version("2027.2")
    @pyaedt_function_handler()
    def plot_power_at_port(
        self, power_type: PowerType, component: str | EmitNode, port_name: str, toward_tx: bool = False
    ) -> Figure:
        """Plots the power trace data output at a given rx side port using matplotlib.

        Parameters
        ----------
        power_type: PowerType
            The type of power to export (NARROWBAND or BROADBAND).
        component: str | EmitNode
            The component node or name to export the power trace from.
        port_name: str
            The rx side port name to export the power trace from.
        toward_tx: bool, optional, default False
            If True, export the trace for power going toward the tx radio.

        Returns
        -------
        matplotlib.pyplot.Figure
            The plot figure with frequency in MHz.
        """
        self.validate()
        keys = ["UseDomain"]
        vals = ["true"]
        keys.append("EmiType")
        vals.append("NBPowerTrace" if power_type == PowerType.NARROWBAND else "BBPowerTrace")
        full_port_name = ""
        if isinstance(component, EmitNode):
            full_port_name = f"{component._full_node_name}:{port_name}"
        else:
            comp_node = self.revision.get_component_node(component)
            if not isinstance(comp_node, EmitNode):
                raise ValueError(f"{component} does not exist.")
            full_port_name = f"{comp_node._full_node_name()}:{port_name}"
        keys.append("RxSidePortSelection") if toward_tx else keys.append("TxSidePortSelection")
        vals.append(full_port_name)
        keys.append("Direction")
        vals.append("Toward" if toward_tx else "Away")

        self.domain._populate_result_trace_properties(keys, vals)
        sim_node: EmitNode = self.revision.get_simulation_node()
        return sim_node._plot("|".join(keys), "|".join(vals))

    @min_aedt_version("2027.2")
    def export_power_at_rx_to_csv(self, power_type: PowerType, file_name: str = "") -> str | None:
        """Exports the power at rx trace data to a CSV file.

        Parameters
        ----------
        power_type: PowerType
            The type of power to export (NARROWBAND or BROADBAND).
        file_name: str[optional]
            full path to the file to export to.

        Returns
        -------
        csv_data: str
            stringified data for the node returned if file_name not specified
        """
        self.validate()
        keys = ["UseDomain"]
        vals = ["true"]
        keys.append("EmiType")
        vals.append("NBPowerAtRx" if power_type == PowerType.NARROWBAND else "BBPowerAtRx")

        self.domain._populate_result_trace_properties(keys, vals)
        sim_node: EmitNode = self.revision.get_simulation_node()
        return sim_node._export_to_csv(file_name, "|".join(keys), "|".join(vals))

    @min_aedt_version("2027.2")
    @pyaedt_function_handler()
    def plot_power_at_rx(self, power_type: PowerType) -> Figure:
        """Plots the power trace data at rx using matplotlib.

        Parameters
        ----------
        power_type: PowerType
            The type of power to export (NARROWBAND or BROADBAND).

        Returns
        -------
        matplotlib.pyplot.Figure
            The plot figure with frequency in MHz.
        """
        self.validate()
        keys = ["UseDomain"]
        vals = ["true"]
        keys.append("EmiType")
        vals.append("NBPowerAtRx" if power_type == PowerType.NARROWBAND else "BBPowerAtRx")

        self.domain._populate_result_trace_properties(keys, vals)
        sim_node: EmitNode = self.revision.get_simulation_node()
        return sim_node._plot("|".join(keys), "|".join(vals))

    @min_aedt_version("2027.1")
    @pyaedt_function_handler()
    def get_domain(self) -> InteractionDomain:
        """Get the interaction domain for this instance.

        Returns
        -------
        InteractionDomain
            The interaction domain.
        """
        return self.domain

    @min_aedt_version("2027.1")
    @pyaedt_function_handler()
    def validate(self) -> None:
        """Validate this interaction instance.

        Raises
        ------
        ValueError
            If the instance is not valid.
        """
        error = self._check_validity()
        if error:
            raise ValueError(error)

    @min_aedt_version("2027.1")
    @pyaedt_function_handler()
    def is_valid(self) -> bool:
        """Check if this interaction instance is still valid.

        Returns
        -------
        bool
            True if the instance is valid, False otherwise.
        """
        return self._check_validity() == ""

    @min_aedt_version("2027.1")
    @pyaedt_function_handler()
    def _check_validity(self) -> str:
        """Check if this interaction instance is still valid.

        Returns
        -------
        str
            An error message if the instance is invalid, empty string if valid.
        """
        sim = self.revision.get_simulation()
        if sim.is_domain_valid(self.domain):
            return "Instance domain is not valid"

        if not self.domain.is_single_instance():
            return "Instance domain is not single instance"
        return ""
