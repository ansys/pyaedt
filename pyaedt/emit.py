"""This module contains the ``Emit`` class."""

from __future__ import absolute_import

import numbers

from .application.AnalsyisEmit import FieldAnalysisEmit
from .application.Variables import Variable
from .desktop import exception_to_desktop
from .generic.general_methods import aedt_exception_handler, generate_unique_name


class Emit(FieldAnalysisEmit, object):
    """Emit class.

    .. note::
       At the moment, this object has very limited functionalities. It
       contains only a skeleton for creating an empty design. No methods
       are implemented yet.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``. If
        ``None``, try to get an active project and, if no projects are
        present, create an empty project.
    designname : str, optional
        Name of the design to select. The default is ``None``. If
        ``None``, try to get an active design and, if no designs are
        present, create an empty design.
    solution_type : str, optional
        Solution type to apply to design. The default is ``None``. If
        ``None``, the default type is applied.
    setup_name : str, optional
       Name of the setup to use as the nominal. The default is
       ``None``. If ``None``, the active setup is used or nothing is
       used.
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``. If ``None``,
        the active setup is used or the latest installed version is
        used.
    NG : bool, optional
        Whether to launch AEDT in the non-graphical mode. The default
        is ``False``, which launches AEDT in the graphical mode.
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``True``.
    release_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``True``.
    student_version : bool, optional
        Whether open AEDT Student Version. The default is ``False``.

    Examples
    --------
    Create an instance of ``Emit`` and connect to an existing Maxwell
    design or create a new Emit design if one does not exist.

    >>> from pyaedt import Emit
    >>> app = Emit()

    Create a instance of ``Emit`` and link to a project named
    ``"projectname"``. If this project does not exist, create one with
    this name.

    >>> app = Emit(projectname)

    Create an instance of ``Emit`` and link to a design named
    ``"designname"`` in a project named ``"projectname"``.
    
    >>> app = Emit(projectname,designame)

    Create an instance of ``Emit`` and open the specified project.

    >>> app = Emit("myfile.aedt")


    """

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=True, release_on_exit=True, student_version=False):
        """Constructor."""
        FieldAnalysisEmit.__init__(self, "EMIT", projectname, designname, solution_type, setup_name,
                                        specified_version, NG, AlwaysNew, release_on_exit, student_version)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to parent object Design """
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)
