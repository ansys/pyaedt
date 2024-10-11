import argparse
import os
import sys
import platform
import shutil

is_iron_python = platform.python_implementation().lower() == "ironpython"
is_linux = os.name == "posix"
is_windows = not is_linux

VENV_DIR_PREFIX = ".pyaedt_env"


def run_pyinstaller_from_c_python(oDesktop):
    # Iron Python script to create the virtual environment and install PyAEDT
    # Get AEDT information
    version = oDesktop.GetVersion()[2:6].replace(".", "")
    # From AEDT 2023.2 the installed CPython version is 3.10
    python_version = "3.10" if version > "231" else "3.7"
    python_version_new = python_version.replace(".", "_")
    # AEDT installation root
    edt_root = os.path.normpath(oDesktop.GetExeDir())
    # CPython interpreter executable
    if is_windows:
        python_exe = os.path.normpath(os.path.join(edt_root, "commonfiles", "CPython", python_version_new,
                                                   "winx64", "Release", "python", "python.exe"))
    else:
        python_exe = os.path.normpath(os.path.join(edt_root, "commonfiles", "CPython", python_version_new,
                                                   "linx64", "Release", "python", "runpython"))

    # Launch this script again from the CPython interpreter. This calls the ``install_pyaedt()`` method,
    # which creates a virtual environment and installs PyAEDT and its dependencies
    command = [f"{python_exe}", f"{os.path.normpath(__file__)}", "--version=" + version]
    if is_student_version(oDesktop):
        command.append("--student")
    if is_linux:
        command.extend([f'--edt_root="{edt_root}"', f'--python_version="{python_version}"'])

    if wheelpyaedt:
        command.extend([f'--wheel="{wheelpyaedt}"'])

    oDesktop.AddMessage("", "", 0, "Installing PyAEDT.")
    if is_windows:
        import subprocess
        process = subprocess.Popen(" ".join(command))
        process.wait()
        return_code = process.returncode
        err_msg = "There was an error while installing PyAEDT."
    else:
        return_code = run_command(" ".join(command))
        err_msg = "There was an error while installing PyAEDT. Refer to the Terminal window where AEDT was launched " \
                  "from."

    if str(return_code) != "0":
        oDesktop.AddMessage("", "", 2, err_msg)
        return
    else:
        oDesktop.AddMessage("", "", 0, "PyAEDT virtual environment created.")

    # Add PyAEDT tabs in AEDT
    # Virtual environment path and Python executable
    if is_windows:
        venv_dir = os.path.join(os.environ["APPDATA"], VENV_DIR_PREFIX, python_version_new)
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_dir = os.path.join(os.environ["HOME"], VENV_DIR_PREFIX, python_version_new)
        python_exe = os.path.join(venv_dir, "bin", "python")
    pyaedt_path = os.path.join(venv_dir, "Lib", "site-packages", "ansys", "aedt", "core")
    if is_linux:
        for dirpath, dirnames, _ in os.walk(venv_dir):
            if "site-packages" in dirnames:
                pyaedt_path = os.path.normpath(
                    os.path.join(dirpath, "site-packages", "ansys", "aedt", "core")
                )
                if os.path.isdir(pyaedt_path):
                    break

    # Create Toolkits in PersonalLib
    import tempfile
    python_script = os.path.join(tempfile.gettempdir(), "configure_pyaedt.py")
    if os.path.isfile(python_script):
        os.remove(python_script)
    with open(python_script, "w") as f:
        # enable in debug mode
        # f.write("import sys\n")
        # f.write('sys.path.insert(0, r"c:\\ansysdev\\git\\repos\\pyaedt")\n')
        if version <= "231":
            f.write("from pyaedt.workflows.installer.pyaedt_installer import add_pyaedt_to_aedt\n")
            f.write(
                f'add_pyaedt_to_aedt(aedt_version="{oDesktop.GetVersion()[:6]}", personallib=r"{oDesktop.GetPersonalLibDirectory()}")\n')
        else:
            f.write("from ansys.aedt.core.workflows.installer.pyaedt_installer import add_pyaedt_to_aedt\n")
            f.write(
                f'add_pyaedt_to_aedt(aedt_version="{oDesktop.GetVersion()[:6]}", personal_lib=r"{oDesktop.GetPersonalLibDirectory()}")\n')

    command = f'"{python_exe}" "{python_script}"'
    oDesktop.AddMessage("", "", 0, "Configuring PyAEDT panels in automation tab.")
    ret_code = os.system(command)
    if ret_code != 0:
        oDesktop.AddMessage("", "", 2, "Error occurred configuring the PyAEDT panels.")
        return
    # Refresh UI
    oDesktop.CloseAllWindows()
    if version >= "232":
        oDesktop.RefreshToolkitUI()
    msg = "PyAEDT configuration complete."
    if is_linux:
        msg += " Please ensure Ansys Electronics Desktop is launched in gRPC mode (i.e. launch ansysedt with -grpcsrv" \
               " argument) to take advantage of the new toolkits."

    if "GetIsNonGraphical" in oDesktop.__dir__() and not oDesktop.GetIsNonGraphical():
        from System.Windows.Forms import MessageBox, MessageBoxButtons, MessageBoxIcon
        oDesktop.AddMessage("", "", 0, msg)
        MessageBox.Show(msg, 'Info', MessageBoxButtons.OK, MessageBoxIcon.Information)
    oDesktop.AddMessage("", "", 0, "Create a project if the PyAEDT panel is not visible.")


