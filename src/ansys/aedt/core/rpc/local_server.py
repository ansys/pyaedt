import pathlib
import sys
import os

sys.path.insert(0, str(pathlib.PurePath(pathlib.PurePath(__file__).parent).joinpath("..", "..")))

from ansys.aedt.core.common_rpc import launch_server

if int(sys.argv[2]) == 1:
    val = True
else:
    val = False

if len(sys.argv)>4:
   threaded = True if sys.argv[4]==1 else False
else:
   threaded = True
launch_server(ansysem_path=sys.argv[1], non_graphical=val, port=int(sys.argv[3]), threaded=threaded)
