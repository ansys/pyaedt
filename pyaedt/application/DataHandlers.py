import warnings
import random
import string
from collections import OrderedDict
from decimal import Decimal
from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from ..modeler.Object3d import EdgePrimitive, FacePrimitive, VertexPrimitive
try:
    import clr
    clr.AddReference("System.Collections")
    from System.Collections.Generic import List
    clr.AddReference("System")
    from System import Double, Array
except ImportError:
    warnings.warn("Pythonnet is needed to run pyaedt")

@aedt_exception_handler
def tuple2dict(t, d):
    """

    Parameters
    ----------
    t :
        
    d :
        

    Returns
    -------

    """
    k = t[0]
    v = t[1]
    if type(v) is list and len(t) > 2:
        d[k] = v
    elif type(v) is list and len(t) == 2 and not v:
        d[k] = None
    elif type(v) is list and type(v[0]) is tuple and len(
            t) == 2:  # len check is to avoid expanding the list with a 3rd element=None
        d[k] = OrderedDict()
        for tt in v:
            tuple2dict(tt, d[k])
    else:
        d[k] = v


@aedt_exception_handler
def dict2arg(d, arg_out):
    """

    Parameters
    ----------
    d :
        
    arg_out :
        

    Returns
    -------

    """
    for k, v in d.items():
        if isinstance(v, OrderedDict):
            arg = ["NAME:" + k]
            dict2arg(v, arg)
            arg_out.append(arg)
        elif v is None:
            arg_out.append(["NAME:" + k])
        elif type(v) is list and len(v)>0 and type(v[0]) is OrderedDict:
            for el in v:
                arg = ["NAME:" + k]
                dict2arg(el, arg)
                arg_out.append(arg)

        else:
            arg_out.append(k + ":=")
            if type(v) is EdgePrimitive or type(v) is FacePrimitive or type(v) is VertexPrimitive:
                arg_out.append(v.id)
            else:
                arg_out.append(v)


@aedt_exception_handler
def arg2dict(arg, dict_out):
    """

    Parameters
    ----------
    arg :
        
    dict_out :
        

    Returns
    -------

    """
    if arg[0][:5] == 'NAME:':
        top_key = arg[0][5:]
        dict_in = OrderedDict()
    else:
        raise ValueError('Incorrect data argument format')
    i = 1
    while i < len(arg):
        if (type(arg[i]) is list or type(arg[i]) is tuple) and arg[i][0][:5] == 'NAME:':
            arg2dict(arg[i], dict_in)
            i += 1
        elif arg[i][-2:] == ':=':
            dict_in[arg[i][:-2]] = arg[i + 1]

            i += 2
        else:
            raise ValueError('Incorrect data argument format')
    dict_out[top_key] = dict_in


@aedt_exception_handler
def create_list_for_csharp(input_list, return_strings=False):
    """

    Parameters
    ----------
    input_list :
        
    return_strings :
         (Default value = False)

    Returns
    -------

    """
    if return_strings:
        col=List[str]()
    else:
        col=List[Double]()

    for el in input_list:
        if return_strings:
            col.Add(str(el))
        else:
            col.Add(el)
    return col


@aedt_exception_handler
def create_table_for_csharp(input_list_of_list, return_strings=True):
    """

    Parameters
    ----------
    input_list_of_list :
        
    return_strings :
         (Default value = True)

    Returns
    -------

    """
    new_table = List[List[str]]()
    for col in input_list_of_list:
        newcol=create_list_for_csharp(col, return_strings)
        new_table.Add(newcol)
    return new_table


@aedt_exception_handler
def format_decimals(el):
    """

    Parameters
    ----------
    el :
        

    Returns
    -------

    """
    if float(el) > 1000:
        num = "{:,.0f}".format(Decimal(el))
    elif float(el) > 1:
        num = "{:,.3f}".format(Decimal(el))
    else:
        num = "{:.3E}".format(Decimal(el))
    return num


@aedt_exception_handler
def random_string(length=6):
    """Generate a random string

    Parameters
    ----------
    length :
        length of the random string (Default value = 6)

    Returns
    -------
    type
        random string

    """
    char_set = string.ascii_uppercase + string.digits
    random_str = ''.join(random.sample(char_set, int(length)))
    return random_str
