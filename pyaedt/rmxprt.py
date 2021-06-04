"""
RMxprt Class
-------------------


Description
==================================================

This class contains all the RMxprt Functionalities. It inherites all the objects that belongs to RMxprt


:Example:

app = Rmxprt()     creates  Rmxprt object and connect to existing RMxprt design (create a new RMxprt design if not present)


app = Rmxprt(projectname)     creates and  Rmxprt and link to projectname project


app = Rmxprt(projectname,designame)     creates and RMxprt object and link to designname design in projectname project


app = Rmxprt("myfile.aedt")     creates and RMxprt object and open specified project



========================================================

"""
from __future__ import absolute_import
from .application.Design import Design
from .application.AnalysisRMxprt import FieldAnalysisRMxprt
from .generic.general_methods import aedt_exception_handler, generate_unique_name


class RMXprtModule(object):
    """ """

    component = None
    prop_servers = None

    @aedt_exception_handler
    def get_prop_server(self, parameter_name):
        """

        Parameters
        ----------
        parameter_name :
            

        Returns
        -------

        """
        prop_server = None
        for key, parameter_list in self.prop_servers.items():
            if parameter_name in parameter_list:
                prop_server = key
                break
        assert prop_server is not None,\
            "Unknown parameter name {0} in component {1}!".format(prop_server, self.component)
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
        parameter_name :
            
        value :
            

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
    """RMxprt Object

    Parameters
    ----------
    projectname :
        name of the project to be selected or full path to the project to be opened  or to the AEDTZ  archive. if None try to get active project and, if nothing present to create an empty one
    designname :
        name of the design to be selected. if None, try to get active design and, if nothing present to create an empty one
    solution_type :
        solution type to be applied to design. if None default is taken
    setup_name :
        setup_name to be used as nominal. if none active setup is taken or nothing

    Returns
    -------

    """

    def __init__(self, projectname=None, designname=None, solution_type=None, model_units=None, setup_name=None):
        FieldAnalysisRMxprt.__init__(self, "RMxprtSolution", projectname, designname, solution_type, setup_name)
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


