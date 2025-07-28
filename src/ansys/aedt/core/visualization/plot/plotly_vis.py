import plotly.graph_objects as go
import numpy as np
import dash
from dash import dcc, html

class Trace:
    def __init__(self):
        self.name = ""
        self._cartesian_data = None
        self._spherical_data = None
        self.x_label = ""
        self.y_label = ""
        self.z_label = ""
        self.trace_style = "solid"
        self.trace_width = 1.5
        self.trace_color = None
        self.symbol_style = "circle"
        self.symbol_color = None
        self.fill_symbol = False

class LimitLine(Trace):
    def __init__(self):
        super().__init__()
        self.hatch_above = True

class ReportPlotter:
    """Plotly Report manager."""
    def __init__(self):
        self._traces = {}
        self._limit_lines = {}
        self._notes = []
        self.show_legend = True
        self.title = ""
        self.fig = None
        self.y_margin_factor = 0.2
        self.x_margin_factor = 0.2

    @property
    def traces(self):
        return self._traces

    @property
    def traces_by_index(self):
        return list(self._traces.values())

    @property
    def trace_names(self):
        return list(self._traces.keys())

    @property
    def limit_lines(self):
        return self._limit_lines

    def add_trace(self, plot_data, data_type=0, properties=None, name=""):
        nt = Trace()
        nt.name = name if name else f"Trace_{len(self.traces)}"
        nt.x_label = properties.get("x_label", "") if properties else ""
        nt.y_label = properties.get("y_label", "") if properties else ""
        nt.z_label = properties.get("z_label", "") if properties else ""
        nt.trace_color = properties.get("trace_color", None) if properties else None
        nt.trace_style = properties.get("trace_style", "solid") if properties else "solid"
        nt.trace_width = properties.get("trace_width", 1.5) if properties else 1.5
        nt.symbol_style = properties.get("symbol_style", "circle") if properties else "circle"
        nt.fill_symbol = properties.get("fill_symbol", False) if properties else False
        nt.symbol_color = properties.get("symbol_color", None) if properties else None
        if data_type == 0:
            nt._cartesian_data = plot_data
        else:
            nt._spherical_data = plot_data
        self._traces[nt.name] = nt
        return True

    def add_limit_line(self, plot_data, hatch_above=True, properties=None, name=""):
        nt = LimitLine()
        nt.hatch_above = hatch_above
        nt.name = name if name else f"Trace_{len(self.traces)}"
        nt.x_label = properties.get("x_label", "") if properties else ""
        nt.y_label = properties.get("y_label", "") if properties else ""
        nt.trace_color = properties.get("trace_color", None) if properties else None
        nt.trace_style = properties.get("trace_style", "solid") if properties else "solid"
        nt.trace_width = properties.get("trace_width", 1.5) if properties else 1.5
        nt.symbol_style = properties.get("symbol_style", "circle") if properties else "circle"
        nt.fill_symbol = properties.get("fill_symbol", False) if properties else False
        nt.symbol_color = properties.get("symbol_color", None) if properties else None
        nt._cartesian_data = plot_data
        self._limit_lines[nt.name] = nt
        return True

    def plot_polar(self, traces=None, to_polar=False, show=True, is_degree=True, figure=None):
        traces_to_plot = self.traces_by_index if traces is None else [self._traces[t] if isinstance(t, str) else self.traces_by_index[t] for t in (traces if isinstance(traces, list) else [traces])]
        self.fig = go.Figure() if figure is None else figure
        rate = np.pi / 180 if is_degree else 1
        for trace in traces_to_plot:
            if not to_polar:
                theta = np.array(trace._cartesian_data[0]) * rate
                r = np.array(trace._cartesian_data[1])
            else:
                x = np.array(trace._cartesian_data[0])
                y = np.array(trace._cartesian_data[1])
                r = np.sqrt(x**2 + y**2)
                theta = np.arctan2(y, x) * rate
            self.fig.add_trace(
                go.Scatterpolar(
                    r=r,
                    theta=theta,
                    mode="lines+markers" if trace.symbol_style else "lines",
                    name=trace.name,
                    line=dict(color=trace.trace_color, width=trace.trace_width, dash=trace.trace_style),
                    marker=dict(symbol=trace.symbol_style, size=8, color=trace.symbol_color),
                )
            )
        # self.fig.update_layout(
        #     polar=dict(
        #         radialaxis_title=traces_to_plot[0].y_label if traces_to_plot else "",
        #         angularaxis_title=traces_to_plot[0].x_label if traces_to_plot else "",
        #         angularaxis_rotation=-90,
        #     ),
        #     # title=self.title,
        #     showlegend=self.show_legend,
        # )
        if show:
            self.fig.show()
        return self.fig

    def plot_2d(self, traces=None, show=True, figure=None):
        traces_to_plot = self.traces_by_index if traces is None else [self._traces[t] if isinstance(t, str) else self.traces_by_index[t] for t in (traces if isinstance(traces, list) else [traces])]
        self.fig = go.Figure() if figure is None else figure
        for trace in traces_to_plot:
            self.fig.add_trace(
                go.Scatter(
                    x=trace._cartesian_data[0],
                    y=trace._cartesian_data[1],
                    mode="lines+markers" if trace.symbol_style else "lines",
                    name=trace.name,
                    line=dict(color=trace.trace_color, width=trace.trace_width, dash=trace.trace_style),
                    marker=dict(symbol=trace.symbol_style, size=8, color=trace.symbol_color),
                )
            )
        self.fig.update_layout(
            xaxis_title=traces_to_plot[0].x_label if traces_to_plot else "",
            yaxis_title=traces_to_plot[0].y_label if traces_to_plot else "",
            title=self.title,
            showlegend=self.show_legend,
        )
        if show:
            self.fig.show()
        return self.fig

    def plot_3d(self, trace=0, show=True, figure=None):
        tr = self.traces_by_index[trace] if isinstance(trace, int) else self._traces[trace]
        self.fig = go.Figure() if figure is None else figure
        self.fig.add_trace(
            go.Surface(
                x=tr._cartesian_data[0],
                y=tr._cartesian_data[1],
                z=tr._cartesian_data[2],
                colorscale="Jet",
                showscale=True,
            )
        )
        self.fig.update_layout(
            title=self.title,
            scene=dict(
                xaxis_title=tr.x_label,
                yaxis_title=tr.y_label,
                zaxis_title=tr.z_label,
            ),
            showlegend=self.show_legend,
        )
        if show:
            self.fig.show()
        return self.fig


# plotter = ReportPlotter()
# # x = [0, 1, 2, 3]
# # y = [1, 2, 3, 4]
# x = np.linspace(-2, 2, 30)
# y = np.linspace(-2, 2, 30)
# x_grid, y_grid = np.meshgrid(x, y)
# z_grid = x_grid**2 + y_grid**2  # Paraboloid surface

# props = {"x_label": "Angle (deg)", "y_label": "Radius"}
# plotter.add_trace([x_grid, y_grid,z_grid], properties=props, name="Parabolid Surface Trace")
# fig = plotter.plot_3d(show=False)  # Show the plot
# # fig.show()

# # Create a dash app
# app = dash.Dash(__name__)
# app.layout = html.Div([
#     html.H2("Plotly Figure in Dash"),
#     dcc.Graph(figure=fig)
# ])

# if __name__ == "__main__":
#     # Example usage
    
#     app.run(debug=True)