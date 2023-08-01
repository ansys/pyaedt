from __future__ import absolute_import  # noreorder

from pyaedt.edb_core.edb_data.nets_data import EDBExtendedNetData

from pyaedt.generic.general_methods import pyaedt_function_handler


class EdbExtendedNets(object):
    """Manages EDB methods for nets management accessible from `Edb.nets` property.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_nets = edbapp.extended_nets
    """

    @pyaedt_function_handler()
    def __getitem__(self, name):
        """Get  a net from the Edb project.

        Parameters
        ----------
        name : str, int

        Returns
        -------
        :class:` :class:`pyaedt.edb_core.edb_data.nets_data.EDBNetsData`

        """
        if name in self.extended_nets:
            return self.extended_nets[name]
        self._pedb.logger.error("Component or definition not found.")
        return

    def __init__(self, p_edb):
        self._pedb = p_edb
        self._extended_nets = {}


    @property
    def _edb(self):
        """ """
        return self._pedb.edb_api

    @property
    def _active_layout(self):
        """ """
        return self._pedb.active_layout

    @property
    def _layout(self):
        """ """
        return self._pedb.layout

    @property
    def _cell(self):
        """ """
        return self._pedb.cell

    @property
    def db(self):
        """Db object."""
        return self._pedb.active_db

    @property
    def _logger(self):
        """Edb logger."""
        return self._pedb.logger

    @property
    def extended_nets(self):
        """Extended nets.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.nets_data.EDBExtendedNetsData`]
            Dictionary of extended nets.
        """
        for extended_net in self._layout.extended_nets:
            self._extended_nets[extended_net.GetName()] = EDBExtendedNetData(self._pedb, extended_net)
        return self._extended_nets

    @pyaedt_function_handler
    def create(self, name, net:list[str]) -> EDBExtendedNetData:
        """

        Parameters
        ----------
        name
        nets

        Returns
        -------

        """
        if name in self._extended_nets:
            self._pedb.logger.error("{} already exists.".format(name))
            return False

        extended_net = EDBExtendedNetData(self._pedb)
        extended_net = extended_net.create(name)
        if isinstance(net, str):
            extended_net.add_net(net)

        return extended_net
