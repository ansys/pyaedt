import re
import os
from datetime import datetime
import math
import cmath
from .general_methods import generate_unique_name, aedt_exception_handler
REAL_IMAG = 'RI'
MAG_ANGLE = 'MA'
DB_ANGLE = 'DB'

keys = {
    REAL_IMAG: ('real', 'imag'),
    MAG_ANGLE: ('mag', 'deg'),
    DB_ANGLE: ('db20', 'deg')
}

def parameter(real=None, imag=None, mag=None, db10=None, db20=None, deg=None,
              rad=None):
    """Initialize a parameter
    Specify:
    * real and (optionally) imag, or
    * mag/db and deg/rad

    Parameters
    ----------
    real :
         (Default value = None)
    imag :
         (Default value = None)
    mag :
         (Default value = None)
    db10 :
         (Default value = None)
    db20 :
         (Default value = None)
    deg :
         (Default value = None)
    rad :
         (Default value = None)

    Returns
    -------

    """
    if real is not None:
        if (mag or db10 or db20 or deg or rad) is not None:
            raise ValueError('Illegal combination of arguments.')
        if imag is None:
            imag = 0
    else: # real is None
        if ((imag is not None) and
            (mag and db10 and db20 is not None) and
            (deg and rad is not None)):
            raise ValueError('Illegal combination of arguments.')

        if db10 is not None:
            mag = 10**(db10 / 10.0)
        elif db20 is not None:
            mag = 10**(db20 / 20.0)
        if deg is not None:
            rad = deg*math.pi/180

        real = mag * math.cos(rad)
        imag = mag * math.sin(rad)

    return complex(real, imag)


def real(arg):
    """

    Parameters
    ----------
    arg :
        

    Returns
    -------
    type
        

    """
    return arg.real


def imag(arg):
    """

    Parameters
    ----------
    arg :
        

    Returns
    -------
    type
        

    """
    return arg.imag


def mag(arg):
    """

    Parameters
    ----------
    arg :
        

    Returns
    -------
    type
        

    """
    return abs(arg)


def db10(arg):
    """

    Parameters
    ----------
    arg :
        

    Returns
    -------
    type
        

    """
    return 10.0 * math.log10(mag(arg))


def db20(arg):
    """

    Parameters
    ----------
    arg :
        

    Returns
    -------
    type
        

    """
    return 20.0 * math.log10(mag(arg))


def rad(arg):
    """

    Parameters
    ----------
    arg :
        

    Returns
    -------
    type
        

    """
    return arg*math.pi/180


def deg(arg):
    """

    Parameters
    ----------
    arg :
        

    Returns
    -------
    type
        

    """
    return arg*180/math.pi


formats = {
    REAL_IMAG: (real, imag),
    MAG_ANGLE: (mag, deg),
    DB_ANGLE: (db20, deg)
}


class ParseError(Exception):
    """ """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "{0}: {1}".format(__class__, self.message)


class TouchstoneData(object):
    """Data Class containing information from Touchstone Read call"""

    def __init__(self, freqs, matrix, portnames):
        self._sweeps_names = ["Freq"]
        self.sweeps= {"Freq":freqs}
        self.ports = portnames
        self.expressions = []
        for el in portnames:
            for el1 in portnames:
                self.expressions.append("S({},{})".format(el,el1))

        self._primary_sweep = "Freq"
        self.solutions_data_real, self.solutions_data_imag = self._solutions_data(matrix)
        self.solutions_data_mag = {}
        self.units_data = {}
        for expr in self.expressions:
            self.solutions_data_mag[expr] = [
                abs(complex(self.solutions_data_real[expr][i], self.solutions_data_imag[expr][i])) for i in
                range(len(self.solutions_data_real[expr]))]

    def _solutions_data(self, matrix):
        """

        Parameters
        ----------
        matrix :
            

        Returns
        -------

        """
        sols_data_real = {}
        sols_data_imag = {}
        i=0
        expression = ""
        for element in matrix:
            k=0
            for expression in self.expressions:
                values = []
                for el in reversed(self._sweeps_names):
                    values.append(self.sweeps[el])
                t=tuple([self.sweeps["Freq"][i]])
                if expression in sols_data_real:
                    sols_data_real[expression].append(element[k].real)
                    sols_data_imag[expression].append(element[k].imag)
                else:
                    sols_data_real[expression]=[element[k].real]
                    sols_data_imag[expression]=[element[k].imag]
                k+=1
            i+=1

        return sols_data_real, sols_data_imag

    def data_magnitude(self, expression=None):
        """Return the data magnitude of the given expression. if no expression is provided, first expression is provided

        Parameters
        ----------
        expression :
            string expression name (Default value = None)

        Returns
        -------
        type
            List of data

        """
        if not expression:
            expression = self.expressions[0]
        return list(self.solutions_data_mag[expression])

    def data_db(self, expression=None):
        """Return the data in db of the given expression. if no expression is provided, first expression is provided

        Parameters
        ----------
        expression :
            string expression name (Default value = None)

        Returns
        -------
        type
            List of data

        """
        if not expression:
            expression = self.expressions[0]
        try:
            return [10*math.log10(i) for i in self.data_magnitude(expression)]
        except:
            print("Error in DB Computation")
            return None

    def data_real(self, expression=None):
        """Return the real part of data  of the given expression. if no expression is provided, first expression is provided

        Parameters
        ----------
        expression :
            string expression name (Default value = None)

        Returns
        -------
        type
            List of data

        """

        if not expression:
            expression = self.expressions[0]
        return list(self.solutions_data_real[expression])

    def data_imag(self, expression=None):
        """Return the imaginary part of data  of the given expression. if no expression is provided, first expression is provided

        Parameters
        ----------
        expression :
            string expression name (Default value = None)

        Returns
        -------
        type
            List of data

        """
        if not expression:
            expression = self.expressions[0]
        return list(self.solutions_data_imag[expression])


