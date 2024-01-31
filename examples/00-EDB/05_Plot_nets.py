# # EDB: plot nets with Matplotlib
#
# This example shows how to use the ``Edb`` class to view nets, layers and
# via geometry directly in Python. The methods demonstrated in this example
# rely on
# [matplotlib](https://matplotlib.org/cheatsheets/_images/cheatsheets-1.png).

# ## Perform required imports

# Perform required imports, which includes importing a section.

import os
import pyaedt
import tempfile

# Download the EDB and copy it into the temporary folder.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
targetfolder = pyaedt.downloads.download_file('edb/ANSYS-HSD_V1.aedb', 
                                              destination=temp_dir.name)

# Create an instance of the Electronics Database usig the
# `pyaedt.Edb` class. 
#
# > Note that units are SI

edb = pyaedt.Edb(edbpath=targetfolder, edbversion="2023.2")

# Display the nets on a layer. Net geometry can be displayed directly in Python usig ``matplotlib`` from
# the ``pyaedt.Edb`` class.

edb.nets.plot("AVCC_1V3")

# Multiple nets may be viewed by passing a list containing the net
# names to the ``plot`` method.

edb.nets.plot(["GND", "GND_DP", "AVCC_1V3"], color_by_net=True)

# All copper on a single layer may also be displayed by passing ``None``
# as the first argument. The 2nd argument is a list 
# of layers to be plotted. In this case, only one 
# layers is displayed.

edb.nets.plot(None, ["1_Top"], color_by_net=True, 
              plot_components_on_top=True)

# A side-view of the layers and padstack geometry is displayed using the
# ``Edb.stackup.plot()`` method.

edb.stackup.plot(scale_elevation=False,
                 plot_definitions=["c100hn140", "c35"])

# Close the EDB.

edb.close_edb()

# Remove all files and the temporary directory.

temp_dir.cleanup()
