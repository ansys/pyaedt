"""
This module contains these classes: `CSVDataset`, `DataSet`, `Expression`, `Variable`, and `VariableManager`.

This module is used to create and edit design and project variables in the 3D tools.

Examples
--------
>>> from pyaedt import Hfss
>>> hfss = Hfss()
>>> hfss["$d"] = "5mm"
>>> hfss["d"] = "5mm"
>>> hfss["postd"] = "1W"

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
    """Convert a temperature from Fahrenheit to Kelvin.
    
    Parameters
    ----------
    val : float
        Temperature value in Fahrenheit.
    inverse : bool, optional
        The default is ``True``.
	
    Returns
    -------
    float
        Temperature value converted to Kelvin.
    
    """
    if inverse:
        return (val - 273.15) * 9 / 5 + 32
    else:
        return (val - 32) * 5 / 9 + 273.15


@aedt_exception_handler
def cel2kel(val, inverse=True):
    """Convert a temperature from Celsius to Kelvin.
    
    Parameters
    ----------
    val : float
        Temperature value in Celsius.
    inverse : bool, optional
        The default is ``True``.
    
    Returns
    -------
    float
        Temperature value converted to Kelvin.
	
    """
    
    if inverse:
        return val - 273.15
    else:
        return val + 273.15


@aedt_exception_handler
def unit_system(units):
    """Retrieve the name of the unit system associated with a unit string. 
    
    Parameters
    ----------
    units : str
        Units for retrieving the associated unit system name.
    
    Returns
    -------
    str
        Key from the ``AEDT_units`` when successful. For example, ``"AngualrSpeed"``.
	``False`` when the units specified are not defined in AEDT units.
    
    """
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
    """Retrieve the unit string of an arithmetic operation on ``Variable`` objects. If no resulting unit system
    is defined for a specific operation (in unit_system_operations), an empty string is returned

    Parameters
    ----------
    unit_system_1 : str
        Name of a unit system, which is a key of ``AEDT_units``.
    unit_system_2 : str
        Name of another unit system, which is a key of ``AEDT_units``.
    operation : str
        Name of an operator within the data set of ``["multiply" ,"divide"]``.

    Returns
    -------
    str
        Unit system when successful, ``""`` when failed.

    """
    try:
        key = "{}_{}_{}".format(unit_system_1, operation, unit_system_2)
        result_unit_system = unit_system_operations[key]
        return SI_units[result_unit_system]
    except KeyError:
        return ""

class CSVDataset:
    """Reads in a CSV file and extracts data, which can be augmented with constant values.
    
    Parameters
    ----------
    csv_file: str, optional
        Input file consisting of delimited data with the first line as the header.
        The CSV value includes the header and data, which supports AEDT units information 
        such as ``"1.23Wb"``. You can also augment the data with constant values.
    separator: str, optional
        Value to use for the delimiter. The default is``None`` in which case a comma is 
        assumed.
    units_dict: dict, optional
        Dictionary consisting of ``{Variable Name: unit}`` to rescale the data
        if it is not in the desired unit system.
    append_dict: dict, optional
        Dictionary consisting of ``{New Variable Name: value}`` to add variables 
        with constant values to all data points. This dictionary is used to add 
        multiple sweeps to one result file.
    valid_solutions : bool, optional
        The default is ``True``.
    invalid_solutions : bool, optional
        The default is ``False``.
         
    """
    @property
    def number_of_rows(self):
        """Number of rows."""
        if self._data:
            for variable, data_list in self._data.items():
                return len(data_list)
        else:
            return 0

    @property
    def number_of_columns(self):
        """Number of columns."""
        return len(self._header)

    @property
    def header(self):
        """Header."""
        return self._header

    @property
    def data(self):
        """Data."""
        return self._data

    @property
    def path(self):
        """Path."""
        return os.path.dirname(os.path.realpath(self._csv_file))

    def __init__(self, csv_file=None, separator=None, units_dict=None, append_dict=None, valid_solutions=True, invalid_solutions=False):
        
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
            assert found_variable, "Input string {} is not a key of the data dictionary.".format(variable)
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
        """Incrementally add the dataset in one CSV file to a dataset in another CSV file.
        
        .. note:
           This assumes that the number of columns in both datasets are the same,
           or that one of the datasets is empty. No checking is done for 
           equivalency of units or variable names.
          
         """

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
    """Decompose a variable value.

    Parameters
    ----------
    variable_value : float

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
    """VariableManager class.

    This class provides for managing design properties and project variables. Design properties
    are the local variables in a design. Project variables are defined at the project 
    level and start with ``$``. 
    
    This class provides access to all variables or a subset of the variables. Manipulation
    of the numerical or string definitions of variable values is provided in the
    :class:`Variable` class.

    Parameters
    ----------
    variables : dict
        Dictionary of all design properties and project variables in the active design.
    design_variables : dict
        Dictionary of all design properties in the active design.
    project_variables : dict
        Dictionary of all project variables available to the active design (key by variable name).
    dependent_variables : dict
        Dictionary of all dependent variables available to the active design (key by variable name).
    independent_variables : dict
       Dictionary of all independent variables (constant numeric values) available to the active 
       design (key by variable name).
    independent_design_variables : dict

    independent_project_variables : dict
    
    variable_names : str or list
        One or more variable names.
    project_variable_names : str or list
        One or more project variable names.
    design_variable_names : str or list
        One or more design variable names.
    dependent_variable_names : str or list
        All dependent variable names within the project.
    independent_variable_names : list of str
        All independent variable names within the project. These can be sweep variables for optimetrics.
    independent_project_variable_names : str or list
        All independent project variable names within the project. These can be sweep variables for optimetrics.
    independent_design_variable_names : str or list
        All independent design properties (local variables) within the project. These can be sweep variables for optimetrics.


    Examples
    --------

    >>> from pyaedt.maxwell import Maxwell3d
    >>> from pyaedt.desktop import Desktop
    >>> d = Desktop()
    >>> aedtapp = Maxwell3d()
    
    Define some test variables.
    
    >>> aedtapp["Var1"] = 3
    >>> aedtapp["Var2"] = "12deg"
    >>> aedtapp["Var3"] = "Var1 * Var2"
    >>> aedtapp["$PrjVar1"] = "pi"

    Get the variable manager for the active design.
    
    >>> v = aedtapp.variable_manager
    
    Get a dictionary of all project and design variables.
    
    >>> v.variables
    {'Var1': <pyaedt.application.Variables.Variable at 0x2661f34c448>,
     'Var2': <pyaedt.application.Variables.Variable at 0x2661f34c308>,
     'Var3': <pyaedt.application.Variables.Expression at 0x2661f34cb48>,
     '$PrjVar1': <pyaedt.application.Variables.Expression at 0x2661f34cc48>}

    Get a dictionary of only the design variables.

    >>> v.design_variables
    {'Var1': <pyaedt.application.Variables.Variable at 0x2661f339508>,
     'Var2': <pyaedt.application.Variables.Variable at 0x2661f3415c8>,
     'Var3': <pyaedt.application.Variables.Expression at 0x2661f341808>}

    Get a dictionary of only the independent design variables.
    
    >>> v.independent_design_variables
    {'Var1': <pyaedt.application.Variables.Variable at 0x2661f335d08>,
     'Var2': <pyaedt.application.Variables.Variable at 0x2661f3557c8>}

    See Also
    --------
    :class:`Variable` class.
    
    """

    @property
    def variables(self):
        """Variables.
        
        Returns
        -------
        dict
            Dictionary of the `Variable` objects for each project variable and each
            design property in the active design.
            
        """
        return self._variable_dict([self.odesign, self.oproject])

    @property
    def design_variables(self):
        """Design variables
        
        Returns
        -------
        dict
            Dictionary of the design properties (local properties) in the design.
        """
        return self._variable_dict([self.odesign])

    @property
    def project_variables(self):
        """Project variables.
        
        Returns
        -------
        dict
            Dictionary of the project properties.
        """
        return self._variable_dict([self.oproject])

    @property
    def independent_variables(self):
        """Independent variables.
        
        Returns
        -------
        dict
            Dictionary of the independent variables (constant numeric values) available to the design.
        """
        return self._variable_dict([self.odesign, self.oproject], dependent=False)

    @property
    def independent_project_variables(self):
        """Independent project variables.
        
        Returns
        -------
        dict
            Dictionary of the independent project variables available to the design.
        """
        return self._variable_dict([self.oproject], dependent=False)

    @property
    def independent_design_variables(self):
        """Independent design variables.
        
        Returns
        -------
        dict
            Dictionary of the independent design properties (local variables) available to the design.
        """
        return self._variable_dict([self.odesign], dependent=False)

    @property
    def dependent_variables(self):
        """Dependent variables.
        
        Returns
        -------
        dict
            Dictionary of the dependent design properties (local variables) and project variables available to the design.
        
        """
        return self._variable_dict([self.odesign, self.oproject], independent=False)

    @property
    def variable_names(self):
        return [var_name for var_name in self.variables]

    @property
    def project_variable_names(self):
        return [var_name for var_name in self.project_variables]

    @property
    def independent_project_variable_names(self):
        return [var_name for var_name in self.independent_project_variables]

    @property
    def design_variable_names(self):
        return [var_name for var_name in self.design_variables]

    @property
    def independent_design_variable_names(self):
        return [var_name for var_name in self.independent_design_variables]

    @property
    def independent_variable_names(self):
        return [var_name for var_name in self.independent_variables]

    @property
    def dependent_variable_names(self):
        return [var_name for var_name in self.dependent_variables]

    @property
    def oproject(self):
        """Project object."""
        return self._parent._oproject

    @property
    def odesign(self):
        """Design object."""
        return self._parent._odesign

    @property
    def _messenger(self):
        """_messenger."""
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
        """Retrieve the variable dictionary.

        Parameters
        ----------
        object_list : list
            List of objects.
        dependent : bool, optional
             Whether to include dependent variables. The default is ``True``.
        independent : bool, optional
             Whether to include independent variables. The default is ``True``.

        Returns
        -------
        dict
            Dictionary of the specified variables.

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
        """Retrieve the variable value of a project or design variable as a string."""
        return self.aedt_object(variable_name).GetVariableValue(variable_name)

    @aedt_exception_handler
    def aedt_object(self, variable):
        """Retrieve an AEDT object.
        
        Parameters
        ----------
        variable
        
        """
        if variable[0] == "$":
            return self.oproject
        else:
            return self.odesign

    @aedt_exception_handler
    def set_variable(self, variable_name, expression=None, readonly=False, hidden=False,
                     description=None, overwrite=True):
        """Set the value of a design property or project variable. 

        Parameters
        ----------
        variable_name : str
            Name of the design property or project variable (``$var``). If this variable 
            does not exist, a new one is created and a value is set.
        expression : str
            Valid string expression within the AEDT design and project structure.
            For example, ``"3*cos(34deg)"``.
        readonly : bool, optional
           Whether to set the design property or project variable to read-only. The 
           default is ``False``.
        hidden :  bool, optional
            Whether to hide the design property or project variable. The 
           default is ``False``.
        description : str, optional 
           Text to display for the design property or project variable in the 
	     ``Properties`` window. The default is ``None``.
        overwrite : bool, optional
            Whether to overwrite an existing value for the design property or
            project variable. The default is ``False``, in which case this method is 
            ignored. 

        Returns
        -------
        bool
             ``True`` when successful, ``False`` when failed.

        Examples
        --------
        Set the value of design property ``p1`` to ``"10mm"``, creating the property 
        if it does not already eixst.
        
        >>> aedtapp.variable_manager.set_variable("p1", expression="10mm")

        Set the value of design property ``p1`` to ``"20mm"`` only if the property does 
        not already exist.
        
        >>> aedtapp.variable_manager.set_variable("p1", expression="20mm", overwrite=False)

        Set the value of design property ``p2`` to ``"10mm"``, creating the property 
        if it does not already exist. Also make it read-only and hidden and add a description.
        
        >>> aedtapp.variable_manager.set_variable(variable_name="p2", expression="10mm", readonly=True, hidden=True,
        ...                                       description="This is the description of this variable.")

        Set the value of the project variable ``$p1`` to ``"30mm"``, creating the variable if it does not exist.
        
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
        elif isinstance(expression, list):
            variable = str(expression)
        elif not expression:
            prop_type = "SeparatorProp"
            variable = ""
            try:
                if self.delete_separator(variable_name):
                    desktop_object.Undo()
                    self._messenger.clear_messages()
                    return
            except:
                pass
        else:
            raise Exception("Unhandled input type to the design property or project variable.")

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
        """Delete a separator from either the active project or design.
        
        Parameters
        ----------
        separator_name : str
	      Value to use for the delimiter. 
        
        Returns
        -------
	  bool
            ``True`` when the separator exists and can be deleted, ``False`` otherwise.
            
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
        """Delete a variable.

        Parameters
        ----------
        sVarName : str
            Name of the variable.


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
                return True
            except:
                pass
        return False


