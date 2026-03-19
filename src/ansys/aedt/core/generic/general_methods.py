# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from __future__ import annotations

import datetime
import difflib
import functools
from functools import update_wrapper
import inspect
import itertools
import logging
import os
import platform
import re
import subprocess  # nosec
import sys
import time
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from numpy import array
from typing import Any
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


def _write_mes(mes_text) -> None:
    if not (settings.enable_debug_logger or settings.enable_debug_edb_logger):
        return
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


def _exception(ex_info, func, args, kwargs, message: str = "Type Error") -> None:
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
        if (
            any(exc in trace for exc in exceptions)
            or "plugins" in trace
            or ("site-packages" in trace and ("\\aedt\\" not in trace and "/aedt/" not in trace))
        ):
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
        if (
            any(exc in trace for exc in exceptions)
            or "plugins" in trace
            or ("site-packages" in trace and ("\\aedt\\" not in trace and "/aedt/" not in trace))
        ):
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


def _check_types(arg) -> str:
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
                v.release_desktop(close_projects=v.close_on_exit, close_on_exit=v.close_on_exit)

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
            msg = str(sys.exc_info()[1])
            if "ANSYS_GRPC_CERTIFICATES" in msg:
                msg = re.sub(
                    r"ANSYS_GRPC_CERTIFICATES", "ANSYS_GRPC_CERTIFICATES", msg.capitalize(), flags=re.IGNORECASE
                )
            else:
                msg = msg.capitalize()
            _exception(sys.exc_info(), user_function, args, kwargs, msg)
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


def deprecate_argument(arg_name: str, version: str = None, message: str = None, removed: bool = False) -> callable:
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
def check_numeric_equivalence(a, b, relative_tolerance: float = 1e-7):
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


def _log_method(func, new_args, new_kwargs) -> None:
    if not (settings.enable_debug_logger or settings.enable_debug_edb_logger):
        return
    if not settings.enable_debug_internal_methods_logger and str(func.__name__)[0] == "_":
        return
    if not settings.enable_debug_geometry_operator_logger and "GeometryOperators" in str(func):
        return
    # Avoid infinite recursion with __repr__ and __str__ methods
    if func.__name__ in ("__repr__", "__str__"):
        return
    try:
        if not func or (
            not settings.enable_debug_edb_logger
            and "Edb" in str(func) + str(new_args)
            or "edb_core" in str(func) + str(new_args)
        ):
            return
    except Exception:
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
def get_version_and_release(input_version: str) -> tuple:
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
def env_path(input_version: str) -> str:
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
    >>> env_path_student("2026.1")
    "C:/Program Files/ANSYSEM/ANSYSEM2026.1/Win64"
    """
    return os.getenv(
        f"ANSYSEM_ROOT{get_version_and_release(input_version)[0]}{get_version_and_release(input_version)[1]}", ""
    )


@pyaedt_function_handler()
def env_value(input_version: str) -> str:
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
    >>> env_value(2026.1)
    "ANSYSEM_ROOT261"
    """
    return f"ANSYSEM_ROOT{get_version_and_release(input_version)[0]}{get_version_and_release(input_version)[1]}"


