Generate report
===============

The Generate Report extension creates a PDF report for the active AEDT design.
The generated report includes the design results currently available as plots in AEDT.

How to use
==========

1. Open the AEDT project and design whose plots you want to include in the report.
2. In the Extension Manager, select **Generate report**.
3. Enter a report name.
4. Optionally, select a folder in which to save the PDF. If no folder is selected, the PDF is saved in the design working directory.
5. Select **Open report after generation** to open the PDF automatically on Windows.
6. Click **Generate Report**.

The extension creates a PDF with a table of contents and a section containing the plots available in the active design.

Output
======

The generated file is named ``<report_name>.pdf``. The AEDT message manager reports the full path after the report is created.

API usage example
=================

The extension is launched from AEDT using the PyAEDT Extension Manager. You can also run it standalone:

.. code:: bash

   python create_report.py
