# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

from __future__ import absolute_import

import datetime
from functools import update_wrapper
import inspect
import itertools
import os
import re
import sys
import tempfile
import time
import traceback

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.aedt_versions import aedt_versions
from ansys.aedt.core.generic.filesystem import check_if_path_exists
from ansys.aedt.core.generic.filesystem import open_file
from ansys.aedt.core.generic.settings import inner_project_settings  # noqa: F401
from ansys.aedt.core.generic.settings import settings

is_ironpython = "IronPython" in sys.version or ".NETFramework" in sys.version
is_linux = os.name == "posix"
is_windows = not is_linux
inside_desktop = True if is_ironpython and "4.0.30319.42000" in sys.version else False

if not is_ironpython:
    import psutil

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


class GrpcApiError(Exception):
    """ """

    pass


class MethodNotSupportedError(Exception):
    """ """

    pass


def _write_mes(mes_text):
    mes_text = str(mes_text)
    parts = [mes_text[i : i + 250] for i in range(0, len(mes_text), 250)]
    for el in parts:
        settings.logger.error(el)


def _get_args_dicts(func, args, kwargs):
    args_name = list(dict.fromkeys(inspect.getfullargspec(func)[0] + list(kwargs.keys())))
    args_dict = dict(list(itertools.zip_longest(args_name, args)) + list(kwargs.items()))
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

    _write_mes("{} on {}".format(message, func.__name__))

    message_to_print = ""
    messages = ""
    from ansys.aedt.core.generic.desktop_sessions import _desktop_sessions

    if len(list(_desktop_sessions.values())) == 1:
        try:
            messages = list(list(_desktop_sessions.values())[0].odesktop.GetMessages("", "", 2))[-1].lower()
        except (GrpcApiError, AttributeError, TypeError, IndexError):
            pass
    if "error" in messages:
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
                _write_mes("    {} = {} ".format(el, args_dict[el]))
    except Exception:
        pyaedt_logger.error("An error occurred while parsing and logging an error with method {}.")

    _write_mes(header)


def raise_exception_or_return_false(e):
    if not settings.enable_error_handler:
        if settings.release_on_exception:
            from ansys.aedt.core.generic.desktop_sessions import _desktop_sessions

            for v in list(_desktop_sessions.values())[:]:
                v.release_desktop(v.launched_by_pyaedt, v.launched_by_pyaedt)
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
            if settings.enable_debug_logger or settings.enable_debug_edb_logger:
                _log_method(user_function, args, kwargs)
            return out
        except MethodNotSupportedError as e:
            message = "This method is not supported in current AEDT design type."
            if settings.enable_screen_logs:
                pyaedt_logger.error("**************************************************************")
                pyaedt_logger.error(
                    "PyAEDT error on method {}:  {}. Check again".format(user_function.__name__, message)
                )
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
                msg = "{} received both {} and {} as arguments!\n".format(func_name, alias, new)
                msg += "{} is deprecated, use {} instead.".format(alias, new)
                raise TypeError(msg)
            pyaedt_logger.warning(
                "Argument `{}` is deprecated for method `{}`; use `{}` instead.".format(alias, func_name, new)
            )
            kwargs[new] = kwargs.pop(alias)


