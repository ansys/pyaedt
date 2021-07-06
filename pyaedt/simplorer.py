"""This module contains the `Simplorer` class."""

from __future__ import absolute_import

import numbers

from .application.AnalysisSimplorer import FieldAnalysisSimplorer
from .application.Variables import Variable
from .desktop import exception_to_desktop
from .generic.general_methods import aedt_exception_handler, generate_unique_name


class Simplorer(FieldAnalysisSimplorer, object):
    """Simplorer class.

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
    Create an instance of `Simplorer` and connect to an existing
    Maxwell design or create a new Maxwell design if one does not
    exist.

    >>> from pyaedt import Simplorer
    >>> app = Simplorer()

    Create a instance of `Simplorer` and link to a project named
    ``"projectname"``. If this project does not exist, create one with
    this name.

    >>> app = Simplorer(projectname)

    Create an instance of `Simplorer` and link to a design named
    ``"designname"`` in a project named ``"projectname"``.

    >>> app = Simplorer(projectname, designame)

    Create an instance of `Simplorer` and open the specified
    project, which is named ``"myfile.aedt"``.

    >>> app = Simplorer("myfile.aedt")
    """

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):
        """Constructor."""
        FieldAnalysisSimplorer.__init__(self, "Twin Builder", projectname, designname, solution_type, setup_name,
                                        specified_version, NG, AlwaysNew, release_on_exit,student_version)


    @aedt_exception_handler
    def create_schematic_from_netlist(self, file_to_import):
        """Create a circuit schematic from an HSpice net list.
        
        Supported currently:
        
        * R
        * L
        * C
        * Diodes
        * Bjts
        * Discrete components with syntax ``Uxxx net1 net2 ... netn modname``

        Parameters
        ----------
        file_to_import : str
            Full path to the HSpice file.

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
             Name of the analysis. The default is ``"TR"``.

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
