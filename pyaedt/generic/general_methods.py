import os
import csv
import string
import random
import time
import datetime
import sys
import traceback
import logging
from functools import wraps
from collections import OrderedDict
import inspect
import itertools

try:
    logger = logging.getLogger('Global')
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
    parts = [mes_text[i:i + 250] for i in range(0, len(mes_text), 250)]
    if logger:
        for el in parts:
            logger.error(el)
    elif os.getenv("PYAEDT_SCREEN_LOGS", "True").lower() in ("true", "1", "t"):
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
    if "oDesktop" in dir(sys.modules['__main__']):
        try:
            messages = list(sys.modules['__main__'].oDesktop.GetMessages("", "", 2))
        except:
            messages = []
        if messages and '[error] Script macro error' in messages[-1]:
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
            _write_mes("Error in : "+el)
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
        return list(eval(str(arg)))
    elif _check_types(arg) == "dict":
        return dict(eval(str(arg)))
    return arg


def _remote_list_conversion(args):
    if not is_remote_server:
        return args
    new_args = []
    if args:
        for arg in args:
            new_args.append(convert_remote_object(arg))
    return new_args


def _remote_dict_conversion(args):
    if not is_remote_server:
        return args

    if args:
        new_kwargs = {}
        for arg in args:
            new_kwargs[arg] = convert_remote_object(args[arg])
    else:
        new_kwargs = args
    return new_kwargs

def _log_method(func, new_args, new_kwargs):
    if str(func.__name__)[0] != "_":
        line_begin = "    Implicit Arguments: "
        line_begin2 = "    Explicit Arguments: "
        message = []
        if new_args:
            object_name = str([new_args[0]])[1:-1]
            id = object_name.find(" object at ")
            if id >= 0:
                object_name = object_name[1:id]
                message.append(" '{}' has been exectuted.".format(
                    object_name + "." + str(func.__name__)))
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


def aedt_exception_handler(func):
    """Decorator for pyaedt Exception Management

    Parameters
    ----------
    func :
        method to be decorated

    Returns
    -------
    type
        function return if correctly executed otherwise it will return False and errors will be plotted

    """

    @wraps(func)
    def inner_function(*args, **kwargs):
        if os.getenv("PYAEDT_ERROR_HANDLER", "True").lower() in ("true", "1", "t"):
            try:
                new_args = _remote_list_conversion(args)
                new_kwargs = _remote_dict_conversion(kwargs)
                out = func(*new_args, **new_kwargs)
                _log_method(func, new_args, new_kwargs)
                return out
            except TypeError:
                _exception(sys.exc_info(), func, args, kwargs, "Type Error")
                return False
            except ValueError:
                _exception(sys.exc_info(), func, args, kwargs, "Value Error")
                return False
            except AttributeError:
                _exception(sys.exc_info(), func, args, kwargs, "Attribute Error")
                return False
            except KeyError:
                _exception(sys.exc_info(), func, args, kwargs, "Key Error")
                return False
            except IndexError:
                _exception(sys.exc_info(), func, args, kwargs, "Index Error")
                return False
            except AssertionError:
                _exception(sys.exc_info(), func, args, kwargs, "Assertion Error")
                return False
            except NameError:
                _exception(sys.exc_info(), func, args, kwargs, "Name Error")
                return False
            except IOError:
                _exception(sys.exc_info(), func, args, kwargs, "IO Error")
                return False
            except MethodNotSupportedError:
                message = "This Method is not supported in current AEDT Design Type."
                if os.getenv("PYAEDT_SCREEN_LOGS", "True").lower() in ("true", "1", "t"):
                    print("**************************************************************")
                    print("pyaedt error on Method {}:  {}. Please Check again".format(func.__name__, message))
                    print("**************************************************************")
                    print("")
                if os.getenv("PYAEDT_FILE_LOGS", "True").lower() in ("true", "1", "t"):
                    logger.error(message)
                return False
            except BaseException:
                _exception(sys.exc_info(), func, args, kwargs, "General or AEDT Error")

                return False
        else:
            return func(*args, **kwargs)

    return inner_function

@aedt_exception_handler
def get_version_and_release(input_version):
    version = int(input_version[2:4])
    release = int(input_version[5])
    if version < 20:
        if release < 3:
            version -= 1
        else:
            release -= 2
    return (version, release)


@aedt_exception_handler
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
    return os.getenv("ANSYSEM_ROOT{0}{1}".format(
        get_version_and_release(input_version)[0],
        get_version_and_release(input_version)[1]), "")


@aedt_exception_handler
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
        get_version_and_release(input_version)[0],
        get_version_and_release(input_version)[1])


@aedt_exception_handler
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
    return os.getenv("ANSYSEMSV_ROOT{0}{1}".format(
        get_version_and_release(input_version)[0],
        get_version_and_release(input_version)[1]), "")


@aedt_exception_handler
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
        get_version_and_release(input_version)[0],
        get_version_and_release(input_version)[1])


@aedt_exception_handler
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


@aedt_exception_handler
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
    return os.path.exists(project_path[:-4]+"lock")

@aedt_exception_handler
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

@aedt_exception_handler
def write_csv(output, list_data, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL):
    if is_ironpython:
        f = open(output, 'wb')
    else:
        f = open(output, 'w', newline='')
    writer = csv.writer(f, delimiter=delimiter, quotechar=quotechar, quoting=quoting)
    for data in list_data:
        writer.writerow(data)
    f.close()
    return True
