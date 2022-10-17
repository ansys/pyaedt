import ast
import codecs
import csv
import datetime
import difflib
import fnmatch
import inspect
import itertools
import json
import logging
import os
import random
import re
import string
import sys
import tempfile
import time
import traceback
from collections import OrderedDict
from functools import update_wrapper

is_ironpython = "IronPython" in sys.version or ".NETFramework" in sys.version
_pythonver = sys.version_info[0]
inside_desktop = True
main_module = sys.modules["__main__"]
try:
    import ScriptEnv

    ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
except:
    inside_desktop = False

is_remote_server = os.getenv("PYAEDT_IRONPYTHON_SERVER", "False").lower() in ("true", "1", "t")

if not is_ironpython:
    import psutil


class MethodNotSupportedError(Exception):
    """ """

    pass


def _write_mes(mes_text):
    mes_text = str(mes_text)
    parts = [mes_text[i : i + 250] for i in range(0, len(mes_text), 250)]
    for el in parts:
        settings.logger.error(el)


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
    tb_data = ex_info[2]
    tb_trace = traceback.format_tb(tb_data)
    if len(tb_trace) > 1:
        tblist = tb_trace[1].split("\n")
    else:
        tblist = tb_trace[0].split("\n")

    message_to_print = ""
    try:
        messages = list(main_module.oDesktop.GetMessages("", "", 2))
    except AttributeError:
        messages = []
    if messages:
        message_to_print = messages[-1]
    for el in tblist:
        if func.__name__ in el:
            _write_mes("Error in : " + el)
    _write_mes("{} - {} -  {}.".format(ex_info[1], func.__name__, message.upper()))

    if message_to_print:
        _write_mes(message_to_print)
    _write_mes("Arguments with values: ")
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


def check_and_download_file(local_path, remote_path, overwrite=True):
    """Check if a file is remote and either download it or return the path.

    Parameters
    ----------
    local_path : str
        Local path to save the file to.
    remote_path : str
        Path to the remote file.
    overwrite : bool
        Whether to overwrite the file if it already exits locally.
        The default is ``True``.

    Returns
    -------
    str
    """
    if settings.remote_rpc_session:
        remote_path = remote_path.replace("\\", "/") if remote_path[0] != "\\" else remote_path
        settings.remote_rpc_session.filemanager.download_file(remote_path, local_path, overwrite=overwrite)
        return local_path
    return remote_path


def check_and_download_folder(local_path, remote_path, overwrite=True):
    """Check if a folder is remote and either download it or return the path.

    Parameters
    ----------
    local_path : str
        Local path to save the folder to.
    remote_path : str
        Path to the remote folder.
    overwrite : bool
        Whether to overwrite the folder if it already exits locally.
        The default is ``True``.

    Returns
    -------
    str
    """
    if settings.remote_rpc_session:
        remote_path = remote_path.replace("\\", "/") if remote_path[0] != "\\" else remote_path
        settings.remote_rpc_session.filemanager.download_folder(remote_path, local_path, overwrite=overwrite)
        return local_path
    return remote_path


def open_file(file_path, file_options="r"):
    """Open a file and return the object.

    Parameters
    ----------
    file_path : str
        Full absolute path to the file (either local or remote).
    file_options : str, optional
        Options for opening the file.

    Returns
    -------
    object
        Opened file.
    """
    file_path = file_path.replace("\\", "/") if file_path[0] != "\\" else file_path
    dir_name = os.path.dirname(file_path)
    if os.path.exists(dir_name):
        return open(file_path, file_options)
    elif settings.remote_rpc_session:
        return settings.remote_rpc_session.open_file(file_path, file_options)
    else:
        return False


