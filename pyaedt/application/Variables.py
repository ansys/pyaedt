"""
Variables Module
----------------

This class contains functionalities to create and edit design
and project variables using the 3D tools.

Examples
--------

>>> from pyaedt.hfss import Hfss
>>> hfss = Hfss()

Create a project variable

>>> hfss["$d"] = "5mm"

Create a local variable

>>> hfss["d"] = "5mm"

Create a postprocessing variable

>>> hfss["postd"] = "1W"

"""
from __future__ import absolute_import
import math
import re
import numbers
import os
from ..generic.general_methods import aedt_exception_handler, generate_unique_name


rad2deg = 180.0/math.pi
deg2rad = math.pi/180.0
sec2min = 1/60.0
sec2hour = 1/3600.0
inv2pi = 0.5/math.pi
invpi = 1.0/math.pi
m2in = 0.0254


@aedt_exception_handler
def dB(x, inverse=True):
    """

    Parameters
    ----------
    x :
        
    inverse :
         (Default value = True)

    Returns
    -------

    """
    if inverse:
        return 20*math.log10(x)
    else:
        return math.pow(10, x/20.0)


@aedt_exception_handler
def fah2kel(val, inverse=True):
    """

    Parameters
    ----------
    val :
        
    inverse :
         (Default value = True)

    Returns
    -------

    """
    if inverse:
        return (val - 273.15) * 9 / 5 + 32
    else:
        return (val - 32) * 5 / 9 + 273.15


@aedt_exception_handler
def cel2kel(val, inverse=True):
    """

    Parameters
    ----------
    val :
        
    inverse :
         (Default value = True)

    Returns
    -------

    """
    if inverse:
        return val - 273.15
    else:
        return val + 273.15


@aedt_exception_handler
def unit_system(units):
    """

    Parameters
    ----------
    units :
        

    Returns
    -------
    type
        

    """
    found = False
    for unit_type, unit_list in AEDT_units.items():
        for test_unit in unit_list:
            if test_unit == units:
                found = True
                break
        if found:
            return unit_type
    raise Exception("Unit {0} is not defined".format(units))


