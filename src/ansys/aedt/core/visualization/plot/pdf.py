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

try:
    from fpdf import FPDF
    from fpdf import FontFace
except ImportError as e:  # pragma: no cover
    from ansys.aedt.core.internal.checks import install_message

    msg_error = install_message("fpdf", "graphics", level="module")
    raise ImportError(msg_error) from e

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
    ansys_version: str = "2025R1"
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


class AnsysReport(FPDF, PyAedtBase):
    """Provide ansys report."""

    def __init__(
        self,
        version: str = "2025R1",
        design_name: str = "design1",
        project_name: str = "AnsysProject",
        tempplate_json_file=None,
    ) -> None:
        super().__init__()
        self.report_specs = ReportSpec()
        self.read_template(tempplate_json_file)
        self.report_specs.ansys_version = version
        self.report_specs.design_name = design_name
        self.report_specs.project_name = project_name
        self.use_portrait = True
        self.__chapter_idx = 0
        self.__sub_chapter_idx = 0
        self.__figure_idx = 1
        self.__table_idx = 1
        self._left_margin = 0
        self.set_top_margin(unit_converter(self.report_specs.top_margin, input_units=self.report_specs.units))
        self.set_right_margin(unit_converter(self.report_specs.right_margin, input_units=self.report_specs.units))
        self.set_left_margin(unit_converter(self.report_specs.left_margin, input_units=self.report_specs.units))
        self.set_auto_page_break(
            True, margin=unit_converter(self.report_specs.bottom_margin, input_units=self.report_specs.units)
        )
        self.alias_nb_pages()

    def read_template(self, template_file: str = None) -> None:
        """Read pdf template.

        Parameters
        ----------
        template_file : str
            Path to the json template file.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.read_template()

        """
        if template_file:
            self.report_specs.template_name = template_file
        if os.path.exists(self.report_specs.template_name):
            with open_file(self.report_specs.template_name, "r") as f:
                tdata = json.load(f)
            self.report_specs = ReportSpec(**tdata)

    def __add_cover_page(self) -> None:
        self.add_page("P" if self.use_portrait else "L")
        self.set_font(self.report_specs.font.lower(), "b", self.report_specs.cover_subtitle_font_size)
        self.y += 40
        self.cell(
            0,
            12,
            "Simulation Report",
            new_x="LMARGIN",
            new_y="NEXT",
            align="L",
        )
        self.ln(10)
        self.set_font(self.report_specs.font.lower(), "B", self.report_specs.cover_title_font_size)
        self.cell(
            0,
            16,
            f"Project Name: {self.report_specs.project_name}",
            new_x="LMARGIN",
            new_y="NEXT",
            align="L",
        )
        self.cell(
            0,
            16,
            f"Design Name: {self.report_specs.design_name}",
            new_x="LMARGIN",
            new_y="NEXT",
            align="L",
        )

    def header(self) -> None:
        """Header.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.header()

        """
        from datetime import date

        def add_field(field_name, field_value) -> None:
            self.set_font(self.report_specs.font.lower(), size=self.report_specs.header_font_size)
            self.cell(
                0,
                3,
                field_name,
                new_x="LMARGIN",
                new_y="NEXT",
                align="L",
            )
            self.set_x(line_x)
            self.cell(
                0,
                3,
                field_value,
                new_x="LMARGIN",
                new_y="NEXT",
                align="L",
            )

        # Logo
        self.set_y(15)
        if self._left_margin == 0:
            self._left_margin = self.l_margin
        self.set_x(self._left_margin)
        line_x = self.x
        line_y = self.y
        delta = (self.w - self.r_margin - self._left_margin) / 5 - 10
        self.set_text_color(*self.report_specs.font_header_color)

        add_field("Project Name", self.report_specs.project_name)
        self.set_y(line_y)
        line_x += delta
        self.set_x(line_x)
        add_field("Design Name", self.report_specs.design_name)

        self.set_y(line_y)
        line_x += delta
        self.set_x(line_x)
        add_field("Ansys Version", self.report_specs.ansys_version)
        self.set_y(line_y)
        line_x += delta
        self.set_x(line_x)
        add_field("PyAEDT Version", self.report_specs.pyaedt_version)
        self.set_y(line_y)
        line_x += delta
        self.set_x(line_x)

        add_field("Date", str(date.today()))
        self.set_y(line_y)
        line_x += delta
        self.set_x(line_x)
        add_field("Revision", self.report_specs.revision)
        self.set_y(10)
        line_x += delta
        self.set_x(self.w - self.r_margin - 33)
        self.image(
            self.report_specs.logo_name,
            self.x,
            self.y,
            unit_converter(self.report_specs.header_image_width, input_units=self.report_specs.units),
        )
        self.set_x(self._left_margin)
        self.set_y(self.t_margin)
        self.line(x1=self._left_margin, y1=self.t_margin - 7, x2=self.w - self.r_margin, y2=self.t_margin - 7)

    # Page footer
    def footer(self) -> None:
        """Footer.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.footer()

        """
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_x(self._left_margin)
        # Arial italic 8
        self.set_font("helvetica", "I", 8)
        self.set_text_color(*self.report_specs.font_header_color)
        # Page number
        self.cell(0, 10, self.report_specs.footer_text, 0, align="L")
        self.cell(0, 10, "Page " + str(self.page_no()) + "/{nb}", align="R")

    def create(self, add_cover_page: bool = True, add_new_section_after: bool = True) -> bool:
        """Create a new report using ``report_specs`` properties.

        Parameters
        ----------
        add_cover_page : bool, optional
            Whether to add cover page or not. Default is ``True``.
        add_new_section_after : bool, optional
            Whether if add a new section after the cover page or not.

        Returns
        -------
        :class:`AnsysReport`

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.create()

        """
        if add_cover_page:
            self.__add_cover_page()
        if add_new_section_after:
            self.add_page("P" if self.use_portrait else "L")
        self._left_margin = self.l_margin
        return True

    def add_project_info(self, design) -> bool:
        """Add project information.

        Parameters
        ----------
        design : object
            Starting application object. For example, ``hfss1= HFSS3DLayout()``.

        Returns
        -------
        bool

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_project_info()

        """
        self.add_page("P" if self.use_portrait else "L")
        self.add_chapter(f"Design {design.design_name} Info")
        msg = f"This section will contain information about project {design.project_name}"
        msg += f" for design {design.design_name}."
        self.add_text(msg)
        msg = f"The design is a {design.design_type} model."
        self.add_text(msg)
        if design.design_type in [
            "Q3D Extractor",
            "Maxwell 3D",
            "HFSS",
            "Icepak",
            DesignType.ICEPAKFEA,
            "Maxwell 2D",
            "2D Extractor",
        ]:
            msg = f"Simulation bounding box is {design.modeler.get_model_bounding_box()}."
            self.add_text(msg)
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
            msg = f"The layout has {stats.num_capacitors} capacitors, {stats.num_resistors} resistors,"
            msg += f"{stats.num_inductors} inductors. The design size is {stats.layout_size}."
            self.add_text(msg)
            msg = f"Furthermore, the layout has {stats.num_nets} nets, {stats.num_traces} traces,"
            msg += f" {stats.num_vias} vias. The stackup total thickness is {stats.stackup_thickness}."
            image_path = os.path.join(design.working_directory, "model.jpg")
            design.modeler.edb.nets.plot(show=False, save_plot=image_path)
            if os.path.exists(image_path):
                self.add_image(image_path, "Model Image")
        elif design.design_type in ["Circuit Design"]:
            msg = f"The schematic has {len(design.modeler.schematic.components)} components."
            self.add_text(msg)

        if design.setups:
            msg = f"The design has {len(design.setups)} simulation setups."
            self.add_text(msg)

        return True

    @property
    def template_name(self) -> str:
        """Name of the template to use.

        It can be a full json path or a string of a json contained in ``"Images"`` folder.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.template_name

        """
        return self.report_specs.template_name

    @template_name.setter
    def template_name(self, value: str) -> None:
        self.report_specs.template_name = value

    @property
    def design_name(self) -> str:
        """Get/set the design name for report header.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.design_name

        """
        return self.report_specs.design_name

    @design_name.setter
    def design_name(self, value: str) -> None:
        self.report_specs.design_name = value

    @property
    def project_name(self) -> str:
        """Get/set the project name for report header.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.project_name

        """
        return self.report_specs.project_name

    @project_name.setter
    def project_name(self, value: str) -> None:
        self.report_specs.project_name = value

    @property
    def aedt_version(self) -> str:
        """Get/set the aedt version for report header.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.aedt_version

        """
        return self.report_specs.ansys_version

    @aedt_version.setter
    def aedt_version(self, value: str) -> None:
        self.report_specs.ansys_version = value

    def add_section(self, portrait: bool = None, page_format: str = "a4") -> None:
        """Add a new section to Pdf.

        Parameters
        ----------
        portrait : bool, optional
            Section orientation. Default ``True`` for portrait.
        page_format : str, optional
            Currently supported formats are a3, a4, a5, letter, legal or a tuple (width, height).

        Returns
        -------
        int,
            Section id.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_section()

        """
        orientation = "portrait"
        if portrait is False:
            orientation = "landscape"
        elif portrait is None:
            orientation = "P" if self.use_portrait else "L"
        self.add_page(orientation=orientation, format=page_format)

    def add_chapter(self, chapter_name: str) -> bool:
        """Add a new chapter.

        Parameters
        ----------
        chapter_name : str
            Chapter name.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_chapter("Chapter 1")

        """
        self.__chapter_idx += 1
        self.__sub_chapter_idx = 0
        txt = f"{self.__chapter_idx} {chapter_name}"
        self.set_font(self.report_specs.font.lower(), "B", self.report_specs.title_font_size)
        self.start_section(txt)
        self.set_text_color(*self.report_specs.font_chapter_color)
        self.cell(
            0,
            12,
            txt,
            new_x="LMARGIN",
            new_y="NEXT",
            align="L",
        )
        self.set_font(self.report_specs.font.lower(), "I", self.report_specs.text_font_size)
        self.set_text_color(*self.report_specs.font_color)
        return True

    def add_sub_chapter(self, chapter_name: str) -> bool:
        """Add a new sub-chapter.

        Parameters
        ----------
        chapter_name : str
            Chapter name.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_sub_chapter("Sub-chapter 1")

        """
        self.__sub_chapter_idx += 1
        txt = f"     {self.__chapter_idx}.{self.__sub_chapter_idx} {chapter_name}"
        self.set_font(self.report_specs.font.lower(), "I", self.report_specs.subtitle_font_size)
        self.start_section(txt.strip(), level=1)
        self.set_text_color(*self.report_specs.font_subchapter_color)
        self.cell(
            0,
            10,
            txt,
            new_x="LMARGIN",
            new_y="NEXT",
            align="L",
        )
        self.set_font(self.report_specs.font.lower(), "I", self.report_specs.text_font_size)
        self.set_text_color(*self.report_specs.font_color)

        return True

    def add_image(
        self,
        path: str,
        caption: str = "",
        width: int = 0,
        height: int = 0,
    ) -> bool:
        """Add a new image.

        Parameters
        ----------
        path : str
            Image path.
        caption : str, optional
            Image caption.
        width : int, optional
            Image width in millimeters.
        height : int, optional
            Image height in millimeters.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_image("image_path", "Image caption", width=100, height=100)

        """
        if width == 0:
            width = self.epw

        self.image(path, h=height, w=width, x=self.epw / 2 - width / 2 + self._left_margin)
        if caption:
            caption = f"Figure {self.__figure_idx}. {caption}"
            self.add_caption(caption)
            self.__figure_idx += 1
        return True

    @requires_graphical_dependency("pillow")
    def add_image_with_aspect_ratio(
        self, path: str, caption: str = "", max_width: float = None, max_height: float = None
    ) -> bool:
        """Add an image to the PDF while maintaining its aspect ratio and fitting within the specified dimensions.

        Parameters
        ----------
        path: str
            Path to the image file.
        caption: str, optional
            Image caption.
        max_width: float, int, optional
            Maximum width available for the image.
        max_height: float, int, optional
            Maximum height available for the image.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_image_with_aspect_ratio("path/to/image.png", caption="My Image", max_width=150, max_height=100)

        """
        from PIL import Image

        # Get image dimensions
        with Image.open(path) as img:
            img_width, img_height = img.size

        # Get page dimensions
        if max_width is None:
            max_width = self.epw - 50  # Default to page width minus margins
        if max_height is None:
            max_height = self.eph - 30 - (self.y - self.t_margin)  # Default to page height minus margins
            if max_height < 0:
                self.add_page_break()
                max_height = self.eph - 30 - (self.y - self.t_margin)
        # Calculate aspect ratio
        aspect_ratio = img_width / img_height

        # Scale dimensions to fit within max_width and max_height
        if max_width / aspect_ratio <= max_height:
            width = max_width
            height = max_width / aspect_ratio
        else:
            height = max_height
            width = max_height * aspect_ratio

        # Add the image to the PDF
        return self.add_image(path, caption=caption, width=width, height=height)

    def add_caption(self, content: str) -> None:
        """Add a new caption.

        Parameters
        ----------
        content : str
            Caption name.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_caption("Figure 1: My Figure")

        """
        self.set_font(self.report_specs.font.lower(), "I", self.report_specs.caption_font_size)
        self.set_text_color(*self.report_specs.font_caption_color)
        self.start_section(content, level=1)
        self.cell(
            0,
            6,
            content,
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
        )
        self.set_font(self.report_specs.font.lower(), "I", self.report_specs.text_font_size)
        self.set_text_color(*self.report_specs.font_color)

    def add_empty_line(self, num_lines: int = 1) -> None:
        """Add a new empty line.

        Parameters
        ----------
        num_lines : int, optional
            Number of lines to add.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_empty_line(num_lines=2)

        """
        self.ln(num_lines * self.font_size)

    def add_page_break(self) -> None:
        """Add a new page break line.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_page_break()

        """
        self.add_page("P" if self.use_portrait else "L")

    def add_table(
        self,
        title: str,
        content: list[list],
        formatting: list = None,
        col_widths: list = None,
    ) -> None:
        """Add a new table from a list of data.

        Data shall be a list of list where every line is either a row or a column.

        Parameters
        ----------
        title : str
            Table title.
        content : list of list
            Table content.
        formatting : list, optional
            List of formatting elements for the table rows. The length of the formatting has
            to be equal to the length of content. Every element is a list of two elements
            (color, background_color).  Color is a RGB list.
        col_widths : list, optional
            List of column widths.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_table("Table Title", [["Header1", "Header2"], ["Row1Col1", "Row1Col2"], ["Row2Col1", "Row2Col2"]])

        """
        self.set_font(self.report_specs.font.lower(), size=self.report_specs.text_font_size)
        self.set_font(self.report_specs.font.lower(), size=self.report_specs.table_font_size)
        with self.table(
            borders_layout="MINIMAL",
            cell_fill_color=200,  # grey
            cell_fill_mode="ROWS",
            line_height=self.font_size * 2.5,
            text_align="CENTER",
            width=160 if self.use_portrait else 260,
            col_widths=col_widths,
            num_heading_rows=1,
            repeat_headings=1,
        ) as table:
            for i, data_row in enumerate(content):
                fill_color = None
                font_color = self.report_specs.font_color

                if formatting:
                    try:
                        font_color = formatting[i][0] if formatting[i][0] else self.report_specs.font_color
                        fill_color = formatting[i][1] if formatting[i][1] else None
                    except IndexError:
                        pass
                style = FontFace(color=font_color, fill_color=fill_color)

                row = table.row()
                for datum in data_row:
                    row.cell(str(datum), style=style)
        self.add_caption(f"Table {self.__table_idx}: {title}")
        self.__table_idx += 1

    def add_text(self, content: str, bold: bool = False, italic: bool = False) -> None:
        """Add a new text.

        Parameters
        ----------
        content : str
            Text content.
        bold : bool, optional
            Whether if text is bold or not. Default is ``True``.
        italic : bool, optional
            Whether if text is italic or not. Default is ``True``.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_text("Some text content", bold=True, italic=False)

        """
        font_type = ""
        if bold:
            font_type = "B"
        if italic:
            font_type += "I"
        self.set_font(self.report_specs.font.lower(), font_type.lower(), self.report_specs.text_font_size)
        self.set_text_color(*self.report_specs.font_color)

        self.multi_cell(
            0,
            6,
            content,
            new_x="LMARGIN",
            new_y="NEXT",
            align="L",
        )

    def add_toc(self) -> None:
        """Add toc.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_toc()

        """

        def p(section_toc, **kwargs) -> None:
            # Inserts a paragraph
            self.cell(w=self.epw, h=self.font_size, text=section_toc, new_x="LMARGIN", new_y="NEXT", **kwargs)

        self.add_page("P" if self.use_portrait else "L")
        self.set_font(self.report_specs.font.lower(), size=self.report_specs.title_font_size)
        self.set_text_color(*self.report_specs.font_color)
        self.underline = True
        self.x = self._left_margin
        p("Table of contents:")
        self.underline = False
        self.y += 10
        self.set_font(self.report_specs.font, size=12)

        for section in self._outline:
            link = self.add_link()
            self.set_link(link, page=section.page_number)
            string1 = f"{' ' * section.level * 2} {section.name}"[:70]
            string2 = f"Page {section.page_number}"
            self.set_x(self._left_margin * 2)
            self.cell(
                w=self.epw - self._left_margin - self.r_margin,
                h=self.font_size,
                text=string1,
                new_x="LMARGIN",
                new_y="LAST",
                align="L",
                link=link,
            )
            self.set_x(self._left_margin * 2)
            self.cell(
                w=self.epw - self._left_margin - self.r_margin,
                h=self.font_size,
                text=string2,
                new_x="LMARGIN",
                new_y="NEXT",
                align="R",
                link=link,
            )

    def save_pdf(self, file_path: str, file_name: str | None = None) -> str:
        """Save pdf.

        Parameters
        ----------
        file_path : str
            Pdf path.
        file_name : str, optional
            File name.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.save_pdf("path/to/save", "report.pdf")

        """
        self.output(os.path.join(file_path, file_name))
        return str(os.path.join(file_path, file_name))

    @requires_graphical_dependency("matplotlib", "pillow")
    def add_chart(self, x_values: list, y_values: list, x_caption: str, y_caption: str, title: str) -> None:
        """Add a chart to the report using matplotlib.

        Parameters
        ----------
        x_values : list
            list of float x values.
        y_values : list
            List of float y values.
        x_caption : str
            X axis caption.
        y_caption : str
            Y axis caption.
        title : str
            Chart title.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.plot.pdf import AnsysReport
        >>> obj = AnsysReport()
        >>> obj.add_chart([1, 2, 3], [4, 5, 6], "X Axis", "Y Axis", "Sample Chart")

        """
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        from matplotlib.figure import Figure
        import numpy as np
        from PIL import Image

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
        # Converting Figure to an image:
        canvas = FigureCanvas(fig)
        canvas.draw()
        img = Image.fromarray(np.asarray(canvas.buffer_rgba()))
        self.image(img, w=self.epw)  # Make the image full width


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


