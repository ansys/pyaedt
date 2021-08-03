import re
import sys
from doctest import DocTestFinder
from types import ModuleType
from textwrap import indent
from argparse import ArgumentParser

import pyaedt
import pdb

def discover_modules(entry=pyaedt, recurse=True):
    """Discover the submodules present under an entry point.

    If ``recurse=True``, search goes all the way into descendants of the
    entry point. Only modules are gathered, because within a module
    ``doctest``'s discovery can work recursively.

    Should work for ``pyaedt`` as entry, but no promises for its more
    general applicability.

    Parameters
    ----------
    entry : module, optional
        The entry point of the submodule search. Defaults to the main
        ``pyaedt`` module.

    recurse : bool, optional
        Whether to recurse into submodules.

    Returns
    -------
    modules : dict of modules
        A (module name -> module) mapping of submodules under ``entry``.

    """

    entry_name = entry.__name__
    found_modules = {}
    next_entries = [entry]
    while next_entries:
        next_modules = {}
        for entry in next_entries:
            for attribute in dir(entry):
                attribute_value = getattr(entry, attribute)
                if not isinstance(attribute_value, ModuleType):
                    continue

                module_name = attribute_value.__name__

                if module_name.startswith(entry_name):
                    next_modules[module_name] = attribute_value

        # find as-of-yet-undiscovered submodules
        next_entries = [
            module
            for module_name, module in next_modules.items()
            if module_name not in found_modules
        ]

        found_modules.update(next_modules)

        if not recurse:
            break

    # Remove the name package folders from the 'found_modules' dicationary.
    for key in list(found_modules.keys()):
        if found_modules[key].__file__.endswith("__init__.py"):
            del found_modules[key]

    return found_modules

def evaluate_examples_coverage(modules=None):
    """Check whether doctests can be run as-is without errors.

    Parameters
    ----------
    modules : dict, optional
        (module name -> module) mapping of submodules defined in a
        package as returned by ``discover_modules()``. If omitted,
        ``discover_modules()`` will be called for ``pyaedt``.

    """

    if modules is None:
        modules = discover_modules()

    # find and parse all docstrings; this will also remove any duplicates
    doctests = {}
    for module_name, module in modules.items():
        doctests[module_name] = {
            doctest.name: doctest
            for doctest in DocTestFinder(recurse=True).find(module, globs={})
            }

    print ("Name                                      Methods     Miss     Cover")
    print ('-' * 79)

    # loop over doctests in alphabetical order for sanity
    sorted_module_names = sorted(doctests)
    all_methods_with_example = []
    all_methods_without_example = []
    for module_name in sorted_module_names:
        methods_with_example = []
        methods_without_example = []

        for dt_name in doctests[module_name]:
            # private methods should not be considered.
            if (not doctests[module_name][dt_name].examples) & (not dt_name.startswith("_")):
                all_methods_without_example.append(dt_name)
                methods_without_example.append(dt_name)
            else:
                methods_with_example.append(dt_name)
                all_methods_with_example.append(dt_name)

        total = len(doctests[module_name])
        missing = len(methods_without_example)
        covered = total - missing
        if total!=0:
            percentage_covered = covered/total*100
        else:
            # If no docstring is found in the module, coverage is considered to be 100%.
            percentage_covered = 100

        print(f'{module_name : <37}{total : ^19}{missing : ^4}{percentage_covered:8.2f}')

    # Get the stats for the entire package
    package_total = len(all_methods_with_example) + len(all_methods_without_example)
    package_missing = len(all_methods_without_example)
    package_percentage_covered = (package_total - package_missing) / package_total * 100
    print ('-' * 79)
    print(f'{"Total" : <37}{package_total : ^19}{package_missing : ^4}{package_percentage_covered:8.2f}')


if __name__ == "__main__":
    evaluate_examples_coverage()
