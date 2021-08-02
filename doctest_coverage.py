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

    Should work for ``pyvista`` as entry, but no promises for its more
    general applicability.

    Parameters
    ----------
    entry : module, optional
        The entry point of the submodule search. Defaults to the main
        ``pyvista`` module.

    recurse : bool, optional
        Whether to recurse into submodules.

    Returns
    -------
    modules : dict of modules
        A (module name -> module) mapping of submodules under ``entry``.

    """

    entry_name = entry.__name__
    found_modules = {}
    next_entries = {entry}
    while next_entries:
        next_modules = {}
        for entry in next_entries:
            for attr_short_name in dir(entry):
                attr = getattr(entry, attr_short_name)
                if not isinstance(attr, ModuleType):
                    continue

                module_name = attr.__name__

                if module_name.startswith(entry_name):
                    next_modules[module_name] = attr

        if not recurse:
            return next_modules
        # find as-of-yet-undiscovered submodules
        next_entries = {
            module
            for module_name, module in next_modules.items()
            if module_name not in found_modules

        }
        for k in list(next_modules.keys()):
            if next_modules[k].__file__.endswith("__init__.py"):
                del next_modules[k]
        found_modules.update(next_modules)

    return found_modules

def check_doctests(modules=None):
    """Check whether doctests can be run as-is without errors.

    Parameters
    ----------
    modules : dict, optional
        (module name -> module) mapping of submodules defined in a
        package as returned by ``discover_modules()``. If omitted,
        ``discover_modules()`` will be called for ``pyvista``.

    respect_skips : bool, optional
        Whether to ignore doctest examples that contain a DOCTEST:+SKIP
        directive.

    verbose : bool, optional
        Whether to print passes/failures as the testing progresses.
        Failures are printed at the end in every case.

    Returns
    -------
    failures : dict of (Exception, str)  tuples
        An (object name -> (exception raised, failing code)) mapping
        of failed doctests under the specified modules.

    """

    if modules is None:
        modules = discover_modules()

    # find and parse all docstrings; this will also remove any duplicates
    doctests = {}
    for module_name, module in modules.items():
        doctests[module_name] = {
            dt.name: dt
            for dt in DocTestFinder(recurse=True).find(module, globs={})
            }

    print ("Name                                      Methods     Miss     Cover")
    print ('-' * 79)


    # loop over doctests in alphabetical order for sanity
    sorted_modules = sorted(doctests)
    for module_name in sorted_modules:
        methods_with_example = []
        methods_without_example = []

        for dt_name in doctests[module_name]:
            if not doctests[module_name][dt_name].examples:
                methods_without_example.append(dt_name)
            else:
                methods_with_example.append(dt_name)

        total = len(doctests[module_name])
        missing = len(methods_without_example)
        covered = total - missing
        if total!=0:
            percentage_covered = covered/total*100
        else:
            percentage_covered = 100

        print(f'{module_name : <37}       {total : ^5}       {missing : ^5}    {percentage_covered}')

        # # mock print to suppress output from a few talkative tests
        # globs = {'print': (lambda *args, **kwargs: ...)}
        # for iline, example in enumerate(dt.examples, start=1):
        #     if (not example.source.strip()
        #             or (respect_skips and skip_pattern.search(example.source))):
        #         continue
        #     try:
        #         exec(example.source, globs)
        #     except Exception as exc:
        #         if verbose:
        #             print(f'FAILED: {dt.name} -- {repr(exc)}')
        #         erroring_code = ''.join([
        #             example.source
        #             for example in dt.examples[:iline]
        #         ])
        #         failures[dt_name] = exc, erroring_code
        #         break
        # else:
        #     if verbose:
        #         print(f'PASSED: {dt.name}')

    # print(f'\n{passes} passes and {fails} failures '
    #       f'out of {total} total doctests.\n')
    # if not fails:
    #     return failures

    # print('List of failures:')
    # for name, (exc, erroring_code) in failures.items():
    #     print('-' * 60)
    #     print(f'{name}:')
    #     print(indent(erroring_code, '    '))
    #     print(repr(exc))
    # print('-' * 60)

    # return failures


if __name__ == "__main__":
    check_doctests()
