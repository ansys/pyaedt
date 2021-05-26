import sys
import os
local_path = os.path.dirname(os.path.realpath(__file__))
pyaedtpath = os.path.join(local_path, "..", )
sys.path.append(os.path.join(pyaedtpath, ".."))

from pyaedt import Desktop

if len(sys.argv) < 2:
    version = "2021.1"
else:
    v = sys.argv[1]
    version = "20" + v[-3:-1] + "." + v[-1:]


local_path = os.path.dirname(os.path.realpath(__file__))
pyaedtpath = os.path.join(local_path, "..", )

d = Desktop("2021.1", True)
desktop = sys.modules['__main__'].oDesktop
pers1 = os.path.join(desktop.GetPersonalLibDirectory(),"pyaedt")

if os.path.exists(pers1):
    print("PersonalLib already mapped")
else:
    os.system('mklink /D "{}" "{}"'.format(pers1, pyaedtpath))

d.force_close_desktop()
