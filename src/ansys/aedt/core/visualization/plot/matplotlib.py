# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

import ast
import warnings

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler

try:
    import numpy as np
except ImportError:
    warnings.warn(
        "The NumPy module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install numpy"
    )

try:
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    import matplotlib.pyplot as plt

    rc_params = {
        "axes.titlesize": 26,  # Use these default settings for Matplotlb axes.
        "axes.labelsize": 20,  # Apply the settings only in this module.
        "xtick.labelsize": 18,
        "ytick.labelsize": 18,
    }

    plt.ioff()
    default_rc_params = plt.rcParams.copy()
    plt.rcParams.update(rc_params)

except ImportError:
    warnings.warn(
        "The Matplotlib module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install matplotlib\n\nRequires CPython."
    )
except Exception:
    warnings.warn("Unknown error occurred while attempting to import Matplotlib.")


def is_notebook():
    """Check if pyaedt is running in Jupyter or not.

    Returns
    -------
    bool
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        else:
            return False
    except NameError:
        return False  # Probably standard Python interpreter


@pyaedt_function_handler()
def plot_polar_chart(
    plot_data, size=(2000, 1000), show_legend=True, xlabel="", ylabel="", title="", snapshot_path=None, show=True
):
    """Create a Matplotlib polar plot based on a list of data.

    Parameters
    ----------
    plot_data : list of list
        List of plot data. Every item has to be in the following format
        ``[x points, y points, label]``.
    size : tuple, optional
        Image size in pixel (width, height).
    show_legend : bool
        Either to show legend or not.
    xlabel : str
        Plot X label.
    ylabel : str
        Plot Y label.
    title : str
        Plot title label.
    snapshot_path : str
        Full path to the image file if a snapshot is needed.
    show : bool, optional
        Whether to render the figure. The default is ``True``. If ``False``, the
        figure is not drawn.

    Returns
    -------
    :class:`matplotlib.pyplot.Figure`
        Matplotlib figure object.
    """
    dpi = 100.0
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

    label_id = 1
    legend = []
    for plot_object in plot_data:
        if len(plot_object) == 3:
            label = plot_object[2]
        else:
            label = "Trace " + str(label_id)
        theta = np.array(plot_object[0])
        r = np.array(plot_object[1])
        ax.plot(theta, r)
        ax.grid(True)
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        legend.append(label)
        label_id += 1

    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    if show_legend:
        ax.legend(legend)

    # fig = plt.gcf()
    fig.set_size_inches(size[0] / dpi, size[1] / dpi)
    if snapshot_path:
        fig.savefig(snapshot_path)
    if show:  # pragma: no cover
        fig.show()
    plt.rcParams.update(default_rc_params)
    return fig


@pyaedt_function_handler()
def plot_3d_chart(plot_data, size=(2000, 1000), xlabel="", ylabel="", title="", snapshot_path=None, show=True):
    """Create a Matplotlib 3D plot based on a list of data.

    Parameters
    ----------
    plot_data : list of list
        List of plot data. Every item has to be in the following format
        ``[x points, y points, z points, label]``.
    size : tuple, optional
        Image size in pixel (width, height).
    xlabel : str, optional
        Plot X label.
    ylabel : str, optional
        Plot Y label.
    title : str, optional
        Plot Title label.
    snapshot_path : str, optional
        Full path to image file if a snapshot is needed.
    show : bool, optional
        Whether to show the plot or return the matplotlib object. Default is `True`.

    Returns
    -------
    :class:`matplotlib.pyplot.Figure`
        Matplotlib figure object.
    """
    dpi = 100.0
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    fig.set_size_inches(size[0] / dpi, size[1] / dpi)
    if isinstance(plot_data[0], np.ndarray):
        x = plot_data[0]
        y = plot_data[1]
        z = plot_data[2]
    else:
        theta_grid, phi_grid = np.meshgrid(plot_data[0], plot_data[1])
        if isinstance(plot_data[2], list):
            r = np.array(plot_data[2])
        else:
            r = plot_data[2]
        x = r * np.sin(theta_grid) * np.cos(phi_grid)
        y = r * np.sin(theta_grid) * np.sin(phi_grid)
        z = r * np.cos(theta_grid)

    ax.set_xlabel(xlabel, labelpad=20)
    ax.set_ylabel(ylabel, labelpad=20)
    ax.set_title(title)
    ax.plot_surface(x, y, z, rstride=1, cstride=1, cmap=plt.get_cmap("jet"), linewidth=0, antialiased=True, alpha=0.8)

    if snapshot_path:
        fig.savefig(snapshot_path)
    if show:  # pragma: no cover
        fig.show()
    plt.rcParams.update(default_rc_params)
    return fig


@pyaedt_function_handler()
def plot_2d_chart(
    plot_data, size=(2000, 1000), show_legend=True, xlabel="", ylabel="", title="", snapshot_path=None, show=True
):
    """Create a Matplotlib figure based on a list of data.

    Parameters
    ----------
    plot_data : list of list
        List of plot data. Every item has to be in the following format
        `[x points, y points, label]`.
    size : tuple, optional
        Image size in pixel (width, height). The default is `(2000,1600)`.
    show_legend : bool, optional
        Either to show legend or not. The default value is ``True``.
    xlabel : str, optional
        Plot X label. The default value is ``""``.
    ylabel : str, optional
        Plot Y label. The default value is ``""``.
    title : str, optional
        Plot Title label. The default value is ``""``.
    snapshot_path : str, optional
        Full path to image file if a snapshot is needed.
        The default value is ``None``.
    show : bool, optional
        Whether to show the plot or return the matplotlib object. Default is `True`.

    Returns
    -------
    :class:`matplotlib.pyplot.Figure`
        Matplotlib figure object.
    """
    dpi = 100.0
    fig, ax = plt.subplots()
    fig.set_size_inches(size[0] / dpi, size[1] / dpi)
    label_id = 1
    for plo_obj in plot_data:
        if isinstance(plo_obj[0], np.ndarray):
            x = plo_obj[0]
            y = plo_obj[1]
        else:
            x = np.array([i for i, j in zip(plo_obj[0], plo_obj[1]) if j])
            y = np.array([i for i in plo_obj[1] if i])
        label = "Plot {}".format(str(label_id))
        if len(plo_obj) > 2:
            label = plo_obj[2]
        ax.plot(x, y, label=label)
        label_id += 1

    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    if show_legend:
        ax.legend()

    if snapshot_path:
        fig.savefig(snapshot_path)
    elif show and not is_notebook():  # pragma: no cover
        fig.show()
    plt.rcParams.update(default_rc_params)
    return fig


@pyaedt_function_handler()
def plot_matplotlib(
    plot_data,
    size=(2000, 1000),
    show_legend=True,
    xlabel="",
    ylabel="",
    title="",
    snapshot_path=None,
    x_limits=None,
    y_limits=None,
    axis_equal=False,
    annotations=None,
    show=True,
):  # pragma: no cover
    """Create a matplotlib plot based on a list of data.

    Parameters
    ----------
    plot_data : list of list
        List of plot data. Every item has to be in the following format
        For type ``fill``: `[x points, y points, color, label, alpha, type=="fill"]`.
        For type ``path``: `[vertices, codes, color, label, alpha, type=="path"]`.
        For type ``contour``: `[vertices, codes, color, label, alpha, line_width, type=="contour"]`.
    size : tuple, optional
        Image size in pixel (width, height). Default is `(2000, 1000)`.
    show_legend : bool, optional
        Either to show legend or not. Default is `True`.
    xlabel : str, optional
        Plot X label. Default is `""`.
    ylabel : str, optional
        Plot Y label. Default is `""`.
    title : str, optional
        Plot Title label. Default is `""`.
    snapshot_path : str, optional
        Full path to image file if a snapshot is needed. Default is `None`.
    x_limits : list, optional
        List of x limits (left and right). Default is `None`.
    y_limits : list, optional
        List of y limits (bottom and top). Default is `None`.
    axis_equal : bool, optional
         Whether to show the same scale on both axis or have a different scale based on plot size.
        Default is `False`.
    annotations : list, optional
        List of annotations to add to the plot. The format is [x, y, string, dictionary of font options].
        Default is `None`.
    show : bool, optional
        Whether to show the plot or return the matplotlib object. Default is `True`.

    Returns
    -------
    :class:`matplotlib.pyplot.Figure`
        Matplotlib figure object.
    """
    dpi = 100.0
    fig, ax = plt.subplots()
    fig.set_size_inches(size[0] / dpi, size[1] / dpi)

    if isinstance(plot_data, str):
        plot_data = ast.literal_eval(plot_data)
    for points in plot_data:
        if points[-1] == "fill":
            plt.fill(points[0], points[1], c=points[2], label=points[3], alpha=points[4])
        elif points[-1] == "path":
            path = Path(points[0], points[1])
            patch = PathPatch(path, color=points[2], alpha=points[4], label=points[3])
            ax.add_patch(patch)
        elif points[-1] == "contour":
            path = Path(points[0], points[1])
            patch = PathPatch(path, color=points[2], alpha=points[4], label=points[3], fill=False, linewidth=points[5])
            ax.add_patch(patch)

    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    if show_legend:
        ax.legend(loc="upper right")

    # evaluating the limits
    xmin = ymin = 1e30
    xmax = ymax = -1e30
    for points in plot_data:
        if points[-1] == "fill":
            xmin = min(xmin, min(points[0]))
            xmax = max(xmax, max(points[0]))
            ymin = min(ymin, min(points[1]))
            ymax = max(ymax, max(points[1]))
        else:
            for p in points[0]:
                xmin = min(xmin, p[0])
                xmax = max(xmax, p[0])
                ymin = min(ymin, p[1])
                ymax = max(ymax, p[1])
    if x_limits:
        ax.set_xlim(x_limits)
    else:
        ax.set_xlim([xmin, xmax])
    if y_limits:
        ax.set_ylim(y_limits)
    else:
        ax.set_ylim([ymin, ymax])

    if axis_equal:
        ax.axis("equal")

    if annotations:
        for annotation in annotations:
            plt.text(annotation[0], annotation[1], annotation[2], **annotation[3])

    if snapshot_path:
        plt.savefig(snapshot_path)
    if show:  # pragma: no cover
        plt.show()
    plt.rcParams.update(default_rc_params)
    return fig


@pyaedt_function_handler()
def plot_contour(
    plot_data,
    size=(2000, 1600),
    xlabel="",
    ylabel="",
    title="",
    polar=False,
    levels=64,
    max_theta=180,
    color_bar=None,
    snapshot_path=None,
    show=True,
):
    """Create a Matplotlib figure contour based on a list of data.

    Parameters
    ----------
    plot_data : list of np.ndarray
        List of plot data. Each item of the list a numpy array. The list has the following format:
        ``[data, x points, y points]``.
    size : tuple, list, optional
        Image size in pixel (width, height). The default is ``(2000,1600)``.
    xlabel : str, optional
        Plot X label. The default value is ``""``.
    ylabel : str, optional
        Plot Y label. The default value is ``""``.
    title : str, optional
        Plot Title label. The default value is ``""``.
    polar : bool, optional
        Generate the plot in polar coordinates. The default is ``True``. If ``False``, the plot
        generated is rectangular.
    levels : int, optional
        Color map levels. The default is ``64``.
    max_theta : float or int, optional
        Maximum theta angle for plotting. It applies only for polar plots.
        The default is ``180``, which plots the data for all angles.
        Setting ``max_theta`` to 90 limits the displayed data to the upper
        hemisphere, that is (0 < theta < 90).
    color_bar : str, optional
        Color bar title. The default is ``None`` in which case the color bar is not included.
    snapshot_path : str, optional
        Full path to image file if a snapshot is needed.
        The default value is ``None``.
    show : bool, optional
        Whether to show the plot or return the matplotlib object. Default is ``True``.

    Returns
    -------
    :class:`matplotlib.pyplot.Figure`
        Matplotlib figure object.
    """

    dpi = 100.0
    figsize = (size[0] / dpi, size[1] / dpi)

    projection = "polar" if polar else "rectilinear"
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={"projection": projection})

    ax.set_xlabel(xlabel)
    if polar:
        ax.set_rticks(np.linspace(0, max_theta, 3))
    else:
        ax.set_ylabel(ylabel)

    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    if len(plot_data) != 3:  # pragma: no cover
        pyaedt_logger.error("Input should contain 3 numpy arrays.")
        return False
    ph = plot_data[2]
    th = plot_data[1]
    data_to_plot = plot_data[0]
    plt.contourf(
        ph,
        th,
        data_to_plot,
        levels=levels,
        cmap="jet",
    )

    if color_bar:
        cbar = plt.colorbar()
        cbar.set_label(color_bar, rotation=270, labelpad=20)

    ax = plt.gca()
    ax.yaxis.set_label_coords(-0.1, 0.5)

    if snapshot_path:
        fig.savefig(snapshot_path)
    if show:  # pragma: no cover
        fig.show()
    plt.rcParams.update(default_rc_params)
    return fig
