"""
Edb: Plot Nets with Matplotlib
------------------------------
This example shows how to use EDB Class to plot a net or a layout.
"""

###############################################################################
# Import Section
# ~~~~~~~~~~~~~~
import shutil
import os
import tempfile
from pyaedt import generate_unique_name, examples, Edb

###############################################################################
# File download
# ~~~~~~~~~~~~~
# In this section the aedb file will be downloaded and copied in Temporary Folder.

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
# This example launches the :class:`pyaedt.Edb` class.
# This example uses EDB 2022R1 and uses SI units.

edb = Edb(edbpath=targetfolder, edbversion="2022.1")

###############################################################################
# Plot a custom set of nets colored by Layer (default).

edb.core_nets.plot("V3P3_S0")

###############################################################################
# Plot a custom set of nets colored by Nets.

edb.core_nets.plot(["VREF", "V3P3_S0"], color_by_net=True)

###############################################################################
# Plot all nets on a layer colored by Nets.

edb.core_nets.plot(None, ["TOP"], color_by_net=True)

###############################################################################
# Close Db

edb.close_edb()
