# ------------------------------------------------------------------------------
#
# This Example shows how to create a pdf file using pyaedt and PDFReport. The pdf routine allows to create tables,
# and images and text. the template is applied and can be customized based on customer needs
#
# -------------------------------------------------------------------------------
import os
import sys
from pyaedt.generic.general_methods import generate_unique_name

sys.path.append(r'..\DLLs\PDFReport')
import clr
clr.AddReference("AnsysReport")
from pyaedt.application.DataHandlers import create_table_for_csharp
import AnsysReport

report = AnsysReport.CreatePdfReport()

project_dir = os.path.join(os.environ['TEMP'], generate_unique_name('Example', n=16))
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
print('project_dir: ' + project_dir)


report.Specs.ModelName = "car.step"
report.Specs.Revision = "Rev1"

report.Specs.AnsysVersion = "2021R1"
report.Specs.ProjectName = "MyProject"
report.AddAnsysHeader()
report.AddFirstPage()
section2 = report.CreateNewSection()

report.AddChapter("Simulation Results")
text = "The project name is " + report.Specs.ProjectName + "."
report.AddText(text)
imagefile = os.path.join(os.path.dirname(__file__), "Examples_Files", "ReportFiles", "powertree.png")
report.AddImageWithCaption(imagefile, "Power Tree", 13)

section3 = report.CreateNewSection("L")
imagefile = os.path.join(os.path.dirname(__file__), "Examples_Files", "ReportFiles", "PWR_GND.png")
report.AddChapter("Layer Power Results")
report.AddImageWithCaption(imagefile, "Power on GND Layer", 13)
section4 = report.CreateNewSection()
report.AddChapter("Voltage Sources")

my_table = [["VoltageSource", "Value"], ["V1", "1V"]]

mytable = create_table_for_csharp(my_table, True)
report.AddTableFromList("Voltage Sources", mytable, True, True)

report.AddImageWithCaption(imagefile, "Power on GND Layer", 13)
report.AddTableOfContent()
filename = report.SavePDF(project_dir)
os.startfile(os.path.join(project_dir, filename))