def pyaedt_function_handler(direct_func=None, **deprecated_kwargs):
    """Provides an exception handler, logging mechanism, and argument converter for client-server
    communications.

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


def _log_method(func, new_args, new_kwargs):
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
        time_msg = " {}days {}h {}m {}sec.".format(d, h, m, int(s))
    elif h > 0:
        time_msg = " {}h {}m {}sec.".format(h, m, int(s))
    else:
        time_msg = "  {}m {}sec {}msec.".format(m, int(s), int(msec))
    if settings.enable_debug_methods_argument_logger:
        args_dict = _get_args_dicts(func, new_args, new_kwargs)
        id = 0
        if new_args:
            object_name = str([new_args[0]])[1:-1]
            id = object_name.find(" object at ")
        if id > 0:
            object_name = object_name[1:id]
            message.append("'{}' was run in {}".format(object_name + "." + str(func.__name__), time_msg))
        else:
            message.append("'{}' was run in {}".format(str(func.__name__), time_msg))
        message.append(line_begin)
        for k, v in args_dict.items():
            if k != "self":
                message.append("    {} = {}".format(k, v))
    for m in message:
        settings.logger.debug(m)


def _retry_ntimes(n, function, *args, **kwargs):
    """

    Parameters
    ----------
    n : int

    function :

    *args :

    **kwargs :


    Returns
    -------

    """
    func_name = None
    try:
        if function.__name__ == "InvokeAedtObjMethod":
            func_name = args[1]
    except Exception:
        pyaedt_logger.debug("An error occurred while accessing the arguments of a function " "called multiple times.")
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
            raise AttributeError("Error in Executing Method {}.".format(function.__name__))
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


@pyaedt_function_handler()
def is_project_locked(project_path):
    """Check if an AEDT project lock file exists.

    Parameters
    ----------
    project_path : str
        Path for the AEDT project.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    if settings.remote_rpc_session:
        if settings.remote_rpc_session.filemanager.pathexists(project_path + ".lock"):
            return True
        else:
            return False
    return check_if_path_exists(project_path + ".lock")


@pyaedt_function_handler()
def available_license_feature(
    feature="electronics_desktop", input_dir=None, port=1055, name="127.0.0.1"
):  # pragma: no cover
    """Check the available license feature.

    Parameters
    ----------
    feature : str
        Feature increment name. The default is the ``"electronics_desktop"``.
    input_dir : str, optional
        AEDT installation path. The default is ``None``, in which case the first identified AEDT
        installation from :func:`ansys.aedt.core.generic.aedt_versions.installed_versions`
        method is taken.
    port : int, optional
        Server port number.
    name : str, optional
        License server name.

    Returns
    -------
    int
        Number of available license features, ``False`` when license server is down.
    """
    import subprocess  # nosec B404

    if not input_dir:
        input_dir = list(aedt_versions.installed_versions.values())[0]

    if is_linux:
        ansysli_util_path = os.path.join(input_dir, "licensingclient", "linx64", "lmutil")
    else:
        ansysli_util_path = os.path.join(input_dir, "licensingclient", "winx64", "lmutil")

    my_env = os.environ.copy()

    tempfile_checkout = tempfile.NamedTemporaryFile(suffix=".txt", delete=False).name

    cmd = [ansysli_util_path, "lmstat", "-f", feature, "-c", str(port) + "@" + str(name)]

    f = open(tempfile_checkout, "w")

    subprocess.Popen(cmd, stdout=f, stderr=f, env=my_env).wait()  # nosec

    f.close()

    available_licenses = 0
    pattern_license = r"Total of\s+(\d+)\s+licenses? issued;\s+Total of\s+(\d+)\s+licenses? in use"
    pattern_error = r"Error getting status"
    with open_file(tempfile_checkout, "r") as f:
        for line in f:
            line = line.strip()
            match_license = re.search(pattern_license, line)
            if match_license:
                total_licenses_issued = int(match_license.group(1))
                total_licenses_in_use = int(match_license.group(2))
                available_licenses = total_licenses_issued - total_licenses_in_use
                break
            match_error = re.search(pattern_error, line)
            if match_error:
                pyaedt_logger.error(line)
                return False
    return available_licenses


