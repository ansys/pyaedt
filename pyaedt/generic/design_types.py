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
    from pyaedt.simplorer import Simplorer
    from pyaedt.emit import Emit
    from pyaedt.aedt_logger import AedtLogger
except:
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
    from pyaedt.simplorer import Simplorer
    from pyaedt.emit import Emit
    from pyaedt.aedt_logger import AedtLogger


design_types = {
    "Maxwell 2D": Maxwell2d,
    "Maxwell 3D": Maxwell3d,
    "Twin Builder": Simplorer,
    "Circuit Design": Circuit,
    "2D Extractor": Q2d,
    "Q3D Extractor": Q3d,
    "HFSS": Hfss,
    "Mechanical": Mechanical,
    "Icepak": Icepak,
    "Rmxprt": Rmxprt,
    "HFSS 3D Layout Design": Hfss3dLayout,
    "EMIT": Emit,
}

