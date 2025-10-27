# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

import logging
import os
from pathlib import Path
import re
import shutil
import subprocess  # nosec
import sys
from typing import List
import warnings
import xml.etree.ElementTree as ET  # nosec

from defusedxml.ElementTree import ParseError
from defusedxml.ElementTree import parse as defused_parse
import defusedxml.minidom
from defusedxml.minidom import parseString

import ansys.aedt.core.extensions
import ansys.aedt.core.extensions.templates
from ansys.aedt.core.generic.file_utils import read_toml
from ansys.aedt.core.generic.settings import is_linux

defusedxml.defuse_stdlib()

AEDT_APPLICATIONS = {
    "circuit": "CircuitDesign",
    "emit": "EMIT",
    "hfss": "HFSS",
    "hfss3dlayout": "HFSS3DLayoutDesign",
    "icepak": "Icepak",
    "maxwell2d": "Maxwell2D",
    "maxwell3d": "Maxwell3D",
    "mechanical": "Mechanical",
    "common": "Common",
    "q2d": "2DExtractor",
    "q3d": "Q3DExtractor",
    "twinbuilder": "TwinBuilder",
}


def add_automation_tab(
    name,
    lib_dir,
    icon_file=None,
    product="Project",
    template="Run PyAEDT Toolkit Script",
    overwrite=False,
    panel="Panel_PyAEDT_Extensions",
    is_custom=False,  # new argument for custom flag
    odesktop=None,
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
    is_custom : bool, optional
        Whether the automation tab is for custom extensions. The default is ``False``.
    odesktop : oDesktop, optional
        Desktop session. The default is ``None``.

    Returns
    -------
    str
        Automation tab path.
    """
    product = tab_map(product)
    toolkit_name = name
    if "/" in name:
        toolkit_name = name.replace("/", "_")
    lib_dir = Path(lib_dir)
    tab_config_file_path = lib_dir / product / "TabConfig.xml"
    if not tab_config_file_path.is_file() or overwrite:
        root = ET.Element("TabConfig")
    else:
        try:
            tree = defused_parse(str(tab_config_file_path))
        except ParseError as e:  # pragma: no cover
            warnings.warn(f"Unable to parse {tab_config_file_path}\nError received = {str(e)}")
            return
        root = tree.getroot()
    panels = root.findall("./panel")
    if panels:
        panel_names = [panel_element.attrib["label"] for panel_element in panels]
        if panel in panel_names:
            panel_element = [panel_element for panel_element in panels if panel_element.attrib["label"] == panel][0]
        else:
            panel_element = ET.SubElement(root, "panel", label=panel)
    else:
        panel_element = ET.SubElement(root, "panel", label=panel)
    buttons = panel_element.findall("./button")
    if buttons:  # pragma: no cover
        button_names = [button.attrib["label"] for button in buttons]
        if name in button_names:
            b = [button for button in buttons if button.attrib["label"] == name][0]
            panel_element.remove(b)
    # For custom extensions, use 'image' and 'script' fields (relative paths)
    if is_custom:
        script = Path(name) / "run_pyaedt_toolkit_script"
        button_kwargs = dict(
            label=name,
            isLarge="1",
            image=str(Path(icon_file).as_posix()),
            script=str(script.as_posix()),
            custom_extension="true",
            type="custom",
        )
    else:
        if not icon_file:
            icon_file = Path(ansys.aedt.core.extensions.__file__).parent / "images" / "large" / "pyansys.png"
        else:
            icon_file = Path(icon_file)

        # For Linux, create symbolic link and use relative path (if not, AEDT panels break)
        if is_linux:  # pragma: no cover
            images_source = Path(ansys.aedt.core.extensions.__file__).parent / "installer" / "images" / "large"
            images_target = lib_dir / product / "images"
            if not images_target.exists() and images_source.exists():
                try:
                    images_target.symlink_to(images_source)
                except Exception:
                    logging.getLogger("Global").warning(
                        f"Could not create symlink from {images_source} to {images_target}"
                    )
                    if odesktop:
                        odesktop.AddMessage(
                            "", "", 0, str(f"Could not create symlink from {images_source} to {images_target}")
                        )
            icon_relative = f"images/{icon_file.name}"
            button_kwargs = dict(
                label=name,
                isLarge="1",
                image=icon_relative,
                script=f"{toolkit_name}/{template}",
            )
        else:
            button_kwargs = dict(
                label=name,
                isLarge="1",
                image=str(icon_file.as_posix()),
                script=f"{toolkit_name}/{template}",
            )
    ET.SubElement(panel_element, "button", **button_kwargs)
    # Backup any existing file if present
    if tab_config_file_path.is_file():
        shutil.copy(str(tab_config_file_path), str(tab_config_file_path) + ".orig")
    create_xml_tab(root, str(tab_config_file_path))
    return str(tab_config_file_path)


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


def is_extension_in_panel(toolkit_dir, product, name, panel="Panel_PyAEDT_Extensions"):
    """Check if a toolkit configuration exists in the panel.

    Parameters
    ----------
    toolkit_dir : str
        Path to the toolkit directory.
    product : str
        Name of the product to check.
    name : str
        Name of the toolkit to check.
    panel : str, optional
        Panel name. The default is ``"Panel_PyAEDT_Extensions"``.

    Returns
    -------
    bool
        True if the extension exists in the panel, False otherwise.
    """
    tab_config_file_path = Path(toolkit_dir) / tab_map(product) / "TabConfig.xml"
    if not tab_config_file_path.is_file():
        return False

    try:
        tree = defused_parse(str(tab_config_file_path))
    except ParseError as e:  # pragma: no cover
        warnings.warn("Unable to parse %s\nError received = %s" % (tab_config_file_path, str(e)))
        return False

    root = tree.getroot()
    panels = root.findall("./panel")

    if not panels:
        return False

    panel_names = [panel_element.attrib["label"] for panel_element in panels]
    if panel not in panel_names:
        return False

    # Get the specific panel
    panel_element = [panel_element for panel_element in panels if panel_element.attrib["label"] == panel][0]
    buttons = panel_element.findall("./button")

    if not buttons:
        return False

    button_names = [button.attrib["label"] for button in buttons]
    return name in button_names


def remove_xml_tab(toolkit_dir, product, name, panel="Panel_PyAEDT_Extensions"):
    """Remove a toolkit configuration from the panel.

    Parameters
    ----------
        toolkit_dir : str
            Path to the toolkit directory.
        product : str
            Name of the product to check.
        name : str
            Name of the toolkit to remove.
        panel : str, optional
            Panel name. The default is ``"Panel_PyAEDT_Extensions"``.
    s

    Returns
    -------
        bool
            True if removal was successful or extension was not found, False if error occurred.
    """
    # Check if extension exists in panel first
    if not is_extension_in_panel(toolkit_dir, tab_map(product), name, panel):
        return True  # Already removed or doesn't exist

    tab_config_file_path = Path(toolkit_dir) / tab_map(product) / "TabConfig.xml"
    try:
        tree = defused_parse(str(tab_config_file_path))
    except ParseError as e:  # pragma: no cover
        warnings.warn("Unable to parse %s\nError received = %s" % (tab_config_file_path, str(e)))
        return False

    root = tree.getroot()
    panels = root.findall("./panel")

    # Find the panel
    panel_element = [panel_element for panel_element in panels if panel_element.attrib["label"] == panel][0]
    buttons = panel_element.findall("./button")

    # Find and remove the button
    button_names = [button.attrib["label"] for button in buttons]
    if name in button_names:
        b = [button for button in buttons if button.attrib["label"] == name][0]
        panel_element.remove(b)

    create_xml_tab(root, str(tab_config_file_path))
    return True


def available_toolkits():
    product_toolkits = {}
    for product_extension, product_name in AEDT_APPLICATIONS.items():
        toml_file = Path(__file__).parent / product_extension / "toolkits_catalog.toml"
        if toml_file.is_file():
            toolkits_catalog = read_toml(str(toml_file))
            product_toolkits[product_name] = toolkits_catalog
    return product_toolkits


def add_script_to_menu(
    name,
    script_file=None,
    template_file="run_pyaedt_toolkit_script",
    icon_file=None,
    product="Project",
    copy_to_personal_lib=True,
    executable_interpreter=None,
    panel="Panel_PyAEDT_Extensions",
    personal_lib=None,
    aedt_version="",
    is_custom=False,
    odesktop=None,
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
    script_file : str, optional
        Full path to the script file. The script will be copied to Personal Lib.
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
    is_custom : bool, optional
    odesktop : oDesktop, optional

    Returns
    -------
    bool

    """
    logger = logging.getLogger("Global")
    if not personal_lib or not aedt_version:
        from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

        if not _desktop_sessions:  # pragma: no cover
            logger.error("Personallib or AEDT version is not provided and there is no available desktop session.")
            return False
        d = list(_desktop_sessions.values())[0]
        personal_lib = d.personallib
        aedt_version = d.aedt_version_id

    if script_file and not Path(script_file).exists():  # pragma: no cover
        logger.error("Script does not exists.")
        return False
    toolkit_dir = Path(personal_lib) / "Toolkits"
    tool_map = tab_map(product)
    file_name = name
    if "/" in file_name:  # pragma: no cover
        file_name = file_name.replace("/", "_")
    tool_dir = toolkit_dir / tool_map / file_name
    lib_dir = tool_dir / "Lib"
    toolkit_rel_lib_dir = lib_dir.relative_to(tool_dir)
    if is_linux and aedt_version <= "2023.1":  # pragma: no cover
        toolkit_rel_lib_dir = Path("Lib") / file_name
        lib_dir = toolkit_dir / toolkit_rel_lib_dir
        toolkit_rel_lib_dir = Path("..") / ".." / toolkit_rel_lib_dir
    if copy_to_personal_lib:
        lib_dir.mkdir(parents=True, exist_ok=True)
    tool_dir.mkdir(parents=True, exist_ok=True)
    dest_script_path = script_file
    if script_file and copy_to_personal_lib:
        dest_script_path = lib_dir / Path(script_file).name
        shutil.copy2(script_file, str(dest_script_path))

    version_agnostic = True
    if aedt_version[2:6].replace(".", "") in sys.executable:  # pragma: no cover
        executable_version_agnostic = sys.executable.replace(aedt_version[2:6].replace(".", ""), "%s")
        version_agnostic = False
    else:
        executable_version_agnostic = sys.executable

    if executable_interpreter:  # pragma: no cover
        version_agnostic = True
        executable_version_agnostic = executable_interpreter

    templates_dir = Path(ansys.aedt.core.extensions.templates.__file__).parent

    ipython_executable = re.sub(
        r"python" + __exe() + r"$",
        "ipython" + __exe(),
        executable_version_agnostic,
    )
    jupyter_executable = re.sub(
        r"python" + __exe() + r"$",
        "jupyter" + __exe(),
        executable_version_agnostic,
    )

    with open(templates_dir / (template_file + ".py_build"), "r") as build_file:
        build_file_data = build_file.read()
        # Ensure replacement values are strings
        build_file_data = build_file_data.replace("##TOOLKIT_REL_LIB_DIR##", str(toolkit_rel_lib_dir))
        build_file_data = build_file_data.replace("##IPYTHON_EXE##", str(ipython_executable))
        build_file_data = build_file_data.replace("##PYTHON_EXE##", str(executable_version_agnostic))
        build_file_data = build_file_data.replace("##JUPYTER_EXE##", str(jupyter_executable))
        build_file_data = build_file_data.replace("##TOOLKIT_NAME##", str(name))
        build_file_data = build_file_data.replace("##EXTENSION_TEMPLATES##", str(templates_dir))
        if dest_script_path:
            extension_dir = Path(dest_script_path).parent
        else:
            extension_dir = Path(ansys.aedt.core.extensions.__file__).parent / "installer"
        build_file_data = build_file_data.replace("##BASE_EXTENSION_LOCATION##", str(extension_dir))
        if script_file:
            build_file_data = build_file_data.replace("##PYTHON_SCRIPT##", str(os.path.basename(script_file)))
        if version_agnostic:
            build_file_data = build_file_data.replace(" % version", "")
        with open(tool_dir / (template_file + ".py"), "w") as out_file:
            out_file.write(build_file_data)

    add_automation_tab(
        name,
        toolkit_dir,
        icon_file=icon_file,
        product=product,
        template=template_file,
        panel=panel,
        is_custom=is_custom,
        odesktop=odesktop,
    )
    logger.info(f"{name} installed")
    if odesktop:
        odesktop.AddMessage("", "", 0, str(f"{name} installed"))
    return True


def tab_map(product):  # pragma: no cover
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


def run_command(command: List[str], desktop_object):  # pragma: no cover
    """Run a command through subprocess.

    .. warning::

        Do not execute this function with untrusted function argument, environment
        variables or pyaedt global settings.
        See the :ref:`security guide<ref_security_consideration>` for details.

    """
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)  # nosec
    except subprocess.CalledProcessError as e:
        desktop_object.logger.error("Error occurred:", e.stderr)
        return e.returncode

    return 0


