import os
import time
import matplotlib.pyplot as plt
import numpy as np
import pyaedt

from ansys.aedt.core.emit_core.emit_constants import TxRxMode, ResultType
from matplotlib.colors import LinearSegmentedColormap
from tx_rx_response import tx_rx_response

timestamp = time.time()
os.environ["ANSYSCL_SESSION_ID"] = f"DUMMY_VALUE_{timestamp:0.0f}"


def get_data():
    project = r'D:/OneDrive - ANSYS, Inc/Documents/GitHub/AH-64 Apache Cosite.aedt'
    desktop = pyaedt.Desktop(specified_version="2025.1", new_desktop=True)

    emit = pyaedt.Emit(project=project)
    revision = emit.results.analyze()
    domain = emit.results.interaction_domain()

    victims = revision.get_receiver_names()
    aggressors = revision.get_interferer_names()

    victim = victims[0]
    aggressor = aggressors[1]

    victim_bands = revision.get_band_names(victim, TxRxMode.RX)
    aggressor_bands = revision.get_band_names(aggressor, TxRxMode.TX)

    victim_band = victim_bands[0]
    aggressor_band = aggressor_bands[0]

    print(f'{victim}:{victim_band}, {aggressor}:{aggressor_band}')

    emi, rx_power, desense, sensitivity = tx_rx_response(aggressor, victim, aggressor_band, victim_band, domain, revision)
    return emi

#xlabel = "Tx channels", ylabel= "Rx channel",
def plot_matrix_heatmap(data, min_val=None, max_val=None,xlabel = "column index", ylabel= "row index",
                        xticks=None, yticks=None, title="Matrix Heatmap", show_values=True,
                        red_threshold=0,
                        yellow_threshold=-10):
    """
    Create a 2D heatmap visualization of a matrix using a rainbow color scale.

    Parameters:
    -----------
    data : numpy.ndarray
        2D array to visualize
    min_val : float, optional
        Minimum value for color scaling. If None, uses data minimum
    max_val : float, optional
        Maximum value for color scaling. If None, uses data maximum
    title : str, optional
        Title for the plot
    show_values : bool, optional
        Whether to show numerical values in each cell
    """

    # Create figure and axis
    plt.figure()

    # If min_val and max_val aren't provided, use data bounds
    if min_val is None:
        min_val = np.min(data)
    if max_val is None:
        max_val = np.max(data)
    # vmin = -200
    # vmax = 200
    vmin = min_val
    vmax = max_val
    v = vmax-vmin
    r = (red_threshold-vmin)/v
    y = (yellow_threshold-vmin)/v

    # Define color segments with positions
    # cdict = {
    #     'red': [[0.0, 0.0, 0.0],  # green
    #             [y, 0.0, 1.0],  # yellow at y#-10
    #             [r, 1.0, 1.0],  # red starts at 0
    #             [1.0, 1.0, 1.0]],  # red
    #     'green': [[0.0, 1.0, 1.0],  # green
    #               [y, 1.0, 1.0],  # yellow at -10
    #               [r, 1.0, 0.0],  # transition to red at 0
    #               [1.0, 0.0, 0.0]],  # red
    #     'blue': [[0.0, 0.0, 0.0],  # green
    #              [y, 0.0, 0.0],  # yellow at -10
    #              [r, 0.0, 0.0],  # red
    #              [1.0, 0.0, 0.0]]  # red
    # }
    cdict = {
        'red': [(0.0, 0.0, 0.0),  # green
                (y, 0.0, 0.0),  # green up to yellow threshold
                (y, 1.0, 1.0),  # sharp transition to yellow
                (r, 1.0, 1.0),  # yellow up to red threshold
                (r, 1.0, 1.0),  # sharp transition to red
                (1.0, 1.0, 1.0)],  # red

        'green': [(0.0, 1.0, 1.0),  # green
                  (y, 1.0, 1.0),  # green up to yellow threshold
                  (y, 1.0, 1.0),  # sharp transition to yellow
                  (r, 1.0, 1.0),  # yellow up to red threshold
                  (r, 0.0, 0.0),  # sharp transition to red
                  (1.0, 0.0, 0.0)],  # red

        'blue': [(0.0, 0.0, 0.0),  # green
                 (y, 0.0, 0.0),  # yellow threshold
                 (r, 0.0, 0.0),  # red threshold
                 (1.0, 0.0, 0.0)]  # red
    }
    custom_cmap = LinearSegmentedColormap('custom', cdict)

    # Use in imshow
    im = plt.imshow(data, cmap=custom_cmap, vmin=min_val, vmax=max_val, aspect='auto')#-200, vmax=200, aspect='auto')#min_val, vmax=max_val)
    # Create the heatmap
    # im = plt.imshow(data, cmap=cmap, vmin=min_val, vmax=max_val) #extent=[xticks[0],xticks[-1],yticks[0],yticks[-1]])

    # Add colorbar
    plt.colorbar(im, label='Values')

    # Add title and labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(range(len(xticks)), xticks)
    plt.yticks(range(len(yticks)), yticks)
    # Show numerical values in each cell if requested
    if show_values:
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                text_color = 'white' if im.norm(data[i, j]) > 0.5 else 'black'
                plt.text(j, i, f'{data[i, j]:.1f}',
                         ha='center', va='center', color=text_color)

    # Adjust layout to prevent cutting off labels
    plt.tight_layout()
    plt.savefig('my_plot.png')
    print(plt.get_backend())
    return plt.gcf()


# Example usage:
if __name__ == "__main__":
    data = get_data()
    data = np.array(np.transpose(data))

    # Create visualization
    plot_matrix_heatmap(data, title="EMI Waterfall")
    plt.show()
