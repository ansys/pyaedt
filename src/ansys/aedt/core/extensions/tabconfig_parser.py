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

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET  # nosec

from defusedxml.ElementTree import ParseError
from defusedxml.ElementTree import parse as defused_parse
import defusedxml.minidom
from defusedxml.minidom import parseString

defusedxml.defuse_stdlib()


@dataclass
class ButtonSpec:
    """Button definition for TabConfig.xml.

    Parameters
    ----------
    label : str
        Button label.
    attributes : dict
        Optional extra attributes (script, image, tooltip, isLarge, ...).
    """

    label: str
    attributes: dict[str, str] = field(default_factory=dict)

    def to_element(self) -> ET.Element:
        attrs = {"label": self.label}
        attrs.update(self.attributes)
        return ET.Element("button", attrs)

    @classmethod
    def from_element(cls, element: ET.Element) -> "ButtonSpec":
        attrs = dict(element.attrib)
        label = attrs.pop("label", "")
        return cls(label=label, attributes=attrs)


@dataclass
class GroupSpec:
    """Group definition inside a gallery."""

    label: str
    image: str | None = None
    buttons: list[ButtonSpec] = field(default_factory=list)

    def to_element(self) -> ET.Element:
        attrs = {"label": self.label}
        if self.image:
            attrs["image"] = self.image
        group_el = ET.Element("group", attrs)
        for button in self.buttons:
            group_el.append(button.to_element())
        return group_el

    @classmethod
    def from_element(cls, element: ET.Element) -> "GroupSpec":
        label = element.attrib.get("label", "")
        image = element.attrib.get("image")
        buttons = [ButtonSpec.from_element(btn) for btn in element.findall("./button")]
        return cls(label=label, image=image, buttons=buttons)


@dataclass
class GallerySpec:
    """Gallery definition containing a header button and grouped buttons."""

    imagewidth: int = 120
    imageheight: int = 72
    header_button: ButtonSpec | None = None
    groups: list[GroupSpec] = field(default_factory=list)

    def to_element(self) -> ET.Element:
        attrs = {"imagewidth": str(self.imagewidth), "imageheight": str(self.imageheight)}
        gallery_el = ET.Element("gallery", attrs)
        if self.header_button:
            gallery_el.append(self.header_button.to_element())
        for group in self.groups:
            gallery_el.append(group.to_element())
        return gallery_el

    @classmethod
    def from_element(cls, element: ET.Element) -> "GallerySpec":
        imagewidth = int(element.attrib.get("imagewidth", "120"))
        imageheight = int(element.attrib.get("imageheight", "72"))
        header_button = None
        header_el = element.find("./button")
        if header_el is not None:
            header_button = ButtonSpec.from_element(header_el)
        groups = [GroupSpec.from_element(grp) for grp in element.findall("./group")]
        return cls(
            imagewidth=imagewidth,
            imageheight=imageheight,
            header_button=header_button,
            groups=groups,
        )


@dataclass
class PanelSpec:
    """Panel definition with direct buttons and galleries."""

    label: str
    buttons: list[ButtonSpec] = field(default_factory=list)
    galleries: list[GallerySpec] = field(default_factory=list)

    def to_element(self) -> ET.Element:
        panel_el = ET.Element("panel", {"label": self.label})
        for button in self.buttons:
            panel_el.append(button.to_element())
        for gallery in self.galleries:
            panel_el.append(gallery.to_element())
        return panel_el

    @classmethod
    def from_element(cls, element: ET.Element) -> "PanelSpec":
        label = element.attrib.get("label", "")
        buttons = [ButtonSpec.from_element(btn) for btn in element.findall("./button")]
        galleries = [GallerySpec.from_element(gal) for gal in element.findall("./gallery")]
        return cls(label=label, buttons=buttons, galleries=galleries)


