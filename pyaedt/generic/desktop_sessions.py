import pyaedt.desktop


class DesktopSession(object):
    def __init__(self, desktop_obj):
        self.machine_name = desktop_obj.machine
        self.port = desktop_obj.port
        self.pid = desktop_obj.aedt_process_id
        self.student_version = desktop_obj.student_version
        self.aedt_version = desktop_obj.aedt_version_id
        self.desktop_object = desktop_obj


class DesktopSessions(object):
    def __init__(self):
        self.sessions = {}

    def __getitem__(self, key):
        return self.sessions[key]

    # def __setitem__(self, key, value):
    #     self.sessions[key] = DesktopSession()

    def add(self, desktop_obj):
        """

        Parameters
        ----------
        desktop_obj : class:`pyaedt.desktop.Desktop`

        """
        if not isinstance(desktop_obj, pyaedt.desktop.Desktop):
            raise TypeError("The argument must be of type `pyaedt.desktop.Desktop`")
        self.sessions[desktop_obj.aedt_process_id] = DesktopSession(desktop_obj)

    def __delitem__(self, key):
        del self.sessions[key]

    def __len__(self):
        return len(self.sessions)

    def keys(self):
        return self.sessions.keys()

    def values(self):
        return self.sessions.values()

    def items(self):
        return self.sessions.items()


_desktop_sessions = DesktopSessions()
