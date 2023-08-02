from __future__ import absolute_import  # noreorder

from typing import Union

from pyaedt.edb_core.edb_data.nets_data import EDBDifferentialPairData
from pyaedt.edb_core.edb_data.nets_data import EDBExtendedNetData
from pyaedt.generic.general_methods import pyaedt_function_handler


class EdbCommon:
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def _layout(self):
        """Get layout.

        Returns
        -------
        :class:` :class:`pyaedt.edb_core.dotnet.layout.LayoutDotNet`
        """
        return self._pedb.layout

    @property
    def _logger(self):
        """EDB logger."""
        return self._pedb.logger


class EdbExtendedNets(EdbCommon, object):
    """Manages EDB methods for managing nets accessible from the ``Edb.extended_nets`` property.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_nets = edbapp.extended_nets
    """

    @pyaedt_function_handler()
    def __getitem__(self, name):
        """Get  a net from the EDB project.

        Parameters
        ----------
        name : str, int
            Name or ID of the net.

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

    @property
    def extended_nets(self):
        """Extended nets.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.nets_data.EDBExtendedNetsData`]
            Dictionary of extended nets.
        """
        nets = {}
        for extended_net in self._layout.extended_nets:
            nets[extended_net.GetName()] = EDBExtendedNetData(self._pedb, extended_net)
        return nets

    @pyaedt_function_handler
    def create(self, name, net: Union[str, list[str]]) -> EDBExtendedNetData:
        """

        Parameters
        ----------
        name : str
            Name of the extended net.
        net : str, list
           Name of the nets to be added into this extended net.

        Returns
        -------
        :class:` :class:`pyaedt.edb_core.edb_data.nets_data.EDBExtendedNetsData`
        """
        if name in self.extended_nets:
            self._pedb.logger.error("{} already exists.".format(name))
            return False

        extended_net = EDBExtendedNetData(self._pedb)
        api_extended_net = extended_net.api_create(name)
        if isinstance(net, str):
            net = [net]
        for i in net:
            api_extended_net.add_net(i)

        return self.extended_nets[name]


class EdbDifferentialPair(EdbCommon, object):
    """Manages EDB methods for managing nets accessible from the ``Edb.differential_pairs`` property.

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
            Name or ID of the net.

        Returns
        -------
        :class:` :class:`pyaedt.edb_core.edb_data.nets_data.EDBDifferentialPairData`

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
        dict[str, :class:`pyaedt.edb_core.edb_data.nets_data.EDBDifferentialPairData`]
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
        name : str
            Name of the differential pair.
        net_p : str
            Name of the positive net.
        net_n : str
            Name of the negative net.

        Returns
        -------
        :class:` :class:`pyaedt.edb_core.edb_data.nets_data.EDBDifferentialPairData`
        """
        if name in self.differential_pairs:
            self._pedb.logger.error("{} already exists.".format(name))
            return False

        diff_pair = EDBDifferentialPairData(self._pedb)
        diff_pair.api_create(name, net_p, net_n)

        return self.differential_pairs[name]