class TabConfigParser:
    """Parser for AEDT TabConfig.xml with add/remove/insert support.

    The supported structure is:
        TabConfig -> panel -> button
        TabConfig -> panel -> gallery -> button -> group -> button

    Examples
    --------
    >>> parser = TabConfigParser("C:/Path/TabConfig.xml")
    >>> parser.add_button("Panel_1", ButtonSpec("New Button", {"script": "X/Y"}))
    >>> parser.add_group_button(
    ...     "Panel_2",
    ...     group_label="Heatsink",
    ...     button=ButtonSpec("Heatsink Creation", {"script": "Geometry/Heatsinks/Heatsink_Creation"}),
    ... )
    >>> parser.save()
    """

    def __init__(self, xml_path: str | Path | None = None) -> None:
        self._path: Path | None = None
        self._root: ET.Element = ET.Element("TabConfig")
        if xml_path:
            self.load(xml_path)

    @property
    def root(self) -> ET.Element:
        return self._root

    @property
    def path(self) -> Path | None:
        return self._path

    def load(self, xml_path: str | Path) -> None:
        path = Path(xml_path)
        if not path.is_file():
            raise FileNotFoundError(f"TabConfig.xml not found: {path}")
        try:
            tree = defused_parse(str(path))
        except ParseError as exc:
            raise ValueError(f"Unable to parse {path}: {exc}") from exc
        self._root = tree.getroot()
        self._path = path

    def save(self, xml_path: str | Path | None = None) -> Path:
        if xml_path:
            self._path = Path(xml_path)
        if not self._path:
            raise ValueError("No output path provided for TabConfig.xml")
        lines = [
            line
            for line in parseString(ET.tostring(self._root)).toprettyxml(indent=" " * 4).split("\n")
            if line.strip()
        ]
        xml_str = "\n".join(lines)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(xml_str, encoding="utf-8")
        return self._path

    def list_panels(self) -> list[str]:
        return [panel.attrib.get("label", "") for panel in self._root.findall("./panel")]

    def get_panel(self, panel_label: str) -> ET.Element | None:
        for panel in self._root.findall("./panel"):
            if panel.attrib.get("label") == panel_label:
                return panel
        return None

    def ensure_panel(self, panel_label: str) -> ET.Element:
        panel = self.get_panel(panel_label)
        if panel is None:
            panel = ET.SubElement(self._root, "panel", label=panel_label)
        return panel

    def add_panel(self, panel: PanelSpec) -> ET.Element:
        existing = self.get_panel(panel.label)
        if existing is not None:
            self._root.remove(existing)
        panel_el = panel.to_element()
        self._root.append(panel_el)
        return panel_el

    def remove_panel(self, panel_label: str) -> bool:
        panel = self.get_panel(panel_label)
        if panel is None:
            return False
        self._root.remove(panel)
        return True

    def add_button(
        self,
        panel_label: str,
        button: ButtonSpec,
        index: int | None = None,
        after_label: str | None = None,
    ) -> ET.Element:
        panel = self.ensure_panel(panel_label)
        self._remove_button_from_panel(panel, button.label)
        button_el = button.to_element()
        return self._insert_element(panel, button_el, index=index, after_label=after_label)

    def remove_button(self, panel_label: str, label: str) -> bool:
        panel = self.get_panel(panel_label)
        if panel is None:
            return False
        return self._remove_button_from_panel(panel, label)

    def remove_button_anywhere(self, panel_label: str, label: str) -> bool:
        panel = self.get_panel(panel_label)
        if panel is None:
            return False
        button, parent, gallery = self._find_button_with_parents(panel, label)
        if not button:
            return False
        parent.remove(button)
        if parent.tag == "group" and not parent.findall("./button"):
            if gallery is not None:
                gallery.remove(parent)
        if parent.tag == "gallery" and not parent.findall("./button") and not parent.findall("./group"):
            panel.remove(parent)
        if parent.tag == "group" and gallery is not None:
            if not gallery.findall("./button") and not gallery.findall("./group"):
                panel.remove(gallery)
        return True

    def add_gallery_group(
        self,
        panel_label: str,
        group_label: str,
        group_image: str | None,
        gallery_button: ButtonSpec | None = None,
        imagewidth: int = 120,
        imageheight: int = 72,
    ) -> tuple[ET.Element, ET.Element]:
        panel = self.ensure_panel(panel_label)
        group_el, gallery_el = self._find_group(panel, group_label)
        if gallery_el is None:
            gallery_el = ET.SubElement(
                panel,
                "gallery",
                imagewidth=str(imagewidth),
                imageheight=str(imageheight),
            )
        else:
            gallery_el.set("imagewidth", str(imagewidth))
            gallery_el.set("imageheight", str(imageheight))
        if gallery_button is not None:
            header_btn = gallery_el.find("./button")
            if header_btn is None:
                gallery_el.insert(0, gallery_button.to_element())
            else:
                gallery_el.remove(header_btn)
                gallery_el.insert(0, gallery_button.to_element())
        if group_el is None:
            attrs = {"label": group_label}
            if group_image:
                attrs["image"] = group_image
            group_el = ET.SubElement(gallery_el, "group", **attrs)
        elif group_image:
            group_el.set("image", group_image)
        return group_el, gallery_el

    def add_group_button(
        self,
        panel_label: str,
        group_label: str,
        button: ButtonSpec,
        group_image: str | None = None,
        gallery_button: ButtonSpec | None = None,
        imagewidth: int = 120,
        imageheight: int = 72,
        index: int | None = None,
        after_label: str | None = None,
    ) -> ET.Element:
        group_el, _ = self.add_gallery_group(
            panel_label=panel_label,
            group_label=group_label,
            group_image=group_image,
            gallery_button=gallery_button,
            imagewidth=imagewidth,
            imageheight=imageheight,
        )
        self._remove_button_from_group(group_el, button.label)
        button_el = button.to_element()
        return self._insert_element(group_el, button_el, index=index, after_label=after_label)

    def remove_group_button(self, panel_label: str, group_label: str, label: str) -> bool:
        panel = self.get_panel(panel_label)
        if panel is None:
            return False
        group_el, gallery_el = self._find_group(panel, group_label)
        if group_el is None:
            return False
        removed = self._remove_button_from_group(group_el, label)
        self._cleanup_group_and_gallery(panel, group_el, gallery_el)
        return removed

    def remove_group(self, panel_label: str, group_label: str) -> bool:
        panel = self.get_panel(panel_label)
        if panel is None:
            return False
        group_el, gallery_el = self._find_group(panel, group_label)
        if group_el is None:
            return False
        if gallery_el is not None:
            gallery_el.remove(group_el)
            if not list(gallery_el):
                panel.remove(gallery_el)
        return True

    def to_model(self) -> list[PanelSpec]:
        return [PanelSpec.from_element(panel) for panel in self._root.findall("./panel")]

    def _find_group(self, panel_el: ET.Element, group_label: str) -> tuple[ET.Element | None, ET.Element | None]:
        for gallery in panel_el.findall("./gallery"):
            for group in gallery.findall("./group"):
                if group.attrib.get("label") == group_label:
                    return group, gallery
        return None, None

    def _find_button_with_parents(self, panel_el: ET.Element, label: str):
        for child in list(panel_el):
            if child.tag == "button" and child.attrib.get("label") == label:
                return child, panel_el, None
            if child.tag == "gallery":
                for gallery_child in list(child):
                    if gallery_child.tag == "button" and gallery_child.attrib.get("label") == label:
                        return gallery_child, child, None
                    if gallery_child.tag == "group":
                        for group_child in list(gallery_child):
                            if group_child.tag == "button" and group_child.attrib.get("label") == label:
                                return group_child, gallery_child, child
        return None, None, None

    def _remove_button_from_panel(self, panel_el: ET.Element, label: str) -> bool:
        for child in list(panel_el):
            if child.tag == "button" and child.attrib.get("label") == label:
                panel_el.remove(child)
                return True
        return False

    def _remove_button_from_group(self, group_el: ET.Element, label: str) -> bool:
        for child in list(group_el):
            if child.tag == "button" and child.attrib.get("label") == label:
                group_el.remove(child)
                return True
        return False

    def _cleanup_group_and_gallery(
        self,
        panel_el: ET.Element,
        group_el: ET.Element,
        gallery_el: ET.Element | None,
    ) -> None:
        if gallery_el is None:
            return
        if group_el.tag == "group" and not group_el.findall("./button"):
            gallery_el.remove(group_el)
        has_group = bool(gallery_el.findall("./group"))
        has_button = bool(gallery_el.findall("./button"))
        if not has_group and not has_button:
            panel_el.remove(gallery_el)

    def _insert_element(
        self,
        parent: ET.Element,
        element: ET.Element,
        index: int | None = None,
        after_label: str | None = None,
    ) -> ET.Element:
        children = list(parent)
        if after_label:
            for idx, child in enumerate(children):
                if child.attrib.get("label") == after_label:
                    parent.insert(idx + 1, element)
                    return element
        if index is None or index >= len(children):
            parent.append(element)
        else:
            parent.insert(index, element)
        return element

    def add_buttons(self, panel_label: str, buttons: Iterable[ButtonSpec]) -> None:
        for button in buttons:
            self.add_button(panel_label, button)
