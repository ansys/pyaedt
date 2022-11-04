class EdbBuilder(object):
    """Provides a data class to overcome EdbLib class limitations in Linux."""

    def __init__(self, edbutils, db, cell):
        self.EdbHandler = edbutils.EdbHandler()
        self.EdbHandler.dB = db
        self.EdbHandler.cell = cell
        self.EdbHandler.layout = cell.GetLayout()
