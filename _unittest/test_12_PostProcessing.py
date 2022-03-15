# standard imports
import os

from _unittest.conftest import BasisTest
from _unittest.conftest import config
from pyaedt import Hfss
from pyaedt.generic.general_methods import is_ironpython

try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

try:
    from IPython.display import Image

    ipython_available = True
except ImportError:
    ipython_available = False

test_project_name = "coax_setup_solved"
test_field_name = "Potter_Horn"


class TestClass(BasisTest, object):
    def setup_class(self):
        # set a scratch directory and the environment / test data
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name=test_project_name)
        self.field_test = BasisTest.add_app(self, project_name=test_field_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01B_Field_Plot(self):
        cutlist = ["Global:XY", "Global:XZ", "Global:YZ"]
        setup_name = self.aedtapp.existing_analysis_sweeps[0]
        quantity_name = "ComplexMag_E"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        min_value = self.aedtapp.post.get_scalar_field_value(quantity_name, "Minimum", setup_name, intrinsics="5GHz")
        plot1 = self.aedtapp.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)
        plot1.IsoVal = "Tone"
        assert plot1.change_plot_scale(min_value, "30000")
        assert self.aedtapp.post.create_fieldplot_volume("inner", "Vector_E", setup_name, intrinsic)
        assert self.aedtapp.post.create_fieldplot_surface(
            self.aedtapp.modeler["outer"].faces[0].id, "Mag_E", setup_name, intrinsic
        )

    @pytest.mark.skipif(is_ironpython, reason="Not running in ironpython")
    def test_01_Animate_plt(self):
        cutlist = ["Global:XY"]
        phases = [str(i * 5) + "deg" for i in range(2)]
        model_gif = self.aedtapp.post.animate_fields_from_aedtplt_2(
            quantityname="Mag_E",
            object_list=cutlist,
            plottype="CutPlane",
            meshplot=False,
            setup_name=self.aedtapp.nominal_adaptive,
            intrinsic_dict={"Freq": "5GHz", "Phase": "0deg"},
            project_path=self.local_scratch.path,
            variation_variable="Phase",
            variation_list=phases,
            show=False,
            export_gif=True,
        )
        assert os.path.exists(model_gif.gif_file)

    @pytest.mark.skipif(config["build_machine"] == True, reason="Not running in non-graphical mode")
    def test_02_export_fields(self):
        quantity_name2 = "ComplexMag_H"
        setup_name = "Setup1 : LastAdaptive"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        vollist = ["NewObject_IJD39Q"]
        plot2 = self.aedtapp.post.create_fieldplot_volume(vollist, quantity_name2, setup_name, intrinsic)

        self.aedtapp.post.export_field_image_with_view(
            plot2.name, plot2.plotFolder, os.path.join(self.local_scratch.path, "prova2.jpg")
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "prova2.jpg"))
        assert os.path.exists(
            plot2.export_image(os.path.join(self.local_scratch.path, "test_x.jpg"), orientation="top")
        )

    def test_03_create_scattering(self):
        setup_name = "Setup1 : Sweep"
        portnames = ["1", "2"]
        assert self.aedtapp.create_scattering("MyTestScattering")
        setup_name = "Setup2 : Sweep"
        assert not self.aedtapp.create_scattering("MyTestScattering2", setup_name, portnames, portnames)

    def test_03_get_solution_data(self):
        trace_names = []
        portnames = ["1", "2"]
        for el in portnames:
            for el2 in portnames:
                trace_names.append("S(" + el + "," + el2 + ")")
        cxt = ["Domain:=", "Sweep"]
        families = {"Freq": ["All"]}
        for el in self.aedtapp.available_variations.nominal_w_values_dict:
            families[el] = self.aedtapp.available_variations.nominal_w_values_dict[el]

        my_data = self.aedtapp.post.get_report_data(expression=trace_names, families_dict=families)
        assert my_data
        assert my_data.sweeps
        assert my_data.expressions
        assert my_data.data_db(trace_names[0])
        assert my_data.data_imag(trace_names[0])
        assert my_data.data_real(trace_names[0])
        assert my_data.data_magnitude(trace_names[0])
        assert my_data.export_data_to_csv(os.path.join(self.local_scratch.path, "output.csv"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "output.csv"))

    def test_04_export_touchstone(self):
        self.aedtapp.export_touchstone("Setup1", "Sweep", os.path.join(self.local_scratch.path, "Setup1_Sweep.S2p"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "Setup1_Sweep.S2p"))

    @pytest.mark.skipif(config["build_machine"] == True, reason="Not running in non-graphical mode")
    def test_05_export_report_to_jpg(self):

        self.aedtapp.post.export_report_to_jpg(self.local_scratch.path, "MyTestScattering")
        assert os.path.exists(os.path.join(self.local_scratch.path, "MyTestScattering.jpg"))

    def test_06_export_report_to_csv(self):
        self.aedtapp.post.export_report_to_csv(self.local_scratch.path, "MyTestScattering")
        assert os.path.exists(os.path.join(self.local_scratch.path, "MyTestScattering.csv"))

    def test_07_export_fields_from_Calculator(self):

        self.aedtapp.post.export_field_file_on_grid(
            "E",
            "Setup1 : LastAdaptive",
            self.aedtapp.available_variations.nominal_w_values,
            os.path.join(self.local_scratch.path, "Efield.fld"),
            grid_stop=[5, 5, 5],
            grid_step=[0.5, 0.5, 0.5],
            isvector=True,
            intrinsics="5GHz",
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "Efield.fld"))

        self.aedtapp.post.export_field_file_on_grid(
            "Mag_E",
            "Setup1 : LastAdaptive",
            self.aedtapp.available_variations.nominal_w_values,
            os.path.join(self.local_scratch.path, "MagEfieldSph.fld"),
            gridtype="Spherical",
            grid_stop=[5, 300, 300],
            grid_step=[5, 50, 50],
            isvector=False,
            intrinsics="5GHz",
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "MagEfieldSph.fld"))

        self.aedtapp.post.export_field_file_on_grid(
            "Mag_E",
            "Setup1 : LastAdaptive",
            self.aedtapp.available_variations.nominal_w_values,
            os.path.join(self.local_scratch.path, "MagEfieldCyl.fld"),
            gridtype="Cylindrical",
            grid_stop=[5, 300, 5],
            grid_step=[5, 50, 5],
            isvector=False,
            intrinsics="5GHz",
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "MagEfieldCyl.fld"))

    @pytest.mark.skipif(
        config["build_machine"], reason="Skipped because it cannot run on build machine in non-graphical mode"
    )
    def test_07_copydata(self):
        assert self.aedtapp.post.copy_report_data("MyTestScattering")

    def test_08_manipulate_report(self):
        assert self.aedtapp.post.rename_report("MyTestScattering", "MyNewScattering")

    def test_09_manipulate_report(self):
        assert self.aedtapp.post.create_rectangular_plot("dB(S(1,1))")
        assert len(self.aedtapp.post.all_report_names) > 0

    def test_09b_export_report(self):
        files = self.aedtapp.export_results()
        assert len(files) > 0

    def test_10_delete_report(self):
        assert self.aedtapp.post.delete_report("MyNewScattering")

    def test_12_steal_on_focus(self):
        assert self.aedtapp.post.steal_focus_oneditor()

    @pytest.mark.skipif(
        config["build_machine"], reason="Skipped because it cannot run on build machine in non-graphical mode"
    )
    def test_13_export_model_picture(self):
        path = self.aedtapp.post.export_model_picture(dir=self.local_scratch.path, name="images")
        assert path
        path = self.aedtapp.post.export_model_picture(show_axis=True, show_grid=False, show_ruler=True)
        assert path
        path = self.aedtapp.post.export_model_picture(name="Ericsson", picturename="test_picture")
        assert path
        path = self.aedtapp.post.export_model_picture(picturename="test_picture")
        assert path

    @pytest.mark.skipif(is_ironpython, reason="Not running in ironpython")
    def test_14_Field_Ploton_cutplanedesignname(self):
        cutlist = ["Global:XY"]
        setup_name = self.aedtapp.existing_analysis_sweeps[0]
        quantity_name = "ComplexMag_E"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        self.aedtapp.logger.info("Generating the plot")
        plot1 = self.aedtapp.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)
        plot1.IsoVal = "Tone"
        assert plot1.update_field_plot_settings()
        self.aedtapp.logger.info("Generating the image")
        plot_obj = self.aedtapp.post.plot_field_from_fieldplot(
            plot1.name,
            project_path=self.local_scratch.path,
            meshplot=False,
            imageformat="jpg",
            view="isometric",
            show=False,
        )
        assert os.path.exists(plot_obj.image_file)

    @pytest.mark.skipif(is_ironpython, reason="Not running in ironpython")
    def test_15_export_plot(self):
        obj = self.aedtapp.post.plot_model_obj(
            show=False, export_path=os.path.join(self.local_scratch.path, "image.jpg")
        )
        assert os.path.exists(obj.image_file)

    @pytest.mark.skipif(is_ironpython, reason="Not running in ironpython")
    def test_16_create_field_plot(self):
        cutlist = ["Global:XY"]
        plot = self.aedtapp.post._create_fieldplot(
            objlist=cutlist,
            quantityName="Mag_E",
            setup_name=self.aedtapp.nominal_adaptive,
            intrinsincList={"Freq": "5GHz", "Phase": "0deg"},
            listtype="CutPlane",
        )
        assert plot

    def test_51_get_efields(self):
        if is_ironpython:
            assert True
        else:
            assert self.field_test.post.get_efields_data(ff_setup="3D")

    @pytest.mark.skipif(
        config["build_machine"] or not ipython_available, reason="Skipped because ipython not available"
    )
    def test_52_display(self):
        img = self.aedtapp.post.nb_display(show_axis=True, show_grid=True, show_ruler=True)
        assert isinstance(img, Image)

    def test_53_line_plot(self):
        udp1 = [0, 0, 0]
        udp2 = [1, 0, 0]
        setup_name = "Setup1 : LastAdaptive"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        self.aedtapp.modeler.create_polyline([udp1, udp2], name="Poly1")
        assert self.aedtapp.post.create_fieldplot_line("Poly1", "Mag_E", setup_name, intrinsic)

    def test_54_reload(self):
        self.aedtapp.save_project()
        app2 = Hfss(self.aedtapp.project_name)
        assert len(app2.post.field_plots) == len(self.aedtapp.post.field_plots)
