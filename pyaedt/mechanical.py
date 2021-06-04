"""
Mechanical Class
----------------------------------------------------------------


Description
==================================================

This class contains all the Mechanical Functionalities. It inherites all the objects that belongs to Mechanical





"""
from __future__ import absolute_import

from .application.Analysis3D import FieldAnalysis3D
from .desktop import exception_to_desktop
from .generic.general_methods import generate_unique_name, aedt_exception_handler
from .modules.Boundary import BoundaryObject
from collections import OrderedDict


class Mechanical(FieldAnalysis3D, object):
    """Mechanical Object

    Parameters
    ----------
    projectname :
        name of the project to be selected or full path to the project to be opened  or to the AEDTZ archive. if None try to get active project and, if nothing present to create an empty one
    designname :
        name of the design to be selected. if None, try to get active design and, if nothing present to create an empty one
    solution_type :
        solution type to be applied to design. if None default is taken
    setup_name :
        setup_name to be used as nominal. if none active setup is taken or nothing

    Returns
    -------

    """

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None):

        FieldAnalysis3D.__init__(self, "Mechanical", projectname, designname, solution_type, setup_name)
    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to parent object Design """
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    @aedt_exception_handler
    def assign_em_losses(self, designname="HFSSDesign1", setupname="Setup1", sweepname="LastAdaptive", map_frequency=None,
                         surface_objects=[], source_project_name=None, paramlist=[], object_list=[]):
        """Map EM losses to Mechanical Design

        Parameters
        ----------
        designname :
            name of design of the source mapping (Default value = "HFSSDesign1")
        map_frequency :
            string containing Frequency to be mapped. It must be None for eigen mode analysis (Default value = None)
        setupname :
            Name of EM Setup (Default value = "Setup1")
        sweepname :
            Name of EM Sweep to be used for mapping. Default no sweep and LastAdaptive to be used
        surface_objects :
            list of objects in the source that are metals (Default value = [])
        source_project_name :
            Name of the source project: None to use source from the same project (Default value = None)
        paramlist :
            list of all params in EM to be mapped (Default value = [])
        object_list :
             (Default value = [])

        Returns
        -------

        """
        assert self.solution_type == "Thermal", "This Method works only in Mechanical Structural Solution"

        self._messenger.add_info_message("Mapping HFSS EM Lossess")
        oName = self.project_name
        if oName == source_project_name or source_project_name is None:
            projname = "This Project*"
        else:
            projname = source_project_name + ".aedt"
        #
        # Generate a list of model objects from the lists made previously and use to map the HFSS losses into Icepak
        #
        if not object_list:
            allObjects = self.modeler.primitives.get_all_objects_names(refresh_list=True)
        else:
            allObjects = object_list[:]
        surfaces = surface_objects
        if map_frequency:
            intr = [map_frequency]
        else:
            intr = []

        argparam = OrderedDict({})
        for el in self.available_variations.nominal_w_values_dict:
            argparam[el] = self.available_variations.nominal_w_values_dict[el]

        for el in paramlist:
            argparam[el]=el

        props = OrderedDict(
            {"Objects": allObjects, "allObjects": False, "Project": projname, "projname": "ElectronicsDesktop",
             "Design": designname, "Soln": setupname + " : " + sweepname, "Params": argparam,
             "ForceSourceToSolve": True, "PreservePartnerSoln": True, "PathRelativeTo": "TargetProject"})
        if intr:
            props["Intrinsics"]= intr
            props["SurfaceOnly"]= surfaces

        name = generate_unique_name("EMLoss")
        bound = BoundaryObject(self, name, props, "EMLoss")
        if bound.create():
            self.boundaries.append(bound)
            self._messenger.add_info_message('EM losses Mapped from design {}'.format(designname))
            return bound
        return False

    @aedt_exception_handler
    def assign_thermal_map(self, object_list, designname="IcepakDesign1", setupname="Setup1", sweepname="SteadyState",
                           source_project_name=None, paramlist=[]):
        """Map Thermal losses to Mechanical Design. It works only coupled with Icepak in 2021r2

        Parameters
        ----------
        designname :
            name of design of the source mapping (Default value = "IcepakDesign1")
        setupname :
            Name of EM Setup (Default value = "Setup1")
        sweepname :
            Name of EM Sweep to be used for mapping. Default no sweep and LastAdaptive to be used
        source_project_name :
            Name of the source project: None to use source from the same project (Default value = None)
        paramlist :
            list of all params in EM to be mapped (Default value = [])
        object_list :
            

        Returns
        -------

        """

        assert self.solution_type == "Structural", "This Method works only in Mechanical Structural Solution"

        self._messenger.add_info_message("Mapping HFSS EM Lossess")
        oName = self.project_name
        if oName == source_project_name or source_project_name is None:
            projname = "This Project*"
        else:
            projname = source_project_name + ".aedt"
        #
        # Generate a list of model objects from the lists made previously and use to map the HFSS losses into Icepak
        #
        if not object_list:
            allObjects = self.modeler.primitives.get_all_objects_names(refresh_list=True)
        else:
            allObjects = object_list[:]
        argparam = OrderedDict({})
        for el in self.available_variations.nominal_w_values_dict:
            argparam[el] = self.available_variations.nominal_w_values_dict[el]

        for el in paramlist:
            argparam[el] = el

        props = OrderedDict(
            {"Objects": allObjects, "Uniform": False, "Project": projname, "Product": "ElectronicsDesktop",
             "Design": designname, "Soln": setupname + " : " + sweepname, "Params": argparam,
             "ForceSourceToSolve": True, "PreservePartnerSoln": True, "PathRelativeTo": "TargetProject"})

        name = generate_unique_name("ThermalLink")
        bound = BoundaryObject(self, name, props, "ThermalCondition")
        if bound.create():
            self.boundaries.append(bound)
            self._messenger.add_info_message('Thermal Conditions Mapped from design {}'.format(designname))
            return bound

        return True

    @aedt_exception_handler
    def assign_uniform_convection(self, objects_list, convection_value, convection_unit="w_per_m2kel",
                                  temperature="AmbientTemp", boundary_name=""):
        """Assign uniform convection to face list

        Parameters
        ----------
        objects_list :
            list of objects/faces
        convection_value :
            convection value
        convection_unit :
            str optional convection units (Default value = "w_per_m2kel")
        temperature :
            optional Temperature (Default value = "AmbientTemp")
        boundary_name :
            optional boundary object name (Default value = "")

        Returns
        -------
        type
            Boundary Object

        """
        assert self.solution_type == "Thermal", "This Method works only in Mechanical Structural Solution"

        props = {}
        objects_list = self.modeler._convert_list_to_ids(objects_list)

        if type(objects_list) is list:
            if type(objects_list[0]) is str:
                props["Objects"] = objects_list
            else:
                props["Faces"] = objects_list

        props["Temperature"] = temperature
        props["Uniform"] = True
        props["FilmCoeff"] = str(convection_value) + convection_unit

        if not boundary_name:
            boundary_name = generate_unique_name("Convection")
        bound = BoundaryObject(self, boundary_name, props, 'Convection')
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_uniform_temperature(self, objects_list, temperature="AmbientTemp", boundary_name=""):
        """Assign Uniform Temperature Boundary. Works only in Thermal module

        Parameters
        ----------
        objects_list :
            list of objects/faces
        temperature :
            Temperature Value (Default value = "AmbientTemp")
        boundary_name :
            str optional boundary name (Default value = "")

        Returns
        -------
        type
            Boundary Object

        """
        assert self.solution_type == "Thermal", "This Method works only in Mechanical Structural Solution"

        props = {}
        objects_list = self.modeler._convert_list_to_ids(objects_list)

        if type(objects_list) is list:
            if type(objects_list[0]) is str:
                props["Objects"] = objects_list
            else:
                props["Faces"] = objects_list

        props["Temperature"] = temperature

        if not boundary_name:
            boundary_name = generate_unique_name("Temp")
        bound = BoundaryObject(self, boundary_name, props, 'Temperature')
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False


    @aedt_exception_handler
    def assign_frictionless_support(self, objects_list,  boundary_name=""):
        """Assign Mechanical Frictionless Support. Works only in Structural Analysis

        Parameters
        ----------
        objects_list :
            list of faces to apply Frictionless support
        boundary_name :
            optional name of boundary (Default value = "")

        Returns
        -------
        type
            boundary object

        """

        assert self.solution_type == "Structural", "This Method works only in Mechanical Structural Solution"

        props = {}
        objects_list = self.modeler._convert_list_to_ids(objects_list)

        if type(objects_list) is list:
            if type(objects_list[0]) is str:
                props["Objects"] = objects_list
            else:
                props["Faces"] = objects_list


        if not boundary_name:
            boundary_name = generate_unique_name("Temp")
        bound = BoundaryObject(self, boundary_name, props, 'Frictionless')
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False
    @aedt_exception_handler
    def assign_fixed_support(self, objects_list,  boundary_name=""):
        """Assign Mechanical Fixed Support. Works only in Structural Analysis

        Parameters
        ----------
        objects_list :
            list of faces to apply Fixed support
        boundary_name :
            optional name of boundary (Default value = "")

        Returns
        -------
        type
            boundary object

        """
        assert self.solution_type =="Structural", "This Method works only in Mechanical Structural Solution"
        props = {}
        objects_list = self.modeler._convert_list_to_ids(objects_list)

        if type(objects_list) is list:
                props["Faces"] = objects_list


        if not boundary_name:
            boundary_name = generate_unique_name("Temp")
        bound = BoundaryObject(self, boundary_name, props, 'FixedSupport')
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @property
    def existing_analysis_sweeps(self):
        """Existing Analysis Setup List
        
        
        :return: Return a list of all defined analysis setup names in the maxwell design.

        Parameters
        ----------

        Returns
        -------

        """
        setup_list = self.existing_analysis_setups
        sweep_list=[]
        for el in setup_list:
                sweep_list.append(el + " : Solution")
        return sweep_list
