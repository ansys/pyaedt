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

from pathlib import Path

import pytest

from ansys.aedt.core.extensions.tabconfig_parser import ButtonSpec
from ansys.aedt.core.extensions.tabconfig_parser import GallerySpec
from ansys.aedt.core.extensions.tabconfig_parser import GroupSpec
from ansys.aedt.core.extensions.tabconfig_parser import PanelSpec
from ansys.aedt.core.extensions.tabconfig_parser import TabConfigParser


def test_buttonspec_roundtrip() -> None:
    button = ButtonSpec("MyButton", {"script": "My/Script", "image": "icon.png"})
    element = button.to_element()
    restored = ButtonSpec.from_element(element)

    assert element.tag == "button"
    assert restored.label == "MyButton"
    assert restored.attributes["script"] == "My/Script"
    assert restored.attributes["image"] == "icon.png"


def test_groupspec_roundtrip() -> None:
    button = ButtonSpec("GroupButton", {"script": "Group/Script"})
    group = GroupSpec("Group1", image="group.png", buttons=[button])
    element = group.to_element()
    restored = GroupSpec.from_element(element)

    assert element.tag == "group"
    assert restored.label == "Group1"
    assert restored.image == "group.png"
    assert restored.buttons[0].label == "GroupButton"


def test_galleryspec_roundtrip() -> None:
    header = ButtonSpec("Header", {"image": "header.png"})
    group = GroupSpec("Group1", buttons=[ButtonSpec("GroupButton", {"script": "G/Script"})])
    gallery = GallerySpec(imagewidth=80, imageheight=72, header_button=header, groups=[group])
    element = gallery.to_element()
    restored = GallerySpec.from_element(element)

    assert element.tag == "gallery"
    assert restored.imagewidth == 80
    assert restored.imageheight == 72
    assert restored.header_button.label == "Header"
    assert restored.groups[0].label == "Group1"


def test_panelspec_roundtrip() -> None:
    button = ButtonSpec("PanelButton", {"script": "Panel/Script"})
    group = GroupSpec("Group1", buttons=[ButtonSpec("Grouped", {"script": "Group/Script"})])
    gallery = GallerySpec(header_button=ButtonSpec("Header", {}), groups=[group])
    panel = PanelSpec("Panel1", buttons=[button], galleries=[gallery])
    element = panel.to_element()
    restored = PanelSpec.from_element(element)

    assert element.tag == "panel"
    assert restored.label == "Panel1"
    assert restored.buttons[0].label == "PanelButton"
    assert restored.galleries[0].header_button.label == "Header"
    assert restored.galleries[0].groups[0].label == "Group1"


def test_parser_save_and_load(tmp_path: Path) -> None:
    parser = TabConfigParser()
    parser.ensure_panel("Panel1")
    parser.add_button("Panel1", ButtonSpec("Button1", {"script": "One"}))
    path = tmp_path / "TabConfig.xml"

    saved_path = parser.save(path)
    loaded = TabConfigParser(saved_path)

    assert saved_path == path
    assert loaded.list_panels() == ["Panel1"]
    assert loaded.has_button("Panel1", "Button1") is True


def test_parser_save_requires_path() -> None:
    parser = TabConfigParser()
    with pytest.raises(ValueError):
        parser.save()


def test_parser_load_errors(tmp_path: Path) -> None:
    parser = TabConfigParser()
    with pytest.raises(FileNotFoundError):
        parser.load(tmp_path / "missing.xml")

    bad_xml = tmp_path / "bad.xml"
    bad_xml.write_text("<TabConfig><panel>")
    with pytest.raises(ValueError):
        parser.load(bad_xml)


def test_panel_management_methods() -> None:
    parser = TabConfigParser()
    panel = parser.ensure_panel("PanelA")

    assert parser.get_panel("PanelA") == panel
    assert parser.list_panels() == ["PanelA"]

    panel_spec = PanelSpec("PanelA", buttons=[ButtonSpec("B1", {"script": "X"})])
    parser.add_panel(panel_spec)
    assert parser.has_button("PanelA", "B1") is True

    assert parser.remove_panel("Missing") is False
    assert parser.remove_panel("PanelA") is True
    assert parser.get_panel("PanelA") is None


