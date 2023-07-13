from pyaedt.generic.general_methods import ET


class LogisticHeader(object):
    def __init__(self):
        self.owner = "Pyaedt"
        self.sender = "Ansys"
        self.enterprise = "Ansys"
        self.code = "UNKNOWN"
        self.person_name = "eba"
        self.enterprise_ref = "UNKNOWN"
        self.role_ref = "Pyaedt"

    def write_xml(self, root):  # pragma no cover
        logistic_header = ET.SubElement(root, "LogisticHeader")
        role = ET.SubElement(logistic_header, "Role")
        role.set("id", self.owner)
        role.set("roleFunction", self.sender)
        enterprise = ET.SubElement(logistic_header, "Enterprise")
        enterprise.set("id", self.enterprise)
        enterprise.set("code", self.code)
        person = ET.SubElement(logistic_header, "Person")
        person.set("name", self.person_name)
        person.set("enterpriseRef", self.enterprise_ref)
        person.set("roleRef", self.role_ref)