def convert_remote_object(arg):
    """Convert a remote list or dictionary to a native list or dictionary.

    .. note::
        This method is needed only on a Cpython-to-Ironpython connection.

    Parameters
    ----------
    arg : dict or list
        Dictionary or list to convert.

    Returns
    -------
    dict or list
        Converted dictionary or list
    """
    if _check_types(arg) == "list":
        if arg.__len__() > 0:
            if (
                isinstance(arg[0], (int, float, str))
                or _check_types(arg[0]) == "list"
                or _check_types(arg[0]) == "dict"
            ):
                a = list(ast.literal_eval(str(arg)))
                for i, el in enumerate(a):
                    a[i] = convert_remote_object(el)
                return a
            else:
                return [arg[i] for i in range(arg.__len__())]
        else:
            return []
    elif _check_types(arg) == "dict":
        a = dict(ast.literal_eval(str(arg)))
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
    if new_args and settings.enable_debug_methods_argument_logger:
        object_name = str([new_args[0]])[1:-1]
        id = object_name.find(" object at ")
        if id >= 0:
            object_name = object_name[1:id]
            message.append(" '{}' has been executed in {}".format(object_name + "." + str(func.__name__), time_msg))
            if new_args[1:]:
                message.append(line_begin + str(new_args[1:])[1:-1])
            if new_kwargs:
                message.append(line_begin2 + str(new_kwargs)[1:-1])

        else:
            message.append(" '{}' has been executed in {}".format(str(func.__name__), time_msg))
            if new_args[1:]:
                message.append(line_begin + str(new_args[1:])[1:-1])
            if new_kwargs:
                message.append(line_begin2 + str(new_kwargs)[1:-1])

    else:

        message.append(" '{}' has been executed in: {}".format(str(func.__name__), time_msg))
        if new_kwargs and settings.enable_debug_methods_argument_logger:
            message.append(line_begin2 + str(new_kwargs)[1:-1])
    for m in message:
        settings.logger.debug(m)


def pyaedt_function_handler(direct_func=None):
    """Provides an exception handler, logging mechanism, and argument converter for client-server
    communications.

    This method returns the function itself if correctly executed. Otherwise, it returns ``False``
    and displays errors.

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
        if not settings.enable_error_handler:
            result = user_function(*args, **kwargs)
            return result
        else:
            if is_remote_server:
                converted_args = _remote_list_conversion(args)
                converted_kwargs = _remote_dict_conversion(kwargs)
                args = converted_args
                kwargs = converted_kwargs
            try:
                settings.time_tick = time.time()
                out = user_function(*args, **kwargs)
                if settings.enable_debug_logger:
                    _log_method(user_function, args, kwargs)
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
                    settings.logger.error(message)
                return False
            except BaseException:
                _exception(sys.exc_info(), user_function, args, kwargs, "General or AEDT Error")
                return False

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
    """Get the path of the version environment variable for an AEDT version.

    Parameters
    ----------
    input_version : str
        AEDT version.

    Returns
    -------
    str
        Path for the version environment variable.

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
    """Get the name of the version environment variable for an AEDT version.

    Parameters
    ----------
    input_version : str
        AEDT version.

    Returns
    -------
    str
        Name for the version environment variable.

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
    """Get the path of the version environment variable for an AEDT student version.

    Parameters
    ----------
    input_version : str
       AEDT student version.

    Returns
    -------
    str
        Path for the student version environment variable.

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
    """Get the name of the version environment variable for an AEDT student version.

    Parameters
    ----------
    input_version : str
        AEDT student version.

    Returns
    -------
    str
         Name for the student version environment variable.

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
    path : str
        Path for the file.


    Returns
    -------
    str
       Name for the file, excluding its extension.

    """
    return os.path.splitext(os.path.split(path)[1])[0]


@pyaedt_function_handler()
def generate_unique_name(rootname, suffix="", n=6):
    """Generate a new name given a root name and optional suffix.

    Parameters
    ----------
    rootname :
        Root name to add random characters to.
    suffix : string
        Suffix to add. The default is ``''``.
    n : int
        Number of random characters to add to the name. The default value is ``6``.

    Returns
    -------
    str
        Newly generated name.

    """
    char_set = string.ascii_uppercase + string.digits
    uName = "".join(random.choice(char_set) for _ in range(n))
    unique_name = rootname + "_" + uName
    if suffix:
        unique_name += "_" + suffix
    return unique_name


@pyaedt_function_handler()
def generate_unique_folder_name(rootname=None, folder_name=None):
    """Generate a new AEDT folder name given a rootname.

    Parameters
    ----------
    rootname : str, optional
        Root name for the new folder. The default is ``None``.
    folder_name : str, optional
        Name for the new AEDT folder if one must be created.

    Returns
    -------
    str
    """
    if not rootname:
        rootname = tempfile.gettempdir()
    if folder_name is None:
        folder_name = generate_unique_name("pyaedt_prj", n=3)
    temp_folder = os.path.join(rootname, folder_name)
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    return temp_folder


