import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src")))

# from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter
from ansys.aedt.core.visualization.plot.plotly_vis import ReportPlotter

# Create a ReportPlotter instance
plotter = ReportPlotter()

# Add a trace (example data)
x = [0, 1, 2, 3]
y = [1, 2, 3, 4]
props = {"x_label": "Angle (deg)", "y_label": "Radius"}
# plotter.add_trace([x, y], properties=props, name="Example Trace")

# Plot in polar coordinates
# fig = plotter.plot_polar(traces=[x, y], to_polar=False, show=True, isplotly=True)
fig = plotter.plot_2d(traces=[x, y], show=True)

# def test_plot_polar_creates_figure():
#     plotter = ReportPlotter()
#     plotter.add_trace([[0, 1, 2], [1, 2, 3]], properties={"x_label": "x", "y_label": "y"})
#     fig = plotter.plot_polar(show=False)
#     assert fig is not None