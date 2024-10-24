if __name__ == "__main__":
    ctl = open("user.ctl", "w")
    ctl.write("begin_data\n")
    ctl.write("timeStep ")
    timeStep = 5e-4
    ctl.write("%e\n" % timeStep)
    ctl.write("end_data\n")
    ctl.close()
