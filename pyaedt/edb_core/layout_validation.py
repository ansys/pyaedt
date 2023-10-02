from pyaedt.generic.general_methods import pyaedt_function_handler


class LayoutValidation:
    """Manages all layout validation capabilities"""

    REPORT_DC_SHORTS = {}

    def __init__(self, pedb):
        self._pedb = pedb

    @pyaedt_function_handler()
    def dc_shorts(self, net_list=None):
        """Find DC shorts on layout.

        Parameters
        ----------
        net_list : str or list[str]
            Optional

        Returns
        -------
        List[List[str, str]]
            [[net name, net name]].

        Examples
        --------

        >>> edb = Edb("edb_file")
        >>> dc_shorts = edb.layout_validation.dc_shorts()

        """
        if not net_list:
            net_list = list(self._pedb.nets.nets.keys())
        elif isinstance(net_list, str):
            net_list = [net_list]
        _objects_list = {}
        _padstacks_list = {}
        for prim in self._pedb.modeler.primitives:
            n_name = prim.net_name
            if n_name in _objects_list:
                _objects_list[n_name].append(prim)
            else:
                _objects_list[n_name] = [prim]
        for pad in list(self._pedb.padstacks.instances.values()):
            n_name = pad.net_name
            if n_name in _padstacks_list:
                _padstacks_list[n_name].append(pad)
            else:
                _padstacks_list[n_name] = [pad]
        dc_shorts = []
        for net in net_list:
            objs = []
            for i in _objects_list.get(net, []):
                objs.append(i)
            for i in _padstacks_list.get(net, []):
                objs.append(i)

            connected_objs = objs[0].get_connected_objects()
            connected_objs.append(objs[0])
            net_dc_shorts = [obj for obj in connected_objs if not obj.net.name == net]
            if net_dc_shorts:
                if not net in self.REPORT_DC_SHORTS:
                    self.REPORT_DC_SHORTS[net] = []
                dc_nets = list(set([obj.net.name for obj in net_dc_shorts]))
                for dc in dc_nets:
                    if dc:
                        dc_shorts.append([net, dc])
                    self.REPORT_DC_SHORTS[net].append(dc)
        return dc_shorts
