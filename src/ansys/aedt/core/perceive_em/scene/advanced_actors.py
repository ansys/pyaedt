# ruff: noqa: E402

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

from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.quaternion import Quaternion
from ansys.aedt.core.perceive_em.scene.actors import Actor


class Bird(Actor, object):
    """Provides an instance of a bird."""

    def __init__(self, input_file, app, parent_node=None, name=None):
        """Bird class."""

        if name is None:
            name = generate_unique_name("bird")

        super(Bird, self).__init__(app, parent_node, name)

        # Actor properties
        self.actor_type = "bird"

        # Bird properties
        self.velocity_mag = None
        self.flap_range = 45
        self.flap_freq = 3

        # Movement
        self.time = 0.0
        self.use_linear_velocity_equation_update = True

        self.__configuration_file = Path(input_file)
        self.__input_dir = self.configuration_file.parent

        self.add_parts_from_json(self.configuration_file)

    @property
    def configuration_file(self):
        return self.__configuration_file

    @property
    def input_dir(self):
        return self.__input_dir

    def update(self, time=0):
        if time is not None:
            delta_time = time - self.time
        else:
            delta_time = 0.0

        self.time = time

        if self.use_linear_velocity_equation_update:
            new_pos = self.coordinate_system.pos + delta_time * self.coordinate_system.lin
            self.coordinate_system.pos = new_pos
            self.coordinate_system.update()
        else:
            self.coordinate_system.update(time=self.time)

        for part in self.parts:
            self._recurse_parts(part, self.parts[part], self.time)

        # print a warning message to let users know that the velocity is being updated based on the linear velocity
        # equation it isn't always clear if the user wants to do this or not, so a warning message is printed so they
        # are aware
        if self.time == 0:
            if self.use_linear_velocity_equation_update:
                self._app.logger.info(f"Using Linear Velocity Equation for Position Update for Actor: {self.name}")

    def _recurse_parts(self, part_name, part, time):
        if "lwing" in part_name:
            phi = 0
            theta = np.radians(self.flap_range * np.cos(2 * np.pi * time / self.flap_freq))
            psi = 0

            quaternions = Quaternion.from_euler([phi, theta, psi], sequence="zxz", extrinsic=False)

            part.coordinate_system.rot = quaternions.to_rotation_matrix()
            part.coordinate_system.ang = [self.flap_range * np.sin(np.pi * time * self.flap_freq), 0, 0]

        elif "rwing" in part_name:
            phi = 0
            theta = np.radians(-self.flap_range * np.cos(2 * np.pi * time / self.flap_freq))
            psi = 0

            quaternions = Quaternion.from_euler([phi, theta, psi], sequence="zxz", extrinsic=False)

            part.coordinate_system.rot = quaternions.to_rotation_matrix()
            part.coordinate_system.ang = [-self.flap_range * np.sin(np.pi * time * self.flap_freq), 0, 0]

        part.coordinate_system.update()

        for child in part.parts:
            recurse_parts(child, part.parts[child], time)
