import csv
import datetime
import fnmatch
import inspect
import itertools
import logging
import os
import random
import re
import string
import sys
import time
import traceback
from collections import OrderedDict
from functools import update_wrapper

try:
    logger = logging.getLogger("Global")
except:
    logger = logging.getLogger(__name__)
is_ironpython = "IronPython" in sys.version or ".NETFramework" in sys.version
_pythonver = sys.version_info[0]
inside_desktop = True
import sys

try:
    import ScriptEnv

    ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
except:
    inside_desktop = False

is_remote_server = os.getenv("PYAEDT_IRONPYTHON_SERVER", "False").lower() in ("true", "1", "t")


class MethodNotSupportedError(Exception):
    """ """

    pass


def _write_mes(mes_text):
    mes_text = str(mes_text)
    parts = [mes_text[i : i + 250] for i in range(0, len(mes_text), 250)]
    if logger:
        for el in parts:
            logger.error(el)
    elif settings.enable_screen_logs:
        for el in parts:
            print(el)


def _exception(ex_info, func, args, kwargs, message="Type Error"):
    """Writes the trace stack to the desktop when a python error occurs

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
    message_to_print = ""
    if "oDesktop" in dir(sys.modules["__main__"]):
        try:
            messages = list(sys.modules["__main__"].oDesktop.GetMessages("", "", 2))
        except:
            messages = []
        if messages and "[error] Script macro error" in messages[-1]:
            message_to_print = messages[-1]
    _write_mes("Method {} Failed:  {}. Please Check again".format(func.__name__, message))
    _write_mes(ex_info[1])
    if message_to_print:
        _write_mes(message_to_print)
    _write_mes("Arguments Provided: ")
    try:
        if int(sys.version[0]) > 2:
            args_name = list(OrderedDict.fromkeys(inspect.getfullargspec(func)[0] + list(kwargs.keys())))
            args_dict = OrderedDict(list(itertools.zip_longest(args_name, args)) + list(kwargs.items()))
        else:
            args_name = list(OrderedDict.fromkeys(inspect.getargspec(func)[0] + list(kwargs.keys())))
            args_dict = OrderedDict(list(itertools.izip(args_name, args)) + list(kwargs.iteritems()))

        for el in args_dict:
            if el != "self":
                _write_mes("    {} = {} ".format(el, args_dict[el]))
    except:
        pass
    tb_data = ex_info[2]
    tb_trace = traceback.format_tb(tb_data)
    if len(tb_trace) > 1:
        tblist = tb_trace[1].split("\n")
    else:
        tblist = tb_trace[0].split("\n")
    for el in tblist:
        if func.__name__ in el:
            _write_mes("Error in : " + el)
    _write_mes("Check Online documentation on: https://aedtdocs.pyansys.com/search.html?q={}".format(func.__name__))


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


def convert_remote_object(arg):
    """Convert Remote list or dict to native list and dictionary.

    .. note::
        This is needed only on Cpython to Ironpython Connection.

    Parameters
    ----------
    arg : dict or list
        Object to convert
    Returns
    -------
    dict or list
    """
    if _check_types(arg) == "list":
        if arg.__len__() > 0:
            if (
                isinstance(arg[0], (int, float, str))
                or _check_types(arg[0]) == "list"
                or _check_types(arg[0]) == "dict"
            ):
                a = list(eval(str(arg)))
                for i, el in enumerate(a):
                    a[i] = convert_remote_object(el)
                return a
            else:
                return [arg[i] for i in range(arg.__len__())]
        else:
            return []
    elif _check_types(arg) == "dict":
        a = dict(eval(str(arg)))
        for k, v in a.items():
            a[k] = convert_remote_object(v)
        return a
    return arg


def _remote_list_conversion(args):
    new_args = []
    if args:
        for arg in args:
            new_args.append(convert_remote_object(arg))
    return new_args


def _remote_dict_conversion(args):
    if args:
        new_kwargs = {}
        for arg in args:
            new_kwargs[arg] = convert_remote_object(args[arg])
    else:
        new_kwargs = args
    return new_kwargs


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
    line_begin = "    Implicit Arguments: "
    line_begin2 = "    Explicit Arguments: "
    message = []
    if new_args:
        object_name = str([new_args[0]])[1:-1]
        id = object_name.find(" object at ")
        if id >= 0:
            object_name = object_name[1:id]
            message.append(" '{}' has been exectuted.".format(object_name + "." + str(func.__name__)))
            if new_args[1:]:
                message.append(line_begin + str(new_args[1:])[1:-1])
            if new_kwargs:
                message.append(line_begin2 + str(new_kwargs)[1:-1])

        else:
            message.append(" '{}' has been exectuted.".format(str(func.__name__)))
            if new_args[1:]:
                message.append(line_begin + str(new_args[1:])[1:-1])
            if new_kwargs:
                message.append(line_begin2 + str(new_kwargs)[1:-1])

    else:
        message.append(" '{}' has been exectuted".format(str(func.__name__)))
        if new_kwargs:
            message.append(line_begin2 + str(new_kwargs)[1:-1])
    for m in message:
        logger.debug(m)


def pyaedt_function_handler(direct_func=None):
    """Decorator for pyaedt Exception, Logging, and Conversion management.
    Provides an exception handler, a logging mechanism and an argument conversion for clien-server
    communications.

    It returns the function itself if correctly executed otherwise it will return False and errors
    will be displayed.

    """

    if callable(direct_func):
        user_function = direct_func
        wrapper = _function_handler_wrapper(user_function)
        return update_wrapper(wrapper, user_function)
    elif direct_func is not None:
        raise TypeError("Expected first argument to be a callable, or None")

    def decorating_function(user_function):
        wrapper = _function_handler_wrapper(user_function)
        return update_wrapper(wrapper, user_function)

    return decorating_function


def _function_handler_wrapper(user_function):
    def wrapper(*args, **kwargs):
        if is_remote_server:
            converted_args = _remote_list_conversion(args)
            converted_kwargs = _remote_dict_conversion(kwargs)
            args = converted_args
            kwargs = converted_kwargs
        if settings.enable_debug_logger:
            _log_method(user_function, args, kwargs)
        if settings.enable_error_handler:
            try:
                out = user_function(*args, **kwargs)
                return out
            except TypeError:
                if not is_remote_server:
                    _exception(sys.exc_info(), user_function, args, kwargs, "Type Error")
                return False
            except ValueError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Value Error")
                return False
            except AttributeError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Attribute Error")
                return False
            except KeyError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Key Error")
                return False
            except IndexError:
                if not is_remote_server:
                    _exception(sys.exc_info(), user_function, args, kwargs, "Index Error")
                    return False
            except AssertionError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Assertion Error")
                return False
            except NameError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Name Error")
                return False
            except IOError:
                _exception(sys.exc_info(), user_function, args, kwargs, "IO Error")
                return False
            except MethodNotSupportedError:
                message = "This Method is not supported in current AEDT Design Type."
                if settings.enable_screen_logs:
                    print("**************************************************************")
                    print("pyaedt error on Method {}:  {}. Please Check again".format(user_function.__name__, message))
                    print("**************************************************************")
                    print("")
                if settings.enable_file_logs:
                    logger.error(message)
                return False
            except BaseException:
                _exception(sys.exc_info(), user_function, args, kwargs, "General or AEDT Error")
                return False

        result = user_function(*args, **kwargs)
        return result

    return wrapper


@pyaedt_function_handler()
def get_version_and_release(input_version):
    version = int(input_version[2:4])
    release = int(input_version[5])
    if version < 20:
        if release < 3:
            version -= 1
        else:
            release -= 2
    return (version, release)


@pyaedt_function_handler()
def env_path(input_version):
    """Return the version Environment Variable name based on an input version string.

    Parameters
    ----------
    input_version : str

    Returns
    -------
    str

    Examples
    --------
    >>> env_path_student("2021.2")
    "C:/Program Files/ANSYSEM/ANSYSEM2021.2/Win64"
    """
    return os.getenv(
        "ANSYSEM_ROOT{0}{1}".format(
            get_version_and_release(input_version)[0], get_version_and_release(input_version)[1]
        ),
        "",
    )


@pyaedt_function_handler()
def env_value(input_version):
    """Return the version Environment Variable value based on an input version string.

    Parameters
    ----------
    input_version : str

    Returns
    -------
    str

    Examples
    --------
    >>> env_value("2021.2")
    "ANSYSEM_ROOT211"
    """
    return "ANSYSEM_ROOT{0}{1}".format(
        get_version_and_release(input_version)[0], get_version_and_release(input_version)[1]
    )


@pyaedt_function_handler()
def env_path_student(input_version):
    """Return the Student version Environment Variable value based on an input version string.

    Parameters
    ----------
    input_version : str

    Returns
    -------
    str

    Examples
    --------
    >>> env_path_student("2021.2")
    "C:/Program Files/ANSYSEM/ANSYSEM2021.2/Win64"
    """
    return os.getenv(
        "ANSYSEMSV_ROOT{0}{1}".format(
            get_version_and_release(input_version)[0], get_version_and_release(input_version)[1]
        ),
        "",
    )


@pyaedt_function_handler()
def env_value_student(input_version):
    """Return the Student version Environment Variable name based on an input version string.

    Parameters
    ----------
    input_version : str

    Returns
    -------
    str

    Examples
    --------
    >>> env_value_student("2021.2")
    "ANSYSEMSV_ROOT211"
    """
    return "ANSYSEMSV_ROOT{0}{1}".format(
        get_version_and_release(input_version)[0], get_version_and_release(input_version)[1]
    )


@pyaedt_function_handler()
def get_filename_without_extension(path):
    """Get the filename without its extension.

    Parameters
    ----------
    path :


    Returns
    -------
    str

    """
    return os.path.splitext(os.path.split(path)[1])[0]


@pyaedt_function_handler()
def generate_unique_name(rootname, suffix="", n=6):
    """Generate a new  name given a rootname and optionally a suffix.

    Parameters
    ----------
    rootname :
        Root name to which add 6 Random chars
    suffix :
        Suffix to be added (Default value = '')
    n :
        Number of random characters in the name. The default value is 6.

    Returns
    -------

    """
    char_set = string.ascii_uppercase + string.digits
    uName = "".join(random.choice(char_set) for _ in range(n))
    unique_name = rootname + "_" + uName
    if suffix:
        unique_name += "_" + suffix
    return unique_name


def _retry_ntimes(n, function, *args, **kwargs):
    """

    Parameters
    ----------
    n :

    function :

    *args :

    **kwargs :


    Returns
    -------

    """
    retry = 0
    ret_val = None
    while retry < n:
        try:
            ret_val = function(*args, **kwargs)
            if not ret_val and type(ret_val) is not float and type(ret_val) is not int:
                ret_val = True
        except:
            retry += 1
            time.sleep(0.1)
        else:
            break
    if retry == n:
        if "__name__" in dir(function):
            raise AttributeError("Error in Executing Method {}.".format(function.__name__))
        else:
            raise AttributeError("Error in Executing Method.")

    return ret_val


def time_fn(fn, *args, **kwargs):
    start = datetime.datetime.now()
    results = fn(*args, **kwargs)
    end = datetime.datetime.now()
    fn_name = fn.__module__ + "." + fn.__name__
    delta = (end - start).microseconds * 1e-6
    print(fn_name + ": " + str(delta) + "s")
    return results


def isclose(a, b, rel_tol=1e-9, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def is_number(a):
    if isinstance(a, float) or isinstance(a, int):
        return True
    elif isinstance(a, str):
        try:
            float(a)
            return True
        except ValueError:
            return False
    else:
        return False
    # return str(a).replace(".", "").replace("+", "").replace("-", "").replace("e","").replace("E","").isnumeric()


def is_project_locked(project_path):
    """Checks if an aedt project lock file exists.

    Parameters
    ----------
    project_path : str
        Aedt project path.

    Returns
    -------
    bool
    """
    return os.path.exists(project_path[:-4] + "lock")


@pyaedt_function_handler()
def remove_project_lock(project_path):
    """Checks if an aedt project exists and try to remove the lock file.

    .. note::
       This operation is risky because the file could be opened in another Desktop instance.

    Parameters
    ----------
    project_path : str
        Aedt project path.

    Returns
    -------
    bool
    """
    if os.path.exists(project_path + ".lock"):
        os.remove(project_path + ".lock")
    return True


@pyaedt_function_handler()
def write_csv(output, list_data, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL):
    if is_ironpython:
        f = open(output, "wb")
    else:
        f = open(output, "w", newline="")
    writer = csv.writer(f, delimiter=delimiter, quotechar=quotechar, quoting=quoting)
    for data in list_data:
        writer.writerow(data)
    f.close()
    return True


@pyaedt_function_handler()
def filter_tuple(value, search_key1, search_key2):
    """Filter a tuple of 2 elements with two search keywords"""
    ignore_case = True

    def _create_pattern(k1, k2):
        k1a = re.sub(r"\?", r".", k1)
        k1b = re.sub(r"\*", r".*?", k1a)
        k2a = re.sub(r"\?", r".", k2)
        k2b = re.sub(r"\*", r".*?", k2a)
        pattern = r".*\({},{}\)".format(k1b, k2b)
        return pattern

    if ignore_case:
        compiled_re = re.compile(_create_pattern(search_key1, search_key2), re.IGNORECASE)
    else:
        compiled_re = re.compile(_create_pattern(search_key1, search_key2))

    m = compiled_re.search(value)
    if m:
        return True
    return False


@pyaedt_function_handler()
def filter_string(value, search_key1):
    """Filter a string"""
    ignore_case = True

    def _create_pattern(k1):
        k1a = re.sub(r"\?", r".", k1.replace("\\", "\\\\"))
        k1b = re.sub(r"\*", r".*?", k1a)
        pattern = r"^{}$".format(k1b)
        return pattern

    if ignore_case:
        compiled_re = re.compile(_create_pattern(search_key1), re.IGNORECASE)
    else:
        compiled_re = re.compile(_create_pattern(search_key1))  # pragma: no cover

    m = compiled_re.search(value)
    if m:
        return True
    return False


@pyaedt_function_handler()
def recursive_glob(startpath, filepattern):
    """Return a list of files matching a pattern, searching recursively from a start path.

    Keyword Arguments:
    startpath -- starting path (directory)
    filepattern -- fnmatch-style filename pattern
    """
    return [
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(startpath)
        for filename in filenames
        if fnmatch.fnmatch(filename, filepattern)
    ]


class Settings(object):
    """Class that manages all PyAEDT Environment Variables and global settings."""

    def __init__(self):
        self._enable_logger = True
        self._enable_desktop_logs = True
        self._enable_screen_logs = True
        self._enable_file_logs = True
        self.pyaedt_server_path = ""
        self._logger_file_path = None
        self._logger_formatter = "%(asctime)s:%(destination)s:%(extra)s%(levelname)-8s:%(message)s"
        self._logger_datefmt = "%Y/%m/%d %H.%M.%S"
        self._enable_debug_edb_logger = False
        self._enable_debug_geometry_operator_logger = False
        self._enable_debug_internal_methods_logger = False
        self._enable_debug_logger = False
        self._enable_error_handler = True
        self._non_graphical = False
        self.aedt_version = None

    @property
    def non_graphical(self):
        """Return the non graphical flag."""
        return self._non_graphical

    @non_graphical.setter
    def non_graphical(self, val):
        self._non_graphical = val

    @property
    def enable_error_handler(self):
        """Return the Environment Variable Content."""
        return self._enable_error_handler

    @enable_error_handler.setter
    def enable_error_handler(self, val):
        self._enable_error_handler = val

    @property
    def enable_desktop_logs(self):
        """Return the Environment Variable Content."""
        return self._enable_desktop_logs

    @enable_desktop_logs.setter
    def enable_desktop_logs(self, val):
        self._enable_desktop_logs = val

    @property
    def enable_screen_logs(self):
        """Return the Environment Variable Content."""
        return self._enable_screen_logs

    @enable_screen_logs.setter
    def enable_screen_logs(self, val):
        self._enable_screen_logs = val

    @property
    def pyaedt_server_path(self):
        """Return the Environment Variable Content."""
        return os.getenv("PYAEDT_SERVER_AEDT_PATH", "")

    @pyaedt_server_path.setter
    def pyaedt_server_path(self, val):
        os.environ["PYAEDT_SERVER_AEDT_PATH"] = str(val)

    @property
    def enable_file_logs(self):
        """Return the Environment Variable Content."""
        return self._enable_file_logs

    @enable_file_logs.setter
    def enable_file_logs(self, val):
        self._enable_file_logs = val

    @property
    def enable_logger(self):
        """Return the Environment Variable Content."""
        return self._enable_logger

    @enable_logger.setter
    def enable_logger(self, val):
        self._enable_logger = val

    @property
    def logger_file_path(self):
        """Return the Environment Variable Content."""
        return self._logger_file_path

    @logger_file_path.setter
    def logger_file_path(self, val):
        self._logger_file_path = val

    @property
    def logger_formatter(self):
        """Return the Environment Variable Content."""
        return self._logger_formatter

    @logger_formatter.setter
    def logger_formatter(self, val):
        self._logger_formatter = val

    @property
    def logger_datefmt(self):
        """Return the Environment Variable Content."""
        return self._logger_datefmt

    @logger_datefmt.setter
    def logger_datefmt(self, val):
        self._logger_datefmt = val

    @property
    def enable_debug_edb_logger(self):
        """Return the Environment Variable Content."""
        return self._enable_debug_edb_logger

    @enable_debug_edb_logger.setter
    def enable_debug_edb_logger(self, val):
        self._enable_debug_edb_logger = val

    @property
    def enable_debug_geometry_operator_logger(self):
        """Return the Environment Variable Content."""
        return self._enable_debug_geometry_operator_logger

    @enable_debug_geometry_operator_logger.setter
    def enable_debug_geometry_operator_logger(self, val):
        self._enable_debug_geometry_operator_logger = val

    @property
    def enable_debug_internal_methods_logger(self):
        """Return the Environment Variable Content."""
        return self._enable_debug_internal_methods_logger

    @enable_debug_internal_methods_logger.setter
    def enable_debug_internal_methods_logger(self, val):
        self._enable_debug_internal_methods_logger = val

    @property
    def enable_debug_logger(self):
        """Return the Environment Variable Content."""
        return self._enable_debug_logger

    @enable_debug_logger.setter
    def enable_debug_logger(self, val):
        self._enable_debug_logger = val


settings = Settings()
