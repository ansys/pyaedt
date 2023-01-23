import os
import shutil
import sys

local_path = os.path.dirname(os.path.realpath(__file__))
pyaedtpath = os.path.join(
    local_path,
    "..",
)
sys.path.append(os.path.join(pyaedtpath, ".."))

from pyaedt import Desktop

if len(sys.argv) < 2:
    version = "2021.2"
else:
    v = sys.argv[1]
    version = "20" + v[-3:-1] + "." + v[-1:]


local_path = os.path.dirname(os.path.realpath(__file__))
pyaedtpath = os.path.join(
    local_path,
    "..",
)

with Desktop(version, True) as d:
    desktop = sys.modules["__main__"].oDesktop
    pers1 = os.path.join(desktop.GetPersonalLibDirectory(), "pyaedt")

    if os.path.exists(pers1):
        print("PersonalLib already mapped")
    else:
        os.system('mklink /D "{}" "{}"'.format(pers1, pyaedtpath))

    toolkits = [
        "2DExtractor",
        "CircuitDesign",
        "Emit",
        "HFSS",
        "HFSS-IE",
        "HFSS3DLayoutDesign",
        "Icepak",
        "Lib",
        "Maxwell2D",
        "Maxwell3D",
        "Q3DExtractor",
        "TwinBuilder",
    ]

    for tk in toolkits:
        if os.access(d.syslib, os.W_OK) is not True:
            tool_dir = os.path.join(d.personallib, "Toolkits", tk, "PyAEDT")
        else:
            tool_dir = os.path.join(d.syslib, "Toolkits", tk, "PyAEDT")

        if not os.path.exists(tool_dir):
            os.makedirs(tool_dir)
        files_to_copy = ["Console", "Run_PyAEDT_Script"]
        for file_name in files_to_copy:
            with open(os.path.join(os.path.dirname(__file__), file_name + ".py_build"), "r") as build_file:
                with open(os.path.join(tool_dir, file_name + ".py"), "w") as out_file:
                    print("Building to " + os.path.join(tool_dir, file_name + ".py"))
                    for line in build_file:
                        line = line.replace("##INSTALL_DIR##", tool_dir).replace("##PYTHON_EXE##", sys.executable)
                        out_file.write(line)
        shutil.copyfile(
            os.path.join(os.path.dirname(__file__), "console_setup"), os.path.join(tool_dir, "console_setup")
        )
