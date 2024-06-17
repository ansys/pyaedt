# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import os
import shutil
import subprocess  # nosec
import sys
import xml.etree.ElementTree as ET  # nosec

import defusedxml.minidom

defusedxml.defuse_stdlib()

import warnings

from defusedxml.ElementTree import ParseError
from defusedxml.minidom import parseString

from pyaedt.generic.general_methods import read_toml
from pyaedt.generic.settings import is_linux
import pyaedt.workflows
import pyaedt.workflows.templates


def add_automation_tab(
    name,
    lib_dir,
    icon_file=None,
    product="Project",
    template="Run PyAEDT Toolkit Script",
    overwrite=False,
    panel="Panel_PyAEDT_Extensions",
):
    """Add an automation tab in AEDT.

    Parameters
    ----------
    name : str
        Toolkit name.
    lib_dir : str
        Path to the library directory.
    icon_file : str
        Full path to the icon file. The default is the PyAnsys icon.
    product : str, optional
        Product directory to install the toolkit.
    template : str, optional
        Script template name to use
    overwrite : bool, optional
        Whether to overwrite the existing automation tab. The default is ``False``, in
        which case is adding new tabs to the existing ones.
    panel : str, optional
        Panel name. The default is ``"Panel_PyAEDT_Extensions"``.

    Returns
    -------
    str
        Automation tab path.

    """

    product = __tab_map(product)

    toolkit_name = name
    if "/" in name:
        toolkit_name = name.replace("/", "_")

    tab_config_file_path = os.path.join(lib_dir, product, "TabConfig.xml")
    if not os.path.isfile(tab_config_file_path) or overwrite:
        root = ET.Element("TabConfig")
    else:
        try:
            tree = ET.parse(tab_config_file_path)  # nosec
        except ParseError as e:  # pragma: no cover
            warnings.warn("Unable to parse %s\nError received = %s" % (tab_config_file_path, str(e)))
            return
        root = tree.getroot()

    panels = root.findall("./panel")
    if panels:
        panel_names = [panel_element.attrib["label"] for panel_element in panels]
        if panel in panel_names:
            # Remove previously existing PyAEDT panel and update with newer one.
            panel_element = [panel_element for panel_element in panels if panel_element.attrib["label"] == panel][0]
        else:
            panel_element = ET.SubElement(root, "panel", label=panel)
    else:
        panel_element = ET.SubElement(root, "panel", label=panel)

    buttons = panel_element.findall("./button")
    if buttons:  # pragma: no cover
        button_names = [button.attrib["label"] for button in buttons]
        if name in button_names:
            # Remove previously existing PyAEDT panel and update with newer one.
            b = [button for button in buttons if button.attrib["label"] == name][0]
            panel_element.remove(b)

    if not icon_file:
        icon_file = os.path.join(os.path.dirname(pyaedt.workflows.__file__), "images", "large", "pyansys.png")

    file_name = os.path.basename(icon_file)

    dest_dir = os.path.normpath(os.path.join(lib_dir, product, toolkit_name, "images", "large"))
    dest_file = os.path.normpath(os.path.join(dest_dir, file_name))
    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    shutil.copy(icon_file, dest_file)

    relative_image_path = os.path.relpath(dest_file, os.path.join(lib_dir, product))

    ET.SubElement(
        panel_element,
        "button",
        label=name,
        isLarge="1",
        image=relative_image_path,
        script="{}/{}".format(toolkit_name, template),
    )

    # Backup any existing file if present
    if os.path.isfile(tab_config_file_path):
        shutil.copy(tab_config_file_path, tab_config_file_path + ".orig")

    create_xml_tab(root, tab_config_file_path)
    return tab_config_file_path


def create_xml_tab(root, output_file):
    """Write the XML file to create the automation tab.

    Parameters
    ----------
    root : :class:xml.etree.ElementTree
        Root element of the main panel.
    output_file : str
        Full name of the file to save the XML tab.
    """
    lines = [line for line in parseString(ET.tostring(root)).toprettyxml(indent=" " * 4).split("\n") if line.strip()]
    xml_str = "\n".join(lines)

    with open(output_file, "w") as f:
        f.write(xml_str)


