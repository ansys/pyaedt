from ..GenericEmitNode import *
class PlotNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    def add_marker(self):
        """Add an icon and/or label to this plot"""
        return self._add_child_node("PlotMarkerNode")

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
    def title(self) -> str:
        """Title
        "Enter title at the top of the plot, room will be made for it."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Title')
        key_val_pair = [i for i in props if 'Title=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @title.setter
    def title(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Title=' + value])

    @property
    def title_font(self):
        """Title Font
        "Configure title font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Title Font')
        key_val_pair = [i for i in props if 'Title Font=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @title_font.setter
    def title_font(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Title Font=' + value])

    @property
    def show_legend(self) -> bool:
        """Show Legend
        "Toggle (on/off) display of plot legend."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Legend')
        key_val_pair = [i for i in props if 'Show Legend=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @show_legend.setter
    def show_legend(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Legend=' + value])

    @property
    def legend_font(self):
        """Legend Font
        "Configure legend font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Legend Font')
        key_val_pair = [i for i in props if 'Legend Font=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @legend_font.setter
    def legend_font(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Legend Font=' + value])

    @property
    def display_cad_overlay(self) -> bool:
        """Display CAD Overlay
        "Toggle on/off overlay of CAD model in plot."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Display CAD Overlay')
        key_val_pair = [i for i in props if 'Display CAD Overlay=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @display_cad_overlay.setter
    def display_cad_overlay(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Display CAD Overlay=' + value])

    @property
    def opacity(self) -> float:
        """Opacity
        "Adjust opacity of CAD model overlay: 0 Transparent - 1 Opaque."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Opacity')
        key_val_pair = [i for i in props if 'Opacity=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @opacity.setter
    def opacity(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Opacity=' + value])

    @property
    def vertical_offset(self) -> float:
        """Vertical Offset
        "Adjust vertical position of CAD model overlay."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Vertical Offset')
        key_val_pair = [i for i in props if 'Vertical Offset=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @vertical_offset.setter
    def vertical_offset(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Vertical Offset=' + value])

    @property
    def range_axis_rotation(self) -> float:
        """Range Axis Rotation
        "Adjust view angle for CAD model overlay by rotating it about plot horizontal axis."
        "Value should be between -180 and 180."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Range Axis Rotation')
        key_val_pair = [i for i in props if 'Range Axis Rotation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @range_axis_rotation.setter
    def range_axis_rotation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Range Axis Rotation=' + value])

    @property
    def lock_axes(self) -> bool:
        """Lock Axes
        "Allow or prevent changing of axes when displayed plot traces are updated."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lock Axes')
        key_val_pair = [i for i in props if 'Lock Axes=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @lock_axes.setter
    def lock_axes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lock Axes=' + value])

    @property
    def x_axis_min(self) -> float:
        """X-axis Min
        "Set lower extent of horizontal axis."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'X-axis Min')
        key_val_pair = [i for i in props if 'X-axis Min=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @x_axis_min.setter
    def x_axis_min(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['X-axis Min=' + value])

    @property
    def x_axis_max(self) -> float:
        """X-axis Max
        "Set upper extent of horizontal axis."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'X-axis Max')
        key_val_pair = [i for i in props if 'X-axis Max=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @x_axis_max.setter
    def x_axis_max(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['X-axis Max=' + value])

    @property
    def y_axis_min(self) -> float:
        """Y-axis Min
        "Set lower extent of vertical axis."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Y-axis Min')
        key_val_pair = [i for i in props if 'Y-axis Min=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @y_axis_min.setter
    def y_axis_min(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Y-axis Min=' + value])

    @property
    def y_axis_max(self) -> float:
        """Y-axis Max
        "Set upper extent of vertical axis."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Y-axis Max')
        key_val_pair = [i for i in props if 'Y-axis Max=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @y_axis_max.setter
    def y_axis_max(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Y-axis Max=' + value])

    @property
    def y_axis_range(self) -> float:
        """Y-axis Range
        "Adjust dB span of vertical axis, makes corresponding adjustment in Y-axis Min."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Y-axis Range')
        key_val_pair = [i for i in props if 'Y-axis Range=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @y_axis_range.setter
    def y_axis_range(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Y-axis Range=' + value])

    @property
    def max_major_ticks(self) -> int:
        """Max Major Ticks
        "Set maximum number of major tick-mark intervals along horizontal axis."
        "Value should be between 1 and 30."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Major Ticks')
        key_val_pair = [i for i in props if 'Max Major Ticks=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @max_major_ticks.setter
    def max_major_ticks(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Major Ticks=' + value])

    @property
    def max_minor_ticks(self) -> int:
        """Max Minor Ticks
        "Set maximum number of minor tick-mark intervals between major ticks along horizontal axis."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Minor Ticks')
        key_val_pair = [i for i in props if 'Max Minor Ticks=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @max_minor_ticks.setter
    def max_minor_ticks(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Minor Ticks=' + value])

    @property
    def max_major_ticks(self) -> int:
        """Max Major Ticks
        "Set maximum number of major tick-mark intervals along vertical axis."
        "Value should be between 1 and 30."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Major Ticks')
        key_val_pair = [i for i in props if 'Max Major Ticks=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @max_major_ticks.setter
    def max_major_ticks(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Major Ticks=' + value])

    @property
    def max_minor_ticks(self) -> int:
        """Max Minor Ticks
        "Set maximum number of minor tick-mark intervals between major ticks along vertical axis."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Minor Ticks')
        key_val_pair = [i for i in props if 'Max Minor Ticks=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @max_minor_ticks.setter
    def max_minor_ticks(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Minor Ticks=' + value])

    @property
    def axis_label_font(self):
        """Axis Label Font
        "Configure axis text labels font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Axis Label Font')
        key_val_pair = [i for i in props if 'Axis Label Font=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @axis_label_font.setter
    def axis_label_font(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Axis Label Font=' + value])

    @property
    def axis_tick_label_font(self):
        """Axis Tick Label Font
        "Configure axis tick numeric labels font family, typeface, and size."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Axis Tick Label Font')
        key_val_pair = [i for i in props if 'Axis Tick Label Font=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @axis_tick_label_font.setter
    def axis_tick_label_font(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Axis Tick Label Font=' + value])

    @property
    def major_grid_line_style(self):
        """Major Grid Line Style
        "Select line style of major-tick grid lines."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Major Grid Line Style')
        key_val_pair = [i for i in props if 'Major Grid Line Style=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @major_grid_line_style.setter
    def major_grid_line_style(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Major Grid Line Style=' + value])
    class MajorGridLineStyleOption(Enum):
            LINES = "Lines"
            DOTTED = "Dotted"
            DASHED = "Dashed"
            DOT_DASH = "Dot-Dash"
            DOT_DOT_DASH = "Dot-Dot-Dash"
            NONE = "None"

    @property
    def major_grid_color(self):
        """Major Grid Color
        "Set color of major-tick grid lines."
        "Color should be in RGB form: #RRGGBB."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Major Grid Color')
        key_val_pair = [i for i in props if 'Major Grid Color=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @major_grid_color.setter
    def major_grid_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Major Grid Color=' + value])

    @property
    def minor_grid_line_style(self):
        """Minor Grid Line Style
        "Select line style of minor-tick grid lines."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Minor Grid Line Style')
        key_val_pair = [i for i in props if 'Minor Grid Line Style=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @minor_grid_line_style.setter
    def minor_grid_line_style(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Minor Grid Line Style=' + value])
    class MinorGridLineStyleOption(Enum):
            LINES = "Lines"
            DOTTED = "Dotted"
            DASHED = "Dashed"
            DOT_DASH = "Dot-Dash"
            DOT_DOT_DASH = "Dot-Dot-Dash"
            NONE = "None"

    @property
    def minor_grid_color(self):
        """Minor Grid Color
        "Set color of minor-tick grid lines."
        "Color should be in RGB form: #RRGGBB."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Minor Grid Color')
        key_val_pair = [i for i in props if 'Minor Grid Color=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @minor_grid_color.setter
    def minor_grid_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Minor Grid Color=' + value])

    @property
    def background_color(self):
        """Background Color
        "Set background color of entire plot."
        "Color should be in RGB form: #RRGGBB."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Background Color')
        key_val_pair = [i for i in props if 'Background Color=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @background_color.setter
    def background_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Background Color=' + value])

    @property
    def bb_power_for_plots_unit(self):
        """BB Power for Plots Unit
        "Units to use for plotting broadband power densities."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'BB Power for Plots Unit')
        key_val_pair = [i for i in props if 'BB Power for Plots Unit=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @bb_power_for_plots_unit.setter
    def bb_power_for_plots_unit(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['BB Power for Plots Unit=' + value])
    class BBPowerforPlotsUnitOption(Enum):
            HERTZ = "hertz"
            KILOHERTZ = "kilohertz"
            MEGAHERTZ = "megahertz"
            GIGAHERTZ = "gigahertz"

    @property
    def bb_power_bandwidth(self) -> float:
        """BB Power Bandwidth
        "Resolution bandwidth for broadband power."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'BB Power Bandwidth')
        key_val_pair = [i for i in props if 'BB Power Bandwidth=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @bb_power_bandwidth.setter
    def bb_power_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['BB Power Bandwidth=' + value])

    @property
    def log_scale(self) -> bool:
        """Log Scale
        "Toggles on/off using a log scale for the X-Axis."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Log Scale')
        key_val_pair = [i for i in props if 'Log Scale=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @log_scale.setter
    def log_scale(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Log Scale=' + value])