@pyaedt_function_handler()
def generate_unique_project_name(rootname=None, folder_name=None, project_name=None, project_format="aedt"):
    """Generate a new AEDT project name given a rootname.

    Parameters
    ----------
    rootname : str, optional
        Root name where the new project is to be created.
    folder_name : str, optional
        Name of the folder to create. The default is ``None``, in which case a random folder
        is created. Use ``""`` if you do not want to create a subfolder.
    project_name : str, optional
        Name for the project. The default is ``None``, in which case a random project is
        created. If a project with this name already exists, a new suffix is added.
    project_format : str, optional
        Project format. The default is ``"aedt"``. Options are ``"aedt"`` and ``"aedb"``.

    Returns
    -------
    str
    """
    if not project_name:
        project_name = generate_unique_name("Project", n=3)
    name_with_ext = project_name + "." + project_format
    folder_path = generate_unique_folder_name(rootname, folder_name=folder_name)
    prj = os.path.join(folder_path, name_with_ext)
    if os.path.exists(prj):
        name_with_ext = generate_unique_name(project_name, n=3) + "." + project_format
        prj = os.path.join(folder_path, name_with_ext)
    return prj


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


def is_array(a):
    try:
        v = list(ast.literal_eval(a))
    except (ValueError, TypeError, NameError, SyntaxError):
        return False
    else:
        if type(v) is list:
            return True
        else:
            return False


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
    return os.path.exists(project_path[:-4] + "lock")


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
    if os.path.exists(project_path + ".lock"):
        os.remove(project_path + ".lock")
    return True


@pyaedt_function_handler()
def read_csv(filename, encoding="utf-8"):
    """Read information from a CSV file and return a list.

    Parameters
    ----------
    filename : str
            Full path and name for the CSV file.
    encoding : str, optional
            File encoding for the CSV file. The default is ``"utf-8"``.

    Returns
    -------
    list

    """

    lines = []
    with codecs.open(filename, "rb", encoding) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            lines.append(row)
    return lines


@pyaedt_function_handler()
def read_tab(filename):
    """Read information from a TAB file and return a list.

    Parameters
    ----------
    filename : str
            Full path and name for the TAB file.

    Returns
    -------
    list

    """
    with open(filename) as my_file:
        lines = my_file.readlines()
    return lines