@pyaedt_function_handler()
def env_path_student(input_version: str) -> str:
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
    >>> env_path_student(2026.1)
    "C:/Program Files/ANSYSEM/ANSYSEM2026.1/Win64"
    """
    return os.getenv(
        f"ANSYSEMSV_ROOT{get_version_and_release(input_version)[0]}{get_version_and_release(input_version)[1]}",
        "",
    )


@pyaedt_function_handler()
def env_value_student(input_version: str) -> str:
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
    >>> env_value_student(2026.1)
    "ANSYSEMSV_ROOT261"
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
def time_fn(fn: callable, *args, **kwargs):
    start = datetime.datetime.now()
    results = fn(*args, **kwargs)
    end = datetime.datetime.now()
    fn_name = fn.__module__ + "." + fn.__name__
    delta = (end - start).microseconds * 1e-6
    print(fn_name + ": " + str(delta) + "s")
    return results


@pyaedt_function_handler()
def filter_tuple(value: str, search_key_1: str, search_key_2: str) -> bool:
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


@pyaedt_function_handler()
def filter_string(value: str, search_key_1: str) -> bool:
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
def number_aware_string_key(s: str) -> tuple:
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


def _run_ss_xlp() -> dict[int, int]:
    """Run 'ss -xlp' command on Linux to find Unix socket ports.

    This function executes the `ss -xlp` command to list Unix sockets and
    extracts port numbers from AEDT socket filenames.

    Returns
    -------
    dict[int, int]
        Dictionary mapping process IDs to port numbers extracted from Unix socket names.

    Examples
    --------
    >>> from ansys.aedt.core.generic.general_methods import _run_ss_xlp
    >>> _run_ss_xlp()
    {12345: 50051, 67890: 50052}
    """
    proc = subprocess.run(
        ["ss", "-xlp"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )  # nosec
    if proc.returncode != 0:
        raise RuntimeError(f"'ss -xlp' failed: {proc.stderr.strip()}")

    lines = proc.stdout.splitlines()
    results = {}

    for line in lines:
        # If the line does not contain "ansysedt.exe", skip it
        if "ansysedt.exe" not in line:
            continue

        # Extract PID from the line (format: "pid=12345")
        pid_match = re.search(r"pid=(\d+)", line)
        pid = int(pid_match.group(1)) if pid_match else None

        # Extract port number from socket filename (for example, "AnsysEMUDS-50051.sock")
        port_match = re.search(r"-(\d+)\.sock", line)
        port = int(port_match.group(1)) if port_match else None

        if pid and port:
            results[pid] = port

    return results


def _get_pids_by_name_windows(image_name: str) -> list[int]:
    """Get a list of process IDs (PIDs) for a given executable name on Windows.

    This function uses the Windows 'tasklist' command to query running processes.

    Parameters
    ----------
    image_name : str
        Process name to search for, for example 'ansysedt.exe' or 'ansysedtsv.exe'.

    Returns
    -------
    list[int]
        List of process IDs matching the given process name.


    Examples
    --------
    >>> from ansys.aedt.core.generic.general_methods import _get_pids_by_name_windows
    >>> _get_pids_by_name_windows("ansysedt.exe")
    [12345, 67890]
    """
    import csv

    if image_name not in ["ansysedt.exe", "ansysedtsv.exe"]:
        raise ValueError(f"Invalid process name: {image_name}")

    # NOTE: Build the tasklist command with filters
    # tasklist - Windows command to display running processes
    # /fi "imagename eq {name}" - Filter to show only processes matching the exact name
    # /fo csv - Format output as CSV for easy parsing
    # /nh - No header row in output (easier to parse)
    cmd = ["tasklist", "/fi", f"imagename eq {image_name}", "/fo", "csv", "/nh"]
    result = subprocess.run(
        cmd, capture_output=True, text=True, shell=False, check=False, creationflags=subprocess.CREATE_NO_WINDOW
    )  # nosec

    # Parse the CSV output from tasklist
    pids = []
    reader = csv.reader(result.stdout.splitlines())
    for row in reader:
        # Skip empty rows (can occur at end of output)
        if not row:  # pragma: no cover
            continue

        # Expected CSV format from tasklist:
        # "Image Name","PID","Session Name","Session#","Mem Usage"
        # Example: "ansysedt.exe","12345","Console","1","245,678 K"
        # Extract column 1 (index 1) which contains the PID
        try:
            pid_str = row[1].strip().strip('"')

            # Validate that PID is a valid integer before converting
            # This prevents errors from malformed output
            if pid_str.isdigit():
                pids.append(int(pid_str))
        except IndexError:  # pragma: no cover
            # IndexError occurs if row doesn't have enough columns
            # This can happen with malformed output or when no sessions available
            continue

    return pids


def _get_target_processes(target_name: list[str]) -> list[tuple[int, list[str]]]:
    """Get process IDs and command line arguments for target processes.

    This function searches for running processes matching the specified names
    and retrieves their command line arguments.

    Parameters
    ----------
    target_name : list[str]
        List of process names to search for. For example, `["ansysedt.exe", "ansysedtsv.exe"]`.

    Returns
    -------
    list[tuple[int, list[str]]]
        List of tuples containing (process_id, command_line_arguments).
        Command line arguments are split into individual strings.

    Notes
    -----
    - On Linux: Uses `pgrep` and reads `/proc/{pid}/cmdline`
    - On Windows: Uses tasklist to query process information.

    Examples
    --------
    >>> from ansys.aedt.core.generic.general_methods import _get_target_processes
    >>> _get_target_processes(["ansysedt.exe"])
    [(12345, ['C:\\Program Files\\...\\ansysedt.exe', '-grpcsrv', '127.0.0.1:50051'])]
    """
    platform_system = platform.system()
    found_data = []

    if platform_system == "Linux":
        # Use pgrep to find PIDs and read command lines from /proc
        try:
            pids = []
            for process_name in target_name:
                pids += subprocess.check_output(["pgrep", "-x", process_name]).decode().split()  # nosec

            for pid in pids:
                if os.path.exists(f"/proc/{pid}/cmdline"):
                    with open(f"/proc/{pid}/cmdline", "rb") as f:
                        # Command line arguments in /proc are null-byte separated
                        cmdline = f.read().decode().split("\0")
                        found_data.append((int(pid), [arg for arg in cmdline if arg]))
        except subprocess.CalledProcessError:
            pyaedt_logger.debug("No matching processes found.")

    elif platform_system == "Windows":
        # Windows implementation uses 'tasklist' command-line tool instead of PowerShell
        # This approach is more reliable and doesn't require PowerShell availability

        # Iterate through all requested process names (["ansysedt.exe", "ansysedtsv.exe"])
        for process_name in target_name:
            # Get all PIDs for this process name using the Windows helper function
            pids = _get_pids_by_name_windows(process_name)

            # For each PID, create a tuple of (PID, process_name)
            # Note: On Windows, we only have the process name, not full command line args
            # This is a limitation of the tasklist command - it doesn't provide full cmdline
            # The full command line will be retrieved later via psutil in other functions
            found_data.extend([(int(pid), process_name) for pid in pids])

    return found_data


@pyaedt_function_handler()
def _check_psutil_connections(pids: list[int]) -> dict[int, list[str, Any]]:
    """Retrieve network connections for specified process IDs.

    This function collects TCP connection information for a list of process IDs,
    returning the IP address, port, and status of each connection. It uses the
    psutil library to query active network connections for each process.

    Parameters
    ----------
    pids : list of int
        List of process IDs to check for active TCP connections.
        These are typically AEDT process IDs (ansysedt.exe or ansysedtsv.exe).

    Returns
    -------
    dict of int to list of dict
        Dictionary mapping each process ID to a list of connection dictionaries.
        Each connection dictionary contains:
        - "ip" : str
            IP address of the local connection endpoint.
        - "port" : int
            Port number of the local connection endpoint.
        - "status" : str
            Connection status, for example "LISTEN", or "ESTABLISHED".
    """
    # Step 1: Initialize result dictionary with empty lists for each PID
    # This ensures every requested PID appears in the result, even if it has no connections
    connections = {i: [] for i in pids}

    # Step 2: Iterate through each process ID to retrieve its network connections
    for i in pids:
        try:
            # Create a psutil.Process object for the given PID
            # This object provides access to process information and system resources
            prc = psutil.Process(i)

            # Get the full command line of the process as a space-separated string
            cmdline = " ".join(prc.cmdline())

            # Get all TCP network connections for this specific process
            # prc.net_connections() returns a list of named tuples (sconn objects)
            # Each connection has attributes: fd, family, type, laddr, raddr, status, pid
            for conn in prc.net_connections():
                # Build a connection dictionary with the information we need
                # conn.laddr: Local address as a named tuple with .ip and .port attributes
                # conn.laddr.ip: Local IP address (e.g., "127.0.0.1", "::", "0.0.0.0")
                # conn.laddr.port: Local port number (integer, e.g., 50051)
                # conn.status: Connection state (e.g., "LISTEN", "ESTABLISHED")
                connection = {
                    "ip": conn.laddr.ip,  # Local IP address
                    "port": conn.laddr.port,  # Local port number
                    "status": conn.status,  # Connection status
                    "cmdline": cmdline,  # Full command line for filtering
                }

                # Append this connection to the list for this PID
                connections[i].append(connection)

        except (AttributeError, KeyError, psutil.ZombieProcess, psutil.NoSuchProcess, psutil.AccessDenied):
            # Handle various exceptions that can occur during process inspection:
            #
            # AttributeError: Raised if conn.laddr is None (connection without local address)
            #                 This can happen for some connection types
            #
            # KeyError: Raised if expected attributes are missing from the connection object
            #           Rare, but possible with certain process states
            #
            # psutil.ZombieProcess: Process has terminated but hasn't been cleaned up by parent
            #                       Common on Linux when processes exit but remain in process table
            #
            # psutil.NoSuchProcess: Process terminated between when we got the PID and now
            #                       This is a race condition that can occur in fast process lifecycles
            #
            # psutil.AccessDenied: Current user does not have permission to access process information
            #
            # Action: Pass silently - the PID will remain in the result with an empty list
            pass

    return connections


@pyaedt_function_handler()
def _check_connection_grpc_port(
    connections: dict[int, list[dict]],
    pid: int,
    version: str | None = None,
    non_graphical: bool | None = None,
) -> int:
    """Find the gRPC port for a specific process from its network connections.

    This function searches through network connections to identify the gRPC port
    that a specific process is listening on. It checks for LISTEN status on
    localhost addresses ("::" or "127.0.0.1") and optionally filters by version
    and graphical mode.

    Parameters
    ----------
    connections : dict of int to list of dict
        Dictionary mapping process IDs to their network connections.
        Each connection dictionary should contain "ip", "port", "status" and "cmdline" keys.
    pid : int
        The process ID to check for an active gRPC listening port.
    version: str, optional
        AEDT version to filter by. If provided, only connections whose command line
        contains this version string are considered. The default is ``None`` (no version filtering).
    non_graphical : bool, optional
        Filter by graphical mode. The default is ``None``.
        - ``True``: Only return port if process has ``-ng`` flag (non-graphical mode)
        - ``False``: Only return port if process does NOT have ``-ng`` flag (graphical mode)
        - ``None``: Ignore graphical mode (return port regardless)

    Returns
    -------
    int
        The gRPC port number if a LISTEN connection is found matching all filters,
        ``-1`` if no matching connection is found.

    """
    # Step 1: Iterate through possible localhost IP addresses
    # Check both IPv6 (::) and IPv4 (127.0.0.1) localhost addresses
    for ip in ["::", "127.0.0.1"]:
        # Step 2: Iterate through all processes in the connections dictionary
        # input_pid: Process ID from the connections dict
        # conn: List of connection dictionaries for that process
        for input_pid, conn in connections.items():
            # Step 3: Iterate through each individual connection for this process
            # el: Connection dictionary with keys: "ip", "port", "status", "cmdline"
            for el in conn:
                # Step 4: Apply the primary filters - PID, IP, and LISTEN status
                if input_pid == pid and el["ip"] == ip and el["status"] == "LISTEN":
                    # Step 5: Apply optional version filter
                    # Two scenarios pass this check:
                    # 1. not version: No version filter specified (version is None or empty)
                    # 2. version in el["cmdline"]: Version string appears in command line
                    # This allows filtering for specific AEDT versions when multiple
                    # versions are running simultaneously
                    if not version or version in el["cmdline"]:
                        # Step 6: Apply optional non-graphical mode filter
                        # This is a three-way check with complex logic:
                        #
                        # Condition 1: non_graphical is None
                        #   - No filtering by graphical mode
                        #   - Accept any connection regardless of -ng flag
                        #
                        # Condition 2: (non_graphical and "-ng" in el["cmdline"])
                        #   - User wants non-graphical sessions only (non_graphical=True)
                        #   - Command line contains -ng flag
                        #   - This matches non-graphical AEDT sessions
                        #
                        # Condition 3: ("-ng" not in el["cmdline"] and not non_graphical)
                        #   - User wants graphical sessions only (non_graphical=False)
                        #   - Command line does NOT contain -ng flag
                        #   - This matches graphical AEDT sessions

                        if (
                            non_graphical is None  # No filtering by graphical mode
                            or (non_graphical and "-ng" in el["cmdline"])  # Want non-graphical, has -ng
                            or ("-ng" not in el["cmdline"] and not non_graphical)  # Want graphical, no -ng
                        ):
                            # Step 7: All filters passed - return the port number
                            return el["port"]

    # Step 8: No matching connection found
    # Return -1 to indicate:
    # - Either the PID doesn't have a LISTEN connection on localhost, OR
    # - The connection exists but doesn't match the version/graphical filters, OR
    # - The process is using COM instead of gRPC
    return -1


@pyaedt_function_handler()
def is_grpc_session_active(port: int) -> bool:
    """Check if a gRPC session is active on the specified port.

    This function verifies whether an AEDT session is actively listening on
    the specified gRPC port. It does not parse process command lines, instead,
    it checks active TCP connections.

    The function uses multiple detection strategies:
    1. On Linux: Checks Unix sockets using `ss -xlp`
    2. Searches for AEDT processes
    3. Verifies TCP connections on localhost (127.0.0.1) for the specified port

    Parameters
    ----------
    port : int
        The gRPC port number to check.

    Returns
    -------
    bool
        ``True`` if an AEDT session is listening on the specified port, ``False`` otherwise.

    Notes
    -----
    - This function is faster than `active_sessions()` but less comprehensive.
    - It only checks if the port is in use, not which version of AEDT is using it.
    - Does not distinguish between graphical and non-graphical sessions.

    Examples
    --------
    Check if port 50051 is in use:
    >>> from ansys.aedt.core.generic.general_methods import is_grpc_session_active
    >>> if is_grpc_session_active(50051):
    ...     print("Port 50051 is occupied.")
    ... else:
    ...     print("Port 50051 is available.")
    """
    # On Linux, try to resolve unknown ports using Unix socket analysis
    if is_linux:
        try:
            sockets = _run_ss_xlp()
            if port in sockets.values():
                return True
        except Exception as e:
            pyaedt_logger.debug(f"Failed to analyze Unix sockets for port detection: {str(e)}")

    targets = ["ansysedt.exe", "ansysedtsv.exe"]
    if is_linux:
        targets.extend(["ansysedt", "ansysedtsv"])

    for target in targets:
        target_processes = _get_target_processes([target])

        # Initialize all found AEDT processes with unknown port (-1)
        # Port will be determined later through socket/connection analysis
        return_dict = {pid: -1 for pid, _ in target_processes}

        connections = _check_psutil_connections(list(return_dict.keys()))
        for pid in return_dict.keys():
            if _check_connection_grpc_port(connections, pid, None, None) == port:
                return True
    return False


@pyaedt_function_handler()
def active_sessions(
    version: str = None, student_version: bool = False, non_graphical: bool | None = None
) -> dict[int, int]:
    """Get information for active AEDT sessions.

    This function detects running AEDT processes and identifies their gRPC ports or
    marks them as COM sessions. It works on both Windows and Linux platforms by using
    multiple detection strategies to ensure reliable session discovery.

    Detection Strategy (in order of execution):
        1. **Process Discovery**: Searches for AEDT processes (ansysedt.exe or ansysedtsv.exe).
        2. **Command-Line Parsing**: Extracts gRPC port from ``-grpcsrv`` command-line argument.
        3. **Unix Socket Analysis** (Linux only): Uses ``ss -xlp`` to find ports from socket files.
        4. **TCP Connection Analysis**: Falls back to checking active TCP connections via psutil.

    Port Detection Results:
        - Positive integer, gRPC session on that port.
        - ``-1``: COM session (no gRPC server running).

    Parameters
    ----------
    version : str, optional
        AEDT version to check. The default is ``None``, in which case all versions are checked.
        When specifying a version, you can use a three-digit format like ``"222"`` or a
        five-digit format like ``"2022.2"``.

    student_version : bool, optional
        Whether to search for student version sessions (ansysedtsv). The default is ``False``.
        When ``True``, searches for ``ansysedtsv.exe`` or ``ansysedtsv`` processes.
    non_graphical : bool, optional
        Whether to filter by non-graphical sessions. The default is ``None``.
        If ``True``, only non-graphical sessions are returned.
        If ``False``, only graphical sessions are returned.
        If ``None``, all sessions are returned regardless of mode.

    Returns
    -------
    dict[int, int]
        Dictionary mapping AEDT process IDs to their corresponding ports.
        Port is set to ``-1`` if the session is using COM instead of gRPC.

    Examples
    --------
    Get all active AEDT sessions (any version, any mode):

    >>> from ansys.aedt.core.generic.general_methods import active_sessions
    >>> active_sessions()
    {12345: 50051, 67890: -1, 23456: 50052}
    # PID 12345 uses gRPC port 50051
    # PID 67890 uses COM (legacy mode)
    # PID 23456 uses gRPC port 50052

    Get only AEDT 2023.2 sessions:

    >>> active_sessions(version="2023.2")
    {12345: 50051}

    Get only non-graphical sessions:

    >>> active_sessions(non_graphical=True)
    {67890: 50052}

    Get student version sessions:

    >>> active_sessions(student_version=True)
    {34567: 50053}

    Combine filters for specific session types:

    >>> active_sessions(version="2024.1", non_graphical=True)
    {45678: 50054}
    """
    # Initialize result dictionary: will map process ID (PID) to port number
    return_dict = {}

    # Step 1: Determine target process names based on version type and operating system
    # Student version uses different executable names (ansysedtsv vs ansysedt)
    if student_version:
        # Linux needs both variants (with and without .exe extension)
        target = ["ansysedtsv", "ansysedtsv.exe"] if is_linux else ["ansysedtsv.exe"]
    else:
        target = ["ansysedt", "ansysedt.exe"] if is_linux else ["ansysedt.exe"]

    # Step 2: Normalize version format to ensure consistent version matching
    # Converts various formats ("2022.2", "222") to a standardized string
    if version and "." in version:
        # Remove "SV" suffix for student versions ("2022.2SV" to "2022.2")
        if student_version and version.endswith("SV"):
            version = version[:-2]
        # Extract last 4 characters and remove dot ("2022.2" to "222")
        version = version[-4:].replace(".", "")

    # Special handling for versions before 2022.1 (version < "221")
    # Convert back to dotted format (e.g., "212" -> "21.2")
    if version and version < "221":
        version = version[:2] + "." + version[2]

    # Step 3: Get all matching AEDT processes from the system
    # Returns list of tuples: [(pid, command_line_args), ...]
    target_processes = _get_target_processes(target)

    # Define standard gRPC port range (50051-50099 are typically used by AEDT)
    # This list is currently created but not actively used in the logic below
    available_ports = [i for i in range(50051, 50100)]

    # Step 4: Extract port information from process command lines
    # AEDT processes launched with gRPC have "-grpcsrv" flag followed by address:port
    for pid, cmd in target_processes:
        # Check if this is a gRPC session (has -grpcsrv argument)
        if "-grpcsrv" in cmd:
            try:
                # Get the argument after "-grpcsrv" (format: "127.0.0.1:50051" or just "50051")
                grpc_arg = cmd[cmd.index("-grpcsrv") + 1]
                prt = grpc_arg.split(":")

                # Parse port number based on format
                if len(prt) == 1:
                    # Format: just port number (e.g., "50051")
                    available_ports.append(int(prt[0]))
                else:
                    # Format: address:port (e.g., "127.0.0.1:50051")
                    available_ports.append(int(prt[1]))
            except (IndexError, ValueError):
                # If parsing fails, try other methods below
                pass
        else:
            # No "-grpcsrv" argument found
            return_dict[pid] = -1

    # Step 5: On Linux, try to resolve unknown ports using Unix socket analysis
    # In Linux, running AEDT locally uses Unix domain sockets with filenames containing port numbers
    # Example socket: AnsysEMUDS-50051.sock
    if is_linux and any(port == -1 for port in return_dict.values()):
        try:
            # Run 'ss -xlp' command to get Unix socket information
            sockets = _run_ss_xlp()  # Returns {pid: port} mapping from socket filenames

            # Update return_dict with discovered ports
            for pid, port in sockets.items():
                # Only update if PID is in our results and port is still unknown (-1)
                if pid in return_dict and return_dict[pid] == -1:
                    return_dict[pid] = port
        except Exception as e:
            # Log but don't fail - we have other detection methods
            pyaedt_logger.debug(f"Failed to analyze Unix sockets for port detection: {str(e)}")

    # Step 6: Fallback method - Try to find ports by checking TCP network connections
    # This works when command-line parsing and Unix socket analysis didn't find the port
    if any(port == -1 for port in return_dict.values()):
        # Get all TCP connections for our AEDT processes
        connections = _check_psutil_connections(list(return_dict.keys()))

        # For each process with unknown port (-1), try to find it via TCP connections
        for pid in [i for i, v in return_dict.items() if v == -1]:
            # Check for LISTEN connections on localhost that match our filters
            # This method also applies version and non_graphical filters
            return_dict[pid] = _check_connection_grpc_port(connections, pid, version, non_graphical)

    return return_dict


@pyaedt_function_handler()
def com_active_sessions(
    version: str | None = None, student_version: bool | None = False, non_graphical: bool | None = False
):
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
def grpc_active_sessions(
    version: str | None = None, student_version: bool | None = False, non_graphical: bool | None = False
):
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


@pyaedt_function_handler()
def conversion_function(data: list | "array", function: str = None):  # pragma: no cover
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
    def _recursive_search(self, dict_in, key: str = "", matching_percentage: float = 0.8):
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
    def _recursive_list(self, dict_in, prefix: str = ""):
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
    def update(self) -> None:
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
def install_with_pip(
    package_name: str, package_path: str = None, upgrade: bool = False, uninstall: bool = False
):  # pragma: no cover
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
