"""
Simplorer Class
----------------------------------------------------------------


Description
==================================================

This class contains all the Simplorer Functionalities.


:Example:

app = Simplorer()     creates and Simplorer object and connect to existing Maxwell design (create a new Maxwell design if not present)


app = Simplorer(projectname)     creates and  Maxwell and link to projectname project


app = Simplorer(projectname,designame)     creates and Maxwell object and link to designname design in projectname project


app = Simplorer("myfile.aedt")     creates and Maxwell object and open specified project


"""
from __future__ import absolute_import

import numbers

from .application.AnalysisSimplorer import FieldAnalysisSimplorer
from .application.Variables import Variable
from .desktop import exception_to_desktop
from .generic.general_methods import aedt_exception_handler, generate_unique_name


class Simplorer(FieldAnalysisSimplorer, object):
    """Simplorer Object

    Parameters
    ----------
    projectname :
        name of the project to be selected or full path to the project to be opened  or to the AEDTZ
        archive. if None try to get active project and, if nothing present to create an empty one
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
        """
        :param projectname: name of the project to be selected or full path to the project to be opened. if None try to
         get active project and, if nothing present to create an empty one
        :param designname: name of the design to be selected. if None, try to get active design and, if nothing present
        to create an empty one
        :param solution_type: solution type to be applied to design. if None default is taken
        :param setup_name: setup_name to be used as nominal. if none active setup is taken or nothing
        """
        FieldAnalysisSimplorer.__init__(self, "Twin Builder", projectname, designname, solution_type, setup_name)


    @aedt_exception_handler
    def create_schematic_from_netlist(self, file_to_import):
        """Create a Circuit Schematic from a spice netlist.
        Supported in this moment:
        -R, L, C, Diodes, Bjts
        -Discrete components with syntax Uxxx net1 net2 ... netn modname

        Parameters
        ----------
        file_to_import :
            full path to spice file

        Returns
        -------
        type
            True if completed

        """
        xpos = 0
        ypos = 0
        delta = 0.0508
        use_instance = True
        with open(file_to_import, 'r') as f:
            for line in f:
                mycomp = None
                fields = line.split(" ")
                name = fields[0]
                if fields[0][0] == "R":
                    value = fields[3][fields[3].find("=") + 1:].strip()
                    mycomp, mycompname = self.modeler.components.create_resistor(name, value, xpos, ypos,
                                                                                 use_instance_id_netlist=use_instance)
                elif fields[0][0] == "L":
                    value = fields[3][fields[3].find("=") + 1:].strip()
                    mycomp, mycompname = self.modeler.components.create_inductor(name, value, xpos, ypos,
                                                                                 use_instance_id_netlist=use_instance)
                elif fields[0][0] == "C":
                    value = fields[3][fields[3].find("=") + 1:].strip()
                    mycomp, mycompname = self.modeler.components.create_capacitor(name, value, xpos, ypos,
                                                                                  use_instance_id_netlist=use_instance)
                elif fields[0][0] == "Q":
                    if len(fields) == 4 and fields[0][0] == "Q":
                        value = fields[3].strip()
                        mycomp, mycompname = self.modeler.components.create_npn(fields[0], value, xpos, ypos,
                                                                               use_instance_id_netlist=use_instance)
                        value = None
                elif fields[0][0] == "D":
                    value = fields[3][fields[3].find("=") + 1:].strip()
                    mycomp, mycompname = self.modeler.components.create_diode(name, value, xpos, ypos,
                                                                              use_instance_id_netlist=use_instance)
                if mycomp:
                    pins = self.modeler.components.get_pins(mycomp)
                    id = 1
                    for pin in pins:
                        if pin == "CH" or pin==fields[0][0]:
                            continue
                        pos = self.modeler.components.get_pin_location(mycomp, pin)
                        if pos[0] < xpos:
                            angle = 6.28318530717959
                        else:
                            angle = 3.14159265358979
                        self.modeler.components.create_page_port(fields[id], pos[0], pos[1], angle)
                        id += 1
                    ypos += delta
                    if ypos > 0.254:
                        xpos += delta
                        ypos = 0
        return True


    @aedt_exception_handler
    def set_end_time(self, expression):
        """

        Parameters
        ----------
        expression :
            

        Returns
        -------

        """
        self.set_sim_setup_parameter('Tend', expression)
        return True

    @aedt_exception_handler
    def set_hmin(self, expression):
        """

        Parameters
        ----------
        expression :
            

        Returns
        -------

        """
        self.set_sim_setup_parameter('Hmin', expression)
        return True

    @aedt_exception_handler
    def set_hmax(self, expression):
        """

        Parameters
        ----------
        expression :
            

        Returns
        -------

        """
        self.set_sim_setup_parameter('Hmax', expression)
        return True

    @aedt_exception_handler
    def set_sim_setup_parameter(self, var_str, expression, analysis_name="TR"):
        """

        Parameters
        ----------
        var_str :
            
        expression :
            
        analysis_name :
             (Default value = "TR")

        Returns
        -------

        """
        if isinstance(expression, Variable):
            value_str = expression.string_value
        # Handle input type int/float, etc (including numeric 0)
        elif isinstance(expression, numbers.Number):
            value_str = str(expression)
        else:
            value_str = expression

        self._odesign.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:BaseElementTab",
                    [
                        "NAME:PropServers",
                        analysis_name
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:" + var_str,
                            "Value:="	, value_str
                        ]
                    ]
                ]
            ])
        return True

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to parent object Design """
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)


