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

from ansys.aedt.core.base import PyAedtBase


# Sample hierarchy for chaining
class Vertex(PyAedtBase):
    def position(self):
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


# ---------------------------
# UNIT TESTS
# ---------------------------


def test_instance_dir_contains_methods():
    cube = Cube()
    d = cube.dir
    assert "faces" in d
    assert all(not i.startswith("_") for i in d)
    assert "dir" not in d  # exclude the property itself


def test_chaining_dir():
    cube = Cube()
    vertex_dir = cube.faces().edges().vertices().dir
    assert "position" in vertex_dir
    assert all(not i.startswith("_") for i in vertex_dir)


def test_base_inheritance():
    assert issubclass(Cube, PyAedtBase)
    cube = Cube()
    assert isinstance(cube, PyAedtBase)


def test_dir_sorted():
    cube = Cube()
    d = cube.dir
    assert d == sorted(d)
