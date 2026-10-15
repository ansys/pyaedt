# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Tests for placement of generated Sphinx deprecation directives."""

import sys

import pytest

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

from ansys.aedt.core.internal.checks import deprecated_doc


class DeprecationExample:
    """Demonstrate deprecation notices on methods and properties.

    This artificial class exists only to preview documentation rendering.
    """

    def current_method(self, value: int = 1) -> int:
        """Return a value without a deprecation notice.

        Parameters
        ----------
        value : int, optional
            Value to return. The default is ``1``.

        Returns
        -------
        int
            Unchanged input value.
        """
        return value

    @deprecated_doc(version="1.10")
    @deprecated("Use current_method() instead. This example will be removed in 2.0.")
    def old_method(self, value: int = 1) -> int:
        """Return a value through the deprecated method.

        This extended description should appear after the generated deprecation
        notice and before the parameter documentation.

        Parameters
        ----------
        value : int, optional
            Value to return. The default is ``1``.

        Returns
        -------
        int
            Unchanged input value.

        Examples
        --------
        Use the replacement method:

        >>> example = DeprecationExample()
        >>> example.current_method(42)
        42
        """
        return self.current_method(value)

    @property
    @deprecated_doc(version="1.10")
    @deprecated("Use current_method() instead.")
    def old_value(self) -> int:
        """Default value exposed through a deprecated property.

        This description should appear below the generated notice.

        Returns
        -------
        int
            Default example value.
        """
        return self.current_method()


def test_example_method_docstring():
    expected = """Return a value through the deprecated method.

.. deprecated:: 1.10
   Use current_method() instead. This example will be removed in 2.0.

This extended description should appear after the generated deprecation
notice and before the parameter documentation.

Parameters
----------
value : int, optional
    Value to return. The default is ``1``.

Returns
-------
int
    Unchanged input value.

Examples
--------
Use the replacement method:

>>> example = DeprecationExample()
>>> example.current_method(42)
42"""

    assert DeprecationExample.old_method.__doc__ == expected


def test_example_property_docstring():
    expected = """Default value exposed through a deprecated property.

.. deprecated:: 1.10
   Use current_method() instead.

This description should appear below the generated notice.

Returns
-------
int
    Default example value."""

    assert DeprecationExample.old_value.__doc__ == expected


def test_multiline_message_without_version():
    @deprecated_doc()
    @deprecated("Use new(). See the migration guide.", category=None)
    def old():
        """Summary."""

    assert old.__doc__ == ("Summary.\n\n.. deprecated:: \n   Use new(). See the migration guide.")


def test_requires_deprecated_marker():
    with pytest.raises(ValueError, match="Apply deprecated_doc above the standard @deprecated decorator."):
        deprecated_doc()(lambda: None)