class Variable(object):
    """Stores variables and provides for performing operations on variables.
    
    This class stores variables and provides for performing operations 
    on variables. It handles the contents of design properties and project 
    variables.

    Parameters
    ----------
    value : float
        Numerical value of the variable in SI units.
    units : str
        Units for the value.

    Examples
    --------
    
    >>> from pyaedt.application.Variables import Variable

    Define a variable using a string value consistent with the AEDT properties.
    
    >>> v = Variable("45mm")

    Define an unitless variable with a value of 3.0.
   
    >>> v = Variable(3.0)

    Define a variable defined by a numeric result and a unit string.
    
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
                "The unit specification {} is inconsistent with the identified units {}.".format(specified_units, self._units)
            self._units = specified_units

        if isinstance(self._value, numbers.Number):
            scale = AEDT_units[self.unit_system][self._units]
            if isinstance(scale, tuple):
                self._value = scale[0](self._value, inverse=False)
            else:
                self._value =  self._value * scale

    @property
    def unit_system(self):
        """Unit system of the expression as a string."""
        return unit_system(self._units)

    @property
    def units(self):
        """Units."""
        return self._units

    @property
    def value(self):
        """Value."""
        return self._value

    @property
    def numeric_value(self):
        """Numeric part of the expression as a float value."""
        if isinstance(self._value, numbers.Number):
            scale = AEDT_units[self.unit_system][self._units]
        if isinstance(scale, tuple):
            return scale[0](self._value, True)
        else:
            return self._value / scale

    @property
    def string_value(self):
        """String value.
        
        The numeric value with the unit is concatenated and returned as a string. The numeric display 
        in the modeler and the string value can differ. For example, you might see ``10mm`` in the 
        modeler and see ``10.0mm`` returned as the string value.
        
        """
        return ('{}{}').format(self.numeric_value, self._units)

    @aedt_exception_handler
    def rescale_to(self, units):
        """Rescale the expression to a new unit within the current unit system.
	
	  Parameters
	  ----------
	  units : str
	      Units to rescale to.

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
            "New unit system {0} is inconsistent with the current unit system {1}."
        self._units = units
        return self


    @aedt_exception_handler
    def format(self, format):
        """Retrieve the string value with the specified numerical formatting.

        Parameters
        ----------
        format : str
            Format for the numeric value of the string. For example, ``'06.2f'``. For 
            more information, see the `PyFormat documentation <https://pyformat.info/>`_.
		
        Returns
        -------
        str
            String value with the specified numerical formatting.

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
        """Multiply the variable with a number or another variable and return a new object.

        Parameters
        ---------
        other : numbers.Number or variable
            Object to be multiplied.

        Returns
        -------
        type
            Variable.

        Examples
        --------
        >>> from pyaedt.application.Variables import Variable

        Multiply ``'Length1'`` by unitless ``'None'``` to obtain ``'Length'``. 
        A numerical value is also considered to be unitless.
        
        >>> v1 = Variable("10mm")
        >>> v2 = Variable(3)
        >>> result_1 = v1 * v2
        >>> result_2 = v1 * 3
        >>> assert result_1.numeric_value == 30.0
        >>> assert result_1.unit_system == "Length"
        >>> assert result_2.numeric_value == result_1.numeric_value
        >>> assert result_2.unit_system == result_1.unit_system

        Multiply voltage times current to obtain power.
        
        >>> v3 = Variable("3mA")
        >>> v4 = Variable("40V")
        >>> result_3 = v3 * v4
        >>> assert result_3.numeric_value == 0.12
        >>> assert result_3.units == "W"
        >>> assert result_3.unit_system == "Power"

        """
        assert isinstance(other, numbers.Number) or isinstance(other, Variable), "Multiplier must be a scalar quantity or a variable."
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
        """Add the variable to another variable to return a new object.

        Parameters
        ---------
        other : Variable
            Object to be multiplied.

        Returns
        -------
        type
            Variable.

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
        assert isinstance(other, Variable), "You can only add a variable with another variable."
        assert self.unit_system == other.unit_system, "Only ``Variable`` objects with the same unit system can be added."
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
        """Subtract another variable from the variable and return a new object.

        Parameters
        ---------
        other : Variable
            Object to be subtracted.

        Returns
        -------
        type
            Variable.

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
        assert isinstance(other, Variable), "You can only subtract a variable from another variable."
        assert self.unit_system == other.unit_system, "Only ``Variable`` objects with the same unit system can be subtracted."
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
        """Divide the variable by a number or another variable and return a new object

        Parameters
        ---------
        other : numbers.Number or variable
            Object by which to divide.

        Returns
        -------
        type
            Variable.

        Examples
        --------
        Divide a variable with units ``"W"`` by a variable with units ``"V"`` and automatically 
        resolve the new units to ``"A"``.
	
        >>> from pyaedt.application.Variables import Variable

        >>> v1 = Variable("10W")
        >>> v2 = Variable("40V")
        >>> result = v1 / v2
        >>> assert result_1.numeric_value == 0.25
        >>> assert result_1.units == "A"
        >>> assert result_1.unit_system == "Current"

        """
        assert isinstance(other, numbers.Number) or isinstance(other, Variable), "Divisor must be a scalar quantity or a variable."
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
        """Divide another object by this object.

        Parameters
        ---------
        other : numbers.Number or variable
            Object to divide by.

        Returns
        -------
        type
            Variable.

        Examples
        --------
        Divide a number by a variable with units ``"s"`` and automatically determine that 
        the result is in ``"Hz"``.
        
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
    """Provides a framework for manipulating variable expressions.
    
    Parameters
    ----------
    expression :
    
    float_value :
    
    """

    def __init__(self, expression, float_value):
        self._expression = expression
        self._value = float_value
        # TODO. Try to identify the unit system from the expression.
        try:
            value, units = decompose_variable_value(expression)
            self._units = units
        except:
            self._units = ''

    @property
    def expression(self):
        """Expression."""
        return str(self._expression)


class DataSet(object):
    """DataSet class.
    
    This class provides for managing data sets.
    
    Parameters
    ----------
    parent :
    name :
    x : float
    y : float
    z : float, optional
        The default is ``None``.
    v : float, optional
       The default is ``None``.
    xunit : str, optional
       The default is ``""``.
    yunit : str, optional
       The default is ``""``.
    zunit : str, optional
       The default is ``""``.
    vunit : str, optional
       The default is ``""``. 
    
    """

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
        """Retrieve arguments."""
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
        """Create a dataset.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.name[0] == "$":
            self._parent._oproject.AddDataset(self._args())
        else:
            self._parent.odesign.AddDataset(self._args())
        return True

    @aedt_exception_handler
    def add_point(self, x, y, z=None, v=None):
        """Add a point to the existing dataset.

        Parameters
        ----------
        x : float
        y : float
        z : float, optional
            The default is ``None``.
        v : float, optional
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.x.append(x)
        self.y.append(y)
        if self.z and self.v:
            self.z.append(z)
            self.v.append(v)

        return self.update()

    @aedt_exception_handler
    def remove_point_from_x(self, x):
        """Remove a point from an X-axis value.

        Parameters
        ----------
        x : float
       
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if x not in self.x:
            self._parent._messenger.add_error_message("Value {} is not found.".format(x))
            return False
        id_to_remove = self.x.index(x)
        return self.remove_point_from_index(id_to_remove)


    @aedt_exception_handler
    def remove_point_from_index(self, id_to_remove):
        """Remove a point from an index.

        Parameters
        ----------
        id_to_remove : int
            ID of the index.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        """Update the dataset.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        """
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
        """Delete the dataset.
        
        Returns
        ------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        if self.name[0] == "$":
            self._parent._oproject.DeleteDataset(self.name)
            del self._parent.project_datasets[self.name]
        else:
            self._parent.odesign.DeleteDataset(self.name)
            del self._parent.project_datasets[self.name]
        return True

    @aedt_exception_handler
    def export(self, dataset_path=None):
        """Export the dataset.

        Parameters
        ----------
        dataset_path : str, optional
            Path to export the dataset to. The default is ``None``, in which
            case the dataset is exported to the project path.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if not dataset_path:
            dataset_path = os.path.join(self._parent.project_path, self.name +".tab")
        if self.name[0] == "$":
            self._parent._oproject.ExportDataset(self.name, dataset_path)
        else:
            self._parent.odesign.ExportDataset(self.name, dataset_path)
        return True
