"""
This class contains all Emit functionalities.


Examples
--------

Create an instance of ``Emit`` and connect to an existing Maxwell design or create a new Emit design if one does not exist.

>>> app = Simplorer()

Create a instance of ``Emit`` and link to a project named ``"projectname"``. If this project does not exist, create one with this name.

>>> app = Simplorer(projectname)

Create an instance of ``Emit`` and link to a design named ``"designname"`` in a project named ``"projectname"``.

>>> app = Simplorer(projectname,designame)

Create an instance of ``Emit`` and open the specified project.

>>> app = Simplorer("myfile.aedt")

"""

from __future__ import absolute_import

import numbers

from .application.AnalsyisEmit import FieldAnalysisEmit
from .application.Variables import Variable
from .desktop import exception_to_desktop
from .generic.general_methods import aedt_exception_handler, generate_unique_name


class Emit(FieldAnalysisEmit, object):
    """Emit Object. This is an alpha implementation of Emit object. it contains only skeleton to create empty design.
    No methods implemented at this stage

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
        Solution type to apply to design. The default is ``None``. If ``None`, the default type is applied.
    setup_name : str, optional
       Name of the setup to use as the nominal. The default is ``None``. If ``None``, the active setup 
       is used or nothing is used.

    Returns
    -------

    """

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=True, release_on_exit=True):
        """
        :param projectname: name of the project to be selected or full path to the project to be opened. if None try to
         get active project and, if nothing present to create an empty one
        :param designname: name of the design to be selected. if None, try to get active design and, if nothing present
        to create an empty one
        :param solution_type: solution type to be applied to design. if None default is taken
        :param setup_name: setup_name to be used as nominal. if none active setup is taken or nothing
        """
        FieldAnalysisEmit.__init__(self, "EMIT", projectname, designname, solution_type, setup_name,
                                        specified_version, NG, AlwaysNew, release_on_exit)



    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to parent object Design """
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

