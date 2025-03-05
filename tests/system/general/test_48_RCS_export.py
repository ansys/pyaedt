# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from pathlib import Path

from ansys.aedt.core.visualization.advanced.rcs_visualization import MonostaticRCSData
from ansys.aedt.core.visualization.post.rcs_exporter import MonostaticRCSExporter
from ansys.aedt.core.visualization.post.solution_data import SolutionData
import pytest

spheres = "RCS"
test_subfolder = "T48"


@pytest.fixture(scope="class")
def project_test(add_app):
    app = add_app(project_name=spheres, subfolder=test_subfolder)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_01_get_rcs(self, project_test):
        freq = [
            "9.250518854999999GHz",
            "9.258846423277779GHz",
            "9.267173991555561GHz",
            "9.27550155983333GHz",
            "9.28382912811111GHz",
            "9.29215669638889GHz",
            "9.30048426466667GHz",
            "9.308811832944439GHz",
            "9.317139401222221GHz",
            "9.325466969500001GHz",
            "9.333794537777781GHz",
            "9.342122106055561GHz",
            "9.35044967433333GHz",
            "9.358777242611112GHz",
            "9.36710481088889GHz",
            "9.37543237916667GHz",
            "9.383759947444441GHz",
            "9.392087515722221GHz",
            "9.400415084GHz",
            "9.40874265227778GHz",
            "9.41707022055555GHz",
            "9.42539778883333GHz",
            "9.433725357111109GHz",
            "9.442052925388889GHz",
            "9.450380493666669GHz",
            "9.45870806194444GHz",
            "9.46703563022222GHz",
            "9.4753631985GHz",
            "9.48369076677778GHz",
            "9.492018335055549GHz",
            "9.500345903333329GHz",
            "9.508673471611109GHz",
            "9.517001039888889GHz",
            "9.525328608166673GHz",
            "9.533656176444451GHz",
            "9.54198374472222GHz",
            "9.550311313GHz",
            "9.55863888127778GHz",
            "9.56696644955556GHz",
            "9.575294017833331GHz",
            "9.583621586111111GHz",
            "9.591949154388891GHz",
            "9.600276722666671GHz",
            "9.60860429094445GHz",
            "9.61693185922222GHz",
            "9.6252594275GHz",
            "9.633586995777778GHz",
            "9.641914564055559GHz",
            "9.650242132333331GHz",
            "9.65856970061111GHz",
            "9.66689726888889GHz",
            "9.67522483716667GHz",
            "9.68355240544444GHz",
            "9.691879973722219GHz",
            "9.700207541999999GHz",
            "9.708535110277779GHz",
            "9.716862678555559GHz",
            "9.72519024683333GHz",
            "9.73351781511111GHz",
            "9.74184538338889GHz",
            "9.75017295166667GHz",
            "9.758500519944439GHz",
            "9.766828088222219GHz",
            "9.775155656500001GHz",
            "9.783483224777781GHz",
            "9.791810793055561GHz",
            "9.80013836133333GHz",
            "9.80846592961111GHz",
            "9.81679349788889GHz",
            "9.82512106616667GHz",
            "9.833448634444441GHz",
            "9.841776202722221GHz",
            "9.850103771000001GHz",
            "9.85843133927778GHz",
            "9.86675890755556GHz",
            "9.87508647583333GHz",
            "9.88341404411111GHz",
            "9.891741612388889GHz",
            "9.900069180666669GHz",
            "9.90839674894444GHz",
            "9.916724317222219GHz",
            "9.9250518855GHz",
            "9.93337945377778GHz",
            "9.941707022055549GHz",
            "9.950034590333329GHz",
            "9.958362158611109GHz",
            "9.966689726888889GHz",
            "9.975017295166669GHz",
            "9.983344863444451GHz",
            "9.99167243172222GHz",
            "10GHz",
            "10.0083275682778GHz",
            "10.0166551365556GHz",
            "10.0249827048333GHz",
            "10.0333102731111GHz",
            "10.0416378413889GHz",
            "10.0499654096667GHz",
            "10.0582929779444GHz",
            "10.0666205462222GHz",
            "10.0749481145GHz",
            "10.0832756827778GHz",
            "10.0916032510556GHz",
            "10.0999308193333GHz",
            "10.1082583876111GHz",
            "10.1165859558889GHz",
            "10.1249135241667GHz",
            "10.1332410924444GHz",
            "10.1415686607222GHz",
            "10.149896229GHz",
            "10.1582237972778GHz",
            "10.1665513655556GHz",
            "10.1748789338333GHz",
            "10.1832065021111GHz",
            "10.1915340703889GHz",
            "10.1998616386667GHz",
            "10.2081892069444GHz",
            "10.2165167752222GHz",
            "10.2248443435GHz",
            "10.2331719117778GHz",
            "10.2414994800556GHz",
            "10.2498270483333GHz",
            "10.2581546166111GHz",
            "10.2664821848889GHz",
            "10.2748097531667GHz",
            "10.2831373214444GHz",
            "10.2914648897222GHz",
            "10.299792458GHz",
            "10.3081200262778GHz",
            "10.3164475945556GHz",
            "10.3247751628333GHz",
            "10.3331027311111GHz",
            "10.3414302993889GHz",
            "10.3497578676667GHz",
            "10.3580854359444GHz",
            "10.3664130042222GHz",
            "10.3747405725GHz",
            "10.3830681407778GHz",
            "10.3913957090556GHz",
            "10.3997232773333GHz",
            "10.4080508456111GHz",
            "10.4163784138889GHz",
            "10.4247059821667GHz",
            "10.4330335504444GHz",
            "10.4413611187222GHz",
            "10.449688687GHz",
            "10.4580162552778GHz",
            "10.4663438235556GHz",
            "10.4746713918333GHz",
            "10.4829989601111GHz",
            "10.4913265283889GHz",
            "10.4996540966667GHz",
            "10.5079816649444GHz",
            "10.5163092332222GHz",
            "10.5246368015GHz",
            "10.5329643697778GHz",
            "10.5412919380556GHz",
            "10.5496195063333GHz",
            "10.5579470746111GHz",
            "10.5662746428889GHz",
            "10.5746022111667GHz",
            "10.5829297794444GHz",
            "10.5912573477222GHz",
            "10.599584916GHz",
            "10.6079124842778GHz",
            "10.6162400525556GHz",
            "10.6245676208333GHz",
            "10.6328951891111GHz",
            "10.6412227573889GHz",
            "10.6495503256667GHz",
            "10.6578778939444GHz",
            "10.6662054622222GHz",
            "10.6745330305GHz",
            "10.6828605987778GHz",
            "10.6911881670556GHz",
            "10.6995157353333GHz",
            "10.7078433036111GHz",
            "10.7161708718889GHz",
            "10.7244984401667GHz",
            "10.7328260084444GHz",
            "10.7411535767222GHz",
            "10.749481145GHz",
        ]
        rcs_data = project_test.get_rcs_data(variation_name="hh_solution", frequencies=freq)
        assert isinstance(rcs_data, MonostaticRCSExporter)

        assert isinstance(rcs_data.model_info, dict)
        assert isinstance(rcs_data.rcs_data, MonostaticRCSData)

        assert Path(rcs_data.metadata_file).is_file()

        assert rcs_data.column_name == "ComplexMonostaticRCSTheta"
        rcs_data.column_name = "ComplexMonostaticRCSPhi"
        assert rcs_data.column_name == "ComplexMonostaticRCSPhi"

        data = rcs_data.get_monostatic_rcs()
        assert isinstance(data, SolutionData)

    def test_02_get_rcs_geometry(self, project_test):
        rcs_exporter = MonostaticRCSExporter(
            project_test,
            setup_name=None,
            frequencies=None,
        )
        assert isinstance(rcs_exporter, MonostaticRCSExporter)
        assert not rcs_exporter.rcs_data
        assert not rcs_exporter.model_info
        metadata_file = rcs_exporter.export_rcs(only_geometry=True)
        assert Path(metadata_file).is_file()
        assert not rcs_exporter.rcs_data
        assert isinstance(rcs_exporter.model_info, dict)
