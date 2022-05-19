"""This module contains the ``MaxwellCircuit`` class."""
from __future__ import absolute_import  # noreorder

import math

from pyaedt.application.AnalysisMaxwellCircuit import AnalysisMaxwellCircuit
from pyaedt.generic.general_methods import pyaedt_function_handler


class MaxwellCircuit(AnalysisMaxwellCircuit, object):
    """Provides the Maxwell Circuit Editor application interface.

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
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``. If ``None``,
        the active setup is used or the latest installed version is
        used.
    non-graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``True``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``True``.
    student_version : bool, optional
        Whether open AEDT Student Version. The default is ``False``.
    machine : str, optional
        Machine name to which connect the oDesktop Session. Works only on 2022R2.
        Remote Server must be up and running with command `"ansysedt.exe -grpcsrv portnum"`.
        If machine is `"localhost"` the server will also start if not present.
    port : int, optional
        Port number of which start the oDesktop communication on already existing server.
        This parameter is ignored in new server creation. It works only on 2022R2.
        Remote Server must be up and running with command `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Only used when ``new_desktop_session = False``, specifies by process ID which instance
        of Electronics Desktop to point PyAEDT at.

    Examples
    --------
    Create an instance of Maxwell Circuit and connect to an existing
    Maxwell circuit design or create a new Maxwell circuit design if one does
    not exist.

    >>> from pyaedt import MaxwellCircuit
    >>> app = MaxwellCircuit()

    Create an instance of Maxwell Circuit and link to a project named
    ``"projectname"``. If this project does not exist, create one with
    this name.

    >>> app = MaxwellCircuit(projectname)

    Create an instance of Maxwell Circuit and link to a design named
    ``"designname"`` in a project named ``"projectname"``.

    >>> app = MaxwellCircuit(projectname, designame)

    Create an instance of Maxwell Circuit and open the specified
    project, which is named ``"myfile.aedt"``.

    >>> app = MaxwellCircuit("myfile.aedt")
    """

    def __init__(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        specified_version=None,
        non_graphical=False,
        new_desktop_session=False,
        close_on_exit=False,
        student_version=False,
        machine="",
        port=0,
        aedt_process_id=None,
    ):
        """Constructor."""
        AnalysisMaxwellCircuit.__init__(
            self,
            "Maxwell Circuit",
            projectname,
            designname,
            specified_version,
            non_graphical,
            new_desktop_session,
            close_on_exit,
            student_version,
            machine,
            port,
            aedt_process_id,
        )

    @pyaedt_function_handler()
    def create_schematic_from_netlist(self, file_to_import):
        """Create a circuit schematic from an HSpice net list.

        Supported currently are:

        * R
        * L
        * C
        * Diodes

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
        with open(file_to_import, "r") as f:
            for line in f:
                mycomp = None
                fields = line.split(" ")
                name = fields[0]
                if fields[0][0] == "R":
                    value = fields[3][fields[3].find("=") + 1 :].strip()
                    mycomp = self.modeler.schematic.create_resistor(
                        name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                elif fields[0][0] == "L":
                    value = fields[3][fields[3].find("=") + 1 :].strip()
                    mycomp = self.modeler.schematic.create_inductor(
                        name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                elif fields[0][0] == "C":
                    value = fields[3][fields[3].find("=") + 1 :].strip()
                    mycomp = self.modeler.schematic.create_capacitor(
                        name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                elif fields[0][0] == "D":
                    value = fields[3][fields[3].find("=") + 1 :].strip()
                    mycomp = self.modeler.schematic.create_diode(
                        name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                if mycomp:
                    id = 1
                    for pin in mycomp.pins:
                        if pin.name == "CH" or pin.name == fields[0][0]:
                            continue
                        pos = pin.location
                        if pos[0] < xpos:
                            angle = 0.0
                        else:
                            angle = math.pi
                        self.modeler.schematic.create_page_port(fields[id], [pos[0], pos[1]], angle)
                        id += 1
                    ypos += delta
                    if ypos > 0.254:
                        xpos += delta
                        ypos = 0
        return True

    def __enter__(self):
        return self
