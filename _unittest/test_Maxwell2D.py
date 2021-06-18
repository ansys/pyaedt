#!/ekm/software/anaconda3/bin/python

import os
import pytest
# Setup paths for module imports
from .conftest import local_path, scratch_path


# Import required modules
from pyaedt import Maxwell2d
from pyaedt.generic.filesystem import Scratch
from pyaedt.modeler.Primitives import Polyline
import gc

class TestMaxwell2D:
    def setup_class(self):

        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            try:
                test_project_name = "Motor_EM_R2019R3"
                example_project = os.path.join(local_path, 'example_models', test_project_name + '.aedt')
                test_project = self.local_scratch.copyfile(example_project)
                self.aedtapp = Maxwell2d(test_project, solution_type="TransientZ")
            except:
                pass
                #self.desktop.force_close_desktop()

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()


    def test_02_create_primitive(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id1 = self.aedtapp.modeler.primitives.create_rectangle(udp,[5,3],name="Rectangle1", matname="copper")
        assert isinstance(id1, int)

    def test_03_create_circle(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id1 = self.aedtapp.modeler.primitives.create_circle(udp,3,0, name="Circle1", matname="copper")
        assert isinstance(id1, int)
        id2 = self.aedtapp.modeler.primitives.create_circle(udp,3,8, name="Circle2", matname="copper")
        assert isinstance(id2, int)

    def test_04_create_ellipse(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id1 = self.aedtapp.modeler.primitives.create_ellipse(udp,3,2, name="Ellipse1", matname="copper")
        assert isinstance(id1, int)

    def test_05_create_poly(self):
        udp = [self.aedtapp.modeler.Position(0, 0, 0),self.aedtapp.modeler.Position(10, 5, 0)]
        id1 = self.aedtapp.modeler.primitives.draw_polyline(udp, name="Ellipse1", matname="copper")
        assert isinstance(id1, Polyline)


    def test_03_assign_initial_mesh_from_slider(self):
        assert self.aedtapp.mesh.assign_initial_mesh_from_slider(4)

    def test_04_create_winding(self):

        bounds = self.aedtapp.assign_winding(current_value=20e-3, coil_terminals= ["Rectangle1"])
        assert bounds
        id1 = self.aedtapp.modeler.primitives.create_rectangle([0,0,0],[3,1],name="Rectangle2", matname="copper")
        bounds = self.aedtapp.assign_winding(current_value=20e-3, coil_terminals=id1)
        assert bounds

    def test_05_create_vector_potential(self):

        bounds = self.aedtapp.assign_vector_potential(self.aedtapp.modeler.primitives["Rectangle1"].edges[0].id, 3)
        assert bounds
        assert bounds.props["Value"] == "3"
        line = self.aedtapp.modeler.primitives.draw_polyline([[0,0,0],[1,0,1]],name="myline")
        bound2 = self.aedtapp.assign_vector_potential("myline", 2)
        assert bound2
        assert bound2.props["Value"] == "2"
        assert bound2.update()

    def test_06_create_region(self):
        self.aedtapp.modeler.primitives.delete("Region")
        assert self.aedtapp.modeler.primitives.create_region([100,100,100,100,100,100])


    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()

    def test_08_generate_design_data(self):
        assert self.aedtapp.generate_design_data()

    def test_read_design_data(self):
        self.aedtapp.read_design_data()

    @pytest.mark.parametrize("material", ["ceramic_material", # material not in library
                                          "steel_stainless"])  # material already in library
    def test_07_assign_material(self, material):
        self.aedtapp.assignmaterial(["Rectangle1"], material)
        assert self.aedtapp.modeler.primitives["Rectangle1"].material_name == material

    def test_assign_torque(self):
        assert self.aedtapp.assign_torque("Rectangle1")

    def test_assign_force(self):
        assert self.aedtapp.assign_force("Rectangle1")