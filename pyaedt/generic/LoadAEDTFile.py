import re
from collections import OrderedDict


# --------------------------------------------------------------------
# public interface


def load_entire_aedt_file(filename):
    """Load the entire AEDT file and return the dictionary

    Parameters
    ----------
    filename :
        AEDT filename with path

    Returns
    -------
    type
        dictionary containing the decoded AEDT file

    """
    return _load_entire_aedt_file(filename)


def load_keyword_in_aedt_file(filename, keyword):
    """Load s specific keyword in the AEDT file and return the dictionary

    Parameters
    ----------
    filename :
        AEDT filename with path
    keyword :
        keyword to search and load

    Returns
    -------
    type
        dictionary containing the decoded AEDT file

    """
    return _load_keyword_in_aedt_file(filename, keyword)

# --------------------------------------------------------------------
# internals


# precompile all Regular expressions
_remove_quotes = re.compile(r"^'(.*?)'$")
_split_list_elements = re.compile(",(?=(?:[^']*'[^']*')*[^']*$)")
_round_bracket_list = re.compile(r"^(?P<KEY1>[^\s]+?)\((?P<LIST1>.+)\)|^'(?P<KEY2>.+?\s.+)'(?<=')\((?P<LIST2>.+)\)")
_square_bracket_list = re.compile(r"^(?P<KEY1>[^\s]+?)\[\d+:(?P<LIST1>.+)\]|^'(?P<KEY2>.+?\s.+)'(?<=')\[\d+:(?P<LIST2>.+)\]")
_key_parse = re.compile(r"(^'(?P<KEY1>.+?)')(?<=')=(?P<VAL1>.+$)|(?P<KEY2>^.+?)=(?P<VAL2>.+$)")
_value_parse1 = re.compile(r"\s")
_value_parse2 = re.compile(r"^'([^']*\s[^']*)(?=')")
_begin_search = re.compile(r"\$begin '(.+)'")

# global variables
_all_lines = []
_len_all_lines = 0
_count = 0


def _parse_value(v):
    """

    Parameters
    ----------
    v :
        

    Returns
    -------

    """
    #  parse the value 'v'
    if v is None:
        pv = v
    elif v == 'true':
        pv = True
    elif v == 'false':
        pv = False
    else:
        try:
            pv = int(v)
        except ValueError:
            try:
                pv = float(v)
            except ValueError:
                m = _remove_quotes.search(v)
                if m:
                    pv = m.group(1)
                else:
                    pv = v
    return pv


def _separate_list_elements(v):
    """

    Parameters
    ----------
    v :
        

    Returns
    -------

    """
    if "(" in v or '=' in v:
        l1 = _split_list_elements.split(v)
    else:
        l1 = v.split(",")
    l2 = [_parse_value(i.strip()) for i in l1]
    return l2


def _decode_value_and_save(k, v, d):
    """

    Parameters
    ----------
    k :
        
    v :
        
    d :
        

    Returns
    -------

    """
    # save key 'k', value 'v' in dict 'd'
    # create a list for key(l1, l2, l3)
    # create a list for key[n: 1, 2, ...n]

    m = _round_bracket_list.search(k)
    if m and m.group('KEY1'):
        v = _separate_list_elements(m.group('LIST1'))
        k = m.group('KEY1')
        d[k] = v
    elif m and m.group('KEY2'):
        v = _separate_list_elements(m.group('LIST2'))
        k = m.group('KEY2')
        d[k] = v
    else:
        m = _square_bracket_list.search(k)
        if m and m.group('KEY1'):
            v = _separate_list_elements(m.group('LIST1'))
            k = m.group('KEY1')
            d[k] = v
        elif m and m.group('KEY2'):
            v = _separate_list_elements(m.group('LIST2'))
            k = m.group('KEY2')
            d[k] = v
        else:
            d[k] = _parse_value(v)


