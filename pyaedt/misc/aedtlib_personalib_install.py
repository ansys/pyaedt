import os
import shutil
import sys
import warnings
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from xml.etree.ElementTree import ParseError

current_dir = os.path.dirname(os.path.realpath(__file__))
pyaedt_path = os.path.join(
    current_dir,
    "..",
)
sys.path.append(os.path.join(pyaedt_path, ".."))

if len(sys.argv) < 2:
    version = "2021.2"
else:
    v = sys.argv[1]
    version = "20" + v[-3:-1] + "." + v[-1:]

pid = 0


def main():
    from pyaedt import Desktop

    with Desktop(version, True, new_desktop_session=True) as d:
        desktop = sys.modules["__main__"].oDesktop
        pers1 = os.path.join(desktop.GetPersonalLibDirectory(), "pyaedt")
        pid = desktop.GetProcessID()
        if os.path.exists(pers1):
            d.logger.info("PersonalLib already mapped")
        else:
            os.system('mklink /D "{}" "{}"'.format(pers1, pyaedt_path))

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
        with open(os.path.join(current_dir, file_name + ".py_build"), "r") as build_file:
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
    shutil.copyfile(os.path.join(current_dir, "console_setup"), os.path.join(lib_dir, "console_setup.py"))
    shutil.copyfile(
        os.path.join(current_dir, "jupyter_template.ipynb"),
        os.path.join(lib_dir, "jupyter_template.ipynb"),
    )
    if version >= "2023.2":
        write_tab_config(os.path.join(toolkit_dir, product), lib_dir)


def write_tab_config(product_toolkit_dir, pyaedt_lib_dir, force_write=False):
    tab_config_file_path = os.path.join(product_toolkit_dir, "TabConfig.xml")
    if not os.path.isfile(tab_config_file_path) or force_write:
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
        if "Panel_PyAEDT" in panel_names:
            # Remove previously existing PyAEDT panel and update with newer one.
            panel = [panel for panel in panels if panel.attrib["label"] == "Panel_PyAEDT"][0]
            root.remove(panel)

    # Write a new "Panel_PyAEDT" sub-element.
    panel = ET.SubElement(root, "panel", label="Panel_PyAEDT")
    gallery = ET.SubElement(panel, "gallery", imagewidth="32", imageheight="32")
    image_rel_path = os.path.relpath(pyaedt_lib_dir, product_toolkit_dir).replace("\\", "/") + "/"
    if image_rel_path == "./":
        image_rel_path = ""
    ET.SubElement(gallery, "button", label="PyAEDT", isLarge="1", image=image_rel_path + "images/large/pyansys.png")
    group = ET.SubElement(gallery, "group", label="PyAEDT", image=image_rel_path + "images/gallery/PyAEDT.png")
    ET.SubElement(group, "button", label="Console", script="PyAEDT/Console")
    ET.SubElement(group, "button", label="Jupyter Notebook", script="PyAEDT/Jupyter")
    ET.SubElement(group, "button", label="Run PyAEDT Script", script="PyAEDT/Run PyAEDT Script")

    # Backup any existing file if present
    if os.path.isfile(tab_config_file_path):
        shutil.copy(tab_config_file_path, tab_config_file_path + ".orig")

    write_pretty_xml(root, tab_config_file_path)

    files_to_copy = ["images/large/pyansys.png", "images/gallery/PyAEDT.png"]
    for file_name in files_to_copy:
        dest_file = os.path.normpath(os.path.join(pyaedt_lib_dir, file_name))
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        shutil.copy(os.path.normpath(os.path.join(current_dir, file_name)), dest_file)


def write_pretty_xml(root, file_path):
    """Write the XML in a pretty format."""
    # If we use the commented code below, then the previously existing lines will have double lines added. We need to
    # split and ignore the double lines.
    # xml_str = parseString(ET.tostring(root)).toprettyxml(indent=" " * 4)
    lines = [line for line in parseString(ET.tostring(root)).toprettyxml(indent=" " * 4).split("\n") if line.strip()]
    xml_str = "\n".join(lines)

    with open(file_path, "w") as f:
        f.write(xml_str)


if __name__ == "__main__":
    main()
