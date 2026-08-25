# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from dataclasses import dataclass
from dataclasses import field
import io
import json
import os

from ansys.aedt.core import __version__
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.aedt_constants import DesignType
from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.internal.checks import check_dependency_available
from ansys.aedt.core.internal.checks import requires_graphical_dependency


@dataclass
class ReportSpec(PyAedtBase):
    """Data class containing all report template specifications.

    Examples
    --------
    >>> from ansys.aedt.core.visualization.plot.pdf import ReportSpec
    >>> obj = ReportSpec()

    """

    document_prefix: str = "ANSS"
    """Value for document prefix."""
    ansys_version: str = "2026.1"
    """Value for ansys version."""
    revision: str = "Rev 1.0"
    """Value for revision."""
    logo_name: str = os.path.join(os.path.dirname(__file__), "../../misc/Ansys.png")
    """Value for logo name."""
    company_name: str = "Ansys Inc."
    """Value for company name."""
    template_name: str = os.path.join(os.path.dirname(__file__), "../../misc/AnsysTemplate.json")
    """Value for template name."""
    design_name: str = "Design1"
    """Value for design name."""
    project_name: str = "Project1"
    """Value for project name."""
    pyaedt_version: str = __version__
    """Value for pyaedt version."""
    units: str = "cm"
    """Value for units."""
    top_margin: float = 3.0
    """Value for top margin."""
    bottom_margin: float = 2.0
    """Value for bottom margin."""
    left_margin: float = 1.0
    """Value for left margin."""
    right_margin: float = 1.0
    """Value for right margin."""
    footer_font_size: int = 7
    """Value for footer font size."""
    footer_text: str = "Copyright (c) 2023, ANSYS Inc. unauthorised use, distribution or duplication is prohibited"
    """Value for footer text."""
    header_font_size: int = 7
    """Value for header font size."""
    header_image_width: float = 3.3
    """Value for header image width."""
    title_font_size: int = 14
    """Value for title font size."""
    subtitle_font_size: int = 12
    """Value for subtitle font size."""
    text_font_size: int = 11
    """Value for text font size."""
    table_font_size: int = 9
    """Value for table font size."""
    caption_font_size: int = 9
    """Value for caption font size."""
    cover_title_font_size: int = 28
    """Value for cover title font size."""
    cover_subtitle_font_size: int = 24
    """Value for cover subtitle font size."""
    font: str = "helvetica"
    """Value for font."""
    chart_width: float = 16.0
    """Value for chart width."""
    font_color: list = field(default_factory=lambda: [0, 0, 0])
    """Value for font color."""
    font_chapter_color: list = field(default_factory=lambda: [0, 0, 0])
    """Value for font chapter color."""
    font_subchapter_color: list = field(default_factory=lambda: [0, 0, 0])
    """Value for font subchapter color."""
    font_header_color: list = field(default_factory=lambda: [0, 0, 0])
    """Value for font header color."""
    font_caption_color: list = field(default_factory=lambda: [0, 0, 0])
    """Value for font caption color."""


@dataclass
class _PdfOxideTextBlock:
    text: str
    font_size: int
    color: tuple[int, int, int]
    bold: bool = False
    italic: bool = False
    align: str = "left"
    outline_level: int | None = None
    leading: float = 1.35


@dataclass
class _PdfOxideSpacerBlock:
    lines: int = 1


@dataclass
class _PdfOxideImageBlock:
    path: str | None = None
    image_bytes: bytes | None = None
    caption: str = ""
    width_mm: float | None = None
    height_mm: float | None = None
    max_width_mm: float | None = None
    max_height_mm: float | None = None
    keep_aspect_ratio: bool = False


@dataclass
class _PdfOxideTableBlock:
    title: str
    content: list[list]
    formatting: list | None = None
    col_widths: list | None = None
    full_width: bool = False


@dataclass
class _PdfOxidePage:
    portrait: bool
    page_format: str | tuple[float, float]
    blocks: list = field(default_factory=list)
    kind: str = "content"


def _pdf_oxide_imports():
    check_dependency_available("pdf_oxide")
    from pdf_oxide import DocumentBuilder

    return DocumentBuilder


def _mm_to_pt(value: float) -> float:
    return value * 72.0 / 25.4


def _pt_to_mm(value: float) -> float:
    return value * 25.4 / 72.0


def _page_size_mm(page_format: str | tuple[float, float], portrait: bool) -> tuple[float, float]:
    formats = {
        "a3": (297.0, 420.0),
        "a4": (210.0, 297.0),
        "a5": (148.0, 210.0),
        "letter": (215.9, 279.4),
        "legal": (215.9, 355.6),
    }
    if isinstance(page_format, tuple):
        width_mm, height_mm = page_format
    else:
        key = page_format.lower()
        if key not in formats:
            raise ValueError(f"Unsupported page format '{page_format}'.")
        width_mm, height_mm = formats[key]
    if portrait:
        return min(width_mm, height_mm), max(width_mm, height_mm)
    return max(width_mm, height_mm), min(width_mm, height_mm)


