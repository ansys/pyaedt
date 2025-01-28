class Node_PlotNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    def export_model(self, file_name):
        """Save this data to a file"""
        return self._export_model(file_name)

    def rename(self, new_name):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def get_title(self):
        """Title
        "Enter title at the top of the plot, room will be made for it."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Title')
    def set_title(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Title=' + value])

    @property
    def get_title_font(self):
        """Title Font
        "Configure title font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Title Font')
    def set_title_font(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Title Font=' + value])

    @property
    def get_show_legend(self):
        """Show Legend
        "Toggle (on/off) display of plot legend."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Legend')
    def set_show_legend(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Legend=' + value])

    @property
    def get_legend_font(self):
        """Legend Font
        "Configure legend font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Legend Font')
    def set_legend_font(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Legend Font=' + value])

    @property
    def get_display_cad_overlay(self):
        """Display CAD Overlay
        "Toggle on/off overlay of CAD model in plot."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Display CAD Overlay')
    def set_display_cad_overlay(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Display CAD Overlay=' + value])

    @property
    def get_opacity(self):
        """Opacity
        "Adjust opacity of CAD model overlay: 0 Transparent - 1 Opaque."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Opacity')
    def set_opacity(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Opacity=' + value])

    @property
    def get_vertical_offset(self):
        """Vertical Offset
        "Adjust vertical position of CAD model overlay."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Vertical Offset')
    def set_vertical_offset(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Vertical Offset=' + value])

    @property
    def get_range_axis_rotation(self):
        """Range Axis Rotation
        "Adjust view angle for CAD model overlay by rotating it about plot horizontal axis."
        "Value should be between -180 and 180."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Range Axis Rotation')
    def set_range_axis_rotation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Range Axis Rotation=' + value])

    @property
    def get_lock_axes(self):
        """Lock Axes
        "Allow or prevent changing of axes when displayed plot traces are updated."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lock Axes')
    def set_lock_axes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lock Axes=' + value])

    @property
    def get_x_axis_min(self):
        """X-axis Min
        "Set lower extent of horizontal axis."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'X-axis Min')
    def set_x_axis_min(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['X-axis Min=' + value])

    @property
    def get_x_axis_max(self):
        """X-axis Max
        "Set upper extent of horizontal axis."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'X-axis Max')
    def set_x_axis_max(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['X-axis Max=' + value])

    @property
    def get_y_axis_min(self):
        """Y-axis Min
        "Set lower extent of vertical axis."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Y-axis Min')
    def set_y_axis_min(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Y-axis Min=' + value])

    @property
    def get_y_axis_max(self):
        """Y-axis Max
        "Set upper extent of vertical axis."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Y-axis Max')
    def set_y_axis_max(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Y-axis Max=' + value])

    @property
    def get_y_axis_range(self):
        """Y-axis Range
        "Adjust dB span of vertical axis, makes corresponding adjustment in Y-axis Min."
        "Value should be greater than 0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Y-axis Range')
    def set_y_axis_range(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Y-axis Range=' + value])

    @property
    def get_max_major_ticks(self):
        """Max Major Ticks
        "Set maximum number of major tick-mark intervals along horizontal axis."
        "Value should be between 1 and 30."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Major Ticks')
    def set_max_major_ticks(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Major Ticks=' + value])

    @property
    def get_max_minor_ticks(self):
        """Max Minor Ticks
        "Set maximum number of minor tick-mark intervals between major ticks along horizontal axis."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Minor Ticks')
    def set_max_minor_ticks(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Minor Ticks=' + value])

    @property
    def get_max_major_ticks(self):
        """Max Major Ticks
        "Set maximum number of major tick-mark intervals along vertical axis."
        "Value should be between 1 and 30."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Major Ticks')
    def set_max_major_ticks(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Major Ticks=' + value])

    @property
    def get_max_minor_ticks(self):
        """Max Minor Ticks
        "Set maximum number of minor tick-mark intervals between major ticks along vertical axis."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Minor Ticks')
    def set_max_minor_ticks(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Minor Ticks=' + value])

    @property
    def get_axis_label_font(self):
        """Axis Label Font
        "Configure axis text labels font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Axis Label Font')
    def set_axis_label_font(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Axis Label Font=' + value])

    @property
    def get_axis_tick_label_font(self):
        """Axis Tick Label Font
        "Configure axis tick numeric labels font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Axis Tick Label Font')
    def set_axis_tick_label_font(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Axis Tick Label Font=' + value])

    @property
    def get_major_grid_line_style(self):
        """Major Grid Line Style
        "Select line style of major-tick grid lines."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Major Grid Line Style')
    def set_major_grid_line_style(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Major Grid Line Style=' + value])
    class MajorGridLineStyleOption(Enum):
        (
            LINES = "Lines"
            DOTTED = "Dotted"
            DASHED = "Dashed"
            DOT_DASH = "Dot-Dash"
            DOT_DOT_DASH = "Dot-Dot-Dash"
            NONE = "None"
        )

    @property
    def get_major_grid_color(self):
        """Major Grid Color
        "Set color of major-tick grid lines."
        "Color should be in RGB form: #RRGGBB."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Major Grid Color')
    def set_major_grid_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Major Grid Color=' + value])

    @property
    def get_minor_grid_line_style(self):
        """Minor Grid Line Style
        "Select line style of minor-tick grid lines."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Minor Grid Line Style')
    def set_minor_grid_line_style(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Minor Grid Line Style=' + value])
    class MinorGridLineStyleOption(Enum):
        (
            LINES = "Lines"
            DOTTED = "Dotted"
            DASHED = "Dashed"
            DOT_DASH = "Dot-Dash"
            DOT_DOT_DASH = "Dot-Dot-Dash"
            NONE = "None"
        )

    @property
    def get_minor_grid_color(self):
        """Minor Grid Color
        "Set color of minor-tick grid lines."
        "Color should be in RGB form: #RRGGBB."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Minor Grid Color')
    def set_minor_grid_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Minor Grid Color=' + value])

    @property
    def get_background_color(self):
        """Background Color
        "Set background color of entire plot."
        "Color should be in RGB form: #RRGGBB."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Background Color')
    def set_background_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Background Color=' + value])

    @property
    def get_bb_power_for_plots_unit(self):
        """BB Power for Plots Unit
        "Units to use for plotting broadband power densities."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'BB Power for Plots Unit')
    def set_bb_power_for_plots_unit(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['BB Power for Plots Unit=' + value])
    class BBPowerforPlotsUnitOption(Enum):
        (
            HERTZ = "hertz"
            KILOHERTZ = "kilohertz"
            MEGAHERTZ = "megahertz"
            GIGAHERTZ = "gigahertz"
        )

    @property
    def get_bb_power_bandwidth(self):
        """BB Power Bandwidth
        "Resolution bandwidth for broadband power."
        "Value should be between 1.0 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'BB Power Bandwidth')
    def set_bb_power_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['BB Power Bandwidth=' + value])

    @property
    def get_log_scale(self):
        """Log Scale
        "Toggles on/off using a log scale for the X-Axis."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Log Scale')
    def set_log_scale(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Log Scale=' + value])

