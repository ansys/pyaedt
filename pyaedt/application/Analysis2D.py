from .Analysis import Analysis
from ..modeler.Model2D import Modeler2D
from ..modules.Mesh import Mesh
from ..generic.general_methods import aedt_exception_handler, generate_unique_name


class FieldAnalysis2D(Analysis):
    """**FieldAnalysis2D class.**
    
    This class is for 2D field analysis setup in Maxwell2D and Q2D.
    
    It is automatically initialized by an application call from one of 
    the 2D tools. See the application function for parameter definitions.

    Parameters
    ----------
    application : str
        2D application that is to initialize the call.
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open. The default is ``None``, in which
        case an attempt is made to get an active project. If no 
        projects are present, an empty project is created.
    designname : str, optional
        Name of the design to select. The default is ``None``, in 
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    solution_type : str, optional
        Solution type to apply to the design. The default is
        ``None``, in which case the default type is applied.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or 
        nothing is used.
    specified_version: str, optional
        Version of AEDT  to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default 
        is ``False``, which launches AEDT in the graphical mode.  
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``.
    release_on_exit : bool, optional
        Whether to release  AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to enable the student version of AEDT. The default 
        is ``False``.

    """
    def __init__(self, application, projectname, designname, solution_type, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):


        Analysis.__init__(self, application, projectname, designname, solution_type, setup_name,
                          specified_version, NG, AlwaysNew, release_on_exit, student_version)
        self._modeler = Modeler2D(self)
        self._mesh = Mesh(self)
        # self._post = PostProcessor(self)

    @property
    def modeler(self):
        """Modeler object."""
        return self._modeler

    @property
    def mesh(self):
        """Mesh object"""
        return self._mesh

    # @property
    # def post(self):
    #     return self._post

    @aedt_exception_handler
    def assignmaterial(self, obj, mat):
        """Assign a material to one or more objects. 

        Parameters
        ----------
        obj : str or list
            One or more objects to assign materials to.
        mat : str
            Material to assign. If this material is not present, it will be 
            created.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        mat = mat.lower()
        selections = self.modeler.convert_to_selections(obj)
        arg1 = ["NAME:Selections"]
        arg1.append("Selections:="), arg1.append(selections)
        arg2 = ["NAME:Attributes"]
        arg2.append("MaterialValue:="), arg2.append(chr(34) + mat + chr(34))
        if mat in self.materials.material_keys:
            Mat = self.materials.material_keys[mat]
            Mat.update()
            if Mat.is_dielectric():
                arg2.append("SolveInside:="), arg2.append(True)
            else:
                arg2.append("SolveInside:="), arg2.append(False)
            self.modeler.oeditor.AssignMaterial(arg1, arg2)
            self._messenger.add_info_message('Assign Material ' + mat + ' to object ' + selections)
            if type(obj) is list:
                for el in obj:
                    self.modeler.primitives[el].material_name = mat
            else:
                self.modeler.primitives[obj].material_name = mat
            return True
        elif self.materials.checkifmaterialexists(mat):
            self.materials._aedmattolibrary(mat)
            Mat = self.materials.material_keys[mat]
            if Mat.is_dielectric():
                arg2.append("SolveInside:="), arg2.append(True)
            else:
                arg2.append("SolveInside:="), arg2.append(False)
            self.modeler.oeditor.AssignMaterial(arg1, arg2)
            self._messenger.add_info_message('Assign Material ' + mat + ' to object ' + selections)
            if type(obj) is list:
                for el in obj:
                    self.modeler.primitives[el].material_name = mat
            else:
                self.modeler.primitives[obj].material_name = mat

            return True
        else:
            self._messenger.add_error_message("Material Does Not Exists")
            return False
