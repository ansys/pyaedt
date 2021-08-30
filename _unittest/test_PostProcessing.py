# standard imports
import os
import sys
try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest
# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path, config

# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch
import gc
test_project_name = "coax_setup_solved"
test_field_name = "Potter_Horn"

try:
    from IPython.display import Image, display
    ipython_available = True
except ImportError:
    ipython_available = False

class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            try:
                example_project = os.path.join(
                    local_path, 'example_models', test_project_name + '.aedtz')
                self.test_project = self.local_scratch.copyfile(example_project)
                example_project2 = os.path.join(
                    local_path, 'example_models', test_field_name + '.aedtz')
                self.test_project2 = self.local_scratch.copyfile(example_project2)
                self.aedtapp = Hfss(self.test_project)
            except:
                pass

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    @pytest.mark.skipif(config["build_machine"]==True, reason="Not running in non-graphical mode")
    def test_01_Field_Ploton_cutplanedesignname(self):
        cutlist = ["Global:XY", "Global:XZ", "Global:YZ"]
        setup_name = self.aedtapp.existing_analysis_sweeps[0]
        quantity_name = "ComplexMag_E"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        plot1 = self.aedtapp.post.create_fieldplot_cutplane(
            cutlist, quantity_name, setup_name, intrinsic)
        plot1.IsoVal = "Tone"
        assert plot1.modify_folder()
        image_file = self.aedtapp.post.plot_field_from_fieldplot(plot1.name, project_path=self.local_scratch.path, meshplot=False,
                                              setup_name=setup_name, imageformat="jpg", view="iso", off_screen=True)
        assert os.path.exists(image_file[0])

    @pytest.mark.skipif(config["build_machine"]==True, reason="Not running in non-graphical mode")
    def test_01_Animate_plt(self):
        cutlist = ["Global:XY"]
        phases = [str(i * 5) + "deg" for i in range(2)]
        gif_file=self.aedtapp.post.animate_fields_from_aedtplt_2(quantityname="Mag_E", object_list=cutlist, plottype="CutPlane",
                                                   meshplot=False, setup_name=self.aedtapp.nominal_adaptive,
                                                   intrinsic_dict={"Freq": "5GHz", "Phase": "0deg"},
                                                   project_path=self.local_scratch.path, variation_variable="Phase",
                                                   variation_list=phases, off_screen=True, export_gif=True)
        assert os.path.exists(gif_file)

    @pytest.mark.skipif(config["build_machine"]==True, reason="Not running in non-graphical mode")
    def test_02_export_fields(self):
        quantity_name2 = "ComplexMag_H"
        setup_name = "Setup1 : LastAdaptive"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        vollist = ["NewObject_IJD39Q"]
        plot2 = self.aedtapp.post.create_fieldplot_volume(
            vollist, quantity_name2, setup_name, intrinsic)
        self.aedtapp.post.export_field_image_with_View(
            plot2.name, os.path.join(self.local_scratch.path, "prova2.jpg"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "prova2.jpg"))

    def test_03_create_scattering(self):
        setup_name = "Setup1 : Sweep"
        portnames = ["1", "2"]
        assert self.aedtapp.create_scattering("MyTestScattering")
        setup_name = "Setup2 : Sweep"
        assert not self.aedtapp.create_scattering(
            "MyTestScattering2", setup_name, portnames, portnames)

    def test_03_get_solution_data(self):
        trace_names = []
        portnames = ["1", "2"]
        for el in portnames:
            for el2 in portnames:
                trace_names.append('S(' + el + ',' + el2 + ')')
        cxt = ['Domain:=', 'Sweep']
        families = ['Freq:=', ['All']]
        my_data = self.aedtapp.post.get_report_data(expression=trace_names)
        assert my_data
        assert my_data.sweeps
        assert my_data.expressions
        assert my_data.data_db(trace_names[0])
        assert my_data.data_imag(trace_names[0])
        assert my_data.data_real(trace_names[0])
        assert my_data.data_magnitude(trace_names[0])

    def test_04_export_touchstone(self):
        self.aedtapp.export_touchstone( "Setup1","Sweep", os.path.join(
            self.local_scratch.path, "Setup1_Sweep.S2p"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "Setup1_Sweep.S2p"))

    @pytest.mark.skipif(config["build_machine"]==True, reason="Not running in non-graphical mode")
    def test_05_export_report_to_jpg(self):

        self.aedtapp.post.export_report_to_jpg(self.local_scratch.path, "MyTestScattering")
        assert os.path.exists(os.path.join(self.local_scratch.path, "MyTestScattering.jpg"))

    def test_06_export_report_to_csv(self):
        self.aedtapp.post.export_report_to_csv(self.local_scratch.path, "MyTestScattering")
        assert os.path.exists(os.path.join(self.local_scratch.path, "MyTestScattering.csv"))

    def test_07_export_fields_from_Calculator(self):

        self.aedtapp.post.export_field_file_on_grid("E", "Setup1 : LastAdaptive", self.aedtapp.available_variations.nominal_w_values,
                                                    os.path.join(
                                                        self.local_scratch.path, "Efield.fld"),
                                                    grid_stop=[5, 5, 5], grid_step=[0.5,0.5,0.5], isvector=True, intrinsics="5GHz")
        assert os.path.exists(os.path.join(self.local_scratch.path, "Efield.fld"))

    @pytest.mark.skipif(config["build_machine"], reason="Skipped because it cannot run on build machine in non-graphical mode")
    def test_07_copydata(self):
        assert self.aedtapp.post.copy_report_data("MyTestScattering")

    def test_08_manipulate_report(self):
        assert self.aedtapp.post.rename_report("MyTestScattering", "MyNewScattering")

    def test_09_manipulate_report(self):
        assert self.aedtapp.post.create_rectangular_plot("dB(S(1,1))")

    def test_10_delete_report(self):
        assert self.aedtapp.post.delete_report("MyNewScattering")

    def test_12_steal_on_focus(self):
        assert self.aedtapp.post.steal_focus_oneditor()

    @pytest.mark.skipif(config["build_machine"], reason="Skipped because it cannot run on build machine in non-graphical mode" )
    def test_13_export_model_picture(self):
        path = self.aedtapp.post.export_model_picture(dir=self.local_scratch.path, name="images")
        assert path
        path = self.aedtapp.post.export_model_picture(
            show_axis=True, show_grid=False, show_ruler=True)
        assert path
        path = self.aedtapp.post.export_model_picture(name="Ericsson", picturename="test_picture")
        assert path
        path = self.aedtapp.post.export_model_picture(picturename="test_picture")
        assert path

    def test_11_get_efields(self):
        if "IronPython" in sys.version or ".NETFramework" in sys.version:

            assert True
        else:
            app2 = Hfss(self.test_project2)
            assert app2.post.get_efields_data(ff_setup="3D")
            app2.close_project(saveproject=False)

    @pytest.mark.skipif(not ipython_available, reason="Skipped because ipython not available" )
    def test_nb_display(self):
        img = self.aedtapp.post.nb_display(show_axis=True, show_grid=True, show_ruler=True)
        assert isinstance(img, Image)