def _decode_key(l, d):
    """

    Parameters
    ----------
    l :
        
    d :
        

    Returns
    -------

    """
    m = _key_parse.search(l)
    if m and m.group('KEY1'):  # key btw ''
        value = m.group('VAL1')
        if "\\'" in value:
            value2 = value.replace("\\'", '"')
        else:
            value2 = value
        if not _value_parse1.search(value2) or _value_parse2.search(value2):  # if there are no spaces in value
            key = m.group('KEY1')                                           # or values with spaces are between quote
            _decode_value_and_save(key, value, d)
        else:  # spaces in value without quotes
            key = l
            value = None
            _decode_value_and_save(key, value, d)
    elif m and m.group('KEY2'):  # key without ''
        value = m.group('VAL2')
        if "\\'" in value:
            value2 = value.replace("\\'", '"')
        else:
            value2 = value
        if not _value_parse1.search(value2) or _value_parse2.search(value2):  # if there are no spaces in value
            key = m.group('KEY2')                                           # or values with spaces are between quote
            _decode_value_and_save(key, value, d)
        else:  # spaces in value without quotes
            key = l
            value = None
            _decode_value_and_save(key, value, d)
    else:  # no = sign found
        key = l
        value = None
        _decode_value_and_save(key, value, d)


def _walk_through_structure(keyword, save_dict):
    """

    Parameters
    ----------
    keyword :
        
    save_dict :
        

    Returns
    -------

    """
    global _count
    begin_key = '$begin \'{}\''.format(keyword)
    end_key = '$end \'{}\''.format(keyword)
    found = False
    saved_value = None
    while _count < _len_all_lines:
        line = _all_lines[_count]
        # begin_key is found
        if begin_key == line.strip():
            found = True
            saved_value = save_dict.get(keyword)               # if the keyword is already present
            if saved_value and type(saved_value) is not list:  # makes the value a list, if it's not already
                saved_value = [saved_value]
            save_dict[keyword] = OrderedDict()
            _count += 1
            continue
        # end_key is found
        if end_key == line.strip(): break
        # between begin_key and end_key
        if found:
            b = _begin_search.search(line)
            if b:  # walk down a level
                nextlvl_begin_key = b.group(1)
                _walk_through_structure(nextlvl_begin_key, save_dict[keyword])
            else:  # decode key
                _decode_key(line, save_dict[keyword])
        _count += 1
    # recompose value if list
    if saved_value:
        saved_value.append(save_dict[keyword])
        save_dict[keyword] = saved_value
    return _count


def _reaf_aedt_file(filename):
    """Read the entire AEDT file discard binary and put ascii line in a list

    Parameters
    ----------
    filename :
        AEDT filename with path

    Returns
    -------

    """
    global _all_lines
    global _len_all_lines
    global _count
    # read the AEDT file and discard the binary part
    temp = open(filename, 'rb').read().splitlines()
    _all_lines = []
    _count = 0
    for line in temp:
        try:
            _all_lines.append(line.decode("utf-8").lstrip('\t'))
        except UnicodeDecodeError:
            break
    _len_all_lines = len(_all_lines)


def _load_entire_aedt_file(filename):
    """Load the entire AEDT file and return the dictionary

    Parameters
    ----------
    filename :
        AEDT filename with path

    Returns
    -------
    type
        dictionary containing the decoded AEDT file

    """
    _reaf_aedt_file(filename)
    # load the aedt file
    begin_key = None
    for line in _all_lines:
        m = _begin_search.search(line)
        if m:
            begin_key = m.group(1)
            break
    main_dict = OrderedDict()
    if begin_key:
        _walk_through_structure(begin_key, main_dict)
    return main_dict


def _load_keyword_in_aedt_file(filename, keyword):
    """Load a specific keyword in the AEDT file and return the dictionary

    Parameters
    ----------
    filename :
        AEDT filename with path
    keyword :
        keyword to search and load

    Returns
    -------
    type
        dictionary containing the decoded AEDT file

    """
    _reaf_aedt_file(filename)
    # load the aedt file
    main_dict = OrderedDict()
    _walk_through_structure(keyword, main_dict)
    return main_dict