@aedt_exception_handler
def get_return_losses(excitation_names, excitation_name_prefix=''):
    """Get the list of all the Returnloss from a list of exctitations. If no excitation is provided it will provide a full list of return Losses
    Example: excitation_names ["1","2"] is_touchstone_expression=False output ["S(1,1)",, S(2,2)]
    Example: excitation_names ["S(1,1)","S(1,2)", S(2,2)] is_touchstone_expression=True output ["S(1,1)",, S(2,2)]

    Parameters
    ----------
    excitation_names :
        list of excitation to include
    excitation_name_prefix :
         (Default value = '')

    Returns
    -------
    type
        list of string representing Return Losses of excitations

    """
    spar = []
    if excitation_name_prefix:
        excitation_names = [i for i in excitation_names if excitation_name_prefix.lower() in i.lower()]
    for i in excitation_names:
        spar.append("S({},{})".format(i, i))
    return spar

@aedt_exception_handler
def get_insertion_losses_from_prefix(expressions, tx_prefix, rx_prefix):
    """Get the list of all the Insertion Losses from prefix.

    Parameters
    ----------
    expressions :
        list of Drivers to include or all nets
    reclist :
        list of Receiver to include. Number of Driver = Number of Receiver an
    tx_prefix :
        prefix for TX (eg. "DIE")
    rx_prefix :
        prefix for RX (eg. "BGA")

    Returns
    -------
    type
        list of string representing Insertion Losses of excitations

    """
    spar = []
    left_list=[]
    right_list=[]
    trlist = [i for i in expressions if tx_prefix in i]
    reclist = [i for i in expressions if rx_prefix in i]
    if len(trlist)!= len(reclist):
        print("TX and RX should be same length lists")
        return False
    for i, j in zip(trlist, reclist):
        spar.append("S({},{})".format(i, j))
    return spar

@aedt_exception_handler
def get_insertion_losses_from_lists(txlist, reclist):
    """Get the list of all the Insertion Losses from two list of exctitations (driver and receiver). Optionally prefix can
    be used to retrieve driver and receiver names.
    Example: excitation_names ["1"] ["2"] output ["S(1,2)"]

    Parameters
    ----------
    txlist :
        list of Drivers to include or all nets
    reclist :
        list of Receiver to include. Number of Driver = Number of Receiver an

    Returns
    -------
    type
        list of string representing Insertion Losses of excitations

    """
    spar = []
    if len(txlist)!= len(reclist):
        print("TX and RX should be same length lists")
        return False
    for i, j in zip(txlist, reclist):
        spar.append("S({},{})".format(i, j))
    return spar

@aedt_exception_handler
def get_next_xtalk(expressions, tx_prefix=""):
    """Get the list of all the Near End XTalk a list of excitation. Optionally prefix can
    be used to retrieve driver names.
    Example: excitation_names ["1", "2", "3"] output ["S(1,2)", "S(1,3)", "S(2,3)"]

    Parameters
    ----------
    expressions :
        list of Drivers to include
    tx_prefix :
        prefix for TX (eg. "DIE") (Default value = "")

    Returns
    -------
    type
        list of string representing Near End XTalks

    """
    next = []
    if tx_prefix:
        trlist = [i for i in expressions if tx_prefix in i]
    else:
        trlist = expressions
    for i in trlist:
        k = trlist.index(i)+1
        while k < len(trlist):
            next.append("S({},{})".format(i, trlist[k]))
            k += 1
    return next

