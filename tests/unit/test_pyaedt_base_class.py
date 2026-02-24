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

from ansys.aedt.core.base import PyAedtBase


# Sample hierarchy for chaining
class Vertex(PyAedtBase):
    def position(self) -> None:
        pass


class Edge(PyAedtBase):
    def vertices(self):
        return Vertex()


class Face(PyAedtBase):
    def edges(self):
        return Edge()


class Cube(PyAedtBase):
    def faces(self):
        return Face()


# Example classes for testing
class Base(PyAedtBase):
    def base_method(self) -> None:
        pass

    def _base_private(self) -> None:
        pass


class Child(Base):
    def child_method(self) -> None:
        pass

    def _child_private(self) -> None:
        pass


# ---------------------------
# UNIT TESTS
# ---------------------------

# tests for public_dir method and DirMixin functionality


def test_instance_dir_contains_methods() -> None:
    cube = Cube()
    d = cube.public_dir
    assert "faces" in d
    assert all(not i.startswith("_") for i in d)
    assert "public_dir" not in d  # exclude the property itself


def test_chaining_dir() -> None:
    cube = Cube()
    vertex_dir = cube.faces().edges().vertices().public_dir
    assert "position" in vertex_dir
    assert all(not i.startswith("_") for i in vertex_dir)


def test_base_inheritance() -> None:
    assert issubclass(Cube, PyAedtBase)
    cube = Cube()
    assert isinstance(cube, PyAedtBase)


def test_dir_sorted() -> None:
    cube = Cube()
    d = cube.public_dir
    assert d == sorted(d)


# tests for __dir__ method and DirMixin functionality


def test_dir_includes_all_attributes() -> None:
    """Ensure __dir__ returns all attributes, not just reordered subset."""
    c = Child()
    default_attrs = object.__dir__(c)
    custom_attrs = c.__dir__()

    # The sets should be identical — only order changes
    assert set(default_attrs) <= set(custom_attrs)
    # There must be at least one public and one private
    assert any(not a.startswith("_") for a in custom_attrs)
    assert any(a.startswith("_") for a in custom_attrs)


def test_dir_orders_public_first() -> None:
    """Public attributes should appear before private ones."""
    c = Child()
    attrs = c.__dir__()
    # Find the first private index
    first_private = next(i for i, a in enumerate(attrs) if a.startswith("_"))
    # Ensure no public names appear after a private
    assert all(a.startswith("_") for a in attrs[first_private:])


def test_dir_preserves_methods_from_parents() -> None:
    """Inherited public and private methods should appear."""
    c = Child()
    attrs = c.__dir__()
    assert "base_method" in attrs
    assert "_base_private" in attrs
    assert "child_method" in attrs
    assert "_child_private" in attrs


def test_dir_is_sorted_within_groups() -> None:
    """Public and private groups should each be alphabetically ordered."""
    c = Child()
    attrs = c.__dir__()
    public = [a for a in attrs if not a.startswith("_")]
    private = [a for a in attrs if a.startswith("_")]
    assert public == sorted(public)
    assert private == sorted(private)


def test_public_dir_with_deprecated_method() -> None:
    """Test that deprecated methods are excluded from public_dir."""

    class VertexWithDeprecatedMethod(PyAedtBase):
        def position(self) -> None:
            """Method that is not deprecated."""

        def position_deprecated(self) -> None:
            """Method that is deprecated.

            .. deprecated:: X.Y.Z
                This method is deprecated. Use something else instead.
            """
            pass

    vertex = VertexWithDeprecatedMethod()

    assert "position_deprecated" not in vertex.public_dir
    assert "position" in vertex.public_dir
    assert "position_deprecated" in dir(vertex)