def add_custom_toolkit(desktop_object, toolkit_name, wheel_toolkit=None, install=True):  # pragma: no cover
    """Add toolkit to AEDT Automation Tab.

    .. warning::

        Do not execute this function with untrusted function argument, environment
        variables or pyaedt global settings.
        See the :ref:`security guide<ref_security_consideration>` for details.

    Parameters
    ----------
    desktop_object : :class:ansys.aedt.core.desktop.Desktop
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
        base_venv = Path(desktop_object.install_path).joinpath(
            "commonfiles",
            "CPython",
            python_version_new,
            "winx64",
            "Release",
            "python",
            "python.exe",
        )
    else:
        base_venv = Path(desktop_object.install_path).joinpath(
            "commonfiles",
            "CPython",
            python_version_new,
            "linx64",
            "Release",
            "python",
            "runpython",
        )

    version = desktop_object.odesktop.GetVersion()[2:6].replace(".", "")

    if not is_linux:
        venv_dir = Path(os.environ["APPDATA"]).joinpath(
            ".pyaedt_env",
            f"toolkits_{python_version_new}",
        )
        python_exe = venv_dir.joinpath("Scripts", "python.exe")
        pip_exe = venv_dir.joinpath("Scripts", "pip.exe")
        package_dir = venv_dir.joinpath("Lib")
    else:
        venv_dir = Path(os.environ["HOME"]).joinpath(
            ".pyaedt_env",
            f"toolkits_{python_version_new}",
        )
        python_exe = venv_dir.joinpath("bin", "python")
        pip_exe = venv_dir.joinpath("bin", "pip")
        package_dir = venv_dir.joinpath("lib")
        edt_root = Path(desktop_object.odesktop.GetExeDir())
        os.environ[f"ANSYSEM_ROOT{version}"] = str(edt_root)
        ld_library_path_dirs_to_add = [
            f"{edt_root}/commonfiles/CPython/{python_version_new}/linx64/Release/python/lib",
            f"{edt_root}/common/mono/Linux64/lib64",
            f"{edt_root}",
        ]
        if version < "232":
            ld_library_path_dirs_to_add.append(f"{edt_root}/Delcross")
        os.environ["LD_LIBRARY_PATH"] = ":".join(ld_library_path_dirs_to_add) + ":" + os.getenv("LD_LIBRARY_PATH", "")

    # Create virtual environment

    if not venv_dir.exists():
        desktop_object.logger.info("Creating virtual environment")
        command = [str(base_venv), "-m", "venv", str(venv_dir)]
        run_command(command, desktop_object)
        desktop_object.logger.info("Virtual environment created.")

    is_installed = False
    script_file = None
    if (package_dir / toolkit_info["script"]).is_dir():
        script_file = package_dir / toolkit_info["script"]
    else:
        for dirpath, dirnames, _ in os.walk(str(package_dir)):
            if "site-packages" in dirnames:
                script_file = Path(
                    dirpath,
                    "site-packages",
                    toolkit_info["script"],
                )
                break
    if script_file and script_file.is_file():
        is_installed = True
    if wheel_toolkit:
        wheel_toolkit = Path(wheel_toolkit)

    desktop_object.logger.info("Installing dependencies")
    if install and wheel_toolkit and wheel_toolkit.exists():
        desktop_object.logger.info("Starting offline installation")
        if is_installed:
            command = [
                str(pip_exe),
                "uninstall",
                "--yes",
                toolkit_info["pip"],
            ]
            run_command(command, desktop_object)
        import zipfile

        unzipped_path = wheel_toolkit.with_name(wheel_toolkit.stem)
        if unzipped_path.exists():
            shutil.rmtree(str(unzipped_path), ignore_errors=True)
        with zipfile.ZipFile(str(wheel_toolkit), "r") as zip_ref:
            zip_ref.extractall(str(unzipped_path))

        package_name = toolkit_info["package"]
        command = [
            str(pip_exe),
            "install",
            "--no-cache-dir",
            "--no-index",
            "--find-links={unzipped_path}",
            package_name,
        ]
        run_command(command, desktop_object)
    elif install and not is_installed:
        # Install the specified package
        command = [
            str(pip_exe),
            "--default-timeout=1000",
            "install",
            toolkit_info["pip"],
        ]
        run_command(command, desktop_object)
    elif not install and is_installed:
        # Uninstall toolkit
        command = [
            str(pip_exe),
            "--default-timeout=1000",
            "uninstall",
            "-y",
            toolkit_info["package"],
        ]
        run_command(command, desktop_object)
    elif install and is_installed:
        # Update toolkit
        command = [
            str(pip_exe),
            "--default-timeout=1000",
            "install",
            toolkit_info["pip"],
            "-U",
        ]
        run_command(command, desktop_object)
    else:
        desktop_object.logger.info("Incorrect input")
        return
    toolkit_dir = Path(desktop_object.personallib) / "Toolkits"
    tool_dir = toolkit_dir / product_name / toolkit_info["name"]

    script_image = Path(ansys.aedt.core.extensions.__file__).parent.joinpath(
        product_name.lower(),
        toolkit_info["icon"],
    )

    if install:
        if not tool_dir.exists():
            # Install toolkit inside AEDT
            add_script_to_menu(
                name=toolkit_info["name"],
                script_file=str(script_file),
                icon_file=str(script_image),
                product=product_name,
                template_file=toolkit_info.get("template", "run_pyaedt_toolkit_script"),
                copy_to_personal_lib=True,
                executable_interpreter=str(python_exe),
                personal_lib=desktop_object.personallib,
                aedt_version=desktop_object.aedt_version_id,
            )
            desktop_object.logger.info(f"{toolkit_info['name']} installed")
            if version > "232":
                desktop_object.odesktop.RefreshToolkitUI()
    else:
        if tool_dir.exists():
            # Install toolkit inside AEDT
            remove_script_from_menu(
                desktop_object=desktop_object,
                name=toolkit_info["name"],
                product=product_name,
            )
            desktop_object.logger.info(f"{toolkit_info['name']} uninstalled")


def remove_script_from_menu(desktop_object, name, product="Project"):
    """Remove a toolkit script from the menu.

    Parameters
    ----------
    desktop_object : :class:ansys.aedt.core.desktop.Desktop
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
    product = tab_map(product)
    toolkit_dir = Path(desktop_object.personallib) / "Toolkits"
    aedt_version = desktop_object.aedt_version_id
    tool_dir = toolkit_dir / product / name

    # Check if extension exists in panel before attempting removal
    if aedt_version >= "2023.2":
        remove_xml_tab(toolkit_dir, product, name)

    shutil.rmtree(str(tool_dir), ignore_errors=True)
    desktop_object.logger.info(f"{name} extension removed successfully.")
    return True


