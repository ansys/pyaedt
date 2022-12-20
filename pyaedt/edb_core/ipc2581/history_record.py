from datetime import date

from pyaedt.generic.general_methods import ET


class HistoryRecord(object):
    def __init__(self):
        self.number = "1"
        self.origination = date.today()
        self.software = "Ansys Pyaedt"
        self.last_changes = date.today()
        self.file_revision = "1"
        self.comment = ""
        self.software_package = "Ansys AEDT"
        self.revision = "R2023.1"
        self.vendor = "Ansys"
        self.certification_status = "CERTIFIED"

    def write_xml(self, root):  # pragma no cover
        history_record = ET.SubElement(root, "HistoryRecord")
        history_record.set("number", self.number)
        history_record.set(
            "origination", "{}_{}_{}".format(self.origination.day, self.origination.month, self.origination.year)
        )
        history_record.set("software", self.software)
        history_record.set(
            "lastChange", "{}_{}_{}".format(self.origination.day, self.origination.month, self.origination.year)
        )
        file_revision = ET.SubElement(history_record, "FileRevision")
        file_revision.set("fileRevisionId", self.file_revision)
        file_revision.set("comment", self.comment)
        software_package = ET.SubElement(file_revision, "SoftwarePackage")
        software_package.set("name", self.software_package)
        software_package.set("revision", self.revision)
        software_package.set("vendor", self.vendor)
        certification = ET.SubElement(software_package, "Certification")
        certification.set("certificationStatus", self.certification_status)
