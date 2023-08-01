from __future__ import absolute_import  # noreorder

from pyaedt.edb_core.edb_data.nets_data import EDBExtendedNetData
from pyaedt.edb_core.edb_data.nets_data import EDBDifferentialPairData
from pyaedt.edb_core.edb_data.nets_data import EDBNetsData

from pyaedt.generic.general_methods import pyaedt_function_handler


class EdbCommon:
    def __init__(self, pedb):
        self._pedb = pedb

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

class EdbExtendedNets(EdbCommon, object):
    """Manages EDB methods for nets management accessible from `Edb.extended_nets` property.

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
        :class:` :class:`pyaedt.edb_core.edb_data.nets_data.EDBExtendedNetsData`

        """
        if name in self.extended_nets:
            return self.extended_nets[name]
        self._pedb.logger.error("Component or definition not found.")
        return

    def __init__(self, p_edb):
        super().__init__(p_edb)
        self._extended_nets = {}


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
        api_extended_net = extended_net.api_create(name)
        if isinstance(net, str):
            api_extended_net.add_net(net)
        else:
            api_extended_net.add_nets(net)

        return self.extended_nets[name]


class EdbDifferentialPair(EdbCommon, object):
    """Manages EDB methods for nets management accessible from `Edb.differential_pairs` property.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_nets = edbapp.differential_pairs
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
        if name in self.differential_pairs:
            return self.differential_pairs[name]
        self._pedb.logger.error("Component or definition not found.")
        return

    def __init__(self, p_edb):
        super().__init__(p_edb)

    @property
    def differential_pairs(self):
        """Extended nets.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.nets_data.EDBExtendedNetsData`]
            Dictionary of extended nets.
        """
        diff_pairs = {}
        for diff_pair in self._layout.differential_pairs:
            diff_pairs[diff_pair.GetName()] = EDBDifferentialPairData(self._pedb, diff_pair)
        return diff_pairs

    @pyaedt_function_handler
    def create(self, name, net_p, net_n) -> EDBExtendedNetData:
        """

        Parameters
        ----------
        name
        nets

        Returns
        -------

        """
        if name in self.differential_pairs:
            self._pedb.logger.error("{} already exists.".format(name))
            return False

        diff_pair = EDBDifferentialPairData(self._pedb)
        api_diff_pair = diff_pair.api_create(name, net_p, net_n)

        return self.differential_pairs[name]