def test_add_button_index_and_after_label() -> None:
    parser = TabConfigParser()
    parser.ensure_panel("Panel")
    parser.add_button("Panel", ButtonSpec("First", {}))
    parser.add_button("Panel", ButtonSpec("Second", {}))
    parser.add_button("Panel", ButtonSpec("Middle", {}), index=1)
    parser.add_button("Panel", ButtonSpec("AfterFirst", {}), after_label="First")

    panel = parser.get_panel("Panel")
    labels = [child.attrib.get("label") for child in list(panel)]
    assert labels == ["First", "AfterFirst", "Middle", "Second"]


def test_remove_button_and_has_button() -> None:
    parser = TabConfigParser()
    parser.ensure_panel("Panel")
    parser.add_button("Panel", ButtonSpec("RemoveMe", {}))

    assert parser.has_button("Panel", "RemoveMe") is True
    assert parser.remove_button("Panel", "RemoveMe") is True
    assert parser.has_button("Panel", "RemoveMe") is False
    assert parser.remove_button("Panel", "Missing") is False


def test_add_gallery_group_updates_header_and_images() -> None:
    parser = TabConfigParser()
    parser.ensure_panel("Panel")
    group_el, gallery_el = parser.add_gallery_group(
        panel_label="Panel",
        group_label="Group",
        group_image="group.png",
        gallery_button=ButtonSpec("Header", {"image": "header.png"}),
        imagewidth=80,
        imageheight=72,
    )

    assert group_el.attrib["label"] == "Group"
    assert group_el.attrib["image"] == "group.png"
    assert gallery_el.attrib["imagewidth"] == "80"
    assert gallery_el.attrib["imageheight"] == "72"
    assert gallery_el.find("./button").attrib["label"] == "Header"

    group_el2, gallery_el2 = parser.add_gallery_group(
        panel_label="Panel",
        group_label="Group",
        group_image="group2.png",
        gallery_button=ButtonSpec("Header2", {"image": "header2.png"}),
        imagewidth=90,
        imageheight=60,
    )

    assert group_el2 is group_el
    assert gallery_el2 is gallery_el
    assert group_el2.attrib["image"] == "group2.png"
    assert gallery_el2.attrib["imagewidth"] == "90"
    assert gallery_el2.attrib["imageheight"] == "60"
    assert gallery_el2.find("./button").attrib["label"] == "Header2"


def test_add_group_button_remove_group_button_cleanup() -> None:
    parser = TabConfigParser()
    parser.ensure_panel("Panel")
    parser.add_group_button(
        panel_label="Panel",
        group_label="Group",
        button=ButtonSpec("Grouped", {"script": "Group/Script"}),
        group_image="group.png",
        gallery_button=ButtonSpec("Header", {}),
    )

    assert parser.has_button("Panel", "Grouped") is True
    assert parser.remove_group_button("Panel", "Group", "Grouped") is True
    assert parser.has_button("Panel", "Grouped") is False
    gallery = parser.get_panel("Panel").find("./gallery")
    assert gallery is not None
    assert gallery.find("./group") is None


def test_remove_group_and_remove_button_anywhere() -> None:
    parser = TabConfigParser()
    parser.ensure_panel("Panel")
    parser.add_group_button(
        panel_label="Panel",
        group_label="Group",
        button=ButtonSpec("Grouped", {"script": "Group/Script"}),
        group_image="group.png",
        gallery_button=ButtonSpec("Header", {}),
    )

    assert parser.remove_group("Panel", "Missing") is False
    assert parser.remove_group("Panel", "Group") is True
    gallery = parser.get_panel("Panel").find("./gallery")
    assert gallery is not None
    assert gallery.find("./group") is None

    parser.add_group_button(
        panel_label="Panel",
        group_label="Group",
        button=ButtonSpec("Grouped", {"script": "Group/Script"}),
        group_image="group.png",
        gallery_button=ButtonSpec("Header", {}),
    )

    assert parser.remove_button_anywhere("Panel", "Grouped") is True
    gallery = parser.get_panel("Panel").find("./gallery")
    assert gallery is not None
    assert gallery.find("./group") is None


def test_add_buttons_and_to_model() -> None:
    parser = TabConfigParser()
    parser.ensure_panel("Panel")
    parser.add_buttons("Panel", [ButtonSpec("A", {}), ButtonSpec("B", {})])

    model = parser.to_model()
    assert model[0].label == "Panel"
    labels = [button.label for button in model[0].buttons]
    assert labels == ["A", "B"]
