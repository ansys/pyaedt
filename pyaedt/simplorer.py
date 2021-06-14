"""
This class contains all Simplorer functionalities.


Examples
--------

Create a ``Simplorer`` object and connect to an existing Maxwell design or cceate a new Maxwell design if one does not exist.

>>> app = Simplorer()

Create a ``Simplorer`` object and link to a project named ``projectname``. If this project does not exist, create one with this name.

>>> app = Simplorer(projectname)

Create a ``Simplorer`` object and link to a design named ``designname`` in a project named ``projectname``.

>>> app = Simplorer(projectname,designame)

Create a ``Simplorer`` object and open the specified project.

>>> app = Simplorer("myfile.aedt")

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
        FieldAnalysisSimplorer.__init__(self, "Twin Builder", projectname, designname, solution_type, setup_name,
                                        specified_version, NG, AlwaysNew, release_on_exit)


    @aedt_exception_handler
    def create_schematic_from_netlist(self, file_to_import):
        """Create a circuit schematic from a spice netlist.
        Supported in this moment:
        -R, L, C, Diodes, Bjts
        -Discrete components with syntax Uxxx net1 net2 ... netn modname

        Parameters
        ----------
        file_to_import : str
            Full path to the spice file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        var_str : string
            Name of the variable.
            
        expression :
            
        analysis_name : str, optional
             The name of the analysis. The default is ``"TR"``.

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


