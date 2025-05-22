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

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.internal.errors import GrpcApiError
from ansys.aedt.core.modules.boundary.common import BoundaryObject


class CreateBoundaryMixin:
    """Mixin that provides methods to apply boundary conditions.

    This mixin is designed to be used in classes that require boundary condition.
    Methods provided by this mixin should be implemented or extended by subclasses
    to define specific boundary condition behaviors.

    Example
    -------
    A class can use the default behavior or use a custom implementation.

    >>> class MyClass(CreateBoundaryMixin):
    >>>     def _create_boundary(self):
    >>> # Use default behavior
    >>>         if boundary_type not in ("SpecificString"):
    >>>             return super()._create_boundary(name, props, boundary_type)
    >>> # Custom implementation to create boundary conditions
    >>>         else:
    >>>             pass
    """

    @pyaedt_function_handler()
    def _create_boundary(self, name, props, boundary_type):
        """Create a boundary.

        Parameters
        ----------
        name : str
            Name of the boundary.
        props : list or dict
            List of properties for the boundary.
        boundary_type :
            Type of the boundary.

        Returns
        -------
        :class:`ansys.aedt.core.modules.boundary.common.BoundaryObject`
            Boundary object.

        """
        try:
            bound = BoundaryObject(self, name, props, boundary_type)
            if not bound.create():
                raise AEDTRuntimeError(f"Failed to create boundary {boundary_type} {name}")

            self._boundaries[bound.name] = bound
            self.logger.info(f"Boundary {boundary_type} {name} has been created.")
            return bound
        except GrpcApiError as e:
            raise AEDTRuntimeError(f"Failed to create boundary {boundary_type} {name}") from e
