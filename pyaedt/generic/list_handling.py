def unique_string_list(element_list, only_string=True):
    """

    Parameters
    ----------
    element_list :
        
    only_string :
         (Default value = True)

    Returns
    -------

    """
    if element_list:
        if isinstance(element_list, list):
            element_list = set(element_list)
        elif isinstance(element_list, str):
            element_list = [element_list]
        else:
            error_message = 'Invalid list data'
            try:
                error_message += ' {}'.format(element_list)
            except:
                pass
            raise Exception(error_message)

        if only_string:
            non_string_entries = [x for x in element_list if type(x) is not str]
            assert not non_string_entries, "Invalid list entries {} are not a string!".format(non_string_entries)

    return element_list

def string_list(element_list):
    """

    Parameters
    ----------
    element_list :
        

    Returns
    -------

    """
    if isinstance(element_list, str):
        element_list = [element_list]
    else:
        assert isinstance(element_list, str), 'Input must be a list or a string'
    return element_list

def ensure_list(element_list):
    """

    Parameters
    ----------
    element_list :
        

    Returns
    -------

    """
    if not isinstance(element_list, list):
        element_list = [element_list]
    return element_list

def variation_string_to_dict(variation_string):
    """Helper function to convert a list of "="-separated strings into a dictionary

    Returns
    -------
    dict
    """
    var_data = variation_string.split()
    variation_dict = {}
    for var in var_data:
        pos_eq = var.find("=")
        var_name = var[0:pos_eq]
        var_value = var[pos_eq+1:].replace('\'', '')
        variation_dict[var_name] = var_value
    return variation_dict
