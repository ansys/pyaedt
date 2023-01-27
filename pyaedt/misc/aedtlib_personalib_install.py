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
pid = 0


def install_toolkit(toolkit_dir, product):
    toolkit_rel_lib_dir = os.path.join("Lib", "PyAEDT")
    lib_dir = os.path.join(toolkit_dir, toolkit_rel_lib_dir)
    tool_dir = os.path.join(toolkit_dir, product, "PyAEDT")
    os.makedirs(lib_dir, exist_ok=True)
    os.makedirs(tool_dir, exist_ok=True)
    files_to_copy = ["Console", "Run_PyAEDT_Script", "Jupyter"]
    jupyter_executable = sys.executable.replace("python.exe", "jupyter.exe")
    ipython_executable = sys.executable.replace("python.exe", "ipython.exe")
    for file_name in files_to_copy:
        with open(os.path.join(os.path.dirname(__file__), file_name + ".py_build"), "r") as build_file:
            file_name_dest = file_name.replace("_", " ") + ".py"
            with open(os.path.join(tool_dir, file_name_dest), "w") as out_file:
                print("Building to " + os.path.join(tool_dir, file_name_dest))
                build_file_data = build_file.read()
                build_file_data = (
                    build_file_data.replace("##TOOLKIT_REL_LIB_DIR##", toolkit_rel_lib_dir)
                    .replace("##PYTHON_EXE##", sys.executable)
                    .replace("##IPYTHON_EXE##", ipython_executable)
                    .replace("##JUPYTER_EXE##", jupyter_executable)
                )
                out_file.write(build_file_data)
    shutil.copyfile(os.path.join(os.path.dirname(__file__), "console_setup"), os.path.join(lib_dir, "console_setup.py"))
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), "jupyter_template.ipynb"),
        os.path.join(lib_dir, "jupyter_template.ipynb"),
    )


with Desktop(version, True, new_desktop_session=True) as d:
    desktop = sys.modules["__main__"].oDesktop
    pers1 = os.path.join(desktop.GetPersonalLibDirectory(), "pyaedt")
    pid = desktop.GetProcessID()
    if os.path.exists(pers1):
        d.logger.info("PersonalLib already mapped")
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
        "Maxwell2D",
        "Maxwell3D",
        "Q3DExtractor",
        "TwinBuilder",
        "Mechanical",
    ]

    for product in toolkits:
        try:
            sys_dir = os.path.join(d.syslib, "Toolkits")
            install_toolkit(sys_dir, product)
            d.logger.info("Installed toolkit for {} in sys lib".format(product))

        except IOError:
            pers_dir = os.path.join(d.personallib, "Toolkits")
            install_toolkit(pers_dir, product)
            d.logger.info("Installed toolkit for {} in personal lib".format(product))
if pid:
    try:
        os.kill(pid, 9)
    except:
        pass
