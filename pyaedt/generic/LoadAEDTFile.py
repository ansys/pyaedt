# -*- coding: utf-8 -*-
import re

from pyaedt.generic.general_methods import open_file

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
    dict
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
    dict
        dictionary containing the decoded AEDT file

    """
    return _load_keyword_in_aedt_file(filename, keyword)


# --------------------------------------------------------------------
# internals


# precompile all Regular expressions
_remove_quotes = re.compile(r"^'(.*?)'$")
_split_list_elements = re.compile(",(?=(?:[^']*'[^']*')*[^']*$)")
_round_bracket_list = re.compile(r"^(?P<SKEY1>\S+?)\((?P<LIST1>.+)\)|^'(?P<SKEY2>.+?\s.+)'(?<=')\((?P<LIST2>.+)\)")
_square_bracket_list = re.compile(
    r"^(?P<SKEY1>\S+?)\[\d+:(?P<LIST1>.+)\]|^'(?P<SKEY2>.+?\s.+)'(?<=')\[\d+:(?P<LIST2>.+)\]"
)
_key_parse = re.compile(r"(^'(?P<KEY1>.+?)')(?<=')=(?P<VAL1>.+$)|(?P<KEY2>^.+?)=(?P<VAL2>.+$)")
_value_parse1 = re.compile(r"\s")
_value_parse2 = re.compile(r"^'([^']*\s[^']*)(?=')")
_begin_search = re.compile(r"\$begin '(.+)'")

# set recognized keywords
_recognized_keywords = ["CurvesInfo"]
_recognized_subkeys = ["simple("]

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
    #  duck typing parse of the value 'v'
    if v is None:
        pv = v
    elif v == "true":
        pv = True
    elif v == "false":
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
    if "(" in v or "=" in v:
        l1 = _split_list_elements.split(v)
    else:
        l1 = v.split(",")
    l2 = [_parse_value(i.strip()) for i in l1]
    return l2


def _decode_recognized_subkeys(sk, d):
    """Special decodings for sub-keys belonging to _recognized_subkeys

    Parameters
    ----------
    sk : str
        dictionary sub-key recognized

    d : dict
        Active dictionary.

    Returns
    -------
    bool
        Returns ``True`` if it finds and decode a recognized value.

    """
    if sk.startswith(_recognized_subkeys[0]):  # 'simple(' is at the beginning of the value
        m = _round_bracket_list.search(sk)
        if m and m.group("SKEY1") == "simple":  # extra verification. SKEY2 is with spaces, so it's not considered here.
            elems = _separate_list_elements(m.group("LIST1"))
            if elems[0] == "thermal_expansion_coeffcient":
                elems[0] = "thermal_expansion_coefficient"  # fix a typo in the amat files. AEDT supports both strings!
            d[elems[0]] = str(elems[1])  # convert to string as it is dedicated to material props
            return True
    return False


def _decode_value_and_save(k, v, d):
    """

    Parameters
    ----------
    k :

    v :

    d :

    """
    # save key 'k', value 'v' in dict 'd'
    # create a list for subkey(l1, l2, l3)
    # create a list for subkey[n: 1, 2, ...n]
    # send recognized sub-keys to _decode_recognized_subkeys
    for rsk in _recognized_subkeys:
        if rsk in k:  # here we simply search if one of the _recognized_subkeys is in k
            if _decode_recognized_subkeys(k, d):  # the exact search is done inside the _decode_recognized_subkeys
                return  # if there is a match we stop the _decode_value_and_save, otherwise we keep going
    m = _round_bracket_list.search(k)
    if m and m.group("SKEY1"):
        v = _separate_list_elements(m.group("LIST1"))
        k = m.group("SKEY1")
        d[k] = v
    elif m and m.group("SKEY2"):
        v = _separate_list_elements(m.group("LIST2"))
        k = m.group("SKEY2")
        d[k] = v
    else:
        m = _square_bracket_list.search(k)
        if m and m.group("SKEY1"):
            v = _separate_list_elements(m.group("LIST1"))
            k = m.group("SKEY1")
            d[k] = v
        elif m and m.group("SKEY2"):
            v = _separate_list_elements(m.group("LIST2"))
            k = m.group("SKEY2")
            d[k] = v
        else:
            d[k] = _parse_value(v)


def _decode_recognized_key(keyword, line, d):
    """Special decodings for keys belonging to  _recognized_keywords

    Parameters
    ----------
    keyword : str
        dictionary key recognized

    line : str
        Line.

    d : dict
        Active dictionary.

    -------

    """
    if keyword == _recognized_keywords[0]:  # 'CurvesInfo'
        m = re.search(r"\'(\d+)\'\((.*)\)$", line)
        if m:
            k = m.group(1)
            v = m.group(2)
            v2 = v.replace("\\'", '"')
            v3 = _separate_list_elements(v2)
            d[k] = v3
    else:  # pragma: no cover
        raise AttributeError("Keyword {} is supposed to be in the recognized_keywords list".format(keyword))


def _decode_key(line, d):
    """

    Parameters
    ----------
    line : str
        Line.

    d : dict
        Active dictionary.

    -------

    """
    m = _key_parse.search(line)
    if m and m.group("KEY1"):  # key btw ''
        value = m.group("VAL1")
        if "\\'" in value:
            value2 = value.replace("\\'", '"')
        else:
            value2 = value
        # if there are no spaces in value
        if not _value_parse1.search(value2) or _value_parse2.search(value2):
            # or values with spaces are between quote
            key = m.group("KEY1")
            _decode_value_and_save(key, value, d)
        else:  # spaces in value without quotes
            key = line
            value = None
            _decode_value_and_save(key, value, d)
    elif m and m.group("KEY2"):  # key without ''
        value = m.group("VAL2")
        if "\\'" in value:
            value2 = value.replace("\\'", '"')
        else:
            value2 = value
        # if there are no spaces in value   or   values with spaces are between quotes
        if not _value_parse1.search(value2) or _value_parse2.search(value2):
            key = m.group("KEY2")
            _decode_value_and_save(key, value, d)
        else:  # spaces in value without quotes
            key = line
            value = None
            _decode_value_and_save(key, value, d)
    else:  # no = sign found
        key = line
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
    begin_key = "$begin '{}'".format(keyword)
    end_key = "$end '{}'".format(keyword)
    found = False
    saved_value = None
    while _count < _len_all_lines:
        line = _all_lines[_count]
        # begin_key is found
        if begin_key == line:
            found = True
            saved_value = save_dict.get(keyword)  # if the keyword is already present
            # makes the value a list, if it's not already
            if saved_value and type(saved_value) is not list:
                saved_value = [saved_value]
            save_dict[keyword] = {}
            _count += 1
            continue
        # end_key is found
        if end_key == line:
            break
        # between begin_key and end_key
        if found:
            b = _begin_search.search(line)
            if b:  # walk down a level
                nextlvl_begin_key = b.group(1)
                _walk_through_structure(nextlvl_begin_key, save_dict[keyword])
            elif keyword in _recognized_keywords:
                _decode_recognized_key(keyword, line, save_dict[keyword])
            else:  # decode key
                _decode_key(line, save_dict[keyword])
        _count += 1
    # recompose value if list
    if saved_value:
        saved_value.append(save_dict[keyword])
        save_dict[keyword] = saved_value
    return _count


def _read_aedt_file(filename):
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

    # read the AEDT file
    with open_file(filename, "rb") as aedt_fh:
        raw_lines = aedt_fh.read().splitlines()
    ascii_lines = []
    for raw_line in raw_lines:
        try:
            ascii_lines.append(raw_line.decode("utf-8").lstrip(" \t"))
        except UnicodeDecodeError:
            continue
    ascii_content = "\n".join(ascii_lines)
    # combine subsequent lines when the line ends in \
    _all_lines = ascii_content.replace("\\\n", "").splitlines()
    _len_all_lines = len(_all_lines)
    _count = 0


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
    global _count
    _read_aedt_file(filename)
    main_dict = {}
    # load the aedt file
    while _count < _len_all_lines:
        line = _all_lines[_count]
        m = _begin_search.search(line)
        if m:
            _walk_through_structure(m.group(1), main_dict)
        _count += 1
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
    _read_aedt_file(filename)
    # load the aedt file
    main_dict = {}
    _walk_through_structure(keyword, main_dict)
    return main_dict
