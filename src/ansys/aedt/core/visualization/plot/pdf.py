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

from dataclasses import dataclass
from dataclasses import field
import json
import os

from fpdf import FPDF
from fpdf import FontFace

from ansys.aedt.core import __version__
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.internal.checks import graphics_required


@dataclass
class ReportSpec(PyAedtBase):
    """Data class containing all report template specifications."""

    document_prefix: str = "ANSS"
    ansys_version: str = "2025R1"
    revision: str = "Rev 1.0"
    logo_name: str = os.path.join(os.path.dirname(__file__), "../../misc/Ansys.png")
    company_name: str = "Ansys Inc."
    template_name: str = os.path.join(os.path.dirname(__file__), "../../misc/AnsysTemplate.json")
    design_name: str = "Design1"
    project_name: str = "Project1"
    pyaedt_version: str = __version__
    units: str = "cm"
    top_margin: float = 3.0
    bottom_margin: float = 2.0
    left_margin: float = 1.0
    right_margin: float = 1.0
    footer_font_size: int = 7
    footer_text: str = "Copyright (c) 2023, ANSYS Inc. unauthorised use, distribution or duplication is prohibited"
    header_font_size: int = 7
    header_image_width: float = 3.3
    title_font_size: int = 14
    subtitle_font_size: int = 12
    text_font_size: int = 11
    table_font_size: int = 9
    caption_font_size: int = 9
    cover_title_font_size: int = 28
    cover_subtitle_font_size: int = 24
    font: str = "helvetica"
    chart_width: float = 16.0
    font_color: list = field(default_factory=lambda: [0, 0, 0])
    font_chapter_color: list = field(default_factory=lambda: [0, 0, 0])
    font_subchapter_color: list = field(default_factory=lambda: [0, 0, 0])
    font_header_color: list = field(default_factory=lambda: [0, 0, 0])
    font_caption_color: list = field(default_factory=lambda: [0, 0, 0])


