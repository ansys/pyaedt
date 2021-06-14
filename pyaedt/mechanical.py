"""
This module contains all Mechanical functionalities in the ``mechanical`` class. 


Examples
--------

Create a ``Mechanical`` object and connect to an existing HFSS design or create a new HFSS design if one does not exist.

>>> aedtapp = Mechanical()

Create a ``Mechanical`` object and link to a project named ``projectname``. If this project does not exist, create one with this name.

>>> aedtapp = Mechanical(projectname)

Create a ``Mechanical`` object and link to a design named ``designname`` in a project named ``projectname``.

>>> aedtapp = Mechanical(projectname,designame)

Create a ``Mechanical`` object and open the specified project.

>>> aedtapp = Mechanical("myfile.aedt")

Create a ``Desktop on 2021R1`` object and then creates an ``Mechanical`` object and open the specified project.

>>> aedtapp = Mechanical(specified_version="2021.1", projectname="myfile.aedt")

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
    projectname : str, optional
         Name of the project to select or the full path to the project or AEDTZ archive to open. 
         The default is ``None``. If ``None``, try to get an active project and, if no projects are present, 
         create an empty project.
    designname : str, optional
        Name of the design to select. The default is ``None``. If ``None``, try to get an active design and, 
        if no designs are present, create an empty design.
    solution_type : str, optional
        Solution type to apply to the design. The default is ``None``. If ``None`, the default type is applied.
    setup_name : str, optional
       Name of the setup to use as the nominal. The default is ``None``. If ``None``, the active setup 
       is used or nothing is used.

    Returns
    -------

    """

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=True, release_on_exit=True):

        FieldAnalysis3D.__init__(self, "Mechanical", projectname, designname, solution_type, setup_name,
                                 specified_version, NG, AlwaysNew, release_on_exit)
    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to parent object Design """
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    @aedt_exception_handler
    def assign_em_losses(self, designname="HFSSDesign1", setupname="Setup1", sweepname="LastAdaptive", map_frequency=None,
                         surface_objects=[], source_project_name=None, paramlist=[], object_list=[]):
        """Map EM losses to a Mechanical design.

        Parameters
        ----------
        designname : str, optional
            Name of the design of the source mapping. The default is ``"HFSSDesign1"``.
        setupname : str, optional
            Name of the EM setup. The default is ``"Setup1"``.
        sweepname : str, optional
            Name of the EM sweep to use for the mapping. The default is no sweep and to use ``"LastAdaptive"``.
        map_frequency : str, optional
            Frequency to map. The default is ``None``. The value must be ``None`` for eigenmode analysis.
        surface_objects : list
            List objects in the source that are metals. The default is ``[]``.
        source_project_name : str, optional
            Name of the source project. The default is ``None``, which uses the source from the same project.
        paramlist : list, optional
            List of all parameters in the EM to map. The default is ``[]``.
        object_list : list, optional
             The default is ``[]``.

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
        # Generate a list of model objects from the lists made previously and use to map the HFSS losses into Icepak.
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
            self._messenger.add_info_message('EM losses mapped from design {}'.format(designname))
            return bound
        return False

    @aedt_exception_handler
    def assign_thermal_map(self, object_list, designname="IcepakDesign1", setupname="Setup1", sweepname="SteadyState",
                           source_project_name=None, paramlist=[]):
        """Map thermal losses to a Mechanical design. This function works only coupled with Icepak in 2021 R2.

        Parameters
        ----------
        object_list : list
        
        designname : str, optional
            Name of the design of the source mapping. The default is ``"IcepakDesign1"``.
        setupname : str, optinal
            Name of the EM setup. The default is ``"Setup1"``.
        sweepname :str, optional
            Name of the EM sweep to use for the mapping. The default is no sweep and to use ``"LastAdaptive"``.
        source_project_name : str, optinal
            Name of the source project. The default is ``None``, which uses the source from the same project.
        paramlist : list, optional
            List of all parameters in the EM to map. The default is ``[]``.
        
            

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
        # Generate a list of model objects from the lists made previously and use to map the HFSS losses into Icepak.
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
        """Assign uniform convection to the face list.

        Parameters
        ----------
        objects_list : list
            List of objects, faces, or both.
        convection_value :
            Convection value.
        convection_unit : str, optional
            Unit of the convection. The default is ``"w_per_m2kel"``.
        temperature : str, optional
            Temperature. The default is ``"AmbientTemp"``.
        boundary_name : str, optional
            Name of the boundary. The default is ``""``.

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
        """Assign a uniform temperature boundary. This function works only in a Thermal analysis.

        Parameters
        ----------
        objects_list : list
            List of objects, faces, or both.
        temperature : str, optional.
            Temperature. The default is ``"AmbientTemp"``.
        boundary_name : str, optional
            Name of the boundary. The default is ``""``.

        Returns
        -------
        type
            Boundary Object

        """
        assert self.solution_type == "Thermal", "This method works only in a Mechanical structural analysis."

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
        """Assign a Mechanical frictionless support. This function works only in a structural analysis.

        Parameters
        ----------
        objects_list : list
            List of faces to apply to the frictionless support.
        boundary_name : str, optional
            Name of boundary. The default is ``""``.

        Returns
        -------
        type
            boundary object

        """

        assert self.solution_type == "Structural", "This Method works only in a Mechanical structural analysis."

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
        """Assign a Mechanical fixed support. This function works only in a Structural analysis.

        Parameters
        ----------
        objects_list : list
            List of faces to apply to the fixed support.
        boundary_name : str, optional
            Name of the boundary. The default is ``""``.

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
        """Get an existing analysis setup list.
                
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
