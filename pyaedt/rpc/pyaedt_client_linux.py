import sys
import os
sys.path.append(pyaedt_path)
sys.path.append(os.path.join(pyaedt_path, "pyaedt", "third_party", "ironpython"))

from pyaedt.rpc.rpyc_services import PyaedtServiceWindows
from rpyc import OneShotServer
OneShotServer(PyaedtServiceWindows, hostname=hostname, port=port,
              protocol_config={'sync_request_timeout': None, 'allow_public_attrs': True, 'allow_setattr': True,
                               'allow_delattr': True}).start()
