import sys

from pyaedt.common_rpc import launch_server
if sys.argv[2]=="0":
    val = False
else:
    val = True
launch_server(ansysem_path=sys.argv[1], non_graphical=val, port=int(sys.argv[3]))