def remove_xml_tab(toolkit_dir, name, panel="Panel_PyAEDT_Extensions"):
    """Remove a toolkit configuration file."""
    tab_config_file_path = os.path.join(toolkit_dir, "TabConfig.xml")
    if not os.path.isfile(tab_config_file_path):  # pragma: no cover
        return True
    try:
        tree = ET.parse(tab_config_file_path)  # nosec
    except ParseError as e:  # pragma: no cover
        warnings.warn("Unable to parse %s\nError received = %s" % (tab_config_file_path, str(e)))
        return
    root = tree.getroot()

    panels = root.findall("./panel")
    if panels:
        panel_names = [panel_element.attrib["label"] for panel_element in panels]
        if panel in panel_names:
            # Remove previously existing PyAEDT panel and update with newer one.
            panel_element = [panel_element for panel_element in panels if panel_element.attrib["label"] == panel][0]
        else:  # pragma: no cover
            panel_element = ET.SubElement(root, "panel", label=panel)
    else:  # pragma: no cover
        panel_element = ET.SubElement(root, "panel", label=panel)

    buttons = panel_element.findall("./button")
    if buttons:
        button_names = [button.attrib["label"] for button in buttons]
        if name in button_names:
            # Remove previously existing PyAEDT panel and update with newer one.
            b = [button for button in buttons if button.attrib["label"] == name][0]
            panel_element.remove(b)

    create_xml_tab(root, tab_config_file_path)


def available_toolkits():
    product_list = [
        "Circuit",
        "EMIT",
        "HFSS",
        "HFSS3DLayout",
        "Icepak",
        "Maxwell2D",
        "Maxwell3D",
        "Mechanical",
        "Project",
        "Q2D",
        "Q3D",
        "TwinBuilder",
    ]

    product_toolkits = {}
    for product in product_list:
        toml_file = os.path.join(os.path.dirname(__file__), product.lower(), "toolkits_catalog.toml")
        if os.path.isfile(toml_file):
            toolkits_catalog = read_toml(toml_file)
            product_toolkits[product] = toolkits_catalog
    return product_toolkits


