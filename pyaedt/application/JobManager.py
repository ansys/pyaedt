
def get_hpc_info(filename):
    """

    Parameters
    ----------
    filename :
        

    Returns
    -------
    type
        

    """
    config_name = ''
    design_type = ''
    with open(filename, 'r') as fid:
        for line in fid:
            if 'ConfigName=' in line:
                config_name = line.strip().replace('ConfigName=', '').replace("'", '')
            elif 'DesignType=' in line:
                design_type = line.strip().replace('DesignType=', '').replace("'", '')
    return config_name, design_type
    pass


def update_hpc_option(self, filnename, propertyname, propertyvalue,
                      isvaluestring=True):
    """Update HPC option into acf configuration file.

    isvaluestring report a true or false depending if value is a string or integer
    nc is the number of core (integer or string)

    Parameters
    ----------
    filnename : str
        Full path to the filename.  Can be acf or txt.

    propertyname : str
        Property name to be updated.

    propertyvalue : 
        Property value to be added.

    isvaluestring : bool, optional
        ``True`` if the value a string.  Default ``True``.

    Returns
    -------

    """
    with open(filnename) as fid:
        for line in fid:
            if propertyname + "=" in line:
                old_prop = line.strip()
                new_line = line
    with open(filnename) as fid:
        if isvaluestring:
            new_line = fid.read().replace(old_prop, propertyname + "=" + "\'" + str(propertyvalue) + "\'")
        else:
            new_line = fid.read().replace(old_prop, propertyname + "=" + str(propertyvalue))

    with open(filnename, "w") as f:
        f.write(new_line)


def update_simulation_cores(self, name, nc):
    """Update HPC Number of Cores in configuration file.
    nc is the number of core (integer or string)

    Parameters
    ----------
    name :
        
    nc :
        

    Returns
    -------

    """
    with open(name) as fid:
        for line in fid:
            if 'NumCores=' in line:
                old_cores = line.strip()
                new_line = line
    with open(name) as fid:
        new_line = fid.read().replace(old_cores, "NumCores=" + str(nc))
    with open(name, "w") as f:
        f.write(new_line)
    return

def update_simulation_engines(self, name, nc):
    """Update HPC Number of Engines in configuration file name.
    nc is the number of Engines (integer or string)

    Parameters
    ----------
    name :
        
    nc :
        

    Returns
    -------

    """
    with open(name) as fid:
        for line in fid:
            if 'NumEngines=' in line:
                old_cores = line.strip()
                new_line = line
    with open(name) as fid:
        new_line = fid.read().replace(old_cores, "NumEngines=" + str(nc))
    with open(name, "w") as f:
        f.write(new_line)
    return

def update_machine_name(self, name, machinename):
    """

    Parameters
    ----------
    name :
        
    machinename :
        

    Returns
    -------

    """
    with open(name) as fid:
        for line in fid:
            if 'MachineName=' in line:
                old_machine = line.strip()
                new_line = line
    with open(name) as fid:
        new_line = fid.read().replace(old_machine, "MachineName=\'" + str(machinename) + "\'")
    with open(name, "w") as f:
        f.write(new_line)
    return

def update_config_name(self, name, machinename):
    """

    Parameters
    ----------
    name :
        
    machinename :
        

    Returns
    -------

    """
    with open(name) as fid:
        for line in fid:
            if 'ConfigName=' in line:
                old_config = line.strip()
                new_line = line
    with open(name) as fid:
        if machinename == "localhost":
            machinename = "Local"
        new_line = fid.read().replace(old_config, "ConfigName='" + str(machinename) + "'")
    with open(name, "w") as f:
        f.write(new_line)
    return

def update_cluster_cores(self, file_name,param_name, param_val):
    """

    Parameters
    ----------
    file_name :
        
    param_name :
        
    param_val :
        

    Returns
    -------

    """
    with open(file_name) as f:
        for line in f:
            if param_name in line:
                old_line = line
    with open(file_name) as f:
        replacement_line = "\\	\\	\\	NumCores=" + str(param_val) + "\\" + chr(10)
        new_line = f.read().replace(old_line,  replacement_line)
    with open(file_name, "w") as f:
        f.write(new_line)
    return

def Update_hpc_template(self, file_name, param_name, param_val):
    """

    Parameters
    ----------
    file_name :
        
    param_name :
        
    param_val :
        

    Returns
    -------

    """
    with open(file_name) as f:
        for line in f:
            if (line.find(param_name) > 0):
                line = f.readline()
                old_line = line
    with open(file_name) as f:
        replacement_line = "\\	\\	\\	Value=\\'" + str(param_val) + "\\'\\" + chr(10)
        new_line = f.read().replace(old_line,  replacement_line)
    with open(file_name, "w") as f:
        f.write(new_line)
    return

