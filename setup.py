import setuptools
import sys
import pip
from _setup_common import (
    name,
    version,
    author,
    maintainer,
    maintainer_email,
    description,
    long_description,
    packages,
    data_files,
    license,
    classifiers,
)


def install(package):
    if hasattr(pip, "main"):
        pip.main(["install", package])
    else:
        pip._internal.main(["install", package])


if sys.version_info >= (3, 9):
    install_requires = ["pywin32 >= 2.2.7;platform_system=='Windows'"]
    install("https://github.com/pyansys/PyAEDT/raw/release/0.3/pythonnet-2.5.2-cp39-cp39-win_amd64.whl")
elif import rpyc
#from pyaedt import Hfss

class MyService(rpyc.Service):
    def __init__(self):
        self.hfss = None
    def on_connect(self, conn):
        # code that runs when a connection is created
        # (to init the service, if needed)
        pass

    def on_disconnect(self, conn):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_start_hfss(self): # this is an exposed method
        self.hfss = Hfss(specified_version="2021.1")
        return self.hfss

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port=18861, protocol_config={'allow_public_attrs': True,})
    t.start()
    install_requires = ["pywin32 >= 2.2.7;platform_system=='Windows'", "pythonnet >= 2.4.0;platform_system=='Windows'"]
else:
    install_requires = []

setuptools.setup(
    name=name,
    version=version,
    author=author,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=install_requires,
    packages=packages,
    data_files=data_files,
    include_package_data=True,
    license=license,
    classifiers=classifiers,
)
