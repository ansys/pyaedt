# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from __future__ import annotations

import logging
import os
from pathlib import Path
import re
import shutil
import subprocess  # nosec
import sys
import warnings

import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.tabconfig_parser import ButtonSpec
from ansys.aedt.core.extensions.tabconfig_parser import TabConfigParser
import ansys.aedt.core.extensions.templates
from ansys.aedt.core.generic.aedt_constants import DesignType
from ansys.aedt.core.generic.file_utils import read_toml
from ansys.aedt.core.generic.settings import is_linux

AEDT_APPLICATIONS = {
    "circuit": "CircuitDesign",
    "emit": "EMIT",
    "hfss": "HFSS",
    "hfss3dlayout": "HFSS3DLayoutDesign",
    "icepak": "Icepak",
    "maxwell2d": "Maxwell2D",
    "maxwell3d": "Maxwell3D",
    "mechanical": DesignType.ICEPAKFEA.NAME,
    "common": "Project",
    "q2d": "2DExtractor",
    "q3d": "Q3DExtractor",
    "twinbuilder": "TwinBuilder",
}


def _iter_panel_button_specs(parser: TabConfigParser, panel_label: str | None = None):
    for panel_spec in parser.to_model():
        if panel_label and panel_spec.label != panel_label:
            continue
        yield from panel_spec.buttons
        for gallery in panel_spec.galleries:
            if gallery.header_button:
                yield gallery.header_button
            for group in gallery.groups:
                yield from group.buttons


def _safe_parse_tabconfig(tabconfig_path, logger=None):
    try:
        return TabConfigParser(tabconfig_path)
    except Exception as exc:
        if logger:
            logger.warning(f"Failed to parse {tabconfig_path}: {exc}")
        return None


def add_automation_tab(
    name: str,
    lib_dir,
    icon_file=None,
    product: str = "Project",
    template: str = "Run PyAEDT Toolkit Script",
    overwrite: bool = False,
    panel: str = "Panel_PyAEDT_Extensions",
    is_custom: bool = False,  # new argument for custom flagº
    odesktop: object = None,
    group_name: str | None = None,
    group_icon: str | None = None,
    gallery_imagewidth: int = 80,
    gallery_imageheight: int = 72,
):
    """Add an automation tab in AEDT.

    Parameters
    ----------
    name : str
        Toolkit name to add.
    lib_dir : str
        Path to the library directory.
    icon_file : str
        Full path to the icon file. The default is the PyAnsys icon.
    product : str, optional
        Product directory to install the toolkit.
    template : str, optional
        Script template name to use.
    overwrite : bool, optional
        Whether to overwrite the existing automation tab. The default is ``False``, in
        which case is adding new tabs to the existing ones.
    panel : str, optional
        Panel name. The default is ``"Panel_PyAEDT_Extensions"``.
    is_custom : bool, optional
        Whether the automation tab is for custom extensions. The default is ``False``.
    group_name : str, optional
        Group name to create grouped buttons. The default is ``None``.
    group_icon : str, optional
        Group icon to use when creating grouped buttons. The default is ``None``.
    gallery_imagewidth : int, optional
        Gallery image width when creating grouped buttons. The default is ``32``.
    gallery_imageheight : int, optional
        Gallery image height when creating grouped buttons. The default is ``32``.
    odesktop : oDesktop, optional
        Desktop session. The default is ``None``.

    Returns
    -------
    str
        Automation tab path.
    """
    product = tab_map(product)
    lib_dir = Path(lib_dir)
    tab_config_file_path = lib_dir / product / "TabConfig.xml"
    parser = TabConfigParser()
    if tab_config_file_path.is_file() and not overwrite:
        try:
            parser.load(tab_config_file_path)
        except ValueError as e:  # pragma: no cover
            warnings.warn(f"Unable to parse {tab_config_file_path}\nError received = {str(e)}")
            return
    parser.ensure_panel(panel)
    parser.remove_button(panel, name)

    default_icon_path = Path(ansys.aedt.core.extensions.__file__).parent / "images" / "large" / "pyansys.png"

    if not is_custom and is_linux:  # pragma: no cover
        images_source = Path(ansys.aedt.core.extensions.__file__).parent / "installer" / "images" / "large"
        images_target = lib_dir / product / "images"
        if not images_target.exists() and images_source.exists():
            try:
                images_target.symlink_to(images_source)
            except Exception:
                logging.getLogger("Global").warning(f"Could not create symlink from {images_source} to {images_target}")
                if odesktop:
                    odesktop.AddMessage(
                        "", "", 0, str(f"Could not create symlink from {images_source} to {images_target}")
                    )

    def _resolve_image_path(path_value: Path | None, is_group_icon: bool = False) -> str | None:
        if not path_value:
            return None
        if is_linux and not is_custom and is_group_icon:
            return f"images/gallery/{path_value.name}"
        elif is_linux and not is_custom:
            return f"images/{path_value.name}"
        return path_value.as_posix()

    if group_name:
        icon_path = Path(icon_file) if icon_file else default_icon_path
        image_value = _resolve_image_path(icon_path)
        group_icon_path = Path(group_icon) if group_icon else None
        if group_icon_path is None:
            raise TypeError("Group icon is required when group_name is provided.")
        group_image_value = _resolve_image_path(group_icon_path, is_group_icon=True)
        gallery_button_attrs = {}
        if group_image_value:
            gallery_button_attrs["image"] = image_value
        gallery_button = (
            ButtonSpec(group_name, gallery_button_attrs) if gallery_button_attrs else ButtonSpec(group_name)
        )
        if is_custom:
            script = Path(name) / "run_pyaedt_toolkit_script"
            button_kwargs = {
                "script": str(script.as_posix()),
                "custom_extension": "true",
                "type": "custom",
            }
        else:
            toolkit_name = name.replace("/", "_")
            button_kwargs = {
                "script": f"{toolkit_name}/{template}",
            }
        parser.add_group_button(
            panel_label=panel,
            group_label=group_name,
            button=ButtonSpec(name, button_kwargs),
            group_image=group_image_value,
            gallery_button=gallery_button,
            imagewidth=gallery_imagewidth,
            imageheight=gallery_imageheight,
        )
    else:
        if is_custom:
            icon_path = Path(icon_file) if icon_file else default_icon_path
            script = Path(name) / "run_pyaedt_toolkit_script"
            button_kwargs = {
                "isLarge": "1",
                "image": str(icon_path.as_posix()),
                "script": str(script.as_posix()),
                "custom_extension": "true",
                "type": "custom",
            }
        else:
            icon_path = Path(icon_file) if icon_file else default_icon_path
            image_value = _resolve_image_path(icon_path)
            toolkit_name = name.replace("/", "_")
            button_kwargs = {
                "isLarge": "1",
                "image": image_value,
                "script": f"{toolkit_name}/{template}",
            }
        parser.add_button(panel, ButtonSpec(name, button_kwargs))
    # Backup any existing file if present
    if tab_config_file_path.is_file():
        shutil.copy(str(tab_config_file_path), str(tab_config_file_path) + ".orig")
    parser.save(tab_config_file_path)
    return str(tab_config_file_path)


