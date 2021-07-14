
def get_hpc_info(filename):
    """Retrieve HPC information.

    Parameters
    ----------
    filename : str
        Name of the file.   

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

    Returns
    -------
    type

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
    """Update the HPC number of cores in the configuration file.
    
    Parameters
    ----------
    name : str
        Name of the configuration file.    
    nc : int or string
        Number of cores.  

    Returns
    -------
    type

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
    """Update the HPC number of simulaton engines in the configuration file.
    
    Parameters
    ----------
    name : str
        Name of the configuration file.   
    nc : int or str
        Number of simulaton engines.   

    Returns
    -------
    type

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
    """Update the machine name.

    Parameters
    ----------
    name : str
        Name of the machine to update.
    machinename : str
        New name of the machine.

    Returns
    -------
    type

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
    """Update the name of the machine.

    Parameters
    ----------
    name : str
        Name of the machine to update.
    machinename : str
        New name of the machine.

    Returns
    -------
    type
    
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

def update_cluster_cores(self, file_name, param_name, param_val):
    """Update the number of cluster cores in the configuration file.

    Parameters
    ----------
    file_name : str
        Full path and name of the configuration file. The file type can be ACF or TXT.   
    param_name : str
        Name of the parameter.      
    param_val : int
         New number of cluster cores. 

    Returns
    -------
    type

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
    """Update a paramerter in the HPC template file.

     Parameters
    ----------
    file_name : str
        Full path and name of the HPC template file.
    param_name : str
        Name of the parameter to update.   
    param_val : int
        Value of the paraemeter.     

    Returns
    -------
    type

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