@aedt_exception_handler
def get_fext_xtalk_from_list(trlist, reclist,  skip_same_index_couples=True):
    """Get the list of all the Far End XTalk from 2 lists of exctitations.  If skip_same_index_couples is true, the tx and rx with same index
    position will be considered insertion losses and excluded from the list
    Example: excitation_names ["1", "2"] ["3","4"] output ["S(1,4)", "S(2,3)"]

    Parameters
    ----------
    trlist :
        list of Drivers to include
    reclist :
        list of Receiver to include
    skip_same_index_couples :
        Boolean ignore TX and RX couple with same index (Default value = True)

    Returns
    -------
    type
        list of string representing Far End XTalks

    """
    fext = []
    for i in trlist:
        for k in reclist:
            if not skip_same_index_couples or reclist.index(k)!= trlist.index(i):
                fext.append("S({},{})".format(i, k))
    return fext

@aedt_exception_handler
def get_fext_xtalk_from_prefix(expressions, tx_prefix, rx_prefix, skip_same_index_couples=True):
    """Get the list of all the Far End XTalk from a list of exctitations and a prefix that will
    be used to retrieve driver and receivers names. If skip_same_index_couples is true, the tx and rx with same index
    position will be considered insertion losses and excluded from the list

    Parameters
    ----------
    expressions :
        list of Receiver to include
    tx_prefix :
        prefix for TX (eg. "DIE")
    reclist :
        list of Receiver to include
    rx_prefix :
        prefix for RX (eg. "BGA")
    skip_same_index_couples :
        Boolean ignore TX and RX couple with same index (Default value = True)

    Returns
    -------
    type
        list of string representing Far End XTalks

    """
    fext = []
    trlist = [i for i in expressions if tx_prefix in i]
    reclist = [i for i in expressions if rx_prefix in i]
    for i in trlist:
        for k in reclist:
            if not skip_same_index_couples or reclist.index(k)!= trlist.index(i):
                fext.append("S({},{})".format(i, k))
    return fext

@aedt_exception_handler
def get_worst_curve_from_solution_data(solution_data, freq_min=None, freq_max=None, worst_is_higher=True,
                                       curve_list=None):
    """This method analyze a solution data object with multiple curves and find the worst curve returning its name and
     a ordered dictionary with each curve mean. Actual algorithm simply takes the mean of the magnitued over the
     frequency range

    Parameters
    ----------
    solution_data :
        SolutionData or TouchstoneData object
    freq_min :
        minimum frequency to analyze (None to 0) (Default value = None)
    freq_max :
        maximum frequency to analyze (None to max freq) (Default value = None)
    worst_is_higher :
        boolean. if True, the worst curve is the one with higher mean value (Default value = True)
    curve_list :
        list of curves on which to search. None to search on all curves (Default value = None)

    Returns
    -------
    type
        worst element str, dictionary of ordered expression and their mean

    """
    if not curve_list:
        curve_list = solution_data.expressions
    return_loss_freq = solution_data.sweeps["Freq"]
    if not freq_min :
        lower_id = 0
    else:
        lower_id = next(x[0] for x in enumerate(return_loss_freq) if x[1] >= freq_min)
    if not freq_max:
        higher_id = len(return_loss_freq)-1
    else:
        if freq_max>= return_loss_freq[-1]:
            higher_id = len(return_loss_freq) - 1
        else:
            higher_id = next(x[0] for x in enumerate(return_loss_freq) if x[1] >= freq_max)

    dict_means = {}
    for el in curve_list:
        data1 = solution_data.data_magnitude(el)[lower_id:higher_id]
        mean1 =sum(data1)/len(data1)
        dict_means[el]= mean1
    dict_means = dict(sorted(dict_means.items(), key=lambda item: item[1], reverse=worst_is_higher))
    worst_el = next(iter(dict_means))
    return worst_el, dict_means