def __exe():
    if not is_linux:
        return ".exe"
    return ""


def get_custom_extensions_from_tabconfig(tabconfig_path, toml_names, options, logger=None):
    """Add custom extensions from TabConfig.xml not in TOML."""
    try:
        tree = defused_parse(str(tabconfig_path))
        root = tree.getroot()
        for panel in root.findall("./panel"):
            for button in panel.findall("./button"):
                label = button.attrib.get("label")
                is_custom = button.attrib.get("custom_extension", "false").lower() == "true"
                if label and is_custom and label not in toml_names and label not in options:
                    options[label] = label
    except Exception as e:
        if logger:
            logger.warning(f"Failed to parse {tabconfig_path}: {e}")
    return options


def get_custom_extension_script(tabconfig_path, label, logger=None):
    """Get script path for a custom extension from TabConfig.xml."""
    try:
        tree = defused_parse(str(tabconfig_path))
        root = tree.getroot()
        for panel in root.findall("./panel"):
            for button in panel.findall("./button"):
                btn_label = button.attrib.get("label")
                is_custom = button.attrib.get("custom_extension", "false").lower() == "true"
                if btn_label == label and is_custom:
                    script_field = button.attrib.get("script", None)
                    return script_field
    except Exception as e:
        if logger:
            logger.warning(f"Failed to parse {tabconfig_path}: {e}")
    return None


def get_custom_extension_image(tabconfig_path, label, logger=None):
    """Get image path for a custom extension from TabConfig.xml."""
    try:
        tree = defused_parse(str(tabconfig_path))
        root = tree.getroot()
        for panel in root.findall("./panel"):
            for button in panel.findall("./button"):
                btn_label = button.attrib.get("label")
                if btn_label == label:
                    return button.attrib.get("image", "")
    except Exception as e:
        if logger:
            logger.warning(f"Failed to parse {tabconfig_path}: {e}")
    return ""
