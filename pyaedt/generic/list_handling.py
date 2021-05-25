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

