###########################
# Control program example #
# 06.05.2021 Irene Woyna  #
###########################

import math
import os.path

ctl = open("user.ctl", "w")
ctl.write("begin_data\n")
ctl.write("timeStep ")
timeStep = 5e-4
ctl.write("%e\n" % timeStep)
ctl.write("end_data\n")
ctl.close()