def add_script_to_menu(
    name,
    script_file,
    template_file="run_pyaedt_toolkit_script",
    icon_file=None,
    product="Project",
    copy_to_personal_lib=True,
    executable_interpreter=None,
    panel="Panel_PyAEDT_Extensions",
    personal_lib=None,
    aedt_version="",
):
    """Add a script to the ribbon menu.

    .. note::
       This method is available in AEDT 2023 R2 and later. PyAEDT must be installed
       in AEDT to allow this method to run. For more information, see `Installation
       <https://aedt.docs.pyansys.com/version/stable/Getting_started/Installation.html>`_.

    Parameters
    ----------
    name : str
        Name of the toolkit to appear in AEDT.
    script_file : str
        Full path to the script file. The script will be moved to Personal Lib.
    template_file : str
        Script template name to use. The default is ``"run_pyaedt_toolkit_script"``.
    icon_file : str, optional
        Full path to the icon (a 30x30 pixel PNG file) to add to the UI.
        The default is ``None``.
    product : str, optional
        Product to which the toolkit applies. The default is ``"Project"``, in which case
        it applies to all designs. You can also specify a product, such as ``"HFSS"``.
    copy_to_personal_lib : bool, optional
        Whether to copy the script to Personal Lib or link the original script. Default is ``True``.
    executable_interpreter : str, optional
        Executable python path. The default is the one current interpreter.
    panel : str, optional
        Panel name. The default is ``"Panel_PyAEDT_Extensions"``.
    personal_lib : str, optional
    aedt_version : str, optional

    Returns
    -------
    bool

    """
    logger = logging.getLogger("Global")
    if not personal_lib or not aedt_version:
        from pyaedt.generic.desktop_sessions import _desktop_sessions

        if not _desktop_sessions:  # pragma: no cover
            logger.error("Personallib or AEDT version is not provided and there is no available desktop session.")
            return False
        d = list(_desktop_sessions.values())[0]
        personal_lib = d.personallib
        aedt_version = d.aedt_version_id
    if script_file and not os.path.exists(script_file):  # pragma: no cover
        logger.error("Script does not exists.")
        return False
    toolkit_dir = os.path.join(personal_lib, "Toolkits")
    tool_map = __tab_map(product)
    file_name = name
    if "/" in file_name:  # pragma: no cover
        file_name = file_name.replace("/", "_")
    tool_dir = os.path.join(toolkit_dir, tool_map, file_name)
    lib_dir = os.path.join(tool_dir, "Lib")
    toolkit_rel_lib_dir = os.path.relpath(lib_dir, tool_dir)
    if is_linux and aedt_version <= "2023.1":  # pragma: no cover
        toolkit_rel_lib_dir = os.path.join("Lib", file_name)
        lib_dir = os.path.join(toolkit_dir, toolkit_rel_lib_dir)
        toolkit_rel_lib_dir = "../../" + toolkit_rel_lib_dir
    os.makedirs(lib_dir, exist_ok=True)
    os.makedirs(tool_dir, exist_ok=True)
    dest_script_path = None
    if script_file and copy_to_personal_lib:
        dest_script_path = os.path.join(lib_dir, os.path.split(script_file)[-1])
        shutil.copy2(script_file, dest_script_path)

    version_agnostic = True
    if aedt_version[2:6].replace(".", "") in sys.executable:  # pragma: no cover
        executable_version_agnostic = sys.executable.replace(aedt_version[2:6].replace(".", ""), "%s")
        version_agnostic = False
    else:
        executable_version_agnostic = sys.executable

    if executable_interpreter:  # pragma: no cover
        version_agnostic = True
        executable_version_agnostic = executable_interpreter

    templates_dir = os.path.dirname(pyaedt.workflows.templates.__file__)

    ipython_executable = executable_version_agnostic.replace("python" + __exe(), "ipython" + __exe())
    jupyter_executable = executable_version_agnostic.replace("python" + __exe(), "jupyter" + __exe())

    with open(os.path.join(templates_dir, template_file + ".py_build"), "r") as build_file:
        with open(os.path.join(tool_dir, template_file + ".py"), "w") as out_file:
            build_file_data = build_file.read()
            build_file_data = build_file_data.replace("##TOOLKIT_REL_LIB_DIR##", toolkit_rel_lib_dir)
            build_file_data = build_file_data.replace("##IPYTHON_EXE##", ipython_executable)
            build_file_data = build_file_data.replace("##PYTHON_EXE##", executable_version_agnostic)
            build_file_data = build_file_data.replace("##JUPYTER_EXE##", jupyter_executable)
            build_file_data = build_file_data.replace("##TOOLKIT_NAME##", file_name)
            if dest_script_path:
                build_file_data = build_file_data.replace("##PYTHON_SCRIPT##", dest_script_path)

            if version_agnostic:
                build_file_data = build_file_data.replace(" % version", "")
            out_file.write(build_file_data)

    add_automation_tab(name, toolkit_dir, icon_file=icon_file, product=product, template=template_file, panel=panel)
    logger.info("{} installed".format(name))
    return True


def __tab_map(product):  # pragma: no cover
    """Map exceptions in AEDT applications."""
    if product.lower() == "hfss3dlayout":
        return "HFSS3DLayoutDesign"
    elif product.lower() == "circuit":
        return "CircuitDesign"
    elif product.lower() == "q2d":
        return "2DExtractor"
    elif product.lower() == "q3d":
        return "Q3DExtractor"
    elif product.lower() == "simplorer":
        return "TwinBuilder"
    else:
        return product