@pyaedt_function_handler()
def read_xlsx(filename):
    """Read information from an XLSX file and return a list.

    Parameters
    ----------
    filename : str
            Full path and name for the XLSX file.

    Returns
    -------
    list

    """
    try:
        import pandas as pd

        lines = pd.read_excel(filename)
        return lines
    except:
        lines = []
        return lines


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
    """Filter a tuple of two elements with two search keywords."""
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
    """Get a list of files matching a pattern, searching recursively from a start path.

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
        return "0" <= c and c <= "9"

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
def _create_json_file(json_dict, full_json_path):
    if not is_ironpython:
        with open(full_json_path, "w") as fp:
            json.dump(json_dict, fp, indent=4)
    else:
        temp_path = full_json_path.replace(".json", "_temp.json")
        with open(temp_path, "w") as fp:
            json.dump(json_dict, fp, indent=4)
        with open(temp_path, "r") as file:
            filedata = file.read()
        filedata = filedata.replace("True", "true")
        filedata = filedata.replace("False", "false")
        with open(full_json_path, "w") as file:
            file.write(filedata)
        os.remove(temp_path)
    return True


@pyaedt_function_handler()
def grpc_active_sessions(version=None, student_version=False, non_graphical=False):
    """Get information for the active gRPC AEDT sessions.

    Parameters
    ----------
    version : str, optional
        Version to check. The default is ``None``, in which case all versions are checked.
        When specififying a version, you can use a three-digit format like ``"222"`` or a
        five-digit format like ``"2022.2"``.
    student_version : bool, optional
        Whether to check for student version sessions. The default is ``False``.
    non_graphical : bool, optional
        Whether to check only for active non-graphical sessions. The default is ``False``.

    Returns
    -------
    list
        List of gRPC ports.
    """
    if student_version:
        keys = ["ansysedtsv.exe"]
    else:
        keys = ["ansysedt.exe"]
    if version and "." in version:
        version = version[-4:].replace(".", "")
    sessions = []
    for p in psutil.process_iter():
        try:
            if p.name() in keys:
                cmd = p.cmdline()
                if "-grpcsrv" in cmd:
                    if non_graphical and "-ng" in cmd or not non_graphical:
                        if not version or (version and version in cmd[0]):
                            sessions.append(
                                int(cmd[cmd.index("-grpcsrv") + 1]),
                            )
        except:
            pass
    return sessions


class PropsManager(object):
    def __getitem__(self, item):
        """Get the `self.props` key value.

        Parameters
        ----------
        item : str
            Key to search
        """
        item_split = item.split("/")
        props = self.props
        found_el = []
        matching_percentage = 1
        while matching_percentage >= 0.4:
            for item_value in item_split:
                found_el = difflib.get_close_matches(item_value, list(props.keys()), 1, 0.8)
                if found_el:
                    props = props[found_el[0]]
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
                if isinstance(v, (dict, OrderedDict)):
                    out_val = self._recursive_search(v, key, matching_percentage)
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
            if isinstance(v, (dict, OrderedDict)):
                available_list.extend(self._recursive_list(v, name))
        return available_list

    @property
    def available_properties(self):
        """Available properties.

        Returns
        -------
        list
        """
        return self._recursive_list(self.props)

    @pyaedt_function_handler()
    def update(self):
        """Update method."""
        pass


class Settings(object):
    """Class that manages all PyAEDT environment variables and global settings."""

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
        self._enable_debug_methods_argument_logger = False
        self._enable_debug_geometry_operator_logger = False
        self._enable_debug_internal_methods_logger = False
        self._enable_debug_logger = False
        self._enable_error_handler = True
        self._non_graphical = False
        self.aedt_version = None
        self.remote_api = False
        self._use_grpc_api = False
        self.machine = ""
        self.port = 0
        self.formatter = None
        self.remote_rpc_session = None
        self.remote_rpc_session_temp_folder = ""
        self.remote_rpc_service_manager_port = 17878
        self._project_properties = {}
        self._project_time_stamp = 0
        self._disable_bounding_box_sat = False
        self._force_error_on_missing_project = False
        self._enable_pandas_output = False
        self.time_tick = time.time()

    @property
    def enable_pandas_output(self):
        """Set/Get a flag to use Pandas to export dict and lists. This applies to Solution data output.
        If ``True`` the property or method will return a pandas object in CPython environment.
        Default is ``False``.

        Returns
        -------
        bool
        """
        return self._enable_pandas_output

    @enable_pandas_output.setter
    def enable_pandas_output(self, val):
        self._enable_pandas_output = val

    @property
    def enable_debug_methods_argument_logger(self):
        """Set/Get a flag to plot methods argument in debug logger.
        Default is ``False``.

        Returns
        -------
        bool
        """
        return self._enable_debug_methods_argument_logger

    @enable_debug_methods_argument_logger.setter
    def enable_debug_methods_argument_logger(self, val):
        self._enable_debug_methods_argument_logger = val

    @property
    def force_error_on_missing_project(self):
        """Set/Get a flag to check project path.
        If ``True`` when passing a project path, the project has to exist otherwise it will raise an error.
        Default is ``False``.

        Returns
        -------
        bool
        """
        return self._force_error_on_missing_project

    @force_error_on_missing_project.setter
    def force_error_on_missing_project(self, val):
        self._force_error_on_missing_project = val

    @property
    def disable_bounding_box_sat(self):
        """Set/Get Bounding Box Sat enablement.

        Returns
        -------
        bool
        """
        return self._disable_bounding_box_sat

    @disable_bounding_box_sat.setter
    def disable_bounding_box_sat(self, val):
        self._disable_bounding_box_sat = val

    @property
    def use_grpc_api(self):
        """Set/Get 20222R2 GPRC API usage or Legacy COM Objectr.

        Returns
        -------
        bool
        """
        return self._use_grpc_api

    @use_grpc_api.setter
    def use_grpc_api(self, val):
        """Set/Get 20222R2 GPRC API usage or Legacy COM Objectr."""
        self._use_grpc_api = val

    @property
    def logger(self):
        """Get the active logger."""
        try:
            return logging.getLogger("Global")
        except:
            return logging.getLogger(__name__)

    @property
    def non_graphical(self):
        """Get the value for the non-graphical flag."""
        return self._non_graphical

    @non_graphical.setter
    def non_graphical(self, val):
        self._non_graphical = val

    @property
    def enable_error_handler(self):
        """Return the content for the environment variable."""
        return self._enable_error_handler

    @enable_error_handler.setter
    def enable_error_handler(self, val):
        self._enable_error_handler = val

    @property
    def enable_desktop_logs(self):
        """Get the content for the environment variable."""
        return self._enable_desktop_logs

    @enable_desktop_logs.setter
    def enable_desktop_logs(self, val):
        self._enable_desktop_logs = val

    @property
    def enable_screen_logs(self):
        """Get the content for the environment variable."""
        return self._enable_screen_logs

    @enable_screen_logs.setter
    def enable_screen_logs(self, val):
        self._enable_screen_logs = val

    @property
    def pyaedt_server_path(self):
        """Get the content for the environment variable."""
        return os.getenv("PYAEDT_SERVER_AEDT_PATH", "")

    @pyaedt_server_path.setter
    def pyaedt_server_path(self, val):
        os.environ["PYAEDT_SERVER_AEDT_PATH"] = str(val)

    @property
    def enable_file_logs(self):
        """Get the content for the environment variable."""
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
