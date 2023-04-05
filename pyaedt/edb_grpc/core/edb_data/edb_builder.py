class EdbBuilder(object):
    """Provides a data class to overcome EdbLib class limitations in Linux."""

    def __init__(self, db, cell):
        self.dB = db
        self.cell = cell
        self.layout = cell.layout
