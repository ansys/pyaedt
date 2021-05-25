import os
from .generic.general_methods import aedt_exception_handler, generate_unique_name, retry_ntimes
from .hfss3dlayout import Hfss3dLayout
from .hfss import Hfss
from .circuit import Circuit
from .q3d import Q2d, Q3d
from .siwave import Siwave
from .icepak import Icepak
from .edb import Edb
from .maxwell import Maxwell2d, Maxwell3d
from .mechanical import Mechanical
from .rmxprt import Rmxprt
from .simplorer import Simplorer
from .desktop import Desktop


@aedt_exception_handler
def pyaedt_help(modulename="index", browser="chrome"):
    """
    Launch Online help. Works on Windows Only (for linux manually launch it from Documentation folder)


    :param modulename: name of the module or search string
    :param browser: string name of the browser. it can be chrome, iexplore, msedge, firefox
    :return: open pyaedt on browser
    """

    if modulename.lower() == "index":
        filename = os.path.join(os.path.dirname(__file__), "Documentation", modulename+".html")
    else:
        filename = os.path.join(os.path.dirname(__file__), "Documentation","API", modulename+".html")

    if os.path.exists(filename):
        filepath = filename.replace(":\\", ":/").replace("\\", "/")
        networkpath = "file:///" + filepath
    else:
        filename = os.path.dirname(__file__)+"/Documentation/search.html?q={}&".format(modulename)
        filepath = filename.replace(":\\", ":/").replace("\\", "/")
        networkpath = "file:///" + filepath
    try:
        os.system("start {} {} ".format(browser, networkpath))
        return True
    except:
        print("Broswer not found")
        return False