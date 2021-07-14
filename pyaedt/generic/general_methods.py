import os
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
logger = logging.getLogger(__name__)
import pkgutil
modules = [tup[1] for tup in pkgutil.iter_modules()]
if 'clr' in modules:
    import clr

class MethodNotSupportedError(Exception):
    """ """
    pass

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
    print("**************************************************************")
    print("pyaedt Error on Method {}:  {}. Please Check again".format(func.__name__, message))
    print("Arguments Provided: ")
    try:

        if int(sys.version[0]) > 2:
            args_name = list(OrderedDict.fromkeys(inspect.getfullargspec(func)[0] + list(kwargs.keys())))
            args_dict = OrderedDict(list(itertools.zip_longest(args_name, args)) + list(kwargs.items()))
        else:
            args_name = list(OrderedDict.fromkeys(inspect.getargspec(func)[0] + list(kwargs.keys())))
            args_dict = OrderedDict(list(itertools.izip(args_name, args)) + list(kwargs.iteritems()))

        for el in args_dict:
            if el != "self":
                print("    {} = {} ".format(el, args_dict[el]))
    except:
        if len(args) > 1:
            print(args[1:], kwargs)
        else:
            print(kwargs)
    ex_value = ex_info[1]
    tb_data = ex_info[2]
    tb_trace = traceback.format_tb(tb_data)
    if len(tb_trace) > 1:
        tblist = tb_trace[1].split('\n')
    else:
        tblist = tb_trace[0].split('\n')
    print("")
    print(str(ex_value))
    if logger:
        logger.error(str(ex_value))
    # self._main.oDesktop.AddMessage(proj_name, des_name, 2, str(ex_value))
    for el in tblist:
        # self._main.oDesktop.AddMessage(proj_name, des_name, 2, el)
        if "inner_function" not in el and "**kwargs" not in el:
            print(el)
            if logger:
                logger.error(el)
    print("")
    print("")
    print("Method Docstring: ")
    print("")
    print(func.__doc__)
    print("************************************************************")


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
        if "PYTEST_CURRENT_TEST" in os.environ or "UNITTEST_CURRENT_TEST" in os.environ:
            # We are running under pytest or unittest, do not use the decorator
            return func(*args, **kwargs)
        else:
            try:
                return func(*args, **kwargs)
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
                print("**************************************************************")
                print("pyaedt Error on Method {}:  {}. Please Check again".format(func.__name__, message))
                print("**************************************************************")
                print("")
                logger.error(message)
                return False
            except BaseException:
                _exception(sys.exc_info(), func, args, kwargs, "General or AEDT Error")
                return False
    return inner_function


@aedt_exception_handler
def env_path(input_version):
    """

    Parameters
    ----------
    input_version :
        

    Returns
    -------

    """
    version = int(input_version[2:4])
    release = int(input_version[5])
    if version < 20:
        if release < 3:
            version -= 1
        else:
            release -= 2
    v_key = "ANSYSEM_ROOT{0}{1}".format(version, release)
    return os.getenv(v_key)


@aedt_exception_handler
def env_value(input_version):
    """

    Parameters
    ----------
    input_version :


    Returns
    -------

    """
    version = int(input_version[2:4])
    release = int(input_version[5])
    if version < 20:
        if release < 3:
            version -= 1
        else:
            release -= 2
    v_key = "ANSYSEM_ROOT{0}{1}".format(version, release)
    return v_key


@aedt_exception_handler
def env_path_student(input_version):
    """Return the Student version Environment Variable value based on an input version string

    Parameters
    ----------
    input_version : str


    Returns
    -------
    str

    Examples
    --------
    >>> env_path_student("2021.1")
    "C:/Program Files/ANSYSEM/ANSYSEM2021.1/Win64"
    """
    version = int(input_version[2:4])
    release = int(input_version[5])
    if version < 20:
        if release < 3:
            version -= 1
        else:
            release -= 2
    v_key = "ANSYSEMSV_ROOT{0}{1}".format(version, release)
    return os.getenv(v_key)


@aedt_exception_handler
def env_value_student(input_version):
    """Return the Student version Environment Variable name based on an input version string

    Parameters
    ----------
    input_version : str


    Returns
    -------
    str

    Examples
    --------
    >>> env_value_student("2021.1")
    "ANSYSEMSV_ROOT211"
    """
    version = int(input_version[2:4])
    release = int(input_version[5])
    if version < 20:
        if release < 3:
            version -= 1
        else:
            release -= 2
    v_key = "ANSYSEMSV_ROOT{0}{1}".format(version, release)
    return v_key


@aedt_exception_handler
def get_filename_without_extension(path):
    """

    Parameters
    ----------
    path :
        

    Returns
    -------

    """
    return os.path.splitext(os.path.split(path)[1])[0]


@aedt_exception_handler
def generate_unique_name(rootname, suffix='', n=6):
    """Generate a new Random name given a rootname and, optionally a suffix

    Parameters
    ----------
    rootname :
        Root name to which add 6 Random chars
    suffix :
        Suffix to be added (Default value = '')
    n :
        Number of random characters in the name, defaults to 6

    Returns
    -------

    """
    char_set = string.ascii_uppercase + string.digits
    uName = ''.join(random.choice(char_set) for _ in range(n))
    unique_name = rootname + "_" + uName
    if suffix:
        unique_name += "_" + suffix
    return unique_name


def retry_ntimes(n, function, *args, **kwargs):
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
            time.sleep(0.05)
        else:
            break
    return ret_val

def time_fn( fn, *args, **kwargs ):
    start = datetime.datetime.now()
    results = fn( *args, **kwargs )
    end = datetime.datetime.now()
    fn_name = fn.__module__ + "." + fn.__name__
    delta = (end - start).microseconds * 1e-6
    print(fn_name + ": " + str(delta) + "s")
    return results

def isclose(a, b, rel_tol=1e-9, abs_tol=0.0):
    return abs(a-b) <= max( rel_tol * max(abs(a), abs(b)), abs_tol )