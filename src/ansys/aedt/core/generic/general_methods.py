# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import datetime
import difflib
import functools
from functools import update_wrapper
import getpass
import inspect
import itertools
import logging
import os
import platform
import re
import sys
import time
import traceback
import warnings

import psutil

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.numbers_utils import _units_assignment
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.internal.errors import GrpcApiError
from ansys.aedt.core.internal.errors import MethodNotSupportedError

system = platform.system()
is_linux = system == "Linux"
is_windows = system == "Windows"
is_macos = system == "Darwin"

inside_desktop_ironpython_console = True if "4.0.30319.42000" in sys.version else False

inclusion_list = [
    "CreateVia",
    "PasteDesign",
    "Paste",
    "PushExcitations",
    "Rename",
    "RestoreProjectArchive",
    "ImportGerber",
    "EditSources",
]


def _write_mes(mes_text):
    mes_text = str(mes_text)
    parts = [mes_text[i : i + 250] for i in range(0, len(mes_text), 250)]
    for el in parts:
        settings.logger.error(el)


def _get_args_dicts(func, args, kwargs):
    if int(sys.version[0]) > 2:
        args_name = list(dict.fromkeys(inspect.getfullargspec(func)[0] + list(kwargs.keys())))
        args_dict = dict(list(itertools.zip_longest(args_name, args)) + list(kwargs.items()))
    else:
        args_name = list(dict.fromkeys(inspect.getargspec(func)[0] + list(kwargs.keys())))
        args_dict = dict(list(itertools.izip(args_name, args)) + list(kwargs.iteritems()))
    return args_dict


def _exception(ex_info, func, args, kwargs, message="Type Error"):
    """Write the trace stack to the desktop when a Python error occurs.

    Parameters
    ----------
    ex_info :

    func :

    args :

    kwargs :

    message :
         (Default value = "Type Error")

    Returns
    -------

    """
    header = "**************************************************************"
    _write_mes(header)
    tb_data = ex_info[2]
    tb_trace = traceback.format_tb(tb_data)

    for trace in traceback.format_stack():
        exceptions = [
            "_exception",
            "pydev",
            "traceback",
            "user_function",
            "__Invoke__",
            "interactiveshell",
            "async_helpers",
            "plugins",
        ]
        if any(exc in trace for exc in exceptions) or ("site-packages" in trace and "pyaedt" not in trace):
            continue
        for el in trace.split("\n"):
            _write_mes(el)
    for trace in tb_trace:
        exceptions = [
            "_exception",
            "pydev",
            "traceback",
            "user_function",
            "__Invoke__",
            "interactiveshell",
            "async_helpers",
            "plugins",
        ]
        if any(exc in trace for exc in exceptions) or ("site-packages" in trace and "pyaedt" not in trace):
            continue
        tblist = trace.split("\n")
        for el in tblist:
            if el:
                _write_mes(el)

    _write_mes(f"{message} on {func.__name__}")

    message_to_print = ""
    messages = ""
    from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

    if len(list(_desktop_sessions.values())) == 1:
        try:
            messages = list(list(_desktop_sessions.values())[0].odesktop.GetMessages("", "", 2))[-1].lower()
        except (GrpcApiError, AttributeError, TypeError, IndexError):
            pass
    if "[error]" in messages:
        message_to_print = messages[messages.index("[error]") :]

    if message_to_print:
        _write_mes("Last Electronics Desktop Message - " + message_to_print)

    try:
        args_dict = _get_args_dicts(func, args, kwargs)
        first_time_log = True

        for el in args_dict:
            if el != "self" and args_dict[el]:
                if first_time_log:
                    _write_mes("Method arguments: ")
                    first_time_log = False
                _write_mes(f"    {el} = {args_dict[el]} ")
    except Exception:
        pyaedt_logger.error("An error occurred while parsing and logging an error with method {}.")

    _write_mes(header)


def _check_types(arg):
    if "netref.builtins.list" in str(type(arg)):
        return "list"
    elif "netref.builtins.dict" in str(type(arg)):
        return "dict"
    elif "netref.__builtin__.list" in str(type(arg)):
        return "list"
    elif "netref.__builtin__.dict" in str(type(arg)):
        return "dict"
    return ""


