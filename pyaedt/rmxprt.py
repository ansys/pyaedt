"""This module contains these classes: `RMXprtModule` and `Rmxprt`."""
from __future__ import absolute_import
from .application.Design import Design
from .application.AnalysisRMxprt import FieldAnalysisRMxprt
from .generic.general_methods import aedt_exception_handler, generate_unique_name


class RMXprtModule(object):
    """RMXertModule class."""

    component = None
    prop_servers = None

    @aedt_exception_handler
    def get_prop_server(self, parameter_name):
        """

        Parameters
        ----------
        parameter_name : str
            Name of the parameter.
            

        Returns
        -------

        """
        prop_server = None
        for key, parameter_list in self.prop_servers.items():
            if parameter_name in parameter_list:
                prop_server = key
                break
        assert prop_server is not None,\
            "Unknown parameter name {0} exists in component {1}.".format(prop_server, self.component)
        return prop_server

    def __init__(self, oeditor):
        self._oeditor = oeditor

    @aedt_exception_handler
    def __setitem__(self, parameter_name, value):
        self.set_rmxprt_parameter(parameter_name, value)
        return True

    @aedt_exception_handler
    def set_rmxprt_parameter(self, parameter_name, value):
        """

        Parameters
        ----------
        parameter_name : str
            Name of the parameter.  
        value :
            Value to assign to the parameter.
            

        Returns
        -------

        """
        prop_server = self.get_prop_server(parameter_name)
        separator = ":" if prop_server else ""
        self._oeditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:" + self.component,
                    [
                        "NAME:PropServers",
                        "{0}{1}{2}".format(self.component, separator, prop_server)
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:" + parameter_name,
                            "Value:="		, value
                        ]
                    ]
                ]
            ])
        return True


class Stator(RMXprtModule):
    """ """
    component = "Stator"
    prop_servers = {"":        ["Outer Diameter", "Inner Diameter", "Length", "Stacking Factor"
                                "Steel Type", "Number of Slots", "Slot Type", "Lamination Sectors",
                                "Press Board Thickness", "Skew Width"],
                    "Slot":    ["Hs0", "Hs1", "Hs2", "Bs0", "Bs1", "Bs2"],
                    "Winding": ["Winding Type", "Parallel Branches"]}


class Rotor(RMXprtModule):
    """ """
    component = "Rotor"
    prop_servers = {"":        ["Outer Diameter"],
                    "Slot":    [],
                    "Winding": []}


class Rmxprt(FieldAnalysisRMxprt):
    """RMxprt application interface.

    This class exposes functionality from RMxprt.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``, in which
        case an attempt is made to get an active project. If no 
        projects are present, an empty project is created.
    designname : str, optional
        Name of the design to select. The default is ``None``, in 
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    solution_type : str, optional
        Solution type to apply to the design. The default is
        ``None``, which applies the default type.
    model_units : str, optional
        Model units.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or 
        nothing is used.
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
    Create an instance of `Rmxprt` and connect to an existing RMxprt
    design or create a new RMxprt design if one does not exist.

    >>> from pyaedt import Rmxprt
    >>> app = Rmxprt()

    Create an instance of `Rmxprt` and link to a project named
    ``"projectname"``. If this project does not exist, create one with
    this name.

    >>> app = Rmxprt(projectname)

    Create an instance of `RMxprt` and link to a design named
    ``"designname"`` in a project named ``"projectname"``.

    >>> app = Rmxprt(projectname,designame)

    Create an instance of `RMxprt` and open the specified project,
    which is ``myfile.aedt``.

    >>> app = Rmxprt("myfile.aedt")
    """

    def __init__(self, projectname=None, designname=None, solution_type=None, model_units=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):
        FieldAnalysisRMxprt.__init__(self, "RMxprtSolution", projectname, designname, solution_type, setup_name,
                                     specified_version, NG, AlwaysNew, release_on_exit, student_version)
        if not model_units or model_units == "mm":
            model_units = "mm"
        else:
            assert model_units == "in", "Invalid model units string {}".format(model_units)
        self.modeler.oeditor.SetMachineUnits(
            [
                "NAME:Units Parameter",
                "Units:=", model_units,
                "Rescale:="    	, False
            ])
        self.stator = Stator(self.modeler.oeditor)
        self.rotor = Rotor(self.modeler.oeditor)

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to parent object Design """
        Design.__exit__(self, ex_type, ex_value, ex_traceback)

    def __enter__(self):
        return self
