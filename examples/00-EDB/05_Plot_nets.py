"""
EDB: plot nets with Matplotlib
------------------------------
This example shows how to use the ``Edb`` class to plot a net or a layout.
"""

###############################################################################
# Import section
# ~~~~~~~~~~~~~~
# Import section.

import shutil
import os
import tempfile
from pyaedt import generate_unique_name, examples, Edb

###############################################################################
# Download file
# ~~~~~~~~~~~~~
# Download the AEDT file and copy it into the temporary folder.

tmpfold = tempfile.gettempdir()
temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
example_path = examples.download_aedb()
targetfolder = os.path.join(temp_folder, "Galileo.aedb")
if os.path.exists(targetfolder):
    shutil.rmtree(targetfolder)
shutil.copytree(example_path[:-8], targetfolder)

###############################################################################
# Launch EDB
# ~~~~~~~~~~
# Launch the :class:`pyaedt.Edb` class, using EDB 2022 R2 and SI units.

edb = Edb(edbpath=targetfolder, edbversion="2022.2")

###############################################################################
# Plot custom set of nets colored by layer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot a custom set of nets colored by layer (default).

edb.core_nets.plot("V3P3_S0")

###############################################################################
# Plot custom set of nets colored by nets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot a custom set of nets colored by nets.

edb.core_nets.plot(["VREF", "V3P3_S0"], color_by_net=True)

###############################################################################
# Plot all nets on a layer colored by nets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot all nets on a layer colored by nets.

edb.core_nets.plot(None, ["TOP"], color_by_net=True)

###############################################################################
# Close EDB
# ~~~~~~~~~
# Close EDB.

edb.close_edb()