def raise_exception_or_return_false(e):
    if not settings.enable_error_handler:
        if settings.release_on_exception:
            from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

            for v in list(_desktop_sessions.values())[:]:
                if v.launched_by_pyaedt:
                    v.close_desktop()
                else:
                    v.release_desktop(False, False)
        raise e
    elif "__init__" in str(e):  # pragma: no cover
        return
    else:
        return False


def _function_handler_wrapper(user_function, **deprecated_kwargs):
    def wrapper(*args, **kwargs):
        if deprecated_kwargs and kwargs:
            deprecate_kwargs(user_function.__name__, kwargs, deprecated_kwargs)
        try:
            settings.time_tick = time.time()
            out = user_function(*args, **kwargs)
            _log_method(user_function, args, kwargs)
            return out
        except MethodNotSupportedError as e:
            message = "This method is not supported in current AEDT design type."
            if settings.enable_screen_logs:
                pyaedt_logger.error("**************************************************************")
                pyaedt_logger.error(f"PyAEDT error on method {user_function.__name__}:  {message}. Check again")
                pyaedt_logger.error("**************************************************************")
                pyaedt_logger.error("")
            if settings.enable_file_logs:
                settings.error(message)
            return raise_exception_or_return_false(e)
        except GrpcApiError as e:
            _exception(sys.exc_info(), user_function, args, kwargs, "AEDT API Error")
            return raise_exception_or_return_false(e)
        except BaseException as e:
            _exception(sys.exc_info(), user_function, args, kwargs, str(sys.exc_info()[1]).capitalize())
            return raise_exception_or_return_false(e)

    return wrapper


def deprecate_kwargs(func_name, kwargs, aliases):
    """Use helper function for deprecating function arguments."""
    for alias, new in aliases.items():
        if alias in kwargs:
            if new in kwargs:
                msg = f"{func_name} received both {alias} and {new} as arguments!\n"
                msg += f"{alias} is deprecated, use {new} instead."
                raise TypeError(msg)
            pyaedt_logger.warning(f"Argument `{alias}` is deprecated for method `{func_name}`; use `{new}` instead.")
            kwargs[new] = kwargs.pop(alias)


