from ..EmitNode import *

class ResultPlotNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    def add_marker(self):
        """Add an icon and/or label to this plot"""
        return self._add_child_node("Plot Marker")

    def export_model(self, file_name):
        """Save this data to a file"""
        return self._export_model(file_name)

    @property
    def title(self) -> str:
        """Title
        "Enter title at the top of the plot, room will be made for it."
        "        """
        val = self._get_property('Title')
        return val

    @title.setter
    def title(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Title={value}'])

    @property
    def title_font(self):
        """Title Font
        "Configure title font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        val = self._get_property('Title Font')
        return val

    @title_font.setter
    def title_font(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Title Font={value}'])

    @property
    def show_legend(self) -> bool:
        """Show Legend
        "Toggle (on/off) display of plot legend."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Legend')
        val = (val == 'true')
        return val

    @show_legend.setter
    def show_legend(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Show Legend={value}'])

    @property
    def legend_font(self):
        """Legend Font
        "Configure legend font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        val = self._get_property('Legend Font')
        return val

    @legend_font.setter
    def legend_font(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Legend Font={value}'])

    @property
    def show_emi_thresholds(self) -> bool:
        """Show EMI Thresholds
        "Toggles on/off visibility of the EMI Thresholds."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show EMI Thresholds')
        val = (val == 'true')
        return val

    @show_emi_thresholds.setter
    def show_emi_thresholds(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Show EMI Thresholds={value}'])

    @property
    def display_cad_overlay(self) -> bool:
        """Display CAD Overlay
        "Toggle on/off overlay of CAD model in plot."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Display CAD Overlay')
        val = (val == 'true')
        return val

    @display_cad_overlay.setter
    def display_cad_overlay(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Display CAD Overlay={value}'])

    @property
    def opacity(self) -> float:
        """Opacity
        "Adjust opacity of CAD model overlay: 0 Transparent - 1 Opaque."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Opacity')
        return val

    @opacity.setter
    def opacity(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Opacity={value}'])

    @property
    def vertical_offset(self) -> float:
        """Vertical Offset
        "Adjust vertical position of CAD model overlay."
        "        """
        val = self._get_property('Vertical Offset')
        return val

    @vertical_offset.setter
    def vertical_offset(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Vertical Offset={value}'])

    @property
    def range_axis_rotation(self) -> float:
        """Range Axis Rotation
        "Adjust view angle for CAD model overlay by rotating it about plot horizontal axis."
        "Value should be between -180 and 180."
        """
        val = self._get_property('Range Axis Rotation')
        return val

    @range_axis_rotation.setter
    def range_axis_rotation(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Range Axis Rotation={value}'])

    @property
    def lock_axes(self) -> bool:
        """Lock Axes
        "Allow or prevent changing of axes when displayed plot traces are updated."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Lock Axes')
        val = (val == 'true')
        return val

    @lock_axes.setter
    def lock_axes(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Lock Axes={value}'])

    @property
    def x_axis_min(self) -> float:
        """X-axis Min
        "Set lower extent of horizontal axis."
        "        """
        val = self._get_property('X-axis Min')
        return val

    @x_axis_min.setter
    def x_axis_min(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'X-axis Min={value}'])

    @property
    def x_axis_max(self) -> float:
        """X-axis Max
        "Set upper extent of horizontal axis."
        "        """
        val = self._get_property('X-axis Max')
        return val

    @x_axis_max.setter
    def x_axis_max(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'X-axis Max={value}'])

    @property
    def y_axis_min(self) -> float:
        """Y-axis Min
        "Set lower extent of vertical axis."
        "        """
        val = self._get_property('Y-axis Min')
        return val

    @y_axis_min.setter
    def y_axis_min(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Y-axis Min={value}'])

    @property
    def y_axis_max(self) -> float:
        """Y-axis Max
        "Set upper extent of vertical axis."
        "        """
        val = self._get_property('Y-axis Max')
        return val

    @y_axis_max.setter
    def y_axis_max(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Y-axis Max={value}'])

    @property
    def y_axis_range(self) -> float:
        """Y-axis Range
        "Adjust dB span of vertical axis, makes corresponding adjustment in Y-axis Min."
        "Value should be greater than 0."
        """
        val = self._get_property('Y-axis Range')
        return val

    @y_axis_range.setter
    def y_axis_range(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Y-axis Range={value}'])

    @property
    def max_major_ticks(self) -> int:
        """Max Major Ticks
        "Set maximum number of major tick-mark intervals along horizontal axis."
        "Value should be between 1 and 30."
        """
        val = self._get_property('Max Major Ticks')
        return val

    @max_major_ticks.setter
    def max_major_ticks(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Max Major Ticks={value}'])

    @property
    def max_minor_ticks(self) -> int:
        """Max Minor Ticks
        "Set maximum number of minor tick-mark intervals between major ticks along horizontal axis."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Max Minor Ticks')
        return val

    @max_minor_ticks.setter
    def max_minor_ticks(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Max Minor Ticks={value}'])

    @property
    def max_major_ticks(self) -> int:
        """Max Major Ticks
        "Set maximum number of major tick-mark intervals along vertical axis."
        "Value should be between 1 and 30."
        """
        val = self._get_property('Max Major Ticks')
        return val

    @max_major_ticks.setter
    def max_major_ticks(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Max Major Ticks={value}'])

    @property
    def max_minor_ticks(self) -> int:
        """Max Minor Ticks
        "Set maximum number of minor tick-mark intervals between major ticks along vertical axis."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Max Minor Ticks')
        return val

    @max_minor_ticks.setter
    def max_minor_ticks(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Max Minor Ticks={value}'])

    @property
    def axis_label_font(self):
        """Axis Label Font
        "Configure axis text labels font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        val = self._get_property('Axis Label Font')
        return val

    @axis_label_font.setter
    def axis_label_font(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Axis Label Font={value}'])

    @property
    def axis_tick_label_font(self):
        """Axis Tick Label Font
        "Configure axis tick numeric labels font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        val = self._get_property('Axis Tick Label Font')
        return val

    @axis_tick_label_font.setter
    def axis_tick_label_font(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Axis Tick Label Font={value}'])

    class MajorGridLineStyleOption(Enum):
            LINES = "Lines"
            DOTTED = "Dotted"
            DASHED = "Dashed"
            DOT_DASH = "Dot-Dash"
            DOT_DOT_DASH = "Dot-Dot-Dash"
            NONE = "None"

    @property
    def major_grid_line_style(self) -> MajorGridLineStyleOption:
        """Major Grid Line Style
        "Select line style of major-tick grid lines."
        "        """
        val = self._get_property('Major Grid Line Style')
        val = self.MajorGridLineStyleOption[val.upper()]
        return val

    @major_grid_line_style.setter
    def major_grid_line_style(self, value: MajorGridLineStyleOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Major Grid Line Style={value.value}'])

    @property
    def major_grid_color(self):
        """Major Grid Color
        "Set color of major-tick grid lines."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Major Grid Color')
        return val

    @major_grid_color.setter
    def major_grid_color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Major Grid Color={value}'])

    class MinorGridLineStyleOption(Enum):
            LINES = "Lines"
            DOTTED = "Dotted"
            DASHED = "Dashed"
            DOT_DASH = "Dot-Dash"
            DOT_DOT_DASH = "Dot-Dot-Dash"
            NONE = "None"

    @property
    def minor_grid_line_style(self) -> MinorGridLineStyleOption:
        """Minor Grid Line Style
        "Select line style of minor-tick grid lines."
        "        """
        val = self._get_property('Minor Grid Line Style')
        val = self.MinorGridLineStyleOption[val.upper()]
        return val

    @minor_grid_line_style.setter
    def minor_grid_line_style(self, value: MinorGridLineStyleOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Minor Grid Line Style={value.value}'])

    @property
    def minor_grid_color(self):
        """Minor Grid Color
        "Set color of minor-tick grid lines."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Minor Grid Color')
        return val

    @minor_grid_color.setter
    def minor_grid_color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Minor Grid Color={value}'])

    @property
    def background_color(self):
        """Background Color
        "Set background color of entire plot."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Background Color')
        return val

    @background_color.setter
    def background_color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Background Color={value}'])

    class BBPowerforPlotsUnitOption(Enum):
            HERTZ = "hertz"
            KILOHERTZ = "kilohertz"
            MEGAHERTZ = "megahertz"
            GIGAHERTZ = "gigahertz"

    @property
    def bb_power_for_plots_unit(self) -> BBPowerforPlotsUnitOption:
        """BB Power for Plots Unit
        "Units to use for plotting broadband power densities."
        "        """
        val = self._get_property('BB Power for Plots Unit')
        val = self.BBPowerforPlotsUnitOption[val.upper()]
        return val

    @bb_power_for_plots_unit.setter
    def bb_power_for_plots_unit(self, value: BBPowerforPlotsUnitOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'BB Power for Plots Unit={value.value}'])

    @property
    def bb_power_bandwidth(self) -> float:
        """BB Power Bandwidth
        "Resolution bandwidth for broadband power."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('BB Power Bandwidth')
        val = self._convert_from_internal_units(float(val), "")
        return val

    @bb_power_bandwidth.setter
    def bb_power_bandwidth(self, value : float|str):
        value = self._convert_to_internal_units(value, "")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'BB Power Bandwidth={value}'])

    @property
    def log_scale(self) -> bool:
        """Log Scale
        "Toggles on/off using a log scale for the X-Axis."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Log Scale')
        val = (val == 'true')
        return val

    @log_scale.setter
    def log_scale(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Log Scale={value}'])

