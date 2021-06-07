"""
Variables Library Class
----------------------------------------------------------------

Disclaimer
============================================================

**Copyright (c) 1986-2021, ANSYS Inc. unauthorised use, distribution or duplication is prohibited**

**This tool release is unofficial and not covered by standard Ansys Support license.**


Description
==================================================

This class contains all the functionalities to create and edit design and project variable in a very easy way in all the 3D Tools

:Example:

hfss = HFSS()
hfss["$d"] = "5mm"   create a project variable


hfss["d"] = "5mm"   create a local variable
pip install sphinx-adc-theme
hfss["postd"] = "1W"   create a postprocessing variable


================

"""
from __future__ import absolute_import
import math
import re
import numbers
import os
from .. import aedt_exception_handler

@aedt_exception_handler
def dB(x, inverse=True):
    if inverse:
        return 20*math.log10(x)
    else:
        return math.pow(10, x/20.0)


@aedt_exception_handler
def fah2kel(val, inverse=True):
    if inverse:
        return (val - 273.15) * 9 / 5 + 32
    else:
        return (val - 32) * 5 / 9 + 273.15


@aedt_exception_handler
def cel2kel(val, inverse=True):
    if inverse:
        return val - 273.15
    else:
        return val + 273.15


@aedt_exception_handler
def unit_system(units):
    """ Return the name of the unit system associated with the given unit string. Return False if the units are
        not known as defined in AEDT_units """
    found = False
    for unit_type, unit_list in AEDT_units.items():
        for test_unit in unit_list:
            if test_unit == units:
                found = True
                break
        if found:
            return unit_type
    return False

#TODO Add additional units
rad2deg = 180.0 / math.pi
deg2rad = math.pi / 180
hour2sec = 3600.0
min2sec = 60.0
sec2min = 1 / 60.0
sec2hour = 1 / 3600.0
inv2pi = 0.5/math.pi
v2pi = 2.0 * math.pi
m2in = 0.0254
m2miles = 1609.344051499

