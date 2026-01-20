# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from __future__ import annotations

import inspect


class DirMixin:
    """Mixin that adds a `.public_dir` property as a shorthand for the built-in `dir()` function.

    This is primarily intended to make interactive exploration and autocomplete faster.
    Instead of typing `dir(obj)`, you can type `obj.public_dir`.

    Examples
    --------
    Create a simple class with the mixin:

    >>> from ansys.aedt.core.base import DirMixin
    >>> class Example(DirMixin):
    ...     def __init__(self):
    ...         self.public_var = 42
    ...         self._private_var = "hidden"
    ...
    ...     def public_method(self):
    ...         return "visible"
    ...
    ...     def _private_method(self):
    ...         return "internal"
    >>> e = Example()
    >>> e.public_dir  # Returns only public, non-deprecated attributes
    ['public_method', 'public_var']

    Compare with standard dir():

    >>> e = Example()
    >>> public_attrs = [a for a in dir(e) if not a.startswith("_")]
    >>> # public_dir is cleaner and excludes internal attributes
    >>> sorted(e.public_dir) == sorted(public_attrs[:-1])  # Excludes 'public_dir' itself
    True

    Use in an interactive session for exploration:

    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> # Instead of dir(hfss), use:
    >>> available_methods = hfss.public_dir
    >>> # This gives you a clean list of public API methods and properties

    """

    def __dir__(self) -> list[str]:
        """Return a list of attributes for this object.

        Public attributes are listed first, followed by private attributes (starting with '_').

        Returns
        -------
        list of str
            List of attribute names, with public attributes first.

        Examples
        --------
        >>> from ansys.aedt.core.base import DirMixin
        >>> class MyClass(DirMixin):
        ...     def __init__(self):
        ...         self.value = 1
        ...         self._internal = 2
        >>> obj = MyClass()
        >>> attrs = dir(obj)
        >>> # Public attributes come first, private attributes at the end
        >>> attrs[0].startswith("_")
        False
        >>> attrs[-1].startswith("_")
        True

        """
        # Get default attribute list, there is a fallback for Python 2 or weird metaclasses
        attrs = super().__dir__() if hasattr(super(), "__dir__") else dir(type(self))
        # Split public vs private
        private = sorted([a for a in attrs if a.startswith("_")], key=lambda x: x.lower())
        public = sorted([a for a in attrs if not a.startswith("_")], key=lambda x: x.lower())
        # Return public first, private at the end
        return public + private

    @property
    def public_dir(self) -> list[str]:
        """Shortcut for dir(self) that excludes private and deprecated attributes.

        Returns
        -------
        list of str
            List of public, non-deprecated attribute names.

        Examples
        --------
        Get only public attributes:

        >>> from ansys.aedt.core.base import DirMixin
        >>> class MyAPI(DirMixin):
        ...     def __init__(self):
        ...         self.setting = "value"
        ...         self._cache = {}
        ...
        ...     def configure(self):
        ...         '''Configure the API'''
        ...         pass
        ...
        ...     def _internal_setup(self):
        ...         '''Internal method'''
        ...         pass
        >>> api = MyAPI()
        >>> api.public_dir
        ['configure', 'setting']

        Filter out deprecated methods:

        >>> class APIWithDeprecated(DirMixin):
        ...     def new_method(self):
        ...         '''New recommended method'''
        ...         pass
        ...
        ...     def old_method(self):
        ...         '''.. deprecated:: 1.0
        ...         Use new_method instead'''
        ...         pass
        >>> obj = APIWithDeprecated()
        >>> "old_method" in obj.public_dir
        False
        >>> "new_method" in obj.public_dir
        True

        """
        result = []
        for name in dir(self):
            if name.startswith("_") or name == "public_dir":
                continue

            # NOTE: Could be necessary to handle properties that raise exceptions, e.g. NotImplementedError
            try:
                obj = getattr(self, name)
            except (AttributeError, RuntimeError):
                continue

            doc = inspect.getdoc(obj)
            if doc and ".. deprecated::" in doc:
                continue

            result.append(name)

        return sorted(result)


class PyAedtBase(DirMixin):
    """Common base class for all PyAEDT classes.

    Inherits from `DirMixin` to provide the `.public_dir` property for quick
    interactive exploration. This class acts as a central place to
    consolidate future mixins or shared functionality.

    Notes
    -----
    - Prefer placing `PyAedtBase` at the rightmost position in multiple inheritance
      to avoid unintentionally overriding behavior from other base classes.
    - Python's method resolution order (MRO) ensures that if `PyAedtBase` is
      inherited multiple times through different paths, it will only appear
      once in the hierarchy.

    Examples
    --------
    Create a custom class inheriting from PyAedtBase:

    >>> from ansys.aedt.core.base import PyAedtBase
    >>> class MyComponent(PyAedtBase):
    ...     def __init__(self, name):
    ...         self.name = name
    ...
    ...     def process(self):
    ...         return f"Processing {self.name}"
    >>> comp = MyComponent("Component1")
    >>> str(comp)
    'Class: __main__.MyComponent'
    >>> comp.process()
    'Processing Component1'

    Use public_dir for API exploration:

    >>> comp = MyComponent("Test")
    >>> methods = comp.public_dir
    >>> "process" in methods
    True
    >>> "_private" in methods  # Private attributes are excluded
    False

    Multiple inheritance with PyAedtBase:

    >>> class Configurable:
    ...     def configure(self):
    ...         return "configured"
    >>> class MyAdvancedComponent(Configurable, PyAedtBase):
    ...     def __init__(self):
    ...         self.value = 42
    >>> adv = MyAdvancedComponent()
    >>> adv.configure()
    'configured'
    >>> # PyAedtBase methods are available
    >>> "configure" in adv.public_dir
    True

    String representation of objects:

    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()  # doctest: +SKIP
    >>> print(hfss)  # doctest: +SKIP
    Class: ansys.aedt.core.hfss.Hfss

    """

    def __repr__(self) -> str:
        """Return the string representation of the object.

        Returns
        -------
        str
            String representation showing the module and class name.

        Examples
        --------
        >>> from ansys.aedt.core.base import PyAedtBase
        >>> class MyClass(PyAedtBase):
        ...     pass
        >>> obj = MyClass()
        >>> repr(obj)
        'Class: __main__.MyClass'

        """
        return f"Class: {self.__class__.__module__}.{self.__class__.__name__}"

    def __str__(self) -> str:
        """Return the string representation of the object.

        Returns
        -------
        str
            String representation showing the module and class name.

        Examples
        --------
        >>> from ansys.aedt.core.base import PyAedtBase
        >>> class MyTool(PyAedtBase):
        ...     def __init__(self, name):
        ...         self.name = name
        >>> tool = MyTool("Analyzer")
        >>> print(tool)
        Class: __main__.MyTool
        >>> str(tool)
        'Class: __main__.MyTool'

        """
        return f"Class: {self.__class__.__module__}.{self.__class__.__name__}"
