import re
import sys

try:
    from pyaedt.hfss3dlayout import Hfss3dLayout
    from pyaedt.hfss import Hfss
    from pyaedt.circuit import Circuit
    from pyaedt.q3d import Q2d, Q3d
    from pyaedt.siwave import Siwave
    from pyaedt.icepak import Icepak
    from pyaedt.edb import Edb
    from pyaedt.maxwell import Maxwell2d, Maxwell3d
    from pyaedt.mechanical import Mechanical
    from pyaedt.rmxprt import Rmxprt
    from pyaedt.twinbuilder import TwinBuilder
    from pyaedt.twinbuilder import TwinBuilder as Simplorer  # noqa: F401 # namespace only for backward compatibility
    from pyaedt.maxwellcircuit import MaxwellCircuit
    from pyaedt.emit import Emit
    from pyaedt.desktop import Desktop
except ImportError:
    from pyaedt.hfss3dlayout import Hfss3dLayout
    from pyaedt.hfss import Hfss
    from pyaedt.circuit import Circuit
    from pyaedt.q3d import Q2d, Q3d
    from pyaedt.siwave import Siwave
    from pyaedt.icepak import Icepak
    from pyaedt.edb import Edb
    from pyaedt.maxwell import Maxwell2d, Maxwell3d
    from pyaedt.mechanical import Mechanical
    from pyaedt.rmxprt import Rmxprt
    from pyaedt.twinbuilder import TwinBuilder
    from pyaedt.twinbuilder import TwinBuilder as Simplorer  # noqa: F401 # namespace only for backward compatibility
    from pyaedt.maxwellcircuit import MaxwellCircuit
    from pyaedt.emit import Emit
    from pyaedt.desktop import Desktop


app_map = {
    "Maxwell 2D": Maxwell2d,
    "Maxwell 3D": Maxwell3d,
    "Maxwell Circuit": MaxwellCircuit,
    "Twin Builder": TwinBuilder,
    "Circuit Design": Circuit,
    "2D Extractor": Q2d,
    "Q3D Extractor": Q3d,
    "HFSS": Hfss,
    "Mechanical": Mechanical,
    "Icepak": Icepak,
    "Rmxprt": Rmxprt,
    "HFSS 3D Layout Design": Hfss3dLayout,
    "EMIT": Emit,
    "EDB": Edb,
    "Desktop": Desktop,
    "Siwave": Siwave,
}


def get_pyaedt_app(project_name=None, design_name=None):
    """Returns the Pyaedt Object of specific projec_name and design_name.

    Parameters
    ----------
    project_name
    design_name

    Returns
    -------
    :class:`pyaedt.Hfss`
        Any of the Pyaedt App initialized.
    """
    main = sys.modules["__main__"]
    if "oDesktop" in dir(main):

        if project_name and project_name not in main.oDesktop.GetProjectList():
            raise AttributeError("Project  {} doesn't exist in current Desktop.".format(project_name))
        if not project_name:
            oProject = main.oDesktop.GetActiveProject()
        else:
            oProject = main.oDesktop.SetActiveProject(project_name)
        if not oProject:
            raise AttributeError("No Project Present.")
        design_names = []
        deslist = list(oProject.GetTopDesignList())
        for el in deslist:
            m = re.search(r"[^;]+$", el)
            design_names.append(m.group(0))
        if design_name and design_name not in design_names:
            raise AttributeError("Design  {} doesn't exists in current Project.".format(design_name))
        if not design_name:
            oDesign = oProject.GetActiveDesign()
        else:
            oDesign = oProject.SetActiveDesign(design_name)
        if not oDesign:
            raise AttributeError("No Design Present.")
        design_type = oDesign.GetDesignType()
        if design_type in list(app_map.keys()):
            version = main.oDesktop.GetVersion().split(".")
            v = ".".join([version[0], version[1]])
            return app_map[design_type](project_name, design_name, specified_version=v)
    return None