#TODO Add additional units
AEDT_units = {
    'AngularSpeed': {'deg_per_hr': sec2hour * deg2rad, 'rad_per_hr': sec2hour, 'deg_per_min': sec2min * deg2rad,
                     'rad_per_min': sec2min, 'deg_per_sec': deg2rad, 'rad_per_sec': 1.0, 'rev_per_sec': inv2pi,
                     'per_sec': inv2pi, 'rpm': sec2min * 2 * math.pi},
    'Angle': {'deg': deg2rad, 'rad': 1.0, 'degmin': deg2rad * 60, 'degsec': deg2rad * 3600},
    'Current': {'fA': 1e-15, 'pA': 1e-12, 'nA': 1e-9, 'uA': 1e-6, 'mA': 1e-3, 'A': 1.0, 'kA': 1e3, 'MegA': 1e6,
                'gA': 1e9, 'dBA': (dB,)},
    'Flux': {'Wb': 1.0, 'mx': 1e-8, 'vh': 3600, 'vs': 1.0},
    'Freq': {'Hz': 1.0, 'kHz': 1e3, 'MHz': 1e6, 'GHz': 1e9, 'THz': 1e12, 'rps': 1.0, 'per_sec': 1.0},
    'Inductance': {'fH': 1e-15, 'pH': 1e-12, 'nH': 1e-9, 'uH': 1e-6, 'mH': 1e-3, 'H': 1.0},
    'Length': {'fm': 1e-15, 'pm': 1e-12, 'nm': 1e-9, 'um': 1e-6, 'mm': 1e-3, 'cm': 1e-2, 'dm': 1e-1, 'meter': 1.0,
               'km': 1e3, 'uin': m2in * 1e-6, 'mil': m2in * 1e-3, 'in': m2in, 'ft': m2in * 12, 'yd': m2in * 144},
    'None': {'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3, '': 1.0, 'k': 1e3, 'meg': 1e6, 'g': 1e9, 't': 1e12},
    'Resistance': {'uOhm': 1e-6, 'mOhm': 1e-3, 'ohm': 1.0, 'kOhm': 1e3, 'megohm': 1e6, 'GOhm': 1e9 },
    'Time': {'fs': 1e-15, 'ps': 1e-12, 'ns': 1e-9, 'us': 1e-6, 'ms': 1e-3, 's': 1, 'min': 60, 'hour': 3600, 'day': 3600*12},
    'Torque': {'fNewtonMeter': 1e-15, 'pNewtonMeter': 1e-12, 'nNewtonMeter': 1e-9, 'uNewtonMeter': 1e-6, 'mNewtonMeter': 1e-3,
               'cNewtonMeter': 1e-2, 'NewtonMeter': 1, 'kNewtonMeter': 1e3, 'megNewtonMeter': 1e6, 'gNewtonMeter': 1e9},
    'Voltage': {'fV': 1e-15, 'pV': 1e-12, 'nV': 1e-9, 'uV': 1e-6, 'mV': 1e-3, 'V': 1.0, 'kV': 1e3, 'MegV': 1e6,
                'gV': 1e9, 'dBV': (dB,)},
    'Temperature': {'kel': 1.0, 'cel': (cel2kel,), 'fah': (fah2kel,)},
    'Power': {'fW': 1e-15, 'pW': 1e-12, 'nW': 1e-9, 'uW': 1e-6, 'mW': 1e-3, 'W': 1.0, 'kW': 1e3, 'megW': 1e6, 'gW': 1e9}
}
SI_units = {
    'AngularSpeed':  'deg_per_sec', 'Angle': 'deg',    'Current': 'A', 'Flux': 'vs',
    'Freq': 'Hz',   'Inductance': 'H',    'Length': 'meter',    'None': '',    'Resistance': 'ohm',
    'Time':  's',   'Torque': 'NewtonMeter',     'Voltage': 'V',    'Temperature': 'kel',    'Power': 'W'}

class CSVDataset:
    """ """

    @property
    def number_of_rows(self):
        """ """
        if self._data:
            for variable, data_list in self._data.items():
                return len(data_list)
        else:
            return 0

    @property
    def number_of_columns(self):
        """ """
        return len(self._header)

    @property
    def header(self):
        """ """
        return self._header

    @property
    def data(self):
        """ """
        return self._data

    @property
    def path(self):
        """ """
        return os.path.dirname(os.path.realpath(self._csv_file))

    def __init__(self, csv_file=None, separator=None, units_dict=None, append_dict=None, valid_solutions=True, invalid_solutions=False):
        ''' Reads in the csv file and extracts header, data and units information as well as being able
            to augment the data with constant values

        :param csv_file:    Input file consisting of delimited data with first line as header file.
                            Data values support AEDT units such as e.g. 1.23Wb
        :param separator:   Data delimiter. Default is comma
        :param units_dict:  Dictionary consisting of {Variable Name: unit} used to rescale data if not in the desired
                            unit system
        :param append_dict: Dictionary {New Variable Name: value} Additional variable with constant value for all
                            Data points. (Used to add multiple sweeps to one result file
        '''
        self._header = []
        self._data = {}
        self._unit_dict = {}
        self._append_dict = {}

        # Set the index counter explicitly to zero
        self._index = 0

        if separator:
            self._separator = separator
        else:
            self._separator = ","

        if units_dict:
            self._unit_dict = units_dict

        if append_dict:
            self._append_dict = append_dict

        self._csv_file = csv_file
        if csv_file:
            with open(csv_file, 'r') as fi:
                file_data = fi.readlines()
                for line in file_data:
                    if self._header:
                        line_data = line.strip().split(self._separator)
                        # Check for invalid data in the line (fields with 'nan')
                        if not 'nan' in line_data:
                            for j, value in enumerate(line_data):
                                var_name = self._header[j]
                                if var_name in self._unit_dict:
                                    var_value = Variable(value).rescale_to(self._unit_dict[var_name]).numeric_value
                                else:
                                    var_value = Variable(value).value
                                self._data[var_name].append(var_value)

                            # Add augmented quantities
                            for entry in self._append_dict:
                                var_value_str = self._append_dict[entry]
                                numeric_value = Variable(var_value_str).numeric_value
                                self._data[entry].append(numeric_value)

                    else:
                        self._header = line.strip().split(",")
                        for additional_quantity_name in self._append_dict:
                            self._header.append(additional_quantity_name)
                        for quantity_name in self._header:
                            self._data[quantity_name] = []

        pass

    @aedt_exception_handler
    def __getitem__(self, item):
        variable_list = item.split(',')
        data_out = CSVDataset()
        for variable in variable_list:
            found_variable = False
            for key_string in self._data:
                if variable in key_string:
                    found_variable = True
                    break
            assert found_variable, "Input string {} is not a key of the data dictionary!".format(variable)
            data_out._data[variable] = self._data[key_string]
            data_out._header.append(variable)
        return data_out

    @aedt_exception_handler
    def __add__(self, other):
        assert self.number_of_columns == other.number_of_columns, "Inconsistent number of columns"
        # Create a new object to return, avoiding changing the original inputs
        new_dataset = CSVDataset()
        # Add empty columns to new_dataset
        for column in self._data:
            new_dataset._data[column] = []

        # Add the data from 'self' to a the new dataset
        for column, row_data in self.data.items():
            for value in row_data:
                new_dataset._data[column].append(value)

        # Add the data from 'other' to a the new dataset
        for column, row_data in other.data.items():
            for value in row_data:
                new_dataset._data[column].append(value)

        return new_dataset

    def __iadd__(self, other):
        ''' Incrementally add one CSVDataset to another. This assumes that the number of columns are the same,
            or that self is an empty CSVDataset. No checking for equivalency of units/variable names is done'''

        # Handle the case of an empty data set and create empty lists for the column data
        if self.number_of_columns == 0:
            self._header = other.header
            for column in other.data:
                self._data[column] = []

        assert self.number_of_columns == other.number_of_columns, "Inconsistent number of columns"

        # Append the data from 'other'
        for column, row_data in other.data.items():
            for value in row_data:
                self._data[column].append(value)


        return self

    # Called when iteration is initialized
    def __iter__(self):

        self._index = 0
        return self

    # Create an iterator to yield the row data as a string as we loop thorugh the object
    def __next__(self):
        if self._index < (self.number_of_rows-1):
            output = []
            for column in self._header:
                string_value = str(self._data[column][self._index])
                output.append(string_value)
            output_string = " ".join(output)
            self._index += 1
        else:
            raise StopIteration

        return output_string

    def next(self):
        """ """
        return self.__next__()

@aedt_exception_handler
def decompose_variable_value(variable_value):
    """

    Parameters
    ----------
    variable_value :
        

    Returns
    -------

    """
    if variable_value == 'nan':
        float_value = 'nan'
        units = ''
    else:
        loc = re.search('[a-zA-Z]+$', variable_value)
        if loc:
            b = loc.span()[0]
            units = variable_value[b:]
            try:
                float_value = float(variable_value[0:b])
            except:
                float_value = variable_value[0:b]
        else:
            try:
                float_value = float(variable_value)
                units = ''
            except:
                float_value = variable_value
                units =''
    return float_value, units


class VariableManager(object):
    """Variable Manager Class"""

    @property
    def variables(self):
        """ """
        return self._variable_dict([self.odesign, self.oproject])

    @property
    def design_variables(self):
        """ """
        return self._variable_dict([self.odesign])

    @property
    def project_variables(self):
        """ """
        return self._variable_dict([self.oproject])

    @property
    def independent_variables(self):
        """ """
        return self._variable_dict([self.odesign, self.oproject], dependent=False)

    @property
    def independent_project_variables(self):
        """ """
        return self._variable_dict([self.oproject], dependent=False)

    @property
    def independent_design_variables(self):
        """ """
        return self._variable_dict([self.odesign], dependent=False)

    @property
    def dependent_variables(self):
        """ """
        return self._variable_dict([self.odesign, self.oproject], independent=False)

    @property
    def variable_names(self):
        """ """
        return [var_name for var_name in self.variables]

    @property
    def project_variable_names(self):
        """ """
        return [var_name for var_name in self.project_variables]

    @property
    def independent_project_variable_names(self):
        """ """
        return [var_name for var_name in self.independent_project_variables]

    @property
    def design_variable_names(self):
        """ """
        return [var_name for var_name in self.design_variables]

    @property
    def independent_design_variable_names(self):
        """ """
        return [var_name for var_name in self.independent_design_variables]

    @property
    def independent_variable_names(self):
        """ """
        return [var_name for var_name in self.independent_variables]

    @property
    def dependent_variable_names(self):
        """ """
        return [var_name for var_name in self.dependent_variables]

    @property
    def oproject(self):
        """ """
        return self._parent._oproject

    @property
    def odesign(self):
        """ """
        return self._parent._odesign

    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    def __init__(self, parent):

        # Global Desktop Environment
        self._parent = parent

    @aedt_exception_handler
    def __getitem__(self, variable_name):
        return self.interpret_variable_value(variable_name)

    @aedt_exception_handler
    def __setitem__(self, variable, value):
        self.set_variable(variable, value)
        return True

    @aedt_exception_handler
    def _variable_dict(self, object_list, dependent=True, independent=True):
        """

        Parameters
        ----------
        object_list :
            
        dependent :
             (Default value = True)
        independent :
             (Default value = True)

        Returns
        -------

        """
        var_dict = {}
        for obj in object_list:
            for variable_name in obj.GetVariables():
                variable_expression = self.get_expression(variable_name)
                try:
                    value = Variable(variable_expression)
                    if independent and type(value.value) is float or type(value.value) is int:
                        var_dict[variable_name] = value
                    elif dependent and type(value.value) is str:
                            float_value = self.get_evaluated_value(variable_name)
                            var_dict[variable_name] = Expression(variable_expression, float_value)
                except:
                    if dependent:
                        float_value = self.get_evaluated_value(variable_name)
                        var_dict[variable_name] = Expression(variable_expression, float_value)

        return var_dict

    @aedt_exception_handler
    def get_evaluated_value(self, variable_name, variation=None):
        """

        Parameters
        ----------
        variable_name :
            
        variation :
             (Default value = None)

        Returns
        -------
        type
            

        """
        if not variation:
            variation = self.odesign.GetNominalVariation()
        return self.odesign.GetVariationVariableValue(variation, variable_name)

    @aedt_exception_handler
    def get_expression(self, variable_name):
        """

        Parameters
        ----------
        variable_name :
            

        Returns
        -------
        type
            

        """
        return self.aedt_object(variable_name).GetVariableValue(variable_name)

    @aedt_exception_handler
    def aedt_object(self, variable):
        """

        Parameters
        ----------
        variable :
            

        Returns
        -------

        """
        if variable[0] == "$":
            return self.oproject
        else:
            return self.odesign

    @aedt_exception_handler
    def interpret_variable_value(self, variable_name):
        """

        Parameters
        ----------
        variable_name :
            

        Returns
        -------

        """
        tol = 0.01
        float_value = self.get_evaluated_value(variable_name)
        expression_value = self.get_expression(variable_name)
        try:
            value = Variable(expression_value)
            check = value.value
            assert (check - float_value) < float_value*tol, "Error in interpreting variable {0}:={1}".format(variable_name, expression_value)
        except:
            value = Expression(expression_value, float_value)
        return value

    @aedt_exception_handler
    def set_variable(self, variable_name, expression=None, prop_type="VariableProp",
                     readonly=False, hidden=False, description="", overwrite=True):
        """Add a design variable to an existing design and overwrite an existing variable if present

        Parameters
        ----------
        variable_name :
            name of the variable
        expression :
            param prop_type: (Default value = None)
        readonly :
            param hidden: (Default value = False)
        description :
            param overwrite: (Default value = "")
        prop_type :
             (Default value = "VariableProp")
        hidden :
             (Default value = False)
        overwrite :
             (Default value = True)

        Returns
        -------

        """

        desktop_object = self.aedt_object(variable_name)
        test = desktop_object.GetName()
        proj_name = self.oproject.GetName()
        var_type = "Project" if test == proj_name else "Local"

        if expression and isinstance(expression, str):
            variable = expression
        else:
            # Handle input type variable
            if isinstance(expression, Variable):
                variable = expression.string_value
            # Handle input type int/float, etc (including numeric 0)
            elif isinstance(expression, numbers.Number):
                variable = str(expression)
            # Handle None, "" as Separator
            elif not expression:
                prop_type = "SeparatorProp"
                variable = ""
                try:
                    if self.delete_separator(variable_name):
                        desktop_object.Undo()
                        self.messenger.clear_messages()
                        return
                except:
                    pass
            else:
                raise Exception("Unhandled input type to design/project variable.")
                #TODO
                #variable = variable.replace("\'", "\"")

        if "post" in variable_name.lower()[0:5]:
            prop_type = "PostProcessingVariableProp"

        # Get all design and project variables in lower case for a case-sensitive comparison
        var_list = desktop_object.GetVariables()
        lower_case_vars = [var_name.lower() for var_name in var_list]

        if variable_name.lower() not in lower_case_vars:

            desktop_object.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:{0}VariableTab".format(var_type),
                        [
                            "NAME:PropServers",
                            "{0}Variables".format(var_type)
                        ],
                        [
                            "NAME:NewProps",
                            [
                                "NAME:" + variable_name,
                                "PropType:=", prop_type,
                                "UserDef:=", True,
                                "Value:=", variable,
                                "Description:=", description,
                                "ReadOnly:=", readonly,
                                "Hidden:=", hidden
                            ]
                        ]
                    ]
                ])
        elif overwrite:
            desktop_object.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:{}VariableTab".format(var_type),
                        [
                            "NAME:PropServers",
                            "{}Variables".format(var_type)
                        ],
                        [
                            "NAME:ChangedProps",
                            [
                                "NAME:" + variable_name,
                                "Value:="		, variable,
                                "Description:="		, description,
                                "ReadOnly:="		, readonly,
                                "Hidden:="		, hidden
                            ]
                        ]
                    ]
                ])

    @aedt_exception_handler
    def delete_separator(self, separator_name):
        """Deletes a separator from either the active project or design

        Parameters
        ----------
        separator_name :
            Separator text

        Returns
        -------
        type
            True if the separator exists and can be deleted, False otherwise

        """
        object_list = [ (self.odesign, "Local"),
                        (self.oproject, "Project")]

        for object_tuple in object_list:
            desktop_object = object_tuple[0]
            var_type = object_tuple[1]
            try:
                desktop_object.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:{0}VariableTab".format(var_type),
                            [
                                "NAME:PropServers",
                                "{0}Variables".format(var_type)
                            ],
                            [
                                "NAME:DeletedProps",
                                separator_name
                            ]
                        ]
                    ])
                return True
            except:
                pass
        return False

    @aedt_exception_handler
    def delete_variable(self, sVarName):
        """

        Parameters
        ----------
        sVarName :
            

        Returns
        -------

        """
        desktop_object = self.aedt_object(sVarName)
        var_type = "Project" if desktop_object == self.oproject else "Local"

        var_list = desktop_object.GetVariables()
        lower_case_vars = [var_name.lower() for var_name in var_list]

        if sVarName.lower() in lower_case_vars:
            try:
                desktop_object.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:{0}VariableTab".format(var_type),
                            [
                                "NAME:PropServers",
                                "{0}Variables".format(var_type)
                            ],
                            [
                                "NAME:DeletedProps",
                                sVarName
                            ]
                        ]
                    ])
            except:
                pass