class AnsysReport(FPDF, PyAedtBase):
    def __init__(self, version="2025R1", design_name="design1", project_name="AnsysProject", tempplate_json_file=None):
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

    def read_template(self, template_file):
        """Reade pdf template.

        template_file : str
            Path to the json template file.
        """
        if template_file:
            self.report_specs.template_name = template_file
        if os.path.exists(self.report_specs.template_name):
            with open_file(self.report_specs.template_name, "r") as f:
                tdata = json.load(f)
            self.report_specs = ReportSpec(**tdata)

    def __add_cover_page(self):
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

    def header(self):
        """Header."""
        from datetime import date

        def add_field(field_name, field_value):
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
    def footer(self):
        """Footer."""
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_x(self._left_margin)
        # Arial italic 8
        self.set_font("helvetica", "I", 8)
        self.set_text_color(*self.report_specs.font_header_color)
        # Page number
        self.cell(0, 10, self.report_specs.footer_text, 0, align="L")
        self.cell(0, 10, "Page " + str(self.page_no()) + "/{nb}", align="R")

    def create(self, add_cover_page=True, add_new_section_after=True):
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
        """
        if add_cover_page:
            self.__add_cover_page()
        if add_new_section_after:
            self.add_page("P" if self.use_portrait else "L")
        self._left_margin = self.l_margin
        return True

    def add_project_info(self, design):
        """
        Add project information.

        Parameters
        ----------
        design : object
            Starting application object. For example, ``hfss1= HFSS3DLayout``.

        Returns
        -------
        bool
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
            "Mechanical",
            "Maxwell 2D",
            "2D Extractor",
        ]:
            msg = f"Simulation bounding box is {design.modeler.get_model_bounding_box()}."
            self.add_text(msg)
            image_path = os.path.join(design.working_directory, "model.jpg")
            design.plot(
                show=False,
                export_path=image_path,
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
            msg = f"The schematic has {len(design.modeler.components.components)} components."
            self.add_text(msg)

        if design.setups:
            msg = f"The design has {len(design.setups)} simulation setups."
            self.add_text(msg)

        return True

    @property
    def template_name(self):
        """Name of the template to use.

        It can be a full json path or a string of a json contained in ``"Images"`` folder.

        Returns
        -------
        str
        """
        return self.report_specs.template_name

    @template_name.setter
    def template_name(self, value):
        self.report_specs.template_name = value

    @property
    def design_name(self):
        """Get/set the design name for report header.

        Returns
        -------
        str
        """
        return self.report_specs.design_name

    @design_name.setter
    def design_name(self, value):
        self.report_specs.design_name = value

    @property
    def project_name(self):
        """Get/set the project name for report header.

        Returns
        -------
        str
        """
        return self.report_specs.project_name

    @project_name.setter
    def project_name(self, value):
        self.report_specs.project_name = value

    @property
    def aedt_version(self):
        """Get/set the aedt version for report header.

        Returns
        -------
        str
        """
        return self.report_specs.ansys_version

    @aedt_version.setter
    def aedt_version(self, value):
        self.report_specs.ansys_version = value

    def add_section(self, portrait=None, page_format="a4"):
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
        """
        orientation = "portrait"
        if portrait is False:
            orientation = "landscape"
        elif portrait is None:
            orientation = "P" if self.use_portrait else "L"
        self.add_page(orientation=orientation, format=page_format)

    def add_chapter(self, chapter_name):
        """Add a new chapter.

        Parameters
        ----------
        chapter_name : str
            Chapter name.
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

    def add_sub_chapter(self, chapter_name):
        """Add a new sub-chapter.

        Parameters
        ----------
        chapter_name : str
            Chapter name.
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
        path,
        caption="",
        width=0,
        height=0,
    ):
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
        """
        if width == 0:
            width = self.epw

        self.image(path, h=height, w=width, x=self.epw / 2 - width / 2 + self._left_margin)
        if caption:
            caption = f"Figure {self.__figure_idx}. {caption}"
            self.add_caption(caption)
            self.__figure_idx += 1
        return True

    def add_image_with_aspect_ratio(self, path, caption="", max_width=None, max_height=None):
        """
        Add an image to the PDF while maintaining its aspect ratio and fitting within the specified dimensions.

        Parameters
        ----------
        path: str
            Path to the image file.
        max_width: float, int, optional
            Maximum width available for the image.
        max_height: float, int, optional
            Maximum height available for the image.
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

    def add_caption(self, content):
        """Add a new caption.

        Parameters
        ----------
        content : str
            Caption name.

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

    def add_empty_line(self, num_lines=1):
        """Add a new empty line.

        Parameters
        ----------
        num_lines : int, optional
            Number of lines to add.
        """
        self.ln(num_lines * self.font_size)

    def add_page_break(self):
        """Add a new page break line."""
        self.add_page("P" if self.use_portrait else "L")

    def add_table(
        self,
        title,
        content,
        formatting=None,
        col_widths=None,
    ):
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

    def add_text(self, content, bold=False, italic=False):
        """Add a new text.

        Parameters
        ----------
        content : str
            Text content.
        bold : bool, optional
            Whether if text is bold or not. Default is ``True``.
        italic : bool, optional
            Whether if text is italic or not. Default is ``True``.
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

    def add_toc(self):
        """Add toc."""

        def p(section, **kwargs):
            # Inserts a paragraph
            self.cell(w=self.epw, h=self.font_size, text=section, new_x="LMARGIN", new_y="NEXT", **kwargs)

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

    def save_pdf(self, file_path, file_name=None):
        """Save pdf.

        Parameters
        ----------
        file_path : str
            Pdf path.
        file_name : str, optional
            File name.
        """
        self.output(os.path.join(file_path, file_name))
        return os.path.join(file_path, file_name)

    @graphics_required
    def add_chart(self, x_values, y_values, x_caption, y_caption, title):
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
