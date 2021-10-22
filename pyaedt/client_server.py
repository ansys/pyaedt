import warnings
try:
    import rpyc
    from rpyc.utils.server import ThreadedServer
except ImportError:
    warnings.warn("rpyc is needed to run the service")

from pyaedt.generic.rpyc_services import GlobalService


def pyaedt_server(hostname, port=18000):
    """Starts an rpyc servers an start listening on specified port. This method has to run on server machine.

    Parameters
    ----------
    hostname : str
        name of the remote machine to connect.
    port : int, optional
        port on which rpyc_server whill listen.


    """
    safe_attrs = {'__abs__', '__add__', '__and__', '__bool__', '__code__', '__cmp__', '__contains__', '__delitem__',
                  '__delslice__', '__div__', '__divmod__', '__doc__', '__eq__', '__float__', '__floordiv__', '__func__',
                  '__ge__',
                  '__getitem__', '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__', '__idiv__',
                  '__ifloordiv__',
                  '__ilshift__', '__imod__', '__imul__', '__index__', '__int__', '__invert__', '__ior__', '__ipow__',
                  '__irshift__', '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__', '__long__',
                  '__lshift__', '__lt__', '__mod__', '__mul__', '__name__', '__ne__', '__neg__', '__new__',
                  '__nonzero__',
                  '__oct__', '__or__', '__pos__', '__pow__', '__radd__', '__rand__', '__rdiv__', '__rdivmod__',
                  '__repr__',
                  '__rfloordiv__', '__rlshift__', '__rmod__', '__rmul__', '__ror__', '__rpow__', '__rrshift__',
                  '__rshift__', '__rsub__', '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__str__',
                  '__sub__',
                  '__truediv__', '__xor__', 'next', '__length_hint__', '__enter__', '__exit__', '__next__',
                  '__format__'}
    t = ThreadedServer(GlobalService, hostname=hostname, port=port,
                       protocol_config={'sync_request_timeout': None, 'allow_public_attrs': True, 'allow_setattr': True,
                                        'safe_attrs': safe_attrs,
                                        'allow_delattr': True})
    t.start()


def pyaedt_client(hostname, server_port=18000):
    """Starts an rpyc client and connects to a remote machine.

    Parameters
    ----------
    hostname : str
        name of the remote machine to connect.
    server_port : int, optional
        port on which rpyc_server is running

    Returns
    -------
    rpyc object.

    Examples
    --------
    >>> client = pyaedt_client("my_server")
    >>> hfss = client.root.hfss(specified_version="2021.2")

    """
    c = rpyc.connect(hostname, server_port, config={'sync_request_timeout': None})
    port = c.root.start_service(hostname)
    return rpyc.connect(hostname, port, config={'sync_request_timeout': None})