@pyaedt_function_handler()
def remove_project_lock(project_path):
    """Check if an AEDT project exists and try to remove the lock file.

    .. note::
       This operation is risky because the file could be opened in another AEDT instance.

    Parameters
    ----------
    project_path : str
        Path for the AEDT project.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    if settings.remote_rpc_session and settings.remote_rpc_session.filemanager.pathexists(project_path + ".lock"):
        settings.remote_rpc_session.filemanager.unlink(project_path + ".lock")
        return True
    if os.path.exists(project_path + ".lock"):
        os.remove(project_path + ".lock")
    return True


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
    for p in psutil.process_iter():
        try:
            if p.name() in keys:
                cmd = p.cmdline()
                if non_graphical and "-ng" in cmd or not non_graphical:
                    if not version or (version and version in cmd[0]):
                        if "-grpcsrv" in cmd:
                            if not version or (version and version in cmd[0]):
                                try:
                                    return_dict[p.pid] = int(cmd[cmd.index("-grpcsrv") + 1])
                                except (IndexError, ValueError):
                                    # default desktop grpc port.
                                    return_dict[p.pid] = 50051
                        else:
                            return_dict[p.pid] = -1
                            for i in psutil.net_connections():
                                if i.pid == p.pid and (i.laddr.port > 50050 and i.laddr.port < 50200):
                                    return_dict[p.pid] = i.laddr.port
                                    break
        except psutil.NoSuchProcess as e:  # pragma: no cover
            pyaedt_logger.debug(f"The process exited and cannot be an active session: {e}")
        except Exception as e:  # pragma: no cover
            pyaedt_logger.error(
                f"A(n) {type(e)} error occurred while retrieving information for the active AEDT sessions: {e}"
            )
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


clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
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

#
# # FIXME: Remove usage of random module once IronPython compatibility is removed
# def _uname(name=None):
#     """Append a 6-digit hash code to a specified name.
#
#     Parameters
#     ----------
#     name : str
#         Name to append the hash code to. The default is ``"NewObject_"``.
#
#     Returns
#     -------
#     str
#
#     """
#     alphabet = string.ascii_uppercase + string.digits
#     if is_ironpython:
#         import random
#
#         unique_name = "".join(random.sample(alphabet, 6))  # nosec B311
#     else:
#         import secrets
#
#         generator = secrets.SystemRandom()
#         unique_name = "".join(secrets.SystemRandom.sample(generator, alphabet, 6))
#     if name:
#         return name + unique_name
#     else:
#         return "NewObject_" + unique_name


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

    return not str(val).strip().lower() in false_items


@pyaedt_function_handler()
def _dim_arg(value, units):
    """Concatenate a specified units string to a numerical input.

    Parameters
    ----------
    value : str or number
        Valid expression string in the AEDT modeler. For example, ``"5mm"``.
    units : str
        Valid units string in the AEDT modeler. For example, ``"mm"``.

    Returns
    -------
    str

    """
    try:
        val = float(value)
        if isinstance(value, int):
            val = value
        return str(val) + units
    except Exception:
        return value


@pyaedt_function_handler()
def _check_installed_version(install_path, long_version):
    """Check installation folder to determine if it is for specified Ansys EM version.

    Parameters
    ----------
    install_path: str
        Installation folder to check.  For example, ``"C:\\Program Files\\AnsysEM\\v231\\Win64"``.
    long_version: str
        Long form of version number.  For example, ``"2023.1"``.

    Returns
    -------
    bool

    """
    product_list_path = os.path.join(install_path, "config", "ProductList.txt")
    if os.path.isfile(product_list_path):
        try:
            with open_file(product_list_path, "r") as f:
                install_version = f.readline().strip()[-6:]
                if install_version == long_version:
                    return True
        except Exception:
            pyaedt_logger.debug("An error occurred while parsing installation version")
    return False


@pyaedt_function_handler()
def install_with_pip(package_name, package_path=None, upgrade=False, uninstall=False):  # pragma: no cover
    """Install a new package using pip.
    This method is useful for installing a package from the AEDT Console without launching the Python environment.

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
    if is_linux and is_ironpython:
        import subprocessdotnet as subprocess  # nosec B404
    else:
        import subprocess  # nosec B404
    executable = '"{}"'.format(sys.executable) if is_windows else sys.executable

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
        if is_linux:
            p = subprocess.Popen(command)
        else:
            p = subprocess.Popen(" ".join(command))
        p.wait()


class Help:  # pragma: no cover
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
        url = self._base_path + "/search.html?q={}".format("+".join(keywords))
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
