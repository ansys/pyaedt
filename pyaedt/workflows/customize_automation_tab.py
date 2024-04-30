# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
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

import os
import shutil
import sys
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

from pyaedt import is_linux
import pyaedt.workflows.templates

"""Methods to add new automation tabs in AEDT."""


def add_automation_tab(
    name, lib_dir, icon_file=None, product="Project", template="Run PyAEDT Toolkit Script", overwrite=False
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

    """

    tab_config_file_path = os.path.join(lib_dir, product, "TabConfig.xml")
    if not os.path.isfile(tab_config_file_path) or overwrite:
        root = ET.Element("TabConfig")
    else:
        try:
            tree = ET.parse(tab_config_file_path)
        except ParseError as e:
            warnings.warn("Unable to parse %s\nError received = %s" % (tab_config_file_path, str(e)))
            return
        root = tree.getroot()

    panels = root.findall("./panel")
    if panels:
        panel_names = [panel.attrib["label"] for panel in panels]
        if "Panel_PyAEDT_Toolkits" in panel_names:
            # Remove previously existing PyAEDT panel and update with newer one.
            panel = [panel for panel in panels if panel.attrib["label"] == "Panel_PyAEDT_Toolkits"][0]
        else:
            panel = ET.SubElement(root, "panel", label="Panel_PyAEDT_Toolkits")
    else:
        panel = ET.SubElement(root, "panel", label="Panel_PyAEDT_Toolkits")

    buttons = panel.findall("./button")
    if buttons:
        button_names = [button.attrib["label"] for button in buttons]
        if name in button_names:
            # Remove previously existing PyAEDT panel and update with newer one.
            b = [button for button in buttons if button.attrib["label"] == name][0]
            panel.remove(b)

    file_name = os.path.basename(icon_file)
    dest_dir = os.path.normpath(os.path.join(lib_dir, product, name, "images", "large"))
    dest_file = os.path.normpath(os.path.join(dest_dir, file_name))
    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    shutil.copy(icon_file, dest_file)

    ET.SubElement(
        panel,
        "button",
        label=name,
        isLarge="1",
        image=dest_file,
        script="{}/{}".format(name, template),
    )

    # Backup any existing file if present
    if os.path.isfile(tab_config_file_path):
        shutil.copy(tab_config_file_path, tab_config_file_path + ".orig")

    create_xml_tab(root, tab_config_file_path)


def remove_automation_tab(name, lib_dir):
    """Remove automation tab in AEDT.

    Parameters
    ----------
    name : str
        Toolkit name.
    lib_dir : str
        Path to the library directory.

    Returns
    -------
    float
        Result of the dot product.

    """

    tab_config_file_path = os.path.join(lib_dir, "TabConfig.xml")
    if not os.path.isfile(tab_config_file_path):
        return True
    try:
        tree = ET.parse(tab_config_file_path)
    except ParseError as e:
        warnings.warn("Unable to parse %s\nError received = %s" % (tab_config_file_path, str(e)))
        return
    root = tree.getroot()

    panels = root.findall("./panel")
    if panels:
        panel_names = [panel.attrib["label"] for panel in panels]
        if "Panel_PyAEDT_Toolkits" in panel_names:
            # Remove previously existing PyAEDT panel and update with newer one.
            panel = [panel for panel in panels if panel.attrib["label"] == "Panel_PyAEDT_Toolkits"][0]
        else:
            panel = ET.SubElement(root, "panel", label="Panel_PyAEDT_Toolkits")
    else:
        panel = ET.SubElement(root, "panel", label="Panel_PyAEDT_Toolkits")

    buttons = panel.findall("./button")
    if buttons:
        button_names = [button.attrib["label"] for button in buttons]
        if name in button_names:
            # Remove previously existing PyAEDT panel and update with newer one.
            b = [button for button in buttons if button.attrib["label"] == toolkitname][0]
            panel.remove(b)

    create_xml_tab(root, tab_config_file_path)


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


def add_script_to_menu(
    desktop_object,
    name,
    script_file,
    template_file="Run_PyAEDT_Toolkit_Script",
    icon_file=None,
    product="Project",
    copy_to_personal_lib=True,
    executable_interpreter=None,
):
    """Add a script to the ribbon menu.

    .. note::
       This method is available in AEDT 2023 R2 and later. PyAEDT must be installed
       in AEDT to allow this method to run. For more information, see `Installation
       <https://aedt.docs.pyansys.com/version/stable/Getting_started/Installation.html>`_.

    Parameters
    ----------
    desktop_object : :class:pyaedt.desktop.Desktop
        Desktop object.
    name : str
        Name of the toolkit to appear in AEDT.
    script_file : str
        Full path to the script file. The script will be moved to Personal Lib.
    template_file : str
        Script template name to use. The default is ``"Run_PyAEDT_Toolkit_Script"``.
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

    Returns
    -------
    bool

    """

    if script_file and not os.path.exists(script_file):
        desktop_object.logger.error("Script does not exists.")
        return False

    toolkit_dir = os.path.join(desktop_object.personallib, "Toolkits")
    aedt_version = desktop_object.aedt_version_id
    tool_dir = os.path.join(toolkit_dir, product, name)
    lib_dir = os.path.join(tool_dir, "Lib")
    toolkit_rel_lib_dir = os.path.relpath(lib_dir, tool_dir)
    if is_linux and aedt_version <= "2023.1":
        toolkit_rel_lib_dir = os.path.join("Lib", toolkit_name)
        lib_dir = os.path.join(toolkit_dir, toolkit_rel_lib_dir)
        toolkit_rel_lib_dir = "../../" + toolkit_rel_lib_dir
    os.makedirs(lib_dir, exist_ok=True)
    os.makedirs(tool_dir, exist_ok=True)

    if script_file and copy_to_personal_lib:
        dest_script_path = os.path.join(lib_dir, os.path.split(script_file)[-1])
        shutil.copy2(script_file, dest_script_path)

    version_agnostic = False
    if aedt_version[2:6].replace(".", "") in sys.executable:
        executable_version_agnostic = sys.executable.replace(aedt_version[2:6].replace(".", ""), "%s")
        version_agnostic = True
    else:
        executable_version_agnostic = sys.executable

    if executable_interpreter:
        executable_version_agnostic = executable_interpreter

    templates_dir = os.path.dirname(pyaedt.workflows.templates.__file__)

    ipython_executable = executable_version_agnostic.replace("python" + __exe(), "ipython" + __exe())
    jupyter_executable = executable_version_agnostic.replace("python" + __exe(), "jupyter" + __exe())

    with open(os.path.join(templates_dir, template_file + ".py_build"), "r") as build_file:
        file_name_dest = template_file.replace("_", " ")
        with open(os.path.join(tool_dir, file_name_dest + ".py"), "w") as out_file:
            build_file_data = build_file.read()
            build_file_data = build_file_data.replace("##TOOLKIT_REL_LIB_DIR##", toolkit_rel_lib_dir)
            build_file_data = build_file_data.replace("##IPYTHON_EXE##", ipython_executable)
            build_file_data = build_file_data.replace("##PYTHON_EXE##", executable_version_agnostic)
            build_file_data = build_file_data.replace("##JUPYTER_EXE##", jupyter_executable)

            if not version_agnostic:
                build_file_data = build_file_data.replace(" % version", "")
            out_file.write(build_file_data)

    if aedt_version >= "2023.2":
        if not icon_file:
            icon_file = os.path.join(os.path.dirname(__file__), "images", "large", "pyansys.png")
        add_automation_tab(name, toolkit_dir, icon_file=icon_file, product=product, template=file_name_dest)
    desktop_object.logger.info("{} installed".format(name))
    return True


def __exe():
    if not is_linux:
        return ".exe"
    return ""
