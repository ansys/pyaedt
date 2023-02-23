from itertools import combinations
import numpy as np
import skrf as rf

class Result:
    def __init__(self, app, setup_name, sweep_name):
        self._app = app

    @property
    def terminal_solution_data(self):
        return


class ResultHfss3dlayout(Result):
    def __init__(self, h3d, setup_name, sweep_name):
        Result.__init__(self, h3d, setup_name, sweep_name)
        self.terminal_solution_data_context = [3, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"]

        ports = h3d.excitations
        port_pairs = list(combinations(ports, 2))

        expression = ["S({}, {})".format(*c) for c in port_pairs]
        solution_data = h3d.oreportsetup.GetSolutionDataPerVariation(
            "Standard",
            "{} : {}".format(setup_name, sweep_name),
            self.terminal_solution_data_context,
            ['Freq:=', ['All'], ""],
            expression

        )
        for d in solution_data:
            freq_points = d.GetSweepValues("Freq")
            sdata_3d = np.zeros([len(freq_points), len(ports), len(ports)])

            for i in port_pairs:
                p_a, p_b = i
                expression = "S({}, {})".format(p_a, p_b)
                p_a_number = ports.index(p_a)
                p_b_number = ports.index(p_b)
                sdata_real = d.GetRealDataValues(expression, True)
                sdata_img = d.GetImagDataValues(expression, True)
                sdata_2d = np.array(sdata_real, dtype=complex) + 1j * np.array(sdata_img, dtype=complex)
                sdata_3d[:, p_a_number, p_b_number] = sdata_2d
                sdata_3d[:, p_b_number, p_a_number] = sdata_2d

            for i in ports:
                p_number = ports.index(i)
                expression = "S({}, {})".format(i, i)
                sdata_real = d.GetRealDataValues(expression, True)
                sdata_img = d.GetImagDataValues(expression, True)
                sdata_2d = np.array(sdata_real, dtype=complex) + 1j * np.array(sdata_img, dtype=complex)
                sdata_3d[:, p_number, p_number] = sdata_2d

            nw = rf.Network(s=sdata_3d, frequency=freq_points, z0=50)
            nw.name = ""