def _font_name(font: str, bold: bool = False, italic: bool = False) -> str:
    base_font = font.lower()
    families = {
        "arial": "Helvetica",
        "helvetica": "Helvetica",
        "times": "Times",
        "times-roman": "Times",
        "courier": "Courier",
    }
    family = families.get(base_font, font)
    if family == "Helvetica":
        if bold and italic:
            return "Helvetica-BoldOblique"
        if bold:
            return "Helvetica-Bold"
        if italic:
            return "Helvetica-Oblique"
        return "Helvetica"
    if family == "Times":
        if bold and italic:
            return "Times-BoldItalic"
        if bold:
            return "Times-Bold"
        if italic:
            return "Times-Italic"
        return "Times-Roman"
    if family == "Courier":
        if bold and italic:
            return "Courier-BoldOblique"
        if bold:
            return "Courier-Bold"
        if italic:
            return "Courier-Oblique"
        return "Courier"
    return font


def _rgb_fraction(
    color: list | tuple | None, default: tuple[float, float, float] = (0.0, 0.0, 0.0)
) -> tuple[float, float, float]:
    if not color:
        return default
    return tuple(channel / 255.0 for channel in color)


def _read_image_bytes(path: str) -> tuple[bytes, int | None, int | None]:
    with open_file(path, "rb") as image_file:
        data = image_file.read()
    try:
        from PIL import Image

        with Image.open(io.BytesIO(data)) as img:
            width_px, height_px = img.size
    except Exception:  # pragma: no cover
        width_px = None
        height_px = None
    return data, width_px, height_px


def _wrap_text_lines(page_builder, text: str, max_width_pt: float) -> list[str]:
    if not text:
        return [""]
    lines = []
    for paragraph in text.splitlines():
        if not paragraph:
            lines.append("")
            continue
        current_line = ""
        for word in paragraph.split():
            if page_builder.measure(word) > max_width_pt:
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                word_lines = []
                word_line = ""
                for character in word:
                    candidate = word_line + character
                    if word_line and page_builder.measure(candidate) > max_width_pt:
                        word_lines.append(word_line)
                        word_line = character
                    else:
                        word_line = candidate
                if word_line:
                    word_lines.append(word_line)
                lines.extend(word_lines[:-1])
                current_line = word_lines[-1]
                continue
            candidate = word if not current_line else f"{current_line} {word}"
            if current_line and page_builder.measure(candidate) > max_width_pt:
                lines.append(current_line)
                current_line = word
            else:
                current_line = candidate
        if current_line:
            lines.append(current_line)
    return lines or [""]


def _draw_colored_text(page_builder, x_pt: float, y_pt: float, text: str, color: tuple[int, int, int]) -> None:
    red, green, blue = _rgb_fraction(color)
    page_builder.at(x_pt, y_pt).inline_color(red, green, blue, str(text))