def read_touchstone(file_path, verbose=False):
    """Load the contents of a Touchstone file into an NPort

    Parameters
    ----------
    file_path :
        
    verbose :
         (Default value = False)

    Returns
    -------
    class:`nport.NPort`
        NPort holding data contained in the Touchstone file

    """
    re_filename = re.compile(r"\.s(?P<ports>\d+)+p", re.I)
    m = re_filename.search(file_path)
    ports = int(m.group('ports'))
    if verbose:
        print("File '%s'" % file_path)
        print("  Number of ports (based on file extension) = %d" % \
              ports)
    file_path = os.path.abspath(file_path)
    file = open(file_path, 'r')
    (frequnit, type, format, z0) = _parse_option_line(file, verbose)
    freqs = []
    matrices = []
    try:
        while True:
            freq, matrix = _parse_next_sample(file, ports, format)
            freqs.append(freq)
            matrices.append(matrix)
    except EOFError:
        pass
    finally:
        file.close()
    file = open(file_path, 'r')
    port_names = _parse_ports_name(file)
    file.close()
    data = TouchstoneData(freqs, matrices, port_names)
    return data


_re_comment = re.compile(r"^\s*!")
_re_options = re.compile(r"^\s*#")
_re_empty = re.compile(r"^\s*$")


def _parse_ports_name(file):
    """Parse and interpret the option line in the touchstone file

    Parameters
    ----------
    file :
        

    Returns
    -------

    """
    portnames=[]
    line = file.readline()
    while not line.startswith('! Port'):
        line = file.readline()
    while line.startswith('! Port'):
        portnames.append(line.split(" = ")[1].strip())
        line = file.readline()
    return portnames


def _parse_option_line(file, verbose=False):
    """Parse and interpret the option line in the touchstone file

    Parameters
    ----------
    file :
        
    verbose :
         (Default value = False)

    Returns
    -------

    """
    prefix = {
        '': 1,
        'K': 1e3,
        'M': 1e6,
        'G': 1e9
    }

    # defaults
    frequnit = 1e9
    format = MAG_ANGLE
    z0 = 50

    # format of the options line (order is unimportant)
    # <frequency unit> <parameter> <format> R <n>
    line = file.readline()
    while not line.startswith('#'):
        line = file.readline()

    options = line[1:].upper().split()

    i = 0
    while i < len(options):
        option = options[i]
        if option in ('GHZ', 'MHZ', 'KHZ', 'HZ'):
            frequnit = prefix[option[:-2]]
        elif option in ('DB', 'MA', 'RI'):
            format = option
        elif option in ('S', 'Y', 'Z', 'H', 'G'):
            parameter = option
        elif option == 'R':
            i += 1
            z0 = float(options[i])
        else:
            raise ParseError('unrecognized option: {0}'.format(option))
        i += 1

    if verbose:
        print("  Frequency unit: %g Hz" % frequnit)
        print("  Parameter:      %s" % type)
        print("  Format:         %s" % format)
        print("  Reference R:    %g" % z0)


    return (frequnit, type, format, z0)


def _get_next_line_data(file):
    """Returns the data on the next line of the input file as an array
    of floats, skipping comment, option and empty lines.

    Parameters
    ----------
    file :
        

    Returns
    -------

    """
    line = '!'
    while _re_comment.search(line) or \
            _re_options.search(line) or \
            _re_empty.search(line):
        line = file.readline()
        if not line:  # end of data
            raise EOFError
    data = []
    line = line.split('!')[0]
    for number in line.split():
        data.append(float(number))
    return data


def _parse_next_sample(file, ports, format):
    """Parse the parameters for the next frequency point

    Parameters
    ----------
    file :
        
    ports :
        
    format :
        

    Returns
    -------

    """
    data = _get_next_line_data(file)
    # data lines always contain an even number of values (2 values
    #  per parameter), *unless* a frequency value is included in
    #  front
    assert len(data) % 2 == 1
    freq = data[0]
    data = data[1:]
    count = 0

    port1 = port2 = 1
    list_data = [None for i in range(ports*ports)]


    while True:
        for i in range(int(len(data) / 2)):
            index = 2 * i
            args = {}
            args[keys[format][0]] = data[index]
            args[keys[format][1]] = data[index + 1]
            try:
                if ports == 2:
                    list_data[(port1-1)*ports + (port2-1)] =parameter(**args)
                else:
                    list_data[(port2-1)*ports + (port1-1)] =parameter(**args)
            except IndexError:
                raise Exception("more ports than reported in the file "
                                "extension")

            port1 += 1
            if port1 > ports:
                port2 += 1
                port1 = 1

        count += len(data) / 2
        if port2 > ports:
            break
        data = _get_next_line_data(file)
        if len(data) % 2 != 0:
            raise Exception("less ports than reported in the file extension")

    assert count == ports ** 2
    return (freq, list_data)