def deprecate_argument(arg_name: str, version: str = None, message: str = None, removed: bool = False):
    """
    Decorator to deprecate a specific argument (positional or keyword) in a function.

    Parameters
    ----------
        arg_name : str
            The name of the deprecated argument.
        version : str
            The version in which the argument was removed.
        message : str, optional
            Custom deprecation message.
        removed : bool
            If ``True``, using the argument raises a TypeError.
            If ``False``, a DeprecationWarning is issued.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            try:
                bound_args = sig.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()
            except TypeError:
                # In case of incomplete binding (e.g. missing required args), skip
                return func(*args, **kwargs)

            if arg_name in bound_args.arguments:
                msg_version = ""
                if version:
                    msg_version = f" in version {version}"
                if removed:
                    raise TypeError(
                        message or f"Argument '{arg_name}' was removed{msg_version} and is no longer supported."
                    )
                else:
                    warn_msg = message or f"Argument '{arg_name}' is deprecated and will be removed{msg_version}."
                    warnings.warn(warn_msg, DeprecationWarning, stacklevel=2)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def pyaedt_function_handler(direct_func=None, **deprecated_kwargs):
    """Provide an exception handler, logging mechanism, and argument converter for client-server communications.

    This method returns the function itself if correctly executed. Otherwise, it returns ``False``
    and displays errors.

    """
    if callable(direct_func):
        user_function = direct_func
        wrapper = _function_handler_wrapper(user_function, **deprecated_kwargs)
        return update_wrapper(wrapper, user_function)
    elif direct_func is not None:
        raise TypeError("Expected first argument to be a callable, or None")

    def decorating_function(user_function):
        wrapper = _function_handler_wrapper(user_function, **deprecated_kwargs)
        return update_wrapper(wrapper, user_function)

    return decorating_function


@pyaedt_function_handler()
def check_numeric_equivalence(a, b, relative_tolerance=1e-7):
    """Check if two numeric values are equivalent to within a relative tolerance.

    Parameters
    ----------
    a : int, float
        Reference value to compare to.
    b : int, float
        Secondary value for the comparison.
    relative_tolerance : float, optional
        Relative tolerance for the equivalence test. The difference is relative to the first value.
        The default is ``1E-7``.

    Returns
    -------
    bool
        ``True`` if the two passed values are equivalent, ``False`` otherwise.
    """
    if abs(a) > 0.0:
        reldiff = abs(a - b) / a
    else:
        reldiff = abs(b)
    return True if reldiff < relative_tolerance else False


def _log_method(func, new_args, new_kwargs):
    if not (settings.enable_debug_logger or settings.enable_debug_edb_logger):
        return
    if not settings.enable_debug_internal_methods_logger and str(func.__name__)[0] == "_":
        return
    if not settings.enable_debug_geometry_operator_logger and "GeometryOperators" in str(func):
        return
    if (
        not settings.enable_debug_edb_logger
        and "Edb" in str(func) + str(new_args)
        or "edb_core" in str(func) + str(new_args)
    ):
        return
    line_begin = "ARGUMENTS: "
    message = []
    delta = time.time() - settings.time_tick
    m, s = divmod(delta, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    msec = (s - int(s)) * 1000
    if d > 0:
        time_msg = f" {d}days {h}h {m}m {int(s)}sec."
    elif h > 0:
        time_msg = f" {h}h {m}m {int(s)}sec."
    else:
        time_msg = f"  {m}m {s}sec {int(msec)}msec."
    if settings.enable_debug_methods_argument_logger:
        args_dict = _get_args_dicts(func, new_args, new_kwargs)
        id = 0
        if new_args:
            object_name = str([new_args[0]])[1:-1]
            id = object_name.find(" object at ")
        if id > 0:
            object_name = object_name[1:id]
            message.append(f"'{object_name + '.' + str(func.__name__)}' was run in {time_msg}")
        else:
            message.append(f"'{str(func.__name__)}' was run in {time_msg}")
        message.append(line_begin)
        for k, v in args_dict.items():
            if k != "self":
                message.append(f"    {k} = {v}")
    for m in message:
        settings.logger.debug(m)


@pyaedt_function_handler()
def get_version_and_release(input_version):
    """Convert the standard five-digit AEDT version format to a tuple of version and release.
    Used for environment variable management.
    """
    version = int(input_version[2:4])
    release = int(input_version[5])
    if version < 20:
        if release < 3:
            version -= 1
        else:
            release -= 2
    return (version, release)


@pyaedt_function_handler()
def _normalize_version_to_string(input_version):
    """Convert various AEDT version formats to a standard five-digit string format.
    Used to check and convert the version user input to a standard format.
    If the input is ``None``, return ``None``.
    """
    error_msg = (
        "Version argument is not valid.\n"
        "Accepted formats are:\n"
        " - 3-digit format (e.g., '232')\n"
        " - 5-digit format (e.g., '2023.2')\n"
        " - Float format (e.g., 2023.2 or 23.2)\n"
        " - Integer format (e.g., 232)\n"
        " - Release format with 'R' (e.g., '2023R2' or '23R2')"
    )
    if input_version is None:
        return None
    if not isinstance(input_version, (str, int, float)):
        raise ValueError(error_msg)
    input_version_str = str(input_version)
    # Matches 2000.0 – 2099.9 style floats and strings
    if re.match(r"^20\d{2}\.\d$", input_version_str):
        return input_version_str
    # Matches 00.0 – 99.9 style floats and strings
    elif re.match(r"^\d{2}\.\d$", input_version_str):
        return "20" + input_version_str
    # Matches 000 – 999 style ints and strings
    elif re.match(r"^\d{3}$", input_version_str):
        return f"20{input_version_str[:2]}.{input_version_str[-1]}"
    # Matches "2025R2" or "2025 R2" string
    elif re.match(r"^20\d{2}\s?R\d$", input_version_str):
        return input_version_str.replace("R", ".").replace(" ", "")
    # Matches "25R2" or "25 R2" string
    elif re.match(r"^\d{2}\s?R\d$", input_version_str):
        return "20" + input_version_str.replace("R", ".").replace(" ", "")
    else:
        raise ValueError(error_msg)


@pyaedt_function_handler()
def _is_version_format_valid(version):
    """Check if the internal version format is valid.
    Version must be a string in the five-digit format (e.g., '2023.2').
    It can optionally end with 'SV' for student versions.
    """
    if not isinstance(version, str):
        return False
    return bool(re.match(r"^\d{4}\.[1-9]\d*(SV)?$", version))


@pyaedt_function_handler()
def env_path(input_version):
    """Get the path of the version environment variable for an AEDT version.

    Parameters
    ----------
    input_version : str
        AEDT version.

    Returns
    -------
    str
        Path of the version environment variable.

    Examples
    --------
    >>> env_path_student("2025.2")
    "C:/Program Files/ANSYSEM/ANSYSEM2025.2/Win64"
    """
    return os.getenv(
        f"ANSYSEM_ROOT{get_version_and_release(input_version)[0]}{get_version_and_release(input_version)[1]}", ""
    )


@pyaedt_function_handler()
def env_value(input_version):
    """Get the name of the version environment variable for an AEDT version.

    Parameters
    ----------
    input_version : str
        AEDT version.

    Returns
    -------
    str
        Name of the version environment variable.

    Examples
    --------
    >>> env_value(2025.2)
    "ANSYSEM_ROOT252"
    """
    return f"ANSYSEM_ROOT{get_version_and_release(input_version)[0]}{get_version_and_release(input_version)[1]}"


@pyaedt_function_handler()
def env_path_student(input_version):
    """Get the path of the version environment variable for an AEDT student version.

    Parameters
    ----------
    input_version : str
       AEDT student version.

    Returns
    -------
    str
        Path of the student version environment variable.

    Examples
    --------
    >>> env_path_student(2025.2)
    "C:/Program Files/ANSYSEM/ANSYSEM2025.2/Win64"
    """
    return os.getenv(
        f"ANSYSEMSV_ROOT{get_version_and_release(input_version)[0]}{get_version_and_release(input_version)[1]}",
        "",
    )


@pyaedt_function_handler()
def env_value_student(input_version):
    """Get the name of the version environment variable for an AEDT student version.

    Parameters
    ----------
    input_version : str
        AEDT student version.

    Returns
    -------
    str
         Name of the student version environment variable.

    Examples
    --------
    >>> env_value_student(2025.2)
    "ANSYSEMSV_ROOT252"
    """
    return f"ANSYSEMSV_ROOT{get_version_and_release(input_version)[0]}{get_version_and_release(input_version)[1]}"


def _retry_ntimes(n, function, *args, **kwargs):
    """Retry a function several times.

    Parameters
    ----------
    n : int
        The number of retries.
    function : function
        Function to retry.
    *args : tuple
        Arguments for the function.
    **kwargs : dict
        Keyword arguments for the function.

    Returns
    -------
    None
    """
    func_name = None
    try:
        if function.__name__ == "InvokeAedtObjMethod":
            func_name = args[1]
    except Exception:
        pyaedt_logger.debug("An error occurred while accessing the arguments of a function called multiple times.")
    retry = 0
    ret_val = None
    # if func_name and func_name not in inclusion_list and not func_name.startswith("Get"):
    if func_name and func_name not in inclusion_list:
        n = 1
    while retry < n:
        try:
            ret_val = function(*args, **kwargs)
        except Exception:
            retry += 1
            time.sleep(settings.retry_n_times_time_interval)
        else:
            return ret_val
    if retry == n:
        if "__name__" in dir(function):
            raise AttributeError(f"Error in Executing Method {function.__name__}.")
        else:
            raise AttributeError("Error in Executing Method.")


@pyaedt_function_handler()
def time_fn(fn, *args, **kwargs):
    start = datetime.datetime.now()
    results = fn(*args, **kwargs)
    end = datetime.datetime.now()
    fn_name = fn.__module__ + "." + fn.__name__
    delta = (end - start).microseconds * 1e-6
    print(fn_name + ": " + str(delta) + "s")
    return results


@pyaedt_function_handler(search_key1="search_key_1", search_key2="search_key_2")
def filter_tuple(value, search_key_1, search_key_2):
    """Filter a tuple of two elements with two search keywords."""
    ignore_case = True

    def _create_pattern(k1, k2):
        k1a = re.sub(r"\?", r".", k1)
        k1b = re.sub(r"\*", r".*?", k1a)
        k2a = re.sub(r"\?", r".", k2)
        k2b = re.sub(r"\*", r".*?", k2a)
        pattern = f".*\\({k1b},{k2b}\\)"
        return pattern

    if ignore_case:
        compiled_re = re.compile(_create_pattern(search_key_1, search_key_2), re.IGNORECASE)
    else:
        compiled_re = re.compile(_create_pattern(search_key_1, search_key_2))

    m = compiled_re.search(value)
    if m:
        return True
    return False


@pyaedt_function_handler(search_key1="search_key_1")
def filter_string(value, search_key_1):
    """Filter a string"""
    ignore_case = True

    def _create_pattern(k1):
        k1a = re.sub(r"\?", r".", k1.replace("\\", "\\\\"))
        k1b = re.sub(r"\*", r".*?", k1a)
        pattern = f"^{k1b}$"
        return pattern

    if ignore_case:
        compiled_re = re.compile(_create_pattern(search_key_1), re.IGNORECASE)
    else:
        compiled_re = re.compile(_create_pattern(search_key_1))  # pragma: no cover

    m = compiled_re.search(value)
    if m:
        return True
    return False


@pyaedt_function_handler()
def number_aware_string_key(s):
    """Get a key for sorting strings that treats embedded digit sequences as integers.

    Parameters
    ----------
    s : str
        String to calculate the key from.

    Returns
    -------
    tuple
        Tuple of key entries.
    """

    def is_digit(c):
        return "0" <= c <= "9"

    result = []
    i = 0
    while i < len(s):
        if is_digit(s[i]):
            j = i + 1
            while j < len(s) and is_digit(s[j]):
                j += 1
            key = int(s[i:j])
            result.append(key)
            i = j
        else:
            j = i + 1
            while j < len(s) and not is_digit(s[j]):
                j += 1
            key = s[i:j]
            result.append(key)
            i = j
    return tuple(result)


@pyaedt_function_handler()
def active_sessions(version=None, student_version=False, non_graphical=False):
    """Get information for the active AEDT sessions.

    Parameters
    ----------
    version : str, optional
        Version to check. The default is ``None``, in which case all versions are checked.
        When specifying a version, you can use a three-digit format like ``"222"`` or a
        five-digit format like ``"2022.2"``.
    student_version : bool, optional
    non_graphical : bool, optional

    Returns
    -------
    dict
        {AEDT PID: port}
        If the PID corresponds to a COM session port is set to -1
    """
    return_dict = {}
    if student_version:
        keys = ["ansysedtsv.exe", "ansysedtsv"]
    else:
        keys = ["ansysedt.exe", "ansysedt"]
    if version and "." in version:
        version = version[-4:].replace(".", "")
    if version and version < "221":
        version = version[:2] + "." + version[2]

    def _normalize_user(u):
        if not u:
            return ""
        # drop domain like DOMAIN\user or any path parts, compare case-insensitive
        return str(u).split("\\")[-1].split("/")[-1].lower()

    def _current_username():
        try:
            return _normalize_user(psutil.Process(os.getpid()).username())
        except Exception:
            # fallback
            return _normalize_user(getpass.getuser())

    current_user = _current_username()

    for p in psutil.process_iter(attrs=("pid", "name", "username", "cmdline")):
        try:
            p_user = _normalize_user(p.info.get("username"))
            if p_user != current_user:
                continue  # skip processes from other users
            # process belongs to current user — safe to use p.info or p
            pid = p.info["pid"]
            name = p.info["name"]
            cmd = p.info.get("cmdline", [])
            if name in keys:
                if non_graphical and "-ng" in cmd or not non_graphical:
                    if not version or (version and version in cmd[0]):
                        if "-grpcsrv" in cmd:
                            if not version or (version and version in cmd[0]):
                                try:
                                    return_dict[pid] = int(cmd[cmd.index("-grpcsrv") + 1])
                                except (IndexError, ValueError):
                                    # default desktop grpc port.
                                    return_dict[pid] = 50051
                        else:
                            return_dict[pid] = -1
                            for i in psutil.net_connections():
                                if i.pid == pid and (i.laddr.port > 50050 and i.laddr.port < 50200):
                                    return_dict[pid] = i.laddr.port
                                    break
        except psutil.NoSuchProcess as e:  # pragma: no cover
            pyaedt_logger.debug(f"The process exited and cannot be an active session: {e}")
        except Exception as e:  # pragma: no cover
            pyaedt_logger.debug(
                f"A(n) {type(e)} error occurred while retrieving information for the active AEDT sessions: {e}"
            )
            pyaedt_logger.debug(traceback.format_exc())
    return return_dict


@pyaedt_function_handler()
def com_active_sessions(version=None, student_version=False, non_graphical=False):
    """Get information for the active COM AEDT sessions.

    Parameters
    ----------
    version : str, optional
        Version to check. The default is ``None``, in which case all versions are checked.
        When specifying a version, you can use a three-digit format like ``"222"`` or a
        five-digit format like ``"2022.2"``.
    student_version : bool, optional
        Whether to check for student version sessions. The default is ``False``.
    non_graphical : bool, optional
        Whether to check only for active non-graphical sessions. The default is ``False``.

    Returns
    -------
    List
        List of AEDT process IDs.
    """
    all_sessions = active_sessions(version, student_version, non_graphical)

    return_list = []
    for s, p in all_sessions.items():
        if p == -1:
            return_list.append(s)
    return return_list


@pyaedt_function_handler()
def grpc_active_sessions(version=None, student_version=False, non_graphical=False):
    """Get information for the active gRPC AEDT sessions.

    Parameters
    ----------
    version : str, optional
        Version to check. The default is ``None``, in which case all versions are checked.
        When specifying a version, you can use a three-digit format like ``"222"`` or a
        five-digit format like ``"2022.2"``.
    student_version : bool, optional
        Whether to check for student version sessions. The default is ``False``.
    non_graphical : bool, optional
        Whether to check only for active non-graphical sessions. The default is ``False``.

    Returns
    -------
    List
        List of gRPC ports.
    """
    all_sessions = active_sessions(version, student_version, non_graphical)

    return_list = []
    for _, p in all_sessions.items():
        if p > -1:
            return_list.append(p)
    return return_list


@pyaedt_function_handler(function_str="function")
def conversion_function(data, function=None):  # pragma: no cover
    """Convert input data based on a specified function string.

    The available functions are:

    - `"dB10"`: Converts the data to decibels using base 10 logarithm.
    - `"dB20"`: Converts the data to decibels using base 20 logarithm.
    - `"abs"`: Computes the absolute value of the data.
    - `"real"`: Computes the real part of the data.
    - `"imag"`: Computes the imaginary part of the data.
    - `"norm"`: Normalizes the data to have values between 0 and 1.
    - `"ang"`: Computes the phase angle of the data in radians.
    - `"ang_deg"`: Computes the phase angle of the data in degrees.

    If an invalid function string is specified, the method returns ``False``.

    Parameters
    ----------
    data : list, numpy.array
        Numerical values to convert. The format can be ``list`` or ``numpy.array``.
    function : str, optional
        Conversion function. The default is `"dB10"`.

    Returns
    -------
    numpy.array or bool
        Converted data, ``False`` otherwise.

    Examples
    --------
    >>> values = [1, 2, 3, 4]
    >>> conversion_function(values, "dB10")
    array([-inf, 0., 4.77, 6.02])

    >>> conversion_function(values, "abs")
    array([1, 2, 3, 4])

    >>> conversion_function(values, "ang_deg")
    array([ 0., 0., 0., 0.])
    """
    import numpy as np

    function = function or "dB10"
    available_functions = {
        "dB10": lambda x: 10 * np.log10(np.abs(x)),
        "dB20": lambda x: 20 * np.log10(np.abs(x)),
        "abs": np.abs,
        "real": np.real,
        "imag": np.imag,
        "norm": lambda x: np.abs(x) / np.max(np.abs(x)),
        "ang": np.angle,
        "ang_deg": lambda x: np.angle(x, deg=True),
    }

    if function not in available_functions:
        logging.error("Specified conversion is not available.")
        return False

    data = available_functions[function](data)
    return data


class PropsManager(PyAedtBase):
    def __getitem__(self, item):
        """Get the `self.props` key value.

        Parameters
        ----------
        item : str
            Key to search
        """
        item_split = item.split("/")
        if len(item_split) == 1:
            item_split = item_split[0].split("__")
        props = self.props
        found_el = []
        matching_percentage = 1
        while matching_percentage >= 0.4:
            for item_value in item_split:
                found_el = self._recursive_search(props, item_value, matching_percentage)
                # found_el = difflib.get_close_matches(item_value, list(props.keys()), 1, matching_percentage)
                if found_el:
                    props = found_el[1][found_el[2]]
                    # props = props[found_el[0]]
            if found_el:
                return props
            else:
                matching_percentage -= 0.02
        self._app.logger.warning("Key %s not found.Check one of available keys in self.available_properties", item)
        return None

    def __setitem__(self, key, value):
        """Set the `self.props` key value.

        Parameters
        ----------
        key : str
            Key to apply.
        value : int, float, bool, str, dict
            Value to apply.
        """
        item_split = key.split("/")
        if len(item_split) == 1:
            item_split = item_split[0].split("__")
        found_el = []
        props = self.props
        matching_percentage = 1
        key_path = []
        while matching_percentage >= 0.4:
            for item_value in item_split:
                found_el = self._recursive_search(props, item_value, matching_percentage)
                if found_el:
                    props = found_el[1][found_el[2]]
                    key_path.append(found_el[2])
            if found_el:
                if matching_percentage < 1:
                    self._app.logger.info(
                        "Key %s matched internal key '%s' with confidence of %s.",
                        key,
                        "/".join(key_path),
                        round(matching_percentage * 100),
                    )
                matching_percentage = 0

            else:
                matching_percentage -= 0.02
        value = _units_assignment(value)
        if found_el:
            found_el[1][found_el[2]] = value
            self.update()
        else:
            props[key] = value
            self.update()
            self._app.logger.warning("Key %s not found. Trying to applying new key ", key)

    @pyaedt_function_handler()
    def _recursive_search(self, dict_in, key="", matching_percentage=0.8):
        f = difflib.get_close_matches(key, list(dict_in.keys()), 1, matching_percentage)
        if f:
            return True, dict_in, f[0]
        else:
            for v in list(dict_in.values()):
                if isinstance(v, dict):
                    out_val = self._recursive_search(v, key, matching_percentage)
                    if out_val:
                        return out_val
                elif isinstance(v, list) and isinstance(v[0], dict):
                    for val in v:
                        out_val = self._recursive_search(val, key, matching_percentage)
                        if out_val:
                            return out_val
        return False

    @pyaedt_function_handler()
    def _recursive_list(self, dict_in, prefix=""):
        available_list = []
        for k, v in dict_in.items():
            if prefix:
                name = prefix + "/" + k
            else:
                name = k
            available_list.append(name)
            if isinstance(v, dict):
                available_list.extend(self._recursive_list(v, name))
        return available_list

    @property
    def available_properties(self):
        """Available properties.

        Returns
        -------
        list
        """
        if self.props:
            return self._recursive_list(self.props)
        return []

    @pyaedt_function_handler()
    def update(self):
        """Update method."""
        pass


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


rgb_color_codes = {
    "Black": (0, 0, 0),
    "Green": (0, 128, 0),
    "White": (255, 255, 255),
    "Red": (255, 0, 0),
    "Lime": (0, 255, 0),
    "Blue": (0, 0, 255),
    "Yellow": (255, 255, 0),
    "Cyan": (0, 255, 255),
    "Magenta": (255, 0, 255),
    "Silver": (192, 192, 192),
    "Gray": (128, 128, 128),
    "Maroon": (128, 0, 0),
    "Olive": (128, 128, 0),
    "Purple": (128, 0, 128),
    "Teal": (0, 128, 128),
    "Navy": (0, 0, 128),
    "copper": (184, 115, 51),
    "stainless steel": (224, 223, 219),
}


@pyaedt_function_handler()
def _to_boolean(val):
    """Retrieve the Boolean value of the provided input.

        If the value is a Boolean, return the value.
        Otherwise check to see if the value is in
        ["false", "f", "no", "n", "none", "0", "[]", "{}", "" ]
        and return True if the value is not in the list.

    Parameters
    ----------
    val : bool or str
        Input value to test for True/False condition.

    Returns
    -------
    bool

    """
    if val is True or val is False:
        return val

    false_items = ["false", "f", "no", "n", "none", "0", "[]", "{}", ""]

    return str(val).strip().lower() not in false_items


@pyaedt_function_handler()
def install_with_pip(package_name, package_path=None, upgrade=False, uninstall=False):  # pragma: no cover
    """Install a new package using pip.

    This method is useful for installing a package from the AEDT Console without launching the Python environment.

    .. warning::

        Do not execute this function with untrusted environment variables.
        See the :ref:`security guide<ref_security_consideration>` for details.

    Parameters
    ----------
    package_name : str
        Name of the package to install.
    package_path : str, optional
        Path for the GitHub package to download and install. For example, ``git+https://.....``.
    upgrade : bool, optional
        Whether to upgrade the package. The default is ``False``.
    uninstall : bool, optional
        Whether to install the package or uninstall the package.
    """
    import subprocess  # nosec B404

    if not package_name or not isinstance(package_name, str):
        raise ValueError("A valid package name must be provided.")

    executable = sys.executable
    commands = []
    if uninstall:
        commands.append([executable, "-m", "pip", "uninstall", "--yes", package_name])
    else:
        if package_path and upgrade:
            commands.append([executable, "-m", "pip", "uninstall", "--yes", package_name])
            command = [executable, "-m", "pip", "install", package_path]
        else:
            command = [executable, "-m", "pip", "install", package_name]
        if upgrade:
            command.append("-U")
        commands.append(command)

    for command in commands:
        try:
            subprocess.run(command, check=True)  # nosec
        except subprocess.CalledProcessError as e:  # nosec
            raise AEDTRuntimeError("An error occurred while installing with pip") from e


class Help(PyAedtBase):  # pragma: no cover
    def __init__(self):
        self._base_path = "https://aedt.docs.pyansys.com/version/stable"
        self.browser = "default"

    def _launch_ur(self, url):
        import webbrowser

        if self.browser != "default":
            webbrowser.get(self.browser).open_new_tab(url)
        else:
            webbrowser.open_new_tab(url)

    def search(self, keywords, app_name=None, search_in_examples_only=False):
        """Search for one or more keywords.

        Parameters
        ----------
        keywords : str or list
        app_name : str, optional
            Name of a PyAEDT app. For example, ``"Hfss"``, ``"Circuit"``, ``"Icepak"``, or any other available app.
        search_in_examples_only : bool, optional
            Whether to search for the one or more keywords only in the PyAEDT examples.
            The default is ``False``.
        """
        if isinstance(keywords, str):
            keywords = [keywords]
        if search_in_examples_only:
            keywords.append("This example")
        if app_name:
            keywords.append(app_name)
        url = self._base_path + f"/search.html?q={'+'.join(keywords)}"
        self._launch_ur(url)

    def getting_started(self):
        """Open the PyAEDT User guide page."""
        url = self._base_path + "/User_guide/index.html"
        self._launch_ur(url)

    def examples(self):
        """Open the PyAEDT Examples page."""
        url = self._base_path + "/examples/index.html"
        self._launch_ur(url)

    def github(self):
        """Open the PyAEDT GitHub page."""
        url = "https://github.com/ansys/pyaedt"
        self._launch_ur(url)

    def changelog(self, release=None):
        """Open the PyAEDT GitHub Changelog for a given release.

        Parameters
        ----------
        release : str, optional
            Release to get the changelog for. For example, ``"0.6.70"``.
        """
        if release is None:
            from ansys.aedt.core import __version__ as release
        url = "https://github.com/ansys/pyaedt/releases/tag/v" + release
        self._launch_ur(url)

    def issues(self):
        """Open the PyAEDT GitHub Issues page."""
        url = "https://github.com/ansys/pyaedt/issues"
        self._launch_ur(url)

    def ansys_forum(self):
        """Open the PyAEDT GitHub Issues page."""
        url = "https://discuss.ansys.com/discussions/tagged/pyaedt"
        self._launch_ur(url)

    def developer_forum(self):
        """Open the Discussions page on the Ansys Developer site."""
        url = "https://developer.ansys.com/"
        self._launch_ur(url)


# class Property(property):
#
#     @pyaedt_function_handler()
#     def getter(self, fget):
#         """Property getter."""
#         return self.__class__.__base__(fget, self.fset, self.fdel, self.__doc__)
#
#     @pyaedt_function_handler()
#     def setter(self, fset):
#         """Property setter."""
#         return self.__class__.__base__(self.fget, fset, self.fdel, self.__doc__)
#
#     @pyaedt_function_handler()
#     def deleter(self, fdel):
#         """Property deleter."""
#         return self.__class__.__base__(self.fget, self.fset, fdel, self.__doc__)

# property = Property

online_help = Help()