class AnsysReport(PyAedtBase):
    """Provide an Ansys report implementation based on pdf-oxide."""

    def __init__(
        self,
        version: str = "2026.1",
        design_name: str = "design1",
        project_name: str = "AnsysProject",
        template_json_file: str | None = None,
    ) -> None:
        self.report_specs = ReportSpec()
        self.read_template(template_json_file)
        self.report_specs.ansys_version = version
        self.report_specs.design_name = design_name
        self.report_specs.project_name = project_name
        self.use_portrait = True
        self.__chapter_idx = 0
        self.__sub_chapter_idx = 0
        self.__figure_idx = 1
        self.__table_idx = 1
        self._pages: list[_PdfOxidePage] = []
        self._toc_requested = False
        self._current_page: _PdfOxidePage | None = None
        self._active_page_builder = None
        self._active_page_width_mm: float | None = None
        self._active_page_height_mm: float | None = None
        self._active_page_number: int | None = None
        self._active_total_pages: int | None = None

    def _margin_mm(self, value: float) -> float:
        converted_value = unit_converter(value, input_units=self.report_specs.units, output_units="mm")
        if isinstance(converted_value, (int, float)):
            return float(converted_value)
        raise TypeError("Report margins must be scalar values.")

    def _top_margin_mm(self) -> float:
        return self._margin_mm(self.report_specs.top_margin)

    def _bottom_margin_mm(self) -> float:
        return self._margin_mm(self.report_specs.bottom_margin)

    def _left_margin_mm(self) -> float:
        return self._margin_mm(self.report_specs.left_margin)

    def _right_margin_mm(self) -> float:
        return self._margin_mm(self.report_specs.right_margin)

    def _effective_width_mm(self, width_mm: float) -> float:
        return width_mm - self._left_margin_mm() - self._right_margin_mm()

    def _content_start_y_mm(self) -> float:
        return self._top_margin_mm() + 2.0

    def _footer_clearance_mm(self) -> float:
        return max(self._bottom_margin_mm(), 24.0)

    def _content_end_y_mm(self, page_height_mm: float) -> float:
        return page_height_mm - self._footer_clearance_mm()

    def _append_page(self, portrait: bool, page_format: str | tuple[float, float], kind: str = "content") -> None:
        page = _PdfOxidePage(portrait=portrait, page_format=page_format, kind=kind)
        self._pages.append(page)
        self._current_page = page

    def _ensure_current_page(self) -> _PdfOxidePage:
        if self._current_page is None:
            self.add_section()
        if self._current_page is None:  # pragma: no cover
            raise RuntimeError("Unable to create a report page.")
        return self._current_page

    def read_template(self, template_file: str | None = None) -> None:
        """Read pdf template."""
        if template_file:
            self.report_specs.template_name = template_file
        if os.path.exists(self.report_specs.template_name):
            with open_file(self.report_specs.template_name, "r") as f:
                tdata = json.load(f)
            self.report_specs = ReportSpec(**tdata)

    def header(self) -> None:
        """Render the page header.

        Override this method to customize headers. It is called for every rendered page.
        """
        if (
            self._active_page_builder is not None
            and self._active_page_width_mm is not None
            and self._active_page_height_mm is not None
        ):
            self._render_header(
                self._active_page_builder,
                self._active_page_width_mm,
                self._active_page_height_mm,
            )

    def footer(self) -> None:
        """Render the page footer.

        Override this method to customize footers. It is called for every rendered page.
        """
        if (
            self._active_page_builder is not None
            and self._active_page_width_mm is not None
            and self._active_page_number is not None
            and self._active_total_pages is not None
        ):
            self._render_footer(
                self._active_page_builder,
                self._active_page_width_mm,
                self._active_page_number,
                self._active_total_pages,
            )

    def _invoke_header(self, page_builder, page_width_mm: float, page_height_mm: float) -> None:
        self._active_page_builder = page_builder
        self._active_page_width_mm = page_width_mm
        self._active_page_height_mm = page_height_mm
        self.header()

    def _invoke_footer(self, page_builder, page_width_mm: float, page_number: int, total_pages: int) -> None:
        self._active_page_builder = page_builder
        self._active_page_width_mm = page_width_mm
        self._active_page_number = page_number
        self._active_total_pages = total_pages
        self.footer()

    def create(self, add_cover_page: bool = True, add_new_section_after: bool = True) -> bool:
        """Create a new report using ``report_specs`` properties."""
        self._pages = []
        self._current_page = None
        self._toc_requested = False
        self.__chapter_idx = 0
        self.__sub_chapter_idx = 0
        self.__figure_idx = 1
        self.__table_idx = 1
        if add_cover_page:
            self._append_page(self.use_portrait, "a4", kind="cover")
        if add_new_section_after:
            self.add_section()
        return True

    def add_section(self, portrait: bool | None = None, page_format: str = "a4") -> None:
        """Add a new section to Pdf."""
        if portrait is None:
            portrait = self.use_portrait
        self._append_page(portrait, page_format)

    def add_page_break(self) -> None:
        """Add a new page break line."""
        page = self._ensure_current_page()
        self._append_page(page.portrait, page.page_format)

    def add_chapter(self, chapter_name: str) -> bool:
        """Add a new chapter."""
        self.__chapter_idx += 1
        self.__sub_chapter_idx = 0
        self._ensure_current_page().blocks.append(
            _PdfOxideTextBlock(
                text=f"{self.__chapter_idx} {chapter_name}",
                font_size=self.report_specs.title_font_size,
                color=tuple(self.report_specs.font_chapter_color),
                bold=True,
                outline_level=0,
            )
        )
        return True

    def add_sub_chapter(self, chapter_name: str) -> bool:
        """Add a new sub-chapter."""
        self.__sub_chapter_idx += 1
        self._ensure_current_page().blocks.append(
            _PdfOxideTextBlock(
                text=f"     {self.__chapter_idx}.{self.__sub_chapter_idx} {chapter_name}",
                font_size=self.report_specs.subtitle_font_size,
                color=tuple(self.report_specs.font_subchapter_color),
                italic=True,
                outline_level=1,
            )
        )
        return True

    def add_caption(self, content: str) -> None:
        """Add a centered italic caption."""
        self._ensure_current_page().blocks.append(
            _PdfOxideTextBlock(
                text=content,
                font_size=self.report_specs.caption_font_size,
                color=tuple(self.report_specs.font_caption_color),
                italic=True,
                align="center",
                outline_level=1,
            )
        )

    def add_text(self, content: str, bold: bool = False, italic: bool = False) -> None:
        """Add a new text."""
        self._ensure_current_page().blocks.append(
            _PdfOxideTextBlock(
                text=content,
                font_size=self.report_specs.text_font_size,
                color=tuple(self.report_specs.font_color),
                bold=bold,
                italic=italic,
            )
        )

    def add_empty_line(self, num_lines: int = 1) -> None:
        """Add a new empty line."""
        self._ensure_current_page().blocks.append(_PdfOxideSpacerBlock(lines=num_lines))

    def add_image(self, path: str, caption: str = "", width: int = 0, height: int = 0) -> bool:
        """Add a new image."""
        self._ensure_current_page().blocks.append(
            _PdfOxideImageBlock(
                path=path,
                caption=caption,
                width_mm=None if width == 0 else float(width),
                height_mm=None if height == 0 else float(height),
            )
        )
        return True

    @requires_graphical_dependency("pillow")
    def add_image_with_aspect_ratio(
        self, path: str, caption: str = "", max_width: float | None = None, max_height: float | None = None
    ) -> bool:
        """Add an image while maintaining its aspect ratio."""
        self._ensure_current_page().blocks.append(
            _PdfOxideImageBlock(
                path=path,
                caption=caption,
                max_width_mm=max_width,
                max_height_mm=max_height,
                keep_aspect_ratio=True,
            )
        )
        return True

    def add_table(
        self,
        title: str,
        content: list[list],
        formatting: list | None = None,
        col_widths: list | None = None,
        full_width: bool = False,
    ) -> None:
        """Add a new table from a list of data."""
        self._ensure_current_page().blocks.append(
            _PdfOxideTableBlock(
                title=title,
                content=content,
                formatting=formatting,
                col_widths=col_widths,
                full_width=full_width,
            )
        )

    def add_toc(self) -> None:
        """Add toc."""
        self._toc_requested = True

    @requires_graphical_dependency("matplotlib", "pillow")
    def add_chart(self, x_values: list, y_values: list, x_caption: str, y_caption: str, title: str) -> None:
        """Add a chart to the report using matplotlib."""
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        from matplotlib.figure import Figure
        import numpy as np

        dpi = 100.0
        figsize = (2000 / dpi, 2000 / dpi)
        fig = Figure(figsize=figsize, dpi=dpi)
        fig.subplots_adjust(top=0.8)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_ylabel(y_caption)
        ax.set_title(title)
        x = np.array(x_values)
        y = np.array(y_values)
        ax.plot(x, y, color="blue", lw=2)
        ax.set_xlabel(x_caption)
        canvas = FigureCanvas(fig)
        canvas.draw()
        image_buffer = io.BytesIO()
        fig.savefig(image_buffer, format="png", dpi=dpi)
        self._ensure_current_page().blocks.append(_PdfOxideImageBlock(image_bytes=image_buffer.getvalue()))

    def add_project_info(self, design) -> bool:
        """Add project information."""
        self.add_section()
        self.add_chapter(f"Design {design.design_name} Info")
        self.add_text(
            "This section will contain information about project "
            f"{design.project_name} for design {design.design_name}."
        )
        self.add_text(f"The design is a {design.design_type} model.")
        if design.design_type in [
            "Q3D Extractor",
            "Maxwell 3D",
            "HFSS",
            "Icepak",
            DesignType.ICEPAKFEA,
            "Maxwell 2D",
            "2D Extractor",
        ]:
            self.add_text(f"Simulation bounding box is {design.modeler.get_model_bounding_box()}.")
            image_path = os.path.join(design.working_directory, "model.jpg")
            design.plot(
                show=False,
                output_file=image_path,
                dark_mode=False,
                show_grid=False,
                show_bounding=False,
            )
            self.add_image(image_path, "Model Image")
        elif design.design_type in ["HFSS3DLayout", "HFSS 3D Layout Design"]:
            stats = design.modeler.edb.get_statistics()
            self.add_text(
                f"The layout has {stats.num_capacitors} capacitors, "
                f"{stats.num_resistors} resistors, {stats.num_inductors} inductors. "
                f"The design size is {stats.layout_size}."
            )
            self.add_text(
                f"Furthermore, the layout has {stats.num_nets} nets, {stats.num_traces} traces, {stats.num_vias} vias. "
                f"The stackup total thickness is {stats.stackup_thickness}."
            )
            image_path = os.path.join(design.working_directory, "model.jpg")
            design.modeler.edb.nets.plot(show=False, save_plot=image_path)
            if os.path.exists(image_path):
                self.add_image(image_path, "Model Image")
        elif design.design_type in ["Circuit Design"]:
            self.add_text(f"The schematic has {len(design.modeler.schematic.components)} components.")
        if design.setups:
            self.add_text(f"The design has {len(design.setups)} simulation setups.")
        return True

    @property
    def template_name(self) -> str:
        return self.report_specs.template_name

    @template_name.setter
    def template_name(self, value: str) -> None:
        self.report_specs.template_name = value

    @property
    def design_name(self) -> str:
        return self.report_specs.design_name

    @design_name.setter
    def design_name(self, value: str) -> None:
        self.report_specs.design_name = value

    @property
    def project_name(self) -> str:
        return self.report_specs.project_name

    @project_name.setter
    def project_name(self, value: str) -> None:
        self.report_specs.project_name = value

    @property
    def aedt_version(self) -> str:
        return self.report_specs.ansys_version

    @aedt_version.setter
    def aedt_version(self, value: str) -> None:
        self.report_specs.ansys_version = value

    def _render_header(self, page_builder, page_width_mm: float, page_height_mm: float) -> None:
        from datetime import date

        page_width_pt = _mm_to_pt(page_width_mm)
        margin_left_pt = _mm_to_pt(self._left_margin_mm())
        margin_right_pt = _mm_to_pt(self._right_margin_mm())
        text_color = tuple(self.report_specs.font_header_color)
        logo_width_pt = 0.0
        logo_gap_pt = _mm_to_pt(4.0)
        if os.path.exists(self.report_specs.logo_name):
            logo_bytes, logo_width_px, logo_height_px = _read_image_bytes(self.report_specs.logo_name)
            logo_width_mm = self._margin_mm(self.report_specs.header_image_width)
            logo_width_pt = _mm_to_pt(logo_width_mm)
            if logo_width_px and logo_height_px:
                logo_height_mm = logo_width_mm * logo_height_px / logo_width_px
            else:
                logo_height_mm = 8.0
            logo_x_pt = page_width_pt - margin_right_pt - logo_width_pt
            logo_y_pt = _mm_to_pt(page_height_mm - 10.0 - logo_height_mm)
            page_builder.image_artifact(
                logo_bytes,
                logo_x_pt,
                logo_y_pt,
                logo_width_pt,
                _mm_to_pt(logo_height_mm),
            )

        fields_left_pt = margin_left_pt
        fields_right_pt = page_width_pt - margin_right_pt - logo_width_pt - logo_gap_pt
        fields = [
            ("Project Name", self.report_specs.project_name),
            ("Design Name", self.report_specs.design_name),
            ("Ansys Version", self.report_specs.ansys_version),
            ("PyAEDT Version", self.report_specs.pyaedt_version),
            ("Date", str(date.today())),
            ("Revision", self.report_specs.revision),
        ]
        column_width_pt = max(1.0, (fields_right_pt - fields_left_pt) / len(fields))
        label_y_pt = _mm_to_pt(page_height_mm - 15.0)
        value_y_pt = _mm_to_pt(page_height_mm - 18.2)
        page_builder.font(_font_name(self.report_specs.font), self.report_specs.header_font_size)
        for index, (label, value) in enumerate(fields):
            x_pt = fields_left_pt + column_width_pt * index
            _draw_colored_text(page_builder, x_pt, label_y_pt, label, text_color)
            for line_index, line in enumerate(_wrap_text_lines(page_builder, str(value), column_width_pt)):
                _draw_colored_text(
                    page_builder,
                    x_pt,
                    value_y_pt - line_index * self.report_specs.header_font_size,
                    line,
                    text_color,
                )

        line_y_pt = _mm_to_pt(page_height_mm - (self._top_margin_mm() - 7.0))
        page_builder.stroke_line(margin_left_pt, line_y_pt, page_width_pt - margin_right_pt, line_y_pt)

    def _render_footer(self, page_builder, page_width_mm: float, page_number: int, total_pages: int) -> None:
        page_width_pt = _mm_to_pt(page_width_mm)
        margin_left_pt = _mm_to_pt(self._left_margin_mm())
        margin_right_pt = _mm_to_pt(self._right_margin_mm())
        footer_color = tuple(self.report_specs.font_header_color)
        page_text = f"Page {page_number}/{total_pages}"
        footer_y_pt = _mm_to_pt(15.0)
        page_builder.font("Helvetica-Oblique", 8.0)
        page_text_width_pt = page_builder.measure(page_text)
        _draw_colored_text(page_builder, margin_left_pt, footer_y_pt, self.report_specs.footer_text, footer_color)
        _draw_colored_text(
            page_builder, page_width_pt - margin_right_pt - page_text_width_pt, footer_y_pt, page_text, footer_color
        )

    def _render_cover_page(self, page_builder, page_width_mm: float, page_height_mm: float) -> None:
        start_y_mm = 55.0
        left_pt = _mm_to_pt(self._left_margin_mm())
        page_builder.font(_font_name(self.report_specs.font, bold=True), self.report_specs.cover_subtitle_font_size)
        page_builder.at(left_pt, _mm_to_pt(page_height_mm - start_y_mm)).text("Simulation Report")
        start_y_mm += 22.0
        page_builder.font(_font_name(self.report_specs.font, bold=True), self.report_specs.cover_title_font_size)
        page_builder.at(left_pt, _mm_to_pt(page_height_mm - start_y_mm)).text(
            f"Project Name: {self.report_specs.project_name}"
        )
        start_y_mm += 20.0
        page_builder.at(left_pt, _mm_to_pt(page_height_mm - start_y_mm)).text(
            f"Design Name: {self.report_specs.design_name}"
        )

    def _advance_content_page(
        self,
        page_builder,
        page_width_mm: float,
        page_height_mm: float,
        page_number: int,
        total_pages: int,
        draw: bool,
    ):
        if draw:
            self._invoke_footer(page_builder, page_width_mm, page_number, total_pages)
            page_builder = page_builder.new_page_same_size()
            self._invoke_header(page_builder, page_width_mm, page_height_mm)
        else:
            page_builder = page_builder.new_page_same_size()
        return page_builder, self._content_start_y_mm(), page_number + 1

    def _render_text_block(
        self,
        page_builder,
        block: _PdfOxideTextBlock,
        cursor_y_mm: float,
        page_width_mm: float,
        page_height_mm: float,
        page_number: int,
        total_pages: int,
        draw: bool,
    ):
        page_builder.font(_font_name(self.report_specs.font, bold=block.bold, italic=block.italic), block.font_size)
        available_width_pt = _mm_to_pt(self._effective_width_mm(page_width_mm))
        lines = _wrap_text_lines(page_builder, block.text, available_width_pt)
        line_height_mm = _pt_to_mm(block.font_size * block.leading)
        left_pt = _mm_to_pt(self._left_margin_mm())
        added_outline = []
        for index, line in enumerate(lines):
            if cursor_y_mm + line_height_mm > self._content_end_y_mm(page_height_mm):
                page_builder, cursor_y_mm, page_number = self._advance_content_page(
                    page_builder, page_width_mm, page_height_mm, page_number, total_pages, draw
                )
                page_builder.font(
                    _font_name(self.report_specs.font, bold=block.bold, italic=block.italic),
                    block.font_size,
                )
            y_pt = _mm_to_pt(page_height_mm - cursor_y_mm - line_height_mm)
            x_pt = left_pt
            if block.align == "center":
                x_pt = left_pt + max(0.0, (available_width_pt - page_builder.measure(line)) / 2.0)
            if draw:
                _draw_colored_text(page_builder, x_pt, y_pt, line, block.color)
            if index == 0 and block.outline_level is not None:
                added_outline.append((block.outline_level, block.text.strip(), page_number))
            cursor_y_mm += line_height_mm
        return page_builder, cursor_y_mm + 1.5, page_number, added_outline

    def _render_image_block(
        self,
        page_builder,
        block: _PdfOxideImageBlock,
        cursor_y_mm: float,
        page_width_mm: float,
        page_height_mm: float,
        page_number: int,
        total_pages: int,
        draw: bool,
    ):
        if block.path:
            image_bytes, image_width_px, image_height_px = _read_image_bytes(block.path)
        elif block.image_bytes:
            image_bytes = block.image_bytes
            try:
                from PIL import Image

                with Image.open(io.BytesIO(image_bytes)) as img:
                    image_width_px, image_height_px = img.size
            except Exception:  # pragma: no cover
                image_width_px = None
                image_height_px = None
        else:
            return page_builder, cursor_y_mm, page_number, []

        available_width_mm = self._effective_width_mm(page_width_mm)
        width_mm = block.width_mm or block.max_width_mm or available_width_mm
        height_mm = block.height_mm
        page_capacity_mm = self._content_end_y_mm(page_height_mm) - self._content_start_y_mm()
        if image_width_px and image_height_px:
            aspect_ratio = image_height_px / image_width_px
            if block.keep_aspect_ratio:
                max_width_mm = block.max_width_mm or available_width_mm
                max_height_mm = block.max_height_mm or (self._content_end_y_mm(page_height_mm) - cursor_y_mm)
                width_mm = max_width_mm
                height_mm = width_mm * aspect_ratio
                if height_mm > max_height_mm:
                    height_mm = max_height_mm
                    width_mm = height_mm / aspect_ratio
            elif height_mm is None:
                height_mm = width_mm * aspect_ratio
        elif height_mm is None:
            height_mm = width_mm

        if (
            cursor_y_mm + height_mm > self._content_end_y_mm(page_height_mm)
            and cursor_y_mm > self._content_start_y_mm()
        ):
            page_builder, cursor_y_mm, page_number = self._advance_content_page(
                page_builder, page_width_mm, page_height_mm, page_number, total_pages, draw
            )
            if block.keep_aspect_ratio:
                max_height_mm = block.max_height_mm or (self._content_end_y_mm(page_height_mm) - cursor_y_mm)
                if height_mm > max_height_mm:
                    if image_width_px and image_height_px:
                        aspect_ratio = image_height_px / image_width_px
                        height_mm = max_height_mm
                        width_mm = height_mm / aspect_ratio
            elif height_mm > page_capacity_mm and height_mm > 0:
                scale = page_capacity_mm / height_mm
                height_mm = page_capacity_mm
                width_mm *= scale

        if cursor_y_mm + height_mm > self._content_end_y_mm(page_height_mm) and height_mm > 0:
            if image_width_px and image_height_px:
                aspect_ratio = image_height_px / image_width_px
                height_mm = max(1.0, self._content_end_y_mm(page_height_mm) - cursor_y_mm)
                width_mm = height_mm / aspect_ratio
            else:
                height_mm = max(1.0, self._content_end_y_mm(page_height_mm) - cursor_y_mm)

        x_mm = self._left_margin_mm() + max(0.0, (available_width_mm - width_mm) / 2.0)
        y_pt = _mm_to_pt(page_height_mm - cursor_y_mm - height_mm)
        if draw:
            page_builder.image_artifact(
                image_bytes,
                _mm_to_pt(x_mm),
                y_pt,
                _mm_to_pt(width_mm),
                _mm_to_pt(height_mm),
            )
        cursor_y_mm += height_mm + 2.0
        outline_entries = []
        if block.caption:
            caption = f"Figure {self.__figure_idx}. {block.caption}"
            self.__figure_idx += 1
            outline_entries.append((2, caption, page_number))
            page_builder, cursor_y_mm, page_number, _ = self._render_text_block(
                page_builder,
                _PdfOxideTextBlock(
                    text=caption,
                    font_size=self.report_specs.caption_font_size,
                    color=tuple(self.report_specs.font_caption_color),
                    italic=True,
                    align="center",
                ),
                cursor_y_mm,
                page_width_mm,
                page_height_mm,
                page_number,
                total_pages,
                draw,
            )
        return page_builder, cursor_y_mm + 1.0, page_number, outline_entries

    def _render_table_block(
        self,
        page_builder,
        block: _PdfOxideTableBlock,
        cursor_y_mm: float,
        page_width_mm: float,
        page_height_mm: float,
        page_number: int,
        total_pages: int,
        draw: bool,
    ):
        available_width_mm = self._effective_width_mm(page_width_mm)
        normal_width_mm = min(available_width_mm, 160.0 if page_width_mm <= page_height_mm else 260.0)
        table_total_width_mm = available_width_mm if block.full_width else normal_width_mm
        if block.col_widths:
            total_width = float(sum(block.col_widths))
            scale = table_total_width_mm / total_width if total_width else 1.0
            col_widths_mm = [float(width) * scale for width in block.col_widths]
        else:
            col_widths_mm = [table_total_width_mm / len(block.content[0])] * len(block.content[0])

        table_font = self.report_specs.table_font_size
        line_height_mm = _pt_to_mm(table_font * 1.3)
        padding_mm = 1.0
        cursor_y_mm += 1.0
        outline_entries = [(2, f"Table {self.__table_idx}: {block.title}", page_number)]
        rows = block.content
        if not rows:
            return page_builder, cursor_y_mm, page_number, outline_entries

        header_row = rows[0]
        row_index = 0
        while row_index < len(rows):
            row = rows[row_index]
            row_font = _font_name(self.report_specs.font, bold=row_index == 0)
            page_builder.font(row_font, table_font)
            wrapped_cells = []
            row_height_mm = line_height_mm + 2 * padding_mm
            for col_index, datum in enumerate(row):
                cell_width_pt = _mm_to_pt(col_widths_mm[col_index] - 2 * padding_mm)
                wrapped = _wrap_text_lines(page_builder, str(datum), cell_width_pt)
                wrapped_cells.append(wrapped)
                row_height_mm = max(row_height_mm, len(wrapped) * line_height_mm + 2 * padding_mm)

            if (
                cursor_y_mm + row_height_mm > self._content_end_y_mm(page_height_mm)
                and cursor_y_mm > self._content_start_y_mm()
            ):
                page_builder, cursor_y_mm, page_number = self._advance_content_page(
                    page_builder, page_width_mm, page_height_mm, page_number, total_pages, draw
                )
                if row_index > 0:
                    row = header_row
                    row_font = _font_name(self.report_specs.font, bold=True)
                    page_builder.font(row_font, table_font)
                    wrapped_cells = []
                    row_height_mm = line_height_mm + 2 * padding_mm
                    for col_index, datum in enumerate(row):
                        cell_width_pt = _mm_to_pt(col_widths_mm[col_index] - 2 * padding_mm)
                        wrapped = _wrap_text_lines(page_builder, str(datum), cell_width_pt)
                        wrapped_cells.append(wrapped)
                        row_height_mm = max(row_height_mm, len(wrapped) * line_height_mm + 2 * padding_mm)
                    row_index -= 1

            x_mm = self._left_margin_mm() + max(0.0, (available_width_mm - table_total_width_mm) / 2.0)
            for col_index, cell_lines in enumerate(wrapped_cells):
                width_mm = col_widths_mm[col_index]
                y_pt = _mm_to_pt(page_height_mm - cursor_y_mm - row_height_mm)
                formatting = None
                if block.formatting and row_index < len(block.formatting):
                    formatting = block.formatting[row_index]

                if row_index == 0:
                    background = (0.78, 0.78, 0.78)
                else:
                    background = None
                    if formatting:
                        if isinstance(formatting, list) and len(formatting) > 1 and formatting[1]:
                            background = _rgb_fraction(formatting[1])

                if draw and background:
                    page_builder.filled_rect(
                        _mm_to_pt(x_mm),
                        y_pt,
                        _mm_to_pt(width_mm),
                        _mm_to_pt(row_height_mm),
                        *background,
                    )
                if draw:
                    page_builder.stroke_rect(_mm_to_pt(x_mm), y_pt, _mm_to_pt(width_mm), _mm_to_pt(row_height_mm))
                    page_builder.font(row_font, table_font)
                    cell_width_pt = _mm_to_pt(width_mm - 2 * padding_mm)
                    for line_index, line in enumerate(cell_lines):
                        text_x_pt = _mm_to_pt(x_mm + padding_mm) + max(
                            0.0, (cell_width_pt - page_builder.measure(line)) / 2.0
                        )
                        text_y_pt = _mm_to_pt(
                            page_height_mm - cursor_y_mm - padding_mm - (line_index + 1) * line_height_mm
                        )
                        page_builder.at(text_x_pt, text_y_pt).text(line)
                x_mm += width_mm
            cursor_y_mm += row_height_mm
            row_index += 1

        page_builder, cursor_y_mm, page_number, _ = self._render_text_block(
            page_builder,
            _PdfOxideTextBlock(
                text=f"Table {self.__table_idx}: {block.title}",
                font_size=self.report_specs.caption_font_size,
                color=tuple(self.report_specs.font_caption_color),
                italic=True,
                align="center",
            ),
            cursor_y_mm + 1.0,
            page_width_mm,
            page_height_mm,
            page_number,
            total_pages,
            draw,
        )
        self.__table_idx += 1
        return page_builder, cursor_y_mm + 1.0, page_number, outline_entries

    def _render_toc_page(
        self, page_builder, page_width_mm: float, page_height_mm: float, outline_entries: list[tuple[int, str, int]]
    ) -> None:
        cursor_y_mm = self._top_margin_mm() + 5.0
        _, cursor_y_mm, _, _ = self._render_text_block(
            page_builder,
            _PdfOxideTextBlock(
                text="Table of contents:",
                font_size=self.report_specs.title_font_size,
                color=tuple(self.report_specs.font_color),
                bold=True,
            ),
            cursor_y_mm,
            page_width_mm,
            page_height_mm,
            0,
            0,
            True,
        )
        cursor_y_mm += 3.0
        left_pt = _mm_to_pt(self._left_margin_mm())
        available_width_pt = _mm_to_pt(self._effective_width_mm(page_width_mm))
        page_builder.font(_font_name(self.report_specs.font), 12.0)
        for level, title, page_number in outline_entries:
            y_pt = _mm_to_pt(page_height_mm - cursor_y_mm - _pt_to_mm(12.0 * 1.2))
            indent_pt = _mm_to_pt(6.0 * level)
            _draw_colored_text(page_builder, left_pt + indent_pt, y_pt, title, tuple(self.report_specs.font_color))
            page_builder.text_in_rect(
                left_pt,
                y_pt,
                available_width_pt,
                _mm_to_pt(5.0),
                f"Page {page_number}",
                "right",
            )
            cursor_y_mm += 5.5

    def _count_physical_pages(self, pages: list[_PdfOxidePage], DocumentBuilder) -> int:
        figure_idx = self.__figure_idx
        table_idx = self.__table_idx
        total_pages = 0
        try:
            for page in pages:
                total_pages += 1
                if page.kind != "content":
                    continue
                page_width_mm, page_height_mm = _page_size_mm(page.page_format, page.portrait)
                page_builder = DocumentBuilder().page(_mm_to_pt(page_width_mm), _mm_to_pt(page_height_mm))
                cursor_y_mm = self._content_start_y_mm()
                current_page_number = total_pages
                for block in page.blocks:
                    if isinstance(block, _PdfOxideTextBlock):
                        page_builder, cursor_y_mm, current_page_number, _ = self._render_text_block(
                            page_builder,
                            block,
                            cursor_y_mm,
                            page_width_mm,
                            page_height_mm,
                            current_page_number,
                            0,
                            False,
                        )
                    elif isinstance(block, _PdfOxideSpacerBlock):
                        cursor_y_mm += block.lines * _pt_to_mm(self.report_specs.text_font_size)
                        if cursor_y_mm > self._content_end_y_mm(page_height_mm):
                            page_builder, cursor_y_mm, current_page_number = self._advance_content_page(
                                page_builder, page_width_mm, page_height_mm, current_page_number, 0, False
                            )
                    elif isinstance(block, _PdfOxideImageBlock):
                        page_builder, cursor_y_mm, current_page_number, _ = self._render_image_block(
                            page_builder,
                            block,
                            cursor_y_mm,
                            page_width_mm,
                            page_height_mm,
                            current_page_number,
                            0,
                            False,
                        )
                    elif isinstance(block, _PdfOxideTableBlock):
                        page_builder, cursor_y_mm, current_page_number, _ = self._render_table_block(
                            page_builder,
                            block,
                            cursor_y_mm,
                            page_width_mm,
                            page_height_mm,
                            current_page_number,
                            0,
                            False,
                        )
                total_pages = current_page_number
                page_builder.done()
            return total_pages
        finally:
            self.__figure_idx = figure_idx
            self.__table_idx = table_idx

    def save_pdf(self, file_path: str, file_name: str | None = None) -> str:
        """Save pdf."""
        if file_name is None:
            raise TypeError("file_name must be provided.")
        DocumentBuilder = _pdf_oxide_imports()
        output_path = os.path.join(file_path, file_name)
        builder = (
            DocumentBuilder()
            .title("Simulation Report")
            .author(self.report_specs.company_name)
            .creator(f"PyAEDT {self.report_specs.pyaedt_version}")
            .subject(f"{self.report_specs.project_name} / {self.report_specs.design_name}")
        )

        pages = list(self._pages)
        if self._toc_requested:
            pages.append(_PdfOxidePage(portrait=self.use_portrait, page_format="a4", kind="toc"))

        total_pages = self._count_physical_pages(pages, DocumentBuilder)
        self.__figure_idx = 1
        self.__table_idx = 1
        outline_entries: list[tuple[int, str, int]] = []
        page_number = 1
        for page in pages:
            page_width_mm, page_height_mm = _page_size_mm(page.page_format, page.portrait)
            page_builder = builder.page(_mm_to_pt(page_width_mm), _mm_to_pt(page_height_mm))

            if page.kind == "cover":
                self._invoke_header(page_builder, page_width_mm, page_height_mm)
                self._render_cover_page(page_builder, page_width_mm, page_height_mm)
                self._invoke_footer(page_builder, page_width_mm, page_number, total_pages)
                page_number += 1
            elif page.kind == "toc":
                self._invoke_header(page_builder, page_width_mm, page_height_mm)
                self._render_toc_page(page_builder, page_width_mm, page_height_mm, outline_entries)
                self._invoke_footer(page_builder, page_width_mm, page_number, total_pages)
                page_number += 1
            else:
                self._invoke_header(page_builder, page_width_mm, page_height_mm)
                cursor_y_mm = self._content_start_y_mm()
                current_page_number = page_number
                for block in page.blocks:
                    if isinstance(block, _PdfOxideTextBlock):
                        page_builder, cursor_y_mm, current_page_number, added_outline = self._render_text_block(
                            page_builder,
                            block,
                            cursor_y_mm,
                            page_width_mm,
                            page_height_mm,
                            current_page_number,
                            total_pages,
                            True,
                        )
                        outline_entries.extend(added_outline)
                    elif isinstance(block, _PdfOxideSpacerBlock):
                        cursor_y_mm += block.lines * _pt_to_mm(self.report_specs.text_font_size)
                        if cursor_y_mm > self._content_end_y_mm(page_height_mm):
                            page_builder, cursor_y_mm, current_page_number = self._advance_content_page(
                                page_builder,
                                page_width_mm,
                                page_height_mm,
                                current_page_number,
                                total_pages,
                                True,
                            )
                    elif isinstance(block, _PdfOxideImageBlock):
                        page_builder, cursor_y_mm, current_page_number, added_outline = self._render_image_block(
                            page_builder,
                            block,
                            cursor_y_mm,
                            page_width_mm,
                            page_height_mm,
                            current_page_number,
                            total_pages,
                            True,
                        )
                        outline_entries.extend(added_outline)
                    elif isinstance(block, _PdfOxideTableBlock):
                        page_builder, cursor_y_mm, current_page_number, added_outline = self._render_table_block(
                            page_builder,
                            block,
                            cursor_y_mm,
                            page_width_mm,
                            page_height_mm,
                            current_page_number,
                            total_pages,
                            True,
                        )
                        outline_entries.extend(added_outline)
                self._invoke_footer(page_builder, page_width_mm, current_page_number, total_pages)
                page_number = current_page_number + 1

            builder = page_builder.done()

        builder.save(output_path)
        return str(output_path)
