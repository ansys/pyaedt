from pyedb import Edb as App

from pyaedt.generic.settings import settings

log = settings.logger

log.warning("pyaedt.edb.Edb is Deprecated. Please use pyedb.Edb or pyaedt.Edb call instead")
Edb = App