def is_extension_in_panel(toolkit_dir, product, name: str, panel: str = "Panel_PyAEDT_Extensions") -> bool:
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
        parser = TabConfigParser(tab_config_file_path)
    except (FileNotFoundError, ValueError) as e:  # pragma: no cover
        warnings.warn("Unable to parse %s\nError received = %s" % (tab_config_file_path, str(e)))
        return False
    return parser.has_button(panel, name)


def available_toolkits():
    product_toolkits = {}
    for product_extension, product_name in AEDT_APPLICATIONS.items():
        toml_file = Path(__file__).parent / product_extension / "toolkits_catalog.toml"
        if toml_file.is_file():
            toolkits_catalog = read_toml(str(toml_file))
            product_toolkits[str(product_name)] = toolkits_catalog
    return product_toolkits


def add_script_to_menu(
    name: str,
    script_file=None,
    template_file: str = "run_pyaedt_toolkit_script",
    icon_file=None,
    product: str = "Project",
    copy_to_personal_lib: bool = True,
    panel: str = "Panel_PyAEDT_Extensions",
    personal_lib=None,
    is_custom: bool = False,
    odesktop=None,
    group_name: str | None = None,
    group_icon=None,
) -> bool:
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
    panel : str, optional
        Panel name. The default is ``"Panel_PyAEDT_Extensions"``.
    personal_lib : str, optional
    is_custom : bool, optional
    odesktop : oDesktop, optional
    group_name : str, optional
        Group name to create grouped buttons. The default is ``None``.
    group_icon : str, optional
        Group icon to use when creating grouped buttons. The default is ``None``.

    Returns
    -------
    bool

    """
    logger = logging.getLogger("Global")
    if not personal_lib:
        from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

        if not _desktop_sessions:  # pragma: no cover
            logger.error("Personallib is not provided. There is no available desktop session.")
            return False
        d = list(_desktop_sessions.values())[0]
        personal_lib = d.personallib

    if script_file and not Path(script_file).exists():  # pragma: no cover
        logger.error("Script does not exist.")
        return False
    toolkit_dir = Path(personal_lib) / "Toolkits"
    tool_map = tab_map(product)
    file_name = name
    if "/" in file_name:  # pragma: no cover
        file_name = file_name.replace("/", "_")
    tool_dir = toolkit_dir / tool_map / file_name
    lib_dir = tool_dir / "Lib"
    if copy_to_personal_lib:
        lib_dir.mkdir(parents=True, exist_ok=True)
    tool_dir.mkdir(parents=True, exist_ok=True)
    dest_script_path = script_file
    if script_file and copy_to_personal_lib:
        dest_script_path = lib_dir / Path(script_file).name
        shutil.copy2(script_file, str(dest_script_path))

    templates_dir = Path(ansys.aedt.core.extensions.templates.__file__).parent

    executable_interpreter = sys.executable
    if is_linux:
        ipython_executable = re.sub(
            r"python3" + __exe() + r"$",
            "ipython" + __exe(),
            executable_interpreter,
        )
        jupyter_executable = re.sub(
            r"python3" + __exe() + r"$",
            "jupyter" + __exe(),
            executable_interpreter,
        )
    else:
        ipython_executable = re.sub(
            r"python" + __exe() + r"$",
            "ipython" + __exe(),
            executable_interpreter,
        )
        jupyter_executable = re.sub(
            r"python" + __exe() + r"$",
            "jupyter" + __exe(),
            executable_interpreter,
        )

    with open(templates_dir / (template_file + ".py_build"), "r") as build_file:
        build_file_data = build_file.read()
        # Ensure replacement values are strings
        build_file_data = build_file_data.replace("##IPYTHON_EXE##", str(ipython_executable))
        build_file_data = build_file_data.replace("##PYTHON_EXE##", str(executable_interpreter))
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
        with open(tool_dir / (template_file + ".py"), "w") as out_file:
            out_file.write(build_file_data)
    names = name
    icons = icon_file
    templates = template_file

    add_automation_tab(
        names,
        toolkit_dir,
        icon_file=icons,
        product=product,
        template=templates,
        panel=panel,
        is_custom=is_custom,
        odesktop=odesktop,
        group_name=group_name,
        group_icon=group_icon,
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
    elif product.lower() == "common":
        return "Project"
    else:
        return product


def run_command(command: list[str], desktop_object):  # pragma: no cover
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


def add_custom_toolkit(desktop_object, toolkit_name, wheel_toolkit=None, install: bool = True):  # pragma: no cover
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
        pip_exe = venv_dir.joinpath("Scripts", "pip.exe")
        package_dir = venv_dir.joinpath("Lib")
    else:
        venv_dir = Path(os.environ["HOME"]).joinpath(
            ".pyaedt_env",
            f"toolkits_{python_version_new}",
        )
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
                personal_lib=desktop_object.personallib,
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


def remove_script_from_menu(desktop_object, name: str, product: str = "Project") -> bool:
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
    tab_config_file_path = Path(toolkit_dir) / tab_map(product) / "TabConfig.xml"
    # Check if extension exists in panel before attempting removal
    if aedt_version >= "2023.2":
        parser = _safe_parse_tabconfig(tab_config_file_path, logger=desktop_object.logger)
        if parser and parser.has_button(panel_label="Panel_PyAEDT_Extensions", label=name):
            parser.remove_button(panel_label="Panel_PyAEDT_Extensions", label=name)
        elif not parser:
            return False
    parser.save(tab_config_file_path)
    shutil.rmtree(str(tool_dir), ignore_errors=True)
    desktop_object.logger.info(f"{name} extension removed successfully.")
    return True


def __exe() -> str:
    if not is_linux:
        return ".exe"
    return ""


def get_custom_extensions_from_tabconfig(tabconfig_path, toml_names, options, logger=None):
    """Add custom extensions from TabConfig.xml not in TOML."""
    parser = _safe_parse_tabconfig(tabconfig_path, logger=logger)
    if not parser:
        return options
    for button in _iter_panel_button_specs(parser):
        is_custom = button.attributes.get("custom_extension", "false").lower() == "true"
        if button.label and is_custom and button.label not in toml_names and button.label not in options:
            options[button.label] = button.label
    return options


def get_custom_extension_script(tabconfig_path, label, logger=None):
    """Get script path for a custom extension from TabConfig.xml."""
    parser = _safe_parse_tabconfig(tabconfig_path, logger=logger)
    if not parser:
        return None
    for button in _iter_panel_button_specs(parser):
        is_custom = button.attributes.get("custom_extension", "false").lower() == "true"
        if button.label == label and is_custom:
            return button.attributes.get("script", None)
    return None


def get_custom_extension_image(tabconfig_path, label, logger=None):
    """Get image path for a custom extension from TabConfig.xml."""
    parser = _safe_parse_tabconfig(tabconfig_path, logger=logger)
    if not parser:
        return ""
    for button in _iter_panel_button_specs(parser):
        if button.label == label:
            return button.attributes.get("image", "")
    return ""