class AnsysReportPdfOxide(PyAedtBase):
    """Provide a pdf-oxide based Ansys report implementation."""

    def __init__(
        self,
        version: str = "2025R1",
        design_name: str = "design1",
        project_name: str = "AnsysProject",
        tempplate_json_file=None,
    ) -> None:
        self.report_specs = ReportSpec()
        self.read_template(tempplate_json_file)
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

    def _margin_mm(self, value: float) -> float:
        return unit_converter(value, input_units=self.report_specs.units, output_units="mm")

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

    def _append_page(self, portrait: bool, page_format: str | tuple[float, float], kind: str = "content") -> None:
        page = _PdfOxidePage(portrait=portrait, page_format=page_format, kind=kind)
        self._pages.append(page)
        self._current_page = page

    def _ensure_current_page(self) -> _PdfOxidePage:
        if self._current_page is None:
            self.add_section()
        return self._current_page

    def read_template(self, template_file: str = None) -> None:
        """Read pdf template."""
        if template_file:
            self.report_specs.template_name = template_file
        if os.path.exists(self.report_specs.template_name):
            with open_file(self.report_specs.template_name, "r") as f:
                tdata = json.load(f)
            self.report_specs = ReportSpec(**tdata)

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

    def add_section(self, portrait: bool = None, page_format: str = "a4") -> None:
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
        self, path: str, caption: str = "", max_width: float = None, max_height: float = None
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
        formatting: list = None,
        col_widths: list = None,
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
            _draw_colored_text(page_builder, x_pt, value_y_pt, value, text_color)

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

    def _render_text_block(
        self, page_builder, block: _PdfOxideTextBlock, cursor_y_mm: float, page_width_mm: float, page_height_mm: float
    ) -> tuple[float, list[tuple[int, str]]]:
        page_builder.font(_font_name(self.report_specs.font, bold=block.bold, italic=block.italic), block.font_size)
        available_width_pt = _mm_to_pt(self._effective_width_mm(page_width_mm))
        lines = _wrap_text_lines(page_builder, block.text, available_width_pt)
        line_height_mm = _pt_to_mm(block.font_size * block.leading)
        left_pt = _mm_to_pt(self._left_margin_mm())
        added_outline = []
        for index, line in enumerate(lines):
            y_pt = _mm_to_pt(page_height_mm - cursor_y_mm - line_height_mm)
            x_pt = left_pt
            if block.align == "center":
                x_pt = left_pt + max(0.0, (available_width_pt - page_builder.measure(line)) / 2.0)
            _draw_colored_text(page_builder, x_pt, y_pt, line, block.color)
            if index == 0 and block.outline_level is not None:
                added_outline.append((block.outline_level, block.text.strip()))
            cursor_y_mm += line_height_mm
        return cursor_y_mm + 1.5, added_outline

    def _render_image_block(
        self, page_builder, block: _PdfOxideImageBlock, cursor_y_mm: float, page_width_mm: float, page_height_mm: float
    ) -> tuple[float, list[tuple[int, str]]]:
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
            return cursor_y_mm, []

        available_width_mm = self._effective_width_mm(page_width_mm)
        width_mm = block.width_mm or block.max_width_mm or available_width_mm
        height_mm = block.height_mm
        if image_width_px and image_height_px:
            aspect_ratio = image_height_px / image_width_px
            if block.keep_aspect_ratio:
                max_width_mm = block.max_width_mm or available_width_mm
                max_height_mm = block.max_height_mm or (page_height_mm - cursor_y_mm - self._bottom_margin_mm() - 10.0)
                width_mm = max_width_mm
                height_mm = width_mm * aspect_ratio
                if height_mm > max_height_mm:
                    height_mm = max_height_mm
                    width_mm = height_mm / aspect_ratio
            elif height_mm is None:
                height_mm = width_mm * aspect_ratio
        elif height_mm is None:
            height_mm = width_mm

        x_mm = self._left_margin_mm() + max(0.0, (available_width_mm - width_mm) / 2.0)
        y_pt = _mm_to_pt(page_height_mm - cursor_y_mm - height_mm)
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
            outline_entries.append((1, caption))
            cursor_y_mm, _ = self._render_text_block(
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
            )
        return cursor_y_mm + 1.0, outline_entries

    def _render_table_block(
        self, page_builder, block: _PdfOxideTableBlock, cursor_y_mm: float, page_width_mm: float, page_height_mm: float
    ) -> tuple[float, list[tuple[int, str]]]:
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

        for row_index, row in enumerate(block.content):
            row_font = _font_name(self.report_specs.font, bold=row_index == 0)
            page_builder.font(row_font, table_font)
            wrapped_cells = []
            row_height_mm = line_height_mm + 2 * padding_mm
            for col_index, datum in enumerate(row):
                cell_width_pt = _mm_to_pt(col_widths_mm[col_index] - 2 * padding_mm)
                wrapped = _wrap_text_lines(page_builder, str(datum), cell_width_pt)
                wrapped_cells.append("\n".join(wrapped))
                row_height_mm = max(row_height_mm, len(wrapped) * line_height_mm + 2 * padding_mm)

            x_mm = self._left_margin_mm() + max(0.0, (available_width_mm - table_total_width_mm) / 2.0)
            for col_index, cell_text in enumerate(wrapped_cells):
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

                if background:
                    page_builder.filled_rect(
                        _mm_to_pt(x_mm),
                        y_pt,
                        _mm_to_pt(width_mm),
                        _mm_to_pt(row_height_mm),
                        *background,
                    )
                page_builder.stroke_rect(_mm_to_pt(x_mm), y_pt, _mm_to_pt(width_mm), _mm_to_pt(row_height_mm))
                page_builder.font(row_font, table_font)
                page_builder.text_in_rect(
                    _mm_to_pt(x_mm + padding_mm),
                    y_pt + _mm_to_pt(padding_mm),
                    _mm_to_pt(width_mm - 2 * padding_mm),
                    _mm_to_pt(row_height_mm - 2 * padding_mm),
                    cell_text,
                    "center",
                )
                x_mm += width_mm
            cursor_y_mm += row_height_mm

        cursor_y_mm, _ = self._render_text_block(
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
        )
        outline_entries = [(1, f"Table {self.__table_idx}: {block.title}")]
        self.__table_idx += 1
        return cursor_y_mm + 1.0, outline_entries

    def _render_toc_page(
        self, page_builder, page_width_mm: float, page_height_mm: float, outline_entries: list[tuple[int, str, int]]
    ) -> None:
        cursor_y_mm = self._top_margin_mm() + 5.0
        cursor_y_mm, _ = self._render_text_block(
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
        )
        cursor_y_mm += 3.0
        left_pt = _mm_to_pt(self._left_margin_mm())
        available_width_pt = _mm_to_pt(self._effective_width_mm(page_width_mm))
        page_builder.font(_font_name(self.report_specs.font), 12.0)
        for level, title, page_number in outline_entries:
            prefix = " " * level * 4
            y_pt = _mm_to_pt(page_height_mm - cursor_y_mm - _pt_to_mm(12.0 * 1.2))
            page_builder.text_in_rect(
                left_pt,
                y_pt,
                available_width_pt,
                _mm_to_pt(5.0),
                f"{prefix}{title}",
            )
            page_builder.text_in_rect(
                left_pt,
                y_pt,
                available_width_pt,
                _mm_to_pt(5.0),
                f"Page {page_number}",
                "right",
            )
            cursor_y_mm += 5.5

    def save_pdf(self, file_path: str, file_name: str | None = None) -> str:
        """Save pdf."""
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

        self.__figure_idx = 1
        self.__table_idx = 1
        outline_entries: list[tuple[int, str, int]] = []
        total_pages = len(pages)

        for page_number, page in enumerate(pages, start=1):
            page_width_mm, page_height_mm = _page_size_mm(page.page_format, page.portrait)
            page_builder = builder.page(_mm_to_pt(page_width_mm), _mm_to_pt(page_height_mm))

            if page.kind == "cover":
                self._render_header(page_builder, page_width_mm, page_height_mm)
                self._render_cover_page(page_builder, page_width_mm, page_height_mm)
                self._render_footer(page_builder, page_width_mm, page_number, total_pages)
            elif page.kind == "toc":
                self._render_header(page_builder, page_width_mm, page_height_mm)
                self._render_toc_page(page_builder, page_width_mm, page_height_mm, outline_entries)
                self._render_footer(page_builder, page_width_mm, page_number, total_pages)
            else:
                self._render_header(page_builder, page_width_mm, page_height_mm)
                cursor_y_mm = self._top_margin_mm() + 2.0
                for block in page.blocks:
                    if isinstance(block, _PdfOxideTextBlock):
                        cursor_y_mm, added_outline = self._render_text_block(
                            page_builder, block, cursor_y_mm, page_width_mm, page_height_mm
                        )
                        for level, title in added_outline:
                            outline_entries.append((level, title, page_number))
                    elif isinstance(block, _PdfOxideSpacerBlock):
                        cursor_y_mm += block.lines * _pt_to_mm(self.report_specs.text_font_size)
                    elif isinstance(block, _PdfOxideImageBlock):
                        cursor_y_mm, added_outline = self._render_image_block(
                            page_builder, block, cursor_y_mm, page_width_mm, page_height_mm
                        )
                        outline_entries.extend((level, title, page_number) for level, title in added_outline)
                    elif isinstance(block, _PdfOxideTableBlock):
                        cursor_y_mm, added_outline = self._render_table_block(
                            page_builder, block, cursor_y_mm, page_width_mm, page_height_mm
                        )
                        outline_entries.extend((level, title, page_number) for level, title in added_outline)
                self._render_footer(page_builder, page_width_mm, page_number, total_pages)

            builder = page_builder.done()

        builder.save(output_path)
        return str(output_path)
