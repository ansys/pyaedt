import sys

import fspy.dll_interface

_this = sys.modules[__name__]
_this._internal_dll_interface = None


def _dll_interface() -> fspy.dll_interface.DllInterface:
    if _this._internal_dll_interface is None:
        _this._internal_dll_interface = fspy.dll_interface.DllInterface(show_gui=False)
    return _this._internal_dll_interface


def api_version() -> str:
    return _dll_interface().api_version()
