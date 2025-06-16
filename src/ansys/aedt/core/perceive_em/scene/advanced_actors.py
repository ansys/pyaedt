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
    """
    Initialize a Bird instance.

    Parameters
    ----------
    input_file : str or Path, optional
        Path to a JSON configuration file to initialize the actor.
    app : object
        The Perceive EM application instance.
    parent_node : object
        The parent scene node to which this actor is attached.
    name : str, optional
        Name of the actor. Default is "Actor".
    """

    def __init__(self, input_file, app, parent_node=None, name=None):
        if name is None:
            name = generate_unique_name("bird")
            while name in self.actors:  # pragma: no cover
                name = generate_unique_name("bird")

        (super(Bird, self).__init__(app=app, parent_node=parent_node, name=name, input_file=input_file),)

        # Actor properties
        self.actor_type = "bird"

        # Bird properties
        self.__flap_range = 45.0
        self.__flap_frequency = 3.0

        # Movement
        self.use_linear_velocity_equation_update = True

        self.add_parts_from_json(self.configuration_file)

    @property
    def flap_range(self):
        """Bird flap range.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_bird("bird", input_data="Bird3.json")
        >>> actor.flap_range
        """
        return self.__flap_range

    @flap_range.setter
    def flap_range(self, value):
        self.__flap_range = value

    @property
    def flap_frequency(self):
        """Bird flap frequency.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_bird("bird", input_data="Bird3.json")
        >>> actor.flap_frequency
        """
        return self.__flap_frequency

    @flap_frequency.setter
    def flap_frequency(self, value):
        self.__flap_frequency = value

    def update(self, time=0.0):
        """
        Update bird parts.

        Parameters:
        ------------
        time : float, optional
            Scene time.

        Returns:
        --------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if time is not None:
            delta_time = time - self.time
        else:
            delta_time = 0.0

        self.time = time

        if self.use_linear_velocity_equation_update:
            new_pos = self.coordinate_system.position + delta_time * self.coordinate_system.linear_velocity
            self.coordinate_system.pos = new_pos
            self.coordinate_system.update()
        else:
            self.coordinate_system.update(time=self.time)

        for part in self.parts:
            self._recurse_parts(part, self.parts[part], self.time)

        # Log a warning message to let users know that the velocity is being updated based on the linear velocity
        # equation it isn't always clear if the user wants to do this or not, so a warning message is printed so they
        # are aware
        if self.time == 0:
            if self.use_linear_velocity_equation_update:
                self._logger.info(f"Using Linear Velocity Equation for Position Update for Actor: {self.name}")
        return True

    def _recurse_parts(self, part_name, part, time):
        """Update parts"""
        if "lwing" in part_name:
            phi = 0
            theta = np.radians(self.flap_range * np.cos(2 * np.pi * time / self.flap_frequency))
            psi = 0

            quaternions = Quaternion.from_euler([phi, theta, psi], sequence="zxz", extrinsic=False)

            part.coordinate_system.rot = quaternions.to_rotation_matrix()
            part.coordinate_system.ang = [self.flap_range * np.sin(np.pi * time * self.flap_frequency), 0, 0]

        elif "rwing" in part_name:
            phi = 0
            theta = np.radians(-self.flap_range * np.cos(2 * np.pi * time / self.flap_frequency))
            psi = 0

            quaternions = Quaternion.from_euler([phi, theta, psi], sequence="zxz", extrinsic=False)

            part.coordinate_system.rot = quaternions.to_rotation_matrix()
            part.coordinate_system.ang = [-self.flap_range * np.sin(np.pi * time * self.flap_frequency), 0, 0]

        part.coordinate_system.update(time)

        for child in part.parts:
            recurse_parts(child, part.parts[child], time)
