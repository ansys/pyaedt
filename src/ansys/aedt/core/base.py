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


import inspect


class DirMixin:
    """
    Mixin that adds a `.public_dir` property as a shorthand for the built-in `dir()` function.

    This is primarily intended to make interactive exploration and autocomplete faster.
    Instead of typing `dir(obj)`, you can type `obj.public_dir`.

    Example
    -------
    >>> class Example(DirMixin):
    ...     def foo(self):
    ...         pass
    >>> e = Example()
    >>> e.public_dir  # same as dir(e)
    """

    def __dir__(self):
        # Get default attribute list, there is a fallback for Python 2 or weird metaclasses
        attrs = super().__dir__() if hasattr(super(), "__dir__") else dir(type(self))
        # Split public vs private
        private = sorted((a for a in attrs if a.startswith("_")), key=str.lower)
        public = sorted((a for a in attrs if not a.startswith("_")), key=str.lower)
        # Return public first, private at the end
        return public + private

    @property
    def public_dir(self):
        """Shortcut for dir(self)."""
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
    """
    Common base class for all PyAEDT classes.

    Inherits from `DirMixin` to provide the `.public_dir` property for quick
    interactive exploration. This class acts as a central place to
    consolidate future mixins or shared functionality.

    Notes
    -----
    - Prefer placing `Base` at the rightmost position in multiple inheritance
      to avoid unintentionally overriding behavior from other base classes.
    - Python's method resolution order (MRO) ensures that if `Base` is
      inherited multiple times through different paths, it will only appear
      once in the hierarchy.
    """

    pass
