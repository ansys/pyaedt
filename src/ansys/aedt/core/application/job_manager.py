# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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


def get_hpc_info(filename):
    """Retrieve HPC information.

    Parameters
    ----------
    filename : str
        Name of the file.

    Returns
    -------
    config_name : str
        Config name.
    design_type : str
        Design name.

    """
    config_name = ""
    design_type = ""
    with open(filename, "r") as fid:
        for line in fid:
            if "ConfigName=" in line:
                config_name = line.strip().replace("ConfigName=", "").replace("'", "")
            elif "DesignType=" in line:
                design_type = line.strip().replace("DesignType=", "").replace("'", "")
    return config_name, design_type


def update_hpc_option(filnename, propertyname, propertyvalue, isvaluestring=True, separator="="):
    """Update an HPC option in the configuration file.

    Parameters
    ----------
    filnename : str
        Full path and name of the configuration file. The file type can be ACF or TXT.
    propertyname : str
        Name of the property to update.
    propertyvalue :
        Value for the property.
    isvaluestring : bool, optional
        Whether the value  is a string. The default is ``True``.
    separator : str, optional
        Separates the property name from its value. The default is ``=``.

    Returns
    -------
    type

    """
    line_number = None
    new_line = ""
    with open(filnename, "r") as file:
        data = file.readlines()
        for i, line in enumerate(data):
            if propertyname + separator in line:
                old_prop = line.strip()
                old_line = line
                line_number = i
                if isvaluestring:
                    new_line = old_line.replace(old_prop, propertyname + separator + "'" + str(propertyvalue) + "'")
                else:
                    new_line = old_line.replace(old_prop, propertyname + separator + str(propertyvalue))
                break

    data[line_number] = new_line
    try:
        with open(filnename, "w") as file:
            file.writelines(data)
        return True
    except IOError:
        return False


def update_simulation_cores(name, nc):
    """Update the HPC number of cores in the configuration file.

    Parameters
    ----------
    name : str
        Name of the configuration file.
    nc : int or string
        Number of simulation cores.

    """
    with open(name) as fid:
        for line in fid:
            if "NumCores=" in line:
                old_cores = line.strip()
                new_line = line
    with open(name) as fid:
        new_line = fid.read().replace(old_cores, "NumCores=" + str(nc))
    with open(name, "w") as f:
        f.write(new_line)


def update_simulation_engines(name, nc):
    """Update the HPC number of simulaton engines in the configuration file.

    Parameters
    ----------
    name : str
        Name of the configuration file.
    nc : int or str
        Number of simulaton engines.

    """
    with open(name) as fid:
        for line in fid:
            if "NumEngines=" in line:
                old_cores = line.strip()
                new_line = line
    with open(name) as fid:
        new_line = fid.read().replace(old_cores, "NumEngines=" + str(nc))
    with open(name, "w") as f:
        f.write(new_line)


def update_machine_name(name, machinename):
    """Update the machine name.

    Parameters
    ----------
    name : str
        Path of the configuration file.
    machinename : str
        New name of the machine.

    """
    with open(name) as fid:
        for line in fid:
            if "MachineName=" in line:
                old_machine = line.strip()
                new_line = line
    with open(name) as fid:
        new_line = fid.read().replace(old_machine, "MachineName='" + str(machinename) + "'")
    with open(name, "w") as f:
        f.write(new_line)


def update_config_name(name, machinename):
    """Update the name of the configuration.

    Parameters
    ----------
    name : str
        Path of the configuration file.
    machinename : str
        New name of the machine.

    """
    with open(name) as fid:
        for line in fid:
            if "ConfigName=" in line:
                old_config = line.strip()
                new_line = line
    with open(name) as fid:
        if machinename == "localhost":
            machinename = "Local"
        new_line = fid.read().replace(old_config, "ConfigName='" + str(machinename) + "'")
    with open(name, "w") as f:
        f.write(new_line)


def update_cluster_cores(file_name, param_name, param_val):
    """Update the number of cluster cores in the configuration file.

    Parameters
    ----------
    file_name : str
        Full path and name of the configuration file. The file type can be ACF or TXT.
    param_name : str
        Name of the parameter.
    param_val : int
         New number of cluster cores.

    """
    with open(file_name) as f:
        for line in f:
            if param_name in line:
                old_line = line
    with open(file_name) as f:
        replacement_line = "\\	\\	\\	NumCores=" + str(param_val) + "\\" + chr(10)
        new_line = f.read().replace(old_line, replacement_line)
    with open(file_name, "w") as f:
        f.write(new_line)


def update_hpc_template(file_name, param_name, param_val):
    """Update a parameter in the HPC template file.

    Parameters
    ----------
    file_name : str
        Full path and name of the HPC template file.
    param_name : str
        Name of the parameter to update.
    param_val : int
        Value of the parameter.

    """
    with open(file_name) as f:
        for line in f:
            if line.find(param_name) > 0:
                line = f.readline()
                old_line = line
    with open(file_name) as f:
        replacement_line = "\\	\\	\\	Value=\\'" + str(param_val) + "\\'\\" + chr(10)
        new_line = f.read().replace(old_line, replacement_line)
    with open(file_name, "w") as f:
        f.write(new_line)
