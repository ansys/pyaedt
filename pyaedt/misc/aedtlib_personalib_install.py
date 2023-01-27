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


def install_toolkit(toolkit_dir, tk):
    lib_dir = os.path.join(toolkit_dir, "Lib", "PyAEDT")
    tool_dir = os.path.join(toolkit_dir, tk, "PyAEDT")
    os.makedirs(lib_dir, exist_ok=True)
    os.makedirs(tool_dir, exist_ok=True)
    files_to_copy = ["Console", "Run_PyAEDT_Script", "Jupyter"]
    for file_name in files_to_copy:
        with open(os.path.join(os.path.dirname(__file__), file_name + ".py_build"), "r") as build_file:
            with open(os.path.join(tool_dir, file_name + ".py"), "w") as out_file:
                print("Building to " + os.path.join(tool_dir, file_name + ".py"))
                build_file_data = build_file.read()
                build_file_data = build_file_data.replace("##INSTALL_DIR##", lib_dir).replace(
                    "##PYTHON_EXE##", sys.executable
                )
                jupyter_executable = sys.executable.replace("python.exe", "jupyter.exe")
                ipython_executable = sys.executable.replace("python,exe", "ipython.exe")
                build_file_data = build_file_data.replace("##IPYTHON_EXE##", ipython_executable).replace(
                    "##JUPYTER_EXE##", jupyter_executable
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

    for tk in toolkits:
        try:
            sys_dir = os.path.join(d.syslib, "Toolkits")
            install_toolkit(sys_dir, tk)
            d.logger.info("Installed toolkit for {} in sys lib".format(tk))

        except IOError:
            pers_dir = os.path.join(d.personallib, "Toolkits", tk, "PyAEDT")
            install_toolkit(pers_dir, tk)
            d.logger.info("Installed toolkit for {} in personal lib".format(tk))
if pid:
    try:
        os.kill(pid, 9)
    except:
        pass