def add_custom_toolkit(desktop_object, toolkit_name, wheel_toolkit=None, install=True):  # pragma: no cover
    """Add toolkit to AEDT Automation Tab.

    Parameters
    ----------
    desktop_object : :class:pyaedt.desktop.Desktop
        Desktop object.
    toolkit_name : str
        Name of toolkit to add.
    wheel_toolkit : str
        Wheelhouse path.
    install : bool, optional
        Whether to install the toolkit.

    Returns
    -------
    bool
    """
    toolkits = available_toolkits()
    toolkit_info = None
    product_name = None
    for product in toolkits:
        if toolkit_name in toolkits[product]:
            toolkit_info = toolkits[product][toolkit_name]
            product_name = product
            break
    if not toolkit_info:
        desktop_object.logger.error("Toolkit does not exist.")
        return False

    # Set Python version based on AEDT version
    python_version = "3.10" if desktop_object.aedt_version_id > "2023.1" else "3.7"
    python_version_new = python_version.replace(".", "_")
    if not is_linux:
        base_venv = os.path.normpath(
            os.path.join(
                desktop_object.install_path,
                "commonfiles",
                "CPython",
                python_version_new,
                "winx64",
                "Release",
                "python",
                "python.exe",
            )
        )
    else:
        base_venv = os.path.normpath(
            os.path.join(
                desktop_object.install_path,
                "commonfiles",
                "CPython",
                python_version_new,
                "linx64",
                "Release",
                "python",
                "runpython",
            )
        )

    def run_command(command):
        try:
            if is_linux:  # pragma: no cover
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
            else:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
            _, stderr = process.communicate()
            ret_code = process.returncode
            if ret_code != 0:
                print("Error occurred:", stderr.decode("utf-8"))
            return ret_code
        except Exception as e:
            print("Exception occurred:", str(e))
            return 1  # Return non-zero exit code for indicating an error

    version = desktop_object.odesktop.GetVersion()[2:6].replace(".", "")

    if not is_linux:
        venv_dir = os.path.join(os.environ["APPDATA"], ".pyaedt_env", "toolkits_{}".format(python_version_new))
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
        package_dir = os.path.join(venv_dir, "Lib")
    else:
        venv_dir = os.path.join(os.environ["HOME"], ".pyaedt_env", "toolkits_{}".format(python_version_new))
        python_exe = os.path.join(venv_dir, "bin", "python")
        pip_exe = os.path.join(venv_dir, "bin", "pip")
        package_dir = os.path.join(venv_dir, "lib")
        edt_root = os.path.normpath(desktop_object.odesktop.GetExeDir())
        os.environ["ANSYSEM_ROOT{}".format(version)] = edt_root
        ld_library_path_dirs_to_add = [
            "{}/commonfiles/CPython/{}/linx64/Release/python/lib".format(edt_root, python_version_new),
            "{}/common/mono/Linux64/lib64".format(edt_root),
            "{}".format(edt_root),
        ]
        if version < "232":
            ld_library_path_dirs_to_add.append("{}/Delcross".format(edt_root))
        os.environ["LD_LIBRARY_PATH"] = ":".join(ld_library_path_dirs_to_add) + ":" + os.getenv("LD_LIBRARY_PATH", "")

    # Create virtual environment

    if not os.path.exists(venv_dir):
        desktop_object.logger.info("Creating virtual environment")
        run_command('"{}" -m venv "{}" --system-site-packages'.format(base_venv, venv_dir))
        desktop_object.logger.info("Virtual environment created.")

    is_installed = False
    script_file = None
    if os.path.isdir(os.path.normpath(os.path.join(package_dir, toolkit_info["script"]))):
        script_file = os.path.normpath(os.path.join(package_dir, toolkit_info["script"]))
    else:
        for dirpath, dirnames, _ in os.walk(package_dir):
            if "site-packages" in dirnames:
                script_file = os.path.normpath(os.path.join(dirpath, "site-packages", toolkit_info["script"]))
                break
    if os.path.isfile(script_file):
        is_installed = True
    if wheel_toolkit:
        wheel_toolkit = os.path.normpath(wheel_toolkit)
    desktop_object.logger.info("Installing dependencies")
    if install and wheel_toolkit and os.path.exists(wheel_toolkit):
        desktop_object.logger.info("Starting offline installation")
        if is_installed:
            run_command('"{}" uninstall --yes {}'.format(pip_exe, toolkit_info["pip"]))
        import zipfile

        unzipped_path = os.path.join(
            os.path.dirname(wheel_toolkit), os.path.splitext(os.path.basename(wheel_toolkit))[0]
        )
        if os.path.exists(unzipped_path):
            shutil.rmtree(unzipped_path, ignore_errors=True)
        with zipfile.ZipFile(wheel_toolkit, "r") as zip_ref:
            zip_ref.extractall(unzipped_path)

        package_name = toolkit_info["package"]
        run_command(
            '"{}" install --no-cache-dir --no-index --find-links={} {}'.format(pip_exe, unzipped_path, package_name)
        )
    elif install and not is_installed:
        # Install the specified package
        run_command('"{}" --default-timeout=1000 install {}'.format(pip_exe, toolkit_info["pip"]))
    elif not install and is_installed:
        # Uninstall toolkit
        run_command('"{}" --default-timeout=1000 uninstall -y {}'.format(pip_exe, toolkit_info["package"]))
    elif install and is_installed:
        # Update toolkit
        run_command('"{}" --default-timeout=1000 install {} -U'.format(pip_exe, toolkit_info["pip"]))
    else:
        desktop_object.logger.info("Incorrect input")
        return
    toolkit_dir = os.path.join(desktop_object.personallib, "Toolkits")
    tool_dir = os.path.join(toolkit_dir, product_name, toolkit_info["name"])

    script_image = os.path.abspath(
        os.path.join(os.path.dirname(pyaedt.workflows.__file__), product_name.lower(), toolkit_info["icon"])
    )

    if install:
        if not os.path.exists(tool_dir):
            # Install toolkit inside AEDT
            add_script_to_menu(
                name=toolkit_info["name"],
                script_file=script_file,
                icon_file=script_image,
                product=product_name,
                template_file=toolkit_info.get("template", "run_pyaedt_toolkit_script"),
                copy_to_personal_lib=True,
                executable_interpreter=python_exe,
                personal_lib=desktop_object.personallib,
                aedt_version=desktop_object.aedt_version_id,
            )
            desktop_object.logger.info("{} installed".format(toolkit_info["name"]))
            if version > "232":
                desktop_object.odesktop.RefreshToolkitUI()
    else:
        if os.path.exists(tool_dir):
            # Install toolkit inside AEDT
            remove_script_from_menu(
                desktop_object=desktop_object,
                name=toolkit_info["name"],
                product=product_name,
            )
            desktop_object.logger.info("Installing dependencies")
            desktop_object.logger.info("{} uninstalled".format(toolkit_info["name"]))


def remove_script_from_menu(desktop_object, name, product="Project"):
    """Remove a toolkit script from the menu.

    Parameters
    ----------
    desktop_object : :class:pyaedt.desktop.Desktop
        Desktop object.
    name : str
        Name of the toolkit to remove.
    product : str, optional
        Product to which the toolkit applies. The default is ``"Project"``, in which case
        it applies to all designs. You can also specify a product, such as ``"HFSS"``.

    Returns
    -------
    bool
    """
    product = __tab_map(product)
    toolkit_dir = os.path.join(desktop_object.personallib, "Toolkits")
    aedt_version = desktop_object.aedt_version_id
    tool_dir = os.path.join(toolkit_dir, product, name)
    shutil.rmtree(tool_dir, ignore_errors=True)
    if aedt_version >= "2023.2":
        remove_xml_tab(os.path.join(toolkit_dir, product), name)
    desktop_object.logger.info("{} toolkit removed successfully.".format(name))
    return True


def __exe():
    if not is_linux:
        return ".exe"
    return ""