class Variable(object):
    """Variable Class. It store Varabiable and allows operations on it"""

    @aedt_exception_handler
    def rescale_to(self, units):
        """Change the unit system of the expression to a new unit within the same unit system

        Parameters
        ----------
        units :
            

        Returns
        -------

        """
        new_unit_system = unit_system(units)
        assert new_unit_system == self.unit_system, \
            "New unit system {0} inconsistent with current unit system {1}."
        self._units = units
        return self

    @property
    def unit_system(self):
        """ """
        return unit_system(self._units)

    @property
    def units(self):
        """ """
        return self._units

    @property
    def value(self):
        """ """
        return self._value

    @property
    def numeric_value(self):
        """ """
        return self._normalize(self._value, inverse=True)

    @property
    def string_value(self):
        """ """
        return str(str(self.numeric_value)  + self._units)

    @aedt_exception_handler
    def format(self, format):
        """

        Parameters
        ----------
        format :
            

        Returns
        -------

        """
        return ('{0:' + format + '}{1}').format(self.numeric_value, self._units)

    def __init__(self, value):
        value, self._units = decompose_variable_value(value)
        self._value = self._normalize(value)

    @aedt_exception_handler
    def __mul__(self, other):
        assert isinstance(other, numbers.Number) or isinstance(other, Variable), "Multiplier must be a scalar quantity or a variable!"
        op_data = Variable(self.string_value)
        if isinstance(other, Variable):
            op_data._units = ""
            op_data._value = self._value * other._value
        else:
            op_data._value = self. value * other
        return op_data

    __rmul__ = __mul__

    # Python 3.x version
    @aedt_exception_handler
    def __truediv__(self, other):
        assert isinstance(other, numbers.Number) or isinstance(other, Variable), "Divisor must be a scalar quantity or a variable!"
        op_data = Variable(self.string_value)
        if isinstance(other, Variable):
            op_data._units = ""
            op_data._value = self._value / other._value
        else:
            op_data._value = self._value / other
        return op_data

    # Python 2.7 version
    @aedt_exception_handler
    def __div__(self, other):
        return self.__truediv__(other)

    @aedt_exception_handler
    def _normalize(self, value, inverse=False):
        """Scale the expression value to the SI units of the given system
            With inverse=True, scale in reverse direction

        Parameters
        ----------
        value :
            
        inverse :
             (Default value = False)

        Returns
        -------

        """
        if value == 'nan' or type(value) is str:
            return value
        else:
            scale = AEDT_units[self.unit_system][self._units]
            if isinstance(scale, tuple):
                return scale[0](value, inverse)
            else:
                if inverse:
                    return value / scale
                else:
                    return value * scale


class Expression(Variable, object):
    """Class to manipulate variable expressions"""

    def __init__(self, expression, float_value):
        self._expression = expression
        self._value = float_value
        # TODO. Try to identify the unit system from the expression !
        try:
            value, units = decompose_variable_value(expression)
            self._units = units
        except:
            self._units = ''

    @property
    def expression(self):
        """ """
        return str(self._expression)


class DataSet(object):
    """Class for Dataset Management"""
    def __init__(self, parent, name, x, y, z=None, v=None, xunit='', yunit='', zunit='', vunit=''):
        self._parent = parent
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.v = v
        self.xunit = xunit
        self.yunit = yunit
        self.zunit = zunit
        self.vunit = vunit

    @aedt_exception_handler
    def _args(self):
        """ """
        arg = []
        arg.append("Name:" + self.name)
        arg2 = ["Name:Coordinates"]
        if self.z is None:
            arg2.append(["NAME:DimUnits", self.xunit, self.yunit])
        elif self.v is not None and self.name[0] == "$":
            arg2.append(["NAME:DimUnits", self.xunit, self.yunit, self.zunit, self.vunit])
        else:
            return False
        if self.z and self.name[0] == "$":
            x, y, z, v = (list(t) for t in zip(*sorted(zip(self.x, self.y, self.z, self.v))))
        else:
            x, y = (list(t) for t in zip(*sorted(zip(self.x, self.y))))
        for i in range(len(x)):
            arg3 = []
            arg3.append("NAME:Coordinate")
            arg4 = ["NAME:CoordPoint"]
            arg4.append(float(x[i]))
            arg4.append(float(y[i]))
            if self.z and self.name[0] == "$":
                arg4.append(float(z[i]))
                arg4.append(float(v[i]))
            arg3.append(arg4)
            arg2.append(arg3)
        arg.append(arg2)
        return arg

    @aedt_exception_handler
    def create(self):
        """Create a new Dataset
        
        
        :return:Bool

        Parameters
        ----------

        Returns
        -------

        """
        if self.name[0] == "$":
            self._parent._oproject.AddDataset(self._args())
        else:
            self._parent.odesign.AddDataset(self._args())
        return True

    @aedt_exception_handler
    def add_point(self, x, y, z=None, v=None):
        """Add a new point to the existing dataset

        Parameters
        ----------
        x :
            float
        y :
            float
        z :
            float or None (Default value = None)
        v :
            float or None (Default value = None)

        Returns
        -------
        type
            Bool

        """
        self.x.append(x)
        self.y.append(y)
        if self.z and self.v:
            self.z.append(z)
            self.v.append(v)

        return self.update()

    @aedt_exception_handler
    def remove_point_from_x(self, x):
        """Remove Point from given x value

        Parameters
        ----------
        x :
            float

        Returns
        -------
        type
            Bool

        """
        if x not in self.x:
            self._parent._messenger.add_error_message("Value {} not found.".format(x))
            return False
        id_to_remove = self.x.index(x)
        return self.remove_point_from_index(id_to_remove)


    @aedt_exception_handler
    def remove_point_from_index(self, id_to_remove):
        """Remove Point from a specific index.

        Parameters
        ----------
        id_to_remove :
            index to remove (integer)

        Returns
        -------
        type
            Bool

        """
        if id_to_remove < len(self.x) > 2:
            self.x.pop(id_to_remove)
            self.y.pop(id_to_remove)
            if self.z and self.v:
                self.z.pop(id_to_remove)
                self.v.pop(id_to_remove)
            return self.update()
        self._parent._messenger.add_error_message("cannot Remove {} index.".format(id_to_remove))
        return False

    @aedt_exception_handler
    def update(self):
        """Update Dataset"""
        args = self._args()
        if not args:
            return False
        if self.name[0] == "$":
            self._parent._oproject.EditDataset(self.name, self._args())
        else:
            self._parent.odesign.EditDataset(self.name, self._args())
        return True

    @aedt_exception_handler
    def delete(self):
        """Delete the dataset."""
        if self.name[0] == "$":
            self._parent._oproject.DeleteDataset(self.name)
            del self._parent.project_datasets[self.name]
        else:
            self._parent.odesign.DeleteDataset(self.name)
            del self._parent.project_datasets[self.name]
        return True

    @aedt_exception_handler
    def export(self, dataset_path=None):
        """Export dataset

        Parameters
        ----------
        dataset_path : str, optional
            Path where to export.  If ``None`` the dataset will be
            exported to project_path (Default value = None)

        """
        if not dataset_path:
            dataset_path = os.path.join(self._parent.project_path, self.name +".tab")
        if self.name[0] == "$":
            self._parent._oproject.ExportDataset(self.name, dataset_path)
        else:
            self._parent.odesign.ExportDataset(self.name, dataset_path)
        return True

