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
from tkinter import ttk
import webbrowser


def create_help_tab_ui(tab_frame, app_instance):
    # Create main frame
    main_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    main_frame.pack(fill="both", expand=True)

    # Documentation links section
    doc_frame = ttk.LabelFrame(main_frame, text="Documentation", style="PyAEDT.TLabelframe")
    doc_frame.pack(fill="x", padx=5, pady=5)
    doc_frame.pack_forget()

    # Check if PDF file exists
    pdf_path = os.path.join(os.path.dirname(__file__), "user_manual.pdf")

    if os.path.exists(pdf_path):
        # Create hyperlink button
        def open_pdf():
            webbrowser.open(pdf_path)

        link = ttk.Button(doc_frame, text="Open User Manual (PDF)", command=open_pdf, style="PyAEDT.TButton")
        link.pack(pady=10)
    else:
        pass
        ttk.Label(doc_frame, text="PDF documentation not found", style="PyAEDT.TLabel").pack(pady=10)

    # Project information section below
    info_frame = ttk.LabelFrame(main_frame, text="Information", style="PyAEDT.TLabelframe")
    info_frame.pack(fill="x", padx=5, pady=5)

    # Project information content
    info_content = ttk.Frame(info_frame, style="PyAEDT.TFrame")
    info_content.pack(fill="both", expand=True, padx=10, pady=5)

    # Use Grid layout to better organize information
    row = 0

    # Version information
    ttk.Label(info_content, text="Version:", font=("Arial", 10, "bold"), style="PyAEDT.TLabel").grid(
        row=row, column=0, sticky="w", pady=(5, 0)
    )
    ttk.Label(info_content, text="0.1", style="PyAEDT.TLabel").grid(row=row, column=1, sticky="w")

    row += 1
    # Author information
    ttk.Label(info_content, text="Authors:", font=("Arial", 10, "bold"), style="PyAEDT.TLabel").grid(
        row=row, column=0, sticky="w", pady=(15, 0)
    )
    authors = [
        "Hui Zhou - Maintainer",
        "Zhen Guo - Maintainer",
        "Haiwen Zhang - Maintainer",
        "Johnny Feng - Documentation",
    ]
    for author in authors:
        row += 1
        ttk.Label(info_content, text=f"• {author}", style="PyAEDT.TLabel").grid(row=row, column=0, columnspan=2, sticky="w", padx=20)

    row += 1
    # Contact information
    ttk.Label(info_content, text="Contact:", font=("Arial", 10, "bold"), style="PyAEDT.TLabel").grid(
        row=row, column=0, sticky="w", pady=(15, 0)
    )
    row += 1
    ttk.Label(info_content, text="Email: support@ansy.com", style="PyAEDT.TLabel").grid(row=row, column=0, columnspan=2, sticky="w", padx=20)
    row += 1
    ttk.Label(info_content, text="Website: https://www.ansys.com", style="PyAEDT.TLabel").grid(
        row=row, column=0, columnspan=2, sticky="w", padx=20
    )

    row += 1
    # Copyright information
    ttk.Label(info_content, text="Copyright:", font=("Arial", 10, "bold"), style="PyAEDT.TLabel").grid(
        row=row, column=0, sticky="w", pady=(15, 0)
    )
    row += 1
    ttk.Label(info_content, text="© 2025 Ansys. All rights reserved.", style="PyAEDT.TLabel").grid(
        row=row, column=0, columnspan=2, sticky="w", padx=20
    )

    # Configure column weights
    info_content.grid_columnconfigure(1, weight=1)
