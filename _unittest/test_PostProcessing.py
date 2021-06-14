# standard imports
import os
import pytest
# Setup paths for module imports
from .conftest import local_path, scratch_path

# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch
import gc

test_project_name = "coax_setup_solved"


class TestDesign:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            try:
                example_project = os.path.join(local_path, 'example_models', test_project_name + '.aedtz')
                self.test_project = self.local_scratch.copyfile(example_project)

                self.aedtapp = Hfss(self.test_project)
            except:
                pass
                #self.desktop.force_close_desktop()


    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    @pytest.mark.skip(reason="Not running in non-graphical mode")
    def test_01_Field_Ploton_cutplanedesignname(self):
        cutlist = ["Global:XY", "Global:XZ", "Global:YZ"]
        setup_name = self.aedtapp.existing_analysis_sweeps[0]
        quantity_name = "ComplexMag_E"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        plot1 = self.aedtapp.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)
        plot1.IsoVal = "Tone"
        assert plot1.modify_folder()
        image_file = self.aedtapp.post.plot_field_from_fieldplot(plot1.name, project_path=self.local_scratch.path, meshplot=False,
                                              setup_name=setup_name, imageformat="jpg", view="iso", off_screen=True)
        assert os.path.exists(image_file[0])

    def test_01_Animate_plt(self):
        cutlist = ["Global:XY"]
        phases = [str(i * 5) + "deg" for i in range(18)]
        gif_file=self.aedtapp.post.animate_fields_from_aedtplt_2(quantityname="Mag_E", object_list=cutlist, plottype="CutPlane",
                                                   meshplot=False, setup_name=self.aedtapp.nominal_adaptive,
                                                   intrinsic_dict={"Freq": "5GHz", "Phase": "0deg"},
                                                   project_path=self.local_scratch.path, variation_variable="Phase",
                                                   variation_list=phases, off_screen=True, export_gif=True)
        assert os.path.exists(gif_file)



    def test_02_export_fields(self):
        quantity_name2 = "ComplexMag_H"
        setup_name = "Setup1 : LastAdaptive"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        vollist = ["NewObject_IJD39Q"]
        plot2 = self.aedtapp.post.create_fieldplot_volume(vollist, quantity_name2, setup_name, intrinsic)
        self.aedtapp.post.export_field_image_with_View(plot2.name, os.path.join(self.local_scratch.path, "prova2.jpg"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "prova2.jpg"))

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
                trace_names.append('S(' + el + ',' + el2 + ')')
        cxt = ['Domain:=', 'Sweep']
        families = ['Freq:=', ['All']]
        my_data = self.aedtapp.post.get_report_data(expression=trace_names)
        assert my_data
        assert my_data.sweeps
        assert my_data.expressions
        assert my_data.data_db

    def test_04_export_touchstone(self):
        self.aedtapp.export_touchstone( "Setup1","Sweep", os.path.join(self.local_scratch.path, "Setup1_Sweep.S2p"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "Setup1_Sweep.S2p"))

    @pytest.mark.skip(reason="Not running in non-graphical mode")
    def test_05_export_report_to_jpg(self):

        self.aedtapp.post.export_report_to_jpg(self.local_scratch.path, "MyTestScattering")
        assert os.path.exists(os.path.join(self.local_scratch.path, "MyTestScattering.jpg"))

    def test_06_export_report_to_csv(self):
        self.aedtapp.post.export_report_to_csv(self.local_scratch.path, "MyTestScattering")
        assert os.path.exists(os.path.join(self.local_scratch.path, "MyTestScattering.csv"))


    def test_07_export_fields_from_Calculator(self):

        self.aedtapp.post.export_field_file_on_grid("E", "Setup1 : LastAdaptive", self.aedtapp.available_variations.nominal_w_values,
                                                    os.path.join(self.local_scratch.path, "Efield.fld"),
                                                    grid_stop=[5, 5, 5], grid_step=[0.5,0.5,0.5], isvector=True, intrinsics="5GHz")
        assert os.path.exists(os.path.join(self.local_scratch.path, "Efield.fld"))

    @pytest.mark.skip("Skipped because it cannot run on build machine in non-graphical mode")
    def test_07_copydata(self):
        assert self.aedtapp.post.copy_report_data("MyTestScattering")

    def test_08_manipulate_report(self):
        assert self.aedtapp.post.rename_report("MyTestScattering", "MyNewScattering")

    def test_09_manipulate_report(self):
        assert self.aedtapp.post.create_rectangular_plot("dB(S(1,1))")

    def test_10_delete_report(self):
        assert self.aedtapp.post.delete_report("MyNewScattering")

    @pytest.mark.skip("Skipped because there is no Plotly on build machine")
    def test_11_export_jpg_from_aedtflt(self):
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        cutlist = ["Global:XY"]
        plot = self.aedtapp.post.create_fieldplot_cutplane(cutlist,"Mag_Jsurf",setup_name=self.aedtapp.nominal_adaptive, intrinsincDict=intrinsic)
        fl = self.aedtapp.post.plot_field_from_fieldplot(plot.name, project_path=self.local_scratch.path, intrinsic_dict=intrinsic, meshplot=True, plot_after_export=False)
        assert len(fl)>0