# Value in new units equals value in old units * scaling vactor of new units
# e.g. value_in_deg Variable("1rad") = 1 * rad2deg
AEDT_units = {
    'AngularSpeed': {'deg_per_hr': hour2sec * deg2rad, 'rad_per_hr': hour2sec, 'deg_per_min': min2sec * deg2rad,
                     'rad_per_min': min2sec, 'deg_per_sec': deg2rad, 'rad_per_sec': 1.0, 'rev_per_sec': v2pi,
                     'per_sec': v2pi, 'rpm': sec2min * v2pi},
    'Angle': {'deg': deg2rad, 'rad': 1.0, 'degmin': deg2rad * sec2min, 'degsec': deg2rad * sec2hour},
    'Current': {'fA': 1e-15, 'pA': 1e-12, 'nA': 1e-9, 'uA': 1e-6, 'mA': 1e-3, 'A': 1.0, 'kA': 1e3, 'MegA': 1e6,
                'gA': 1e9, 'dBA': (dB,)},
    'Flux': {'Wb': 1.0, 'mx': 1e-8, 'vh': 3600, 'vs': 1.0},
    'Freq': {'Hz': 1.0, 'kHz': 1e3, 'MHz': 1e6, 'GHz': 1e9, 'THz': 1e12, 'rps': 1.0, 'per_sec': 1.0},
    'Inductance': {'fH': 1e-15, 'pH': 1e-12, 'nH': 1e-9, 'uH': 1e-6, 'mH': 1e-3, 'H': 1.0},
    'Length': {'fm': 1e-15, 'pm': 1e-12, 'nm': 1e-9, 'um': 1e-6, 'mm': 1e-3, 'cm': 1e-2, 'dm': 1e-1, 'meter': 1.0,
               'km': 1e3, 'uin': m2in * 1e-6, 'mil': m2in * 1e-3, 'in': m2in, 'ft': m2in * 12, 'yd': m2in * 144},
    'Mass': {'ug': 1e-9, 'mg': 1e-6, 'g': 1e-3, 'kg': 1.0, 'ton': 1000, 'oz': 0.0283495, 'lb': 0.453592 },
    'None': {'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3, '': 1.0, 'k': 1e3, 'meg': 1e6, 'g': 1e9, 't': 1e12},
    'Resistance': {'uOhm': 1e-6, 'mOhm': 1e-3, 'ohm': 1.0, 'kOhm': 1e3, 'megohm': 1e6, 'GOhm': 1e9 },
    'Speed': {'mm_per_sec': 1e-3, 'cm_per_sec': 1e-2, 'm_per_sec': 1.0, 'km_per_sec': 1e3, 'inches_per_sec': m2in,
              'feet_per_sec': m2in * 12, 'feet_per_min': m2in * 12 * sec2min, 'km_per_min': 60e3, 'm_per_h': 3600,
              'miles_per_hour': m2miles * sec2hour, 'miles_per_minute': m2miles * sec2min, 'miles_per_sec': m2miles},
    'Time': {'fs': 1e-15, 'ps': 1e-12, 'ns': 1e-9, 'us': 1e-6, 'ms': 1e-3, 's': 1, 'min': 60, 'hour': 3600, 'day': 3600*12},
    'Torque': {'fNewtonMeter': 1e-15, 'pNewtonMeter': 1e-12, 'nNewtonMeter': 1e-9, 'uNewtonMeter': 1e-6, 'mNewtonMeter': 1e-3,
               'cNewtonMeter': 1e-2, 'NewtonMeter': 1, 'kNewtonMeter': 1e3, 'megNewtonMeter': 1e6, 'gNewtonMeter': 1e9},
    'Voltage': {'fV': 1e-15, 'pV': 1e-12, 'nV': 1e-9, 'uV': 1e-6, 'mV': 1e-3, 'V': 1.0, 'kV': 1e3, 'MegV': 1e6,
                'gV': 1e9, 'dBV': (dB,)},
    'Temperature': {'kel': 1.0, 'cel': (cel2kel,), 'fah': (fah2kel,)},
    'Power': {'fW': 1e-15, 'pW': 1e-12, 'nW': 1e-9, 'uW': 1e-6, 'mW': 1e-3, 'W': 1.0, 'kW': 1e3, 'megW': 1e6, 'gW': 1e9}
}
SI_units = {
    'AngularSpeed':  'rad_per_sec',
    'Angle': 'deg',
    'Current': 'A',
    'Flux': 'vs',
    'Freq': 'Hz',
    'Inductance': 'H',
    'Length': 'meter',
    'Mass': 'kg',
    'None': '',
    'Resistance': 'ohm',
    'Time':  's',
    'Torque': 'NewtonMeter',
    'Voltage': 'V',
    'Temperature': 'kel',
    'Power': 'W'}

unit_system_operations = {
    # Multiplication of physical domains
    'Voltage_multiply_Current': 'Power',
    'Torque_multiply_AngularSpeed': 'Power',
    'AngularSpeed_multiply_Time': 'Angle',
    'Current_multiply_Resistance': 'Voltage',
    'AngularSpeed_multiply_Inductance': 'Resistance',
    'Speed_multiply_Time': 'Length',

    # Division of Physical Domains
    'Power_divide_Voltage': 'Current',
    'Power_divide_Current': 'Voltage',
    'Power_divide_AngularSpeed': 'Torque',
    'Power_divide_Torque': 'AngularSpeed',
    'Angle_divide_AngularSpeed': 'Time',
    'Angle_divide_Time': 'AngularSpeed',
    'Voltage_divide_Current': 'Resistance',
    'Voltage_divide_Resistance': 'Current',
    'Resistance_divide_AngularSpeed': 'Inductance',
    'Resistance_divide_Inductance': 'AngularSpeed',
    'None_divide_Freq': 'Time',
    'None_divide_Time': 'Freq',
    'Length_divide_Time': 'Speed',
    'Length_divide_Speed': 'Time'
}

def _resolve_unit_system(unit_system_1, unit_system_2, operation):
    """
    Attempts to return the unit string of an arithmetic operation on Variable objects. If no resulting unit system
    is defined for a specific operation (in unit_system_operations), an empty string is returned

    Parameters
    ----------
    unit_system_1 : str
    Name of a unit system (key of AEDT_units)

    unit_system_2 : str
    Name of another unit system (key of AEDT_units)

    operation : str
    Name of an operator within the set of ["multiply" ,"divide"]

    Returns
    -------
    str

    """
    try:
        key = "{}_{}_{}".format(unit_system_1, operation, unit_system_2)
        result_unit_system = unit_system_operations[key]
        return SI_units[result_unit_system]
    except KeyError:
        return ""

class CSVDataset:

    @property
    def number_of_rows(self):
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

    # Create an iterator to yield the row data as a string as we loop through the object
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
    # set default return values - then check for valid units
    float_value = variable_value
    units =''

    if isinstance(variable_value, numbers.Number):
        float_value = variable_value
    elif isinstance(variable_value, str) and variable_value != 'nan':
        try:
            # Handle a numerical value in string form
            float_value = float(variable_value)
        except ValueError:
            # search for a valid units string at the end of the variable_value
            loc = re.search('[a-z_A-Z]+$', variable_value)
            if loc:
                loc_units = loc.span()[0]
                extract_units = variable_value[loc_units:]
                if unit_system(extract_units):
                    try:
                        float_value = float(variable_value[0:loc_units])
                        units = extract_units
                    except ValueError:
                        float_value = variable_value

    return float_value, units


class VariableManager(object):
    """
    Variable Manager Class

    This object manages the design properties (local variables in a design) and project variables (Variables defined
    at the project level (starting with $). This class provides access to all or a subset of the variables. Manipulation
    of the numerical or string definition of the variable values is provided in the 'Variable' class.

    Attributes
    ------
    variables : dict of Variable
        Dictionary of all design properties and project variables in the active design

    design_variables : dict of Variable
        Dictionary of all design properties (local variables) in the active design

    project_variables : dict of Variable
        Dictionary of all project variables (starting with '$') available to the active design (key by variable name)

    dependent_variables : dict of Variable
       Dictionary of all dependent variables available to the active design (key by variable name)

    independent_variables : dict of Variable
       Dictionary of all independent variables (constant numeric values) available to the active design (key by variable name)

    independent_design_variables : dict of Variable

    independent_project_variables : dict of Variable

    variable_names : list of str
    project_variable_names : list of str
    design_variable_names : list of str
    dependent_variable_names : list of str
        List of all dependent variable names within the project
            independent_variable_names : list of str
        List of all independent variable names within the project (can be sweep variables for optimetrics)
    independent_project_variable_names : list of str
        List of all independent variable names within the project (can be sweep variables for optimetrics)
    independent_design_variable_names : list of str
        List of all independent variable names within the project (can be sweep variables for optimetrics)


    Examples
    ------

    >>> from pyaedt.Maxwell import Maxwell3D
    >>> from pyaedt.Desktop import Desktop
    >>> d = Desktop()
    >>> aedtapp = Maxwell3D()
    >>> # Define some test variables
    >>> aedtapp["Var1"] = 3
    >>> aedtapp["Var2"] = "12deg"
    >>> aedtapp["Var3"] = "Var1 * Var2"
    >>> aedtapp["$PrjVar1"] = "pi"

    >>> # Get the variable manager for the active design
    >>> v = aedtapp.variable_manager
    >>> # get a dictionary of all project & design variables
    >>> v.variables

    {'Var1': <pyaedt.application.Variables.Variable at 0x2661f34c448>,
     'Var2': <pyaedt.application.Variables.Variable at 0x2661f34c308>,
     'Var3': <pyaedt.application.Variables.Expression at 0x2661f34cb48>,
     '$PrjVar1': <pyaedt.application.Variables.Expression at 0x2661f34cc48>}

    >>> # get a dictionary of just the design variables
    >>> v.design_variables

    {'Var1': <pyaedt.application.Variables.Variable at 0x2661f339508>,
     'Var2': <pyaedt.application.Variables.Variable at 0x2661f3415c8>,
     'Var3': <pyaedt.application.Variables.Expression at 0x2661f341808>}

    >>> # get a dictionary of just the independent design variables
    >>> v.independent_design_variables
    {'Var1': <pyaedt.application.Variables.Variable at 0x2661f335d08>,
     'Var2': <pyaedt.application.Variables.Variable at 0x2661f3557c8>}

    See Also
    ------
    Variable class


    """
    @property
    def variables(self):
        """
        Returns a dictionary of Variable objects for each project variable and each
        design property in the active design

        Returns
        -------
            dict of Variable
        """
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
        return self.variables[variable_name]

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
                    if independent and isinstance(value.value, numbers.Number) :
                        var_dict[variable_name] = value
                    elif dependent and type(value.value) is str:
                        float_value = self._parent.get_evaluated_value(variable_name)
                        var_dict[variable_name] = Expression(variable_expression, float_value)
                except:
                    if dependent:
                        float_value = self._parent.get_evaluated_value(variable_name)
                        var_dict[variable_name] = Expression(variable_expression, float_value)

        return var_dict

    @aedt_exception_handler
    def get_expression(self, variable_name):
        """ Return the variable value of a project or design variable as a string"""
        return self.aedt_object(variable_name).GetVariableValue(variable_name)

    @aedt_exception_handler
    def aedt_object(self, variable):
        if variable[0] == "$":
            return self.oproject
        else:
            return self.odesign

    @aedt_exception_handler
    def set_variable(self, variable_name, expression=None, readonly=False, hidden=False,
                     description=None, overwrite=True):
        """Set the value of a project variable or design property

        If the specified variable name does not exist, create a new property and set the value.

        Parameters
        ----------
        variable_name : str
        Name of a design property or project variable ($var) to be set.

        expression : str
        Valid string expression within the AEDT design/project structure, e.g. "3*cos(34deg)"

        readonly : bool, default=False
        Set the "read-only" flag for the property

        hidden : bool, default=False
        Set the "hidden" flag for the property

        description : str, default=None
        Description string to be displayed in the properties window

        overwrite : bool, default=True
        Overwrite the value of an existing property, if False - ignore this command

        Returns
        -------
        bool

        Examples
        --------
        Set the value of the design property p1 to "10mm" - create the property if it does not exist already
        >>> aedtapp.variable_manager.set_variable("p1", expression="10mm")

        Set the value of the design property p1 to "20mm" only if the property does not exist already
        >>> aedtapp.variable_manager.set_variable("p1", expression="20mm", overwrite=False)

        Set the value of the design property p2 to "10mm"  - create the property if it does not exist already and
        add additional flags "read-only" and "hidden" plus a description text
        >>> aedtapp.variable_manager.set_variable(variable_name="p2", expression="10mm", readonly=True, hidden=True,
        ...                                       description="This is a description of this variable")

        Set the value of the project variable $p1 to "30mm" - create the variable if it does not exist
        >>> aedtapp.variable_manager.set_variable["$p1"] == "30mm"

        """
        if not description:
            description = ""

        desktop_object = self.aedt_object(variable_name)
        test = desktop_object.GetName()
        proj_name = self.oproject.GetName()
        var_type = "Project" if test == proj_name else "Local"

        prop_type="VariableProp"

        if isinstance(expression, str):
            # Handle string type variable (including arbitrary expression)# Handle input type variable
            variable = expression
        elif isinstance(expression, Variable):
            # Handle input type variable
            variable = expression.string_value
        elif isinstance(expression, numbers.Number):
            # Handle input type int/float, etc (including numeric 0)
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

        return True

    @aedt_exception_handler
    def delete_separator(self, separator_name):
        """
            Deletes a separator from either the active project or design

        :param separator_name: Separator text
        :return: True if the separator exists and can be deleted, False otherwise
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
    """
    Variable Class. It stores Variables and allows operations on it

    This object handles the contents of design properties and project variables.

    Parameters
    ----------
    value
    units

    Attributes
    ------
    string_value : str
        Value string as stored in the AEDT properties window, e.g. "5mm"
    unit_system : str
        String descriptor of the unit system, e.g. 'Length'
    units : str
        The defined variable units
    numerical_value : float
        numerical value of the variable in the defined variable units
    value : float
        The numerical value of the variable in SI-Units

    Examples
    --------
    >>> from pyaedt.application.Variables import Variable

    Define a variable using a string-value consistent with the AEDT properties
    >>> v = Variable("45mm")

    A unitless variable with value 3.0
    >>> v = Variable(3.0)

    A variable defined by a numeric result and a unit string
    >>> v = Variable(3.0 * 4.5, units="mm")
    >>> assert v.numeric_value = 13.5
    >>> assert v.units = "mm"

    """

    def __init__(self, value, units=None):

        if units:
            if unit_system(units):
                specified_units = units

        self._units = None
        self._expression = value
        self._value, self._units = decompose_variable_value(value)

        # If units have been specified, check for a conflict and otherwise use the specified unit system
        if units:
            assert not self._units, \
                "Inconsistent unit specification {} made vs identified units {}".format(specified_units, self._units)
            self._units = specified_units

        if isinstance(self._value, numbers.Number):
            scale = AEDT_units[self.unit_system][self._units]
            if isinstance(scale, tuple):
                self._value = scale[0](self._value, inverse=False)
            else:
                self._value =  self._value * scale

    @property
    def unit_system(self):
        """ Return the unit system of the expression as a string """
        return unit_system(self._units)

    @property
    def units(self):
        """ Return the units of the expression as a string """
        return self._units

    @property
    def value(self):
        """ Return the value of the expression as a float value in SI units"""
        return self._value

    @property
    def numeric_value(self):
        """ Return the numeric part of the expression as a float value """
        if isinstance(self._value, numbers.Number):
            scale = AEDT_units[self.unit_system][self._units]
        if isinstance(scale, tuple):
            return scale[0](self._value, True)
        else:
            return self._value / scale

    @property
    def string_value(self):
        """
        Concatenate the numeric value with the unit and return as string. There can be differences in the
        numeric display, e.g. 10mm in the modeler could be 10.0mm returned from string_value
        """
        return ('{}{}').format(self.numeric_value, self._units)

    @aedt_exception_handler
    def rescale_to(self, units):
        """ Change the unit system of the expression to a new unit within the same unit system

        Examples
        --------
        >>> from pyaedt.application.Variables import Variable

        >>> v = Variable("10W")
        >>> assert v.numeric_value == 10
        >>> assert v.units == "W"
        >>> v.rescale_to("kW")
        >>> assert v.numeric_value == 0.01
        >>> assert v.units == "kW"

        """
        new_unit_system = unit_system(units)
        assert new_unit_system == self.unit_system, \
            "New unit system {0} inconsistent with current unit system {1}."
        self._units = units
        return self


    @aedt_exception_handler
    def format(self, format):
        """Return the string value with specified numerical formatting

        Parameters
        ----------
        format : str
            Format string for the numeric value of the string e.g. '06.2f' (see https://pyformat.info/)

        Returns
        -------
        str

        Examples
        --------
        >>> from pyaedt.application.Variables import Variable

        >>> v = Variable("10W")
        >>> assert v.format("f") == '10.000000W'
        >>> assert v.format("06.2f") == '010.00W'
        >>> assert v.format("6.2f") == ' 10.00W'

        """
        return ('{0:' + format + '}{1}').format(self.numeric_value, self._units)

    @aedt_exception_handler
    def __mul__(self, other):
        """Multiply the Variable with a number or another Variable and return a new object

        Parameters
        ---------
        other : numbers.Number or Variable
            object to be multiplied

        Returns
        -------
        Variable

        Examples
        --------
        >>> from pyaedt.application.Variables import Variable

        Multiply 'Length' by unitless ('None') to obtain 'Length'. A numerical value is also considered to be unitless
        >>> v1 = Variable("10mm")
        >>> v2 = Variable(3)
        >>> result_1 = v1 * v2
        >>> result_2 = v1 * 3
        >>> assert result_1.numeric_value == 30.0
        >>> assert result_1.unit_system == "Length"
        >>> assert result_2.numeric_value == result_1.numeric_value
        >>> assert result_2.unit_system == result_1.unit_system

        Multiply 'Voltage' times 'Current' to obtain 'Power'
        >>> v3 = Variable("3mA")
        >>> v4 = Variable("40V")
        >>> result_3 = v3 * v4
        >>> assert result_3.numeric_value == 0.12
        >>> assert result_3.units == "W"
        >>> assert result_3.unit_system == "Power"

        """
        assert isinstance(other, numbers.Number) or isinstance(other, Variable), "Multiplier must be a scalar quantity or a variable!"
        if isinstance(other, numbers.Number):
            result_value = self.numeric_value * other
            result_units = self.units
        else:
            if self.unit_system == "None":
                return self.numeric_value * other
            elif other.unit_system == "None":
                return other.numeric_value * self
            else:
                result_value = self.value * other.value
                result_units = _resolve_unit_system(self.unit_system, other.unit_system, "multiply")
                if not result_units:
                    result_units = _resolve_unit_system(other.unit_system, self.unit_system, "multiply")

        return Variable("{}{}".format(result_value, result_units))

    __rmul__ = __mul__

    @aedt_exception_handler
    def __add__(self, other):
        """Add the Variable with another Variable and return a new object

        Parameters
        ---------
        other : Variable
            object to be multiplied

        Returns
        -------
        Variable

        Examples
        --------
        >>> from pyaedt.application.Variables import Variable

        >>> v1 = Variable("3mA")
        >>> v2 = Variable("10A")
        >>> result = v1 + v2
        >>> assert result.numeric_value == 10.003
        >>> assert result.units == "A"
        >>> assert result.unit_system == "Current"

        """
        assert isinstance(other, Variable), "Can only add Variable with Variable"
        assert self.unit_system == other.unit_system, "Only Variable objects with the same unit system can be added"
        result_value = self.value + other.value
        result_units = SI_units[self.unit_system]
        # If the units of the two operands are different, return SI-Units
        result_variable = Variable("{}{}".format(result_value, result_units))

        # If the units of both operands are the same, return those units
        if self.units == other.units:
            result_variable.rescale_to(self.units)

        return result_variable

    @aedt_exception_handler
    def __sub__(self, other):
        """Subtract another Variable from the Variable and return a new object

        Parameters
        ---------
        other : Variable
            object to be subtracted

        Returns
        -------
        Variable

        Examples
        --------
        >>> from pyaedt.application.Variables import Variable
        >>> v3 = Variable("3mA")
        >>> v4 = Variable("10A")
        >>> result_2 = v3 - v4
        >>> assert result_2.numeric_value == -9.997
        >>> assert result_2.units == "A"
        >>> assert result_2.unit_system == "Current"

        """
        assert isinstance(other, Variable), "Can only subtract Variable from Variable"
        assert self.unit_system == other.unit_system, "Only Variable objects with the same unit system can be added"
        result_value = self.value - other.value
        result_units = SI_units[self.unit_system]
        # If the units of the two operands are different, return SI-Units
        result_variable = Variable("{}{}".format(result_value, result_units))

        # If the units of both operands are the same, return those units
        if self.units == other.units:
            result_variable.rescale_to(self.units)

        return result_variable

    # Python 3.x version
    @aedt_exception_handler
    def __truediv__(self, other):
        """Divide the Variable with a number or another Variable and return a new object

        Parameters
        ---------
        other : numbers.Number or Variable
            divisor object

        Returns
        -------
        Variable

        Examples
        --------
        Divide a variable with units 'W' with a variable with units 'V'. Automatically resolve the new units to 'A'
        >>> from pyaedt.application.Variables import Variable
        >>> v1 = Variable("10W")
        >>> v2 = Variable("40V")
        >>> result = v1 / v2
        >>> assert result_1.numeric_value == 0.25
        >>> assert result_1.units == "A"
        >>> assert result_1.unit_system == "Current"

        """
        assert isinstance(other, numbers.Number) or isinstance(other, Variable), "Divisor must be a scalar quantity or a variable!"
        if isinstance(other, numbers.Number):
            result_value = self.numeric_value / other
            result_units = self.units
        else:
            result_value = self.value / other.value
            result_units = _resolve_unit_system(self.unit_system, other.unit_system, "divide")

        return Variable("{}{}".format(result_value, result_units))

    # Python 2.7 version
    @aedt_exception_handler
    def __div__(self, other):
        return self.__truediv__(other)

    @aedt_exception_handler
    def __rtruediv__(self, other):
        """Divide the other object by this object

        Parameters
        ---------
        other : numbers.Number or Variable
            Dividend object

        Returns
        -------
        Variable

        Examples
        --------
        Divide a number by a Variable with units 's'. Automatically determine the result is in 'Hz'
        >>> from pyaedt.application.Core.Variables import Variable
        >>> v = Variable("1s")
        >>> result = 3.0 / v
        >>> assert result.numeric_value == 3.0
        >>> assert result.units == "Hz"
        >>> assert result.unit_system == "Freq"

        """
        assert isinstance(other, numbers.Number), "Dividend must be a numerical quantity!"
        result_value = other / self.value
        result_units = _resolve_unit_system("None", self.unit_system, "divide")
        return Variable("{}{}".format(result_value, result_units))

    # Python 2.7 version
    @aedt_exception_handler
    def __div__(self, other):
        return self.__rtruediv__(other)

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

