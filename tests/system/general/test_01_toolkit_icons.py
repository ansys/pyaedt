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

import os

import defusedxml.ElementTree as ET
import defusedxml.minidom

defusedxml.defuse_stdlib()


from ansys.aedt.core.workflows.customize_automation_tab import add_automation_tab
import pytest


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_00_write_new_xml(self):
        file_path = add_automation_tab(name="Test", lib_dir=self.local_scratch.path)
        root = self.validate_file_exists_and_pyaedt_tabs_added(file_path)
        panels = root.findall("./panel")
        panel_names = [panel.attrib["label"] for panel in panels]
        assert len(panel_names) == 1

    def test_01_add_pyaedt_config_to_existing_existing_xml(self):
        """
        First write a dummy XML with a different Panel and then add PyAEDT's tabs
        :return:
        """
        file_path = os.path.join(self.local_scratch.path, "Project", "TabConfig.xml")
        with open(file_path, "w") as fid:
            fid.write(
                """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<TabConfig>
    <panel label="Panel_1">
        <gallery imagewidth="32" imageheight="32">
            <button label="Dummy1" />
            <group label="Dummy1">
                <button label="Dummy 1" script="ScriptDir/Dummy1" />
                <button label="Dummy 2" script="ScriptDir/Dummy2" />
            </group>
        </gallery>
    </panel>
</TabConfig>
"""
            )

        file_path = add_automation_tab(name="Test", lib_dir=self.local_scratch.path)
        root = self.validate_file_exists_and_pyaedt_tabs_added(file_path)
        panels = root.findall("./panel")
        panel_names = [panel.attrib["label"] for panel in panels]
        assert len(panel_names) == 2
        assert "Panel_1" in panel_names

    def test_03_overwrite_existing_pyaedt_config(self):
        file_path = os.path.join(self.local_scratch.path, "Project", "TabConfig.xml")
        with open(file_path, "w") as fid:
            fid.write(
                """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<TabConfig>
    <panel label="Panel_PyAEDT">
        <gallery imagewidth="32" imageheight="32">
            <button label="Dummy1" />
            <group label="Dummy1">
                <button label="Dummy 1" script="ScriptDir/Dummy1" />
                <button label="Dummy 2" script="ScriptDir/Dummy2" />
            </group>
        </gallery>
    </panel>
</TabConfig>
"""
            )
        file_path = add_automation_tab(name="Test", lib_dir=self.local_scratch.path)
        root = self.validate_file_exists_and_pyaedt_tabs_added(file_path)
        panels = root.findall("./panel")
        panel_names = [panel.attrib["label"] for panel in panels]
        assert len(panel_names) == 2

    def test_04_write_to_existing_file_but_no_panels(self):
        file_path = os.path.join(self.local_scratch.path, "Project", "TabConfig.xml")
        with open(file_path, "w") as fid:
            fid.write(
                """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<TabConfig>
    <junk label="Junk_1" />
</TabConfig>
"""
            )
        file_path = add_automation_tab(name="Test", lib_dir=self.local_scratch.path)
        root = self.validate_file_exists_and_pyaedt_tabs_added(file_path)
        junks = root.findall("./junk")
        junk_names = [junk.attrib["label"] for junk in junks]
        assert junk_names[0] == "Junk_1"
        assert len(junks) == 1
        panels = root.findall("./panel")
        panel_names = [panel.attrib["label"] for panel in panels]
        assert len(panel_names) == 1

    @staticmethod
    def validate_file_exists_and_pyaedt_tabs_added(file_path):
        assert os.path.isfile(file_path) is True
        assert ET.parse(file_path) is not None
        tree = ET.parse(file_path)
        root = tree.getroot()
        panels = root.findall("./panel")
        panel_names = [panel.attrib["label"] for panel in panels]
        assert "Panel_PyAEDT_Extensions" in panel_names
        return root