def parse_arguments_for_pyaedt_installer(args=None):
    parser = argparse.ArgumentParser(description="Install PyAEDT")
    if is_linux:
        parser.add_argument("--edt_root", help="AEDT's path (required for Linux)", required=True)
        parser.add_argument("--python_version", help="Python version (required for Linux)", required=True)

    parser.add_argument("--version", "-v", help="AEDT's 3 digit version", required=True)
    parser.add_argument("--student", "--student_version", "-sv", help="Is Student version", action="store_true")
    parser.add_argument("--wheel", "--wheel_house", "-whl", type=str, help="Wheel house path")
    args = parser.parse_args(args)
    if len(sys.argv[1:]) == 0 and args is None:
        parser.print_help()
        parser.error("No arguments given!")
    return args


def install_pyaedt():
    # This is called when run from CPython
    args = parse_arguments_for_pyaedt_installer()

    python_version = "3_10"
    if args.version <= "231":
        python_version = "3_7"

    if is_windows:
        venv_dir = os.path.join(os.environ["APPDATA"], VENV_DIR_PREFIX, python_version)
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        venv_dir = os.path.join(os.environ["HOME"], VENV_DIR_PREFIX, python_version)
        python_exe = os.path.join(venv_dir, "bin", "python")
        pip_exe = os.path.join(venv_dir, "bin", "pip")
        os.environ[f"ANSYSEM_ROOT{args.version}"] = args.edt_root
        ld_library_path_dirs_to_add = [
            f"{args.edt_root}/commonfiles/CPython/{args.python_version.replace('.', '_')}/linx64/Release/python/lib",
            f"{args.edt_root}/common/mono/Linux64/lib64",
            f"{args.edt_root}",
        ]
        if args.version < "232":
            ld_library_path_dirs_to_add.append(f"{args.edt_root}/Delcross")
        os.environ["LD_LIBRARY_PATH"] = ":".join(ld_library_path_dirs_to_add) + ":" + os.getenv("LD_LIBRARY_PATH", "")
        os.environ["TK_LIBRARY"] = ("{}/commonfiles/CPython/{}/linx64/Release/python/lib/tk8.5".
                                    format(args.edt_root,
                                           args.python_version.replace(
                                               ".", "_")))
        os.environ["TCL_LIBRARY"] = ("{}/commonfiles/CPython/{}/linx64/Release/python/lib/tcl8.5".
                                     format(args.edt_root,
                                            args.python_version.replace(
                                                ".", "_")))

    if not os.path.exists(venv_dir):

        if args.version == "231":
            run_command(f'"{sys.executable}" -m venv "{venv_dir}" --system-site-packages')
        else:
            run_command(f'"{sys.executable}" -m venv "{venv_dir}"')

        if args.wheel and os.path.exists(args.wheel):
            wheel_pyaedt = args.wheel
            if wheel_pyaedt.endswith(".zip"):
                import zipfile
                unzipped_path = os.path.join(os.path.dirname(wheel_pyaedt),
                                             os.path.splitext(os.path.basename(wheel_pyaedt))[0])
                if os.path.exists(unzipped_path):
                    shutil.rmtree(unzipped_path, ignore_errors=True)
                with zipfile.ZipFile(wheel_pyaedt, 'r') as zip_ref:
                    # Extract all contents to a directory. (You can specify a different extraction path if needed.)
                    zip_ref.extractall(unzipped_path)
            else:
                # Extracted folder.
                unzipped_path = wheel_pyaedt
            if args.version <= "231":
                run_command(
                    f'"{pip_exe}" install --no-cache-dir --no-index --find-links={unzipped_path} pyaedt[all,dotnet]')
            else:
                run_command(
                    f'"{pip_exe}" install --no-cache-dir --no-index --find-links={unzipped_path} pyaedt[installer]')

        else:
            run_command(f'"{python_exe}" -m pip install --upgrade pip')
            run_command(f'"{pip_exe}" --default-timeout=1000 install wheel')
            # run_command(
            # '"{}" --default-timeout=1000 install git+https://github.com/ansys/pyaedt.git@main'.format(pip_exe))
            if args.version <= "231":
                run_command(f'"{pip_exe}" --default-timeout=1000 install pyaedt[all]=="0.9.0"')
                run_command(f'"{pip_exe}" --default-timeout=1000 install jupyterlab')
                run_command(f'"{pip_exe}" --default-timeout=1000 install ipython -U')
                run_command(f'"{pip_exe}" --default-timeout=1000 install ipyvtklink')
            else:
                run_command(f'"{pip_exe}" --default-timeout=1000 install pyaedt[installer]')

        if args.version == "231":
            run_command(f'"{pip_exe}" uninstall -y pywin32')

    else:
        run_command(f'"{pip_exe}" uninstall --yes pyaedt')

        if args.wheel and os.path.exists(args.wheel):
            wheel_pyaedt = args.wheel
            import zipfile
            unzipped_path = os.path.join(os.path.dirname(wheel_pyaedt),
                                         os.path.splitext(os.path.basename(wheel_pyaedt))[0])
            if os.path.exists(unzipped_path):
                shutil.rmtree(unzipped_path, ignore_errors=True)
            with zipfile.ZipFile(wheel_pyaedt, 'r') as zip_ref:
                # Extract all contents to a directory. (You can specify a different extraction path if needed.)
                zip_ref.extractall(unzipped_path)
            if args.version <= "231":
                run_command(f'"{pip_exe}" install --no-cache-dir --no-index --find-links={unzipped_path} pyaedt["all]=="0.9.0"')
            else:
                run_command(f'"{pip_exe}" install --no-cache-dir --no-index --find-links={unzipped_path} pyaedt["installer]')
        else:
            if args.version <= "231":
                run_command(f'"{pip_exe}" --default-timeout=1000 install pyaedt[all]=="0.9.0"')
                run_command(f'"{pip_exe}" --default-timeout=1000 install jupyterlab')
                run_command(f'"{pip_exe}" --default-timeout=1000 install ipython -U')
                run_command(f'"{pip_exe}" --default-timeout=1000 install ipyvtklink')
            else:
                run_command(f'"{pip_exe}" --default-timeout=1000 install pyaedt[installer]')
    sys.exit(0)


def is_student_version(oDesktop):
    edt_root = os.path.normpath(oDesktop.GetExeDir())
    if is_windows and os.path.isdir(edt_root):
        if any("ansysedtsv" in fn.lower() for fn in os.listdir(edt_root)):
            return True
    return False


def run_command(command):
    if is_windows:
        command = f'"{command}"'
    ret_code = os.system(command)
    return ret_code


if __name__ == "__main__":

    if is_iron_python:
        # Check if wheelhouse defined. Wheelhouse is created for Windows only.
        wheelpyaedt = []
        # Retrieve the script arguments
        script_args = ScriptArgument.split()
        if len(script_args) == 1:
            wheelpyaedt = script_args[0]
            if not os.path.exists(wheelpyaedt):
                wheelpyaedt = []
        run_pyinstaller_from_c_python(oDesktop)
    else:
        install_pyaedt()
