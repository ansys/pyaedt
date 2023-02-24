from itertools import combinations
import numpy as np
import skrf as rf


class ResultHfss3dlayout:
    def __init__(self, h3d):
        self._h3d = h3d

    def get_s_parameter(self, setup_name, sweep_name):
        h3d = self._h3d

        s_parameters = []
        context = [3, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"]

        ports = h3d.excitations
        port_order = {ports.index(p): p for p in ports}
        port_pairs = list(combinations(ports, 2))
        port_pairs.extend([(p, p) for p in ports])

        solution = "{} : {}".format(setup_name, sweep_name)
        expression = ["S({}, {})".format(*c) for c in port_pairs]

        variation = ['Freq:=', ['All']]
        for name in h3d._odesign.GetVariables() + h3d._oproject.GetVariables():
            variation.append(name + ":=")
            value = "All"
            variation.append([value])

        solution_data = h3d.oreportsetup.GetSolutionDataPerVariation(
            "Standard",
            solution,
            context,
            variation,
            expression
        )
        for d in solution_data:
            freq_points = rf.Frequency.from_f(d.GetSweepValues("Freq"), unit="Hz")


            sdata_3d = np.zeros([len(freq_points), len(ports), len(ports)], dtype=complex)
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

            var = {}
            for name in d.GetDesignVariableNames():
                value = d.GetDesignVariableValue(name)
                var[name] = value
            params = {"variant": var,
                      "port_order": port_order}
            nw = rf.Network(s=sdata_3d, frequency=freq_points, z0=50.+0.j, params=params)
            s_parameters.append(nw)
        return s_parameters
