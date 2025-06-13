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

import numpy as np
import scipy.interpolate

from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler


class CoordinateSystem:
    def __init__(self, actor):
        """Initialize CoordinateSystem instance."""
        # Internal property

        # Perceive EM API
        self._actor = actor
        self._app = actor._app
        self._api = self._app.api
        self._rss = self._app.radar_sensor_scenario

        # Coordinate system properties
        self._time = 0

        # Private properties
        self.__rotation = np.eye(3)
        self.__position = np.zeros(3)
        self.__linear_velocity = np.zeros(3)
        self.__angular_velocity = np.zeros(3)
        self.__transformation_matrix = np.eye(4)

        # Public properties
        self.transforms = None
        self.velocity_estimator = None

    @property
    def rotation(self):
        return np.array(self.__rotation)

    @rotation.setter
    def rotation(self, value):
        self.__rotation = value

    @property
    def position(self):
        return np.array(self.__position)

    @position.setter
    def position(self, value):
        self.__position = value

    @property
    def linear_velocity(self):
        return np.array(self.__linear_velocity)

    @linear_velocity.setter
    def linear_velocity(self, value):
        self.__linear_velocity = value

    @property
    def angular_velocity(self):
        return np.array(self.__angular_velocity)

    @angular_velocity.setter
    def angular_velocity(self, value):
        self.__angular_velocity = value

    @property
    @perceive_em_function_handler
    def transformation_matrix(self):
        self.update()
        (ret, rot, pos, lin, ang) = self._app.api.coordSysInGlobal(self._actor.scene_node)
        self.__transformation_matrix = np.concatenate((np.asarray(rot), np.asarray(pos).reshape((-1, 1))), axis=1)
        self.__transformation_matrix = np.concatenate((self.__transformation_matrix, np.array([[0, 0, 0, 1]])), axis=0)
        return self.__transformation_matrix

    @transformation_matrix.setter
    def transformation_matrix(self, value):
        self.__position = value[0:3, 3]
        self.__rotation = value[0:3, 0:3]
        self.update()

    @perceive_em_function_handler
    def update(self, time=None):
        if time is not None:
            self._update_with_transforms(time)

        if self._actor.parent_node is None:
            self._app.api.setCoordSysInGlobal(
                self._actor.scene_node,
                np.ascontiguousarray(self.rotation, dtype=np.float64),
                np.ascontiguousarray(self.position, dtype=np.float64),
                np.ascontiguousarray(self.linear_velocity, dtype=np.float64),
                np.ascontiguousarray(self.angular_velocity, dtype=np.float64),
            )
        else:
            self._app.api.setCoordSysInParent(
                self._actor.scene_node,
                np.ascontiguousarray(self.rotation, dtype=np.float64),
                np.ascontiguousarray(self.position, dtype=np.float64),
                np.ascontiguousarray(self.linear_velocity, dtype=np.float64),
                np.ascontiguousarray(self.angular_velocity, dtype=np.float64),
            )

    @perceive_em_function_handler
    def _update_with_transforms(self, time=0):
        dt = time - self._time

        self._time = time

        if self.transforms is not None and time is not None:
            temp_transform = self.transforms(np.mod(time, self.transforms.x[-1]))  # account for limited time animations
            self.position = temp_transform[0:3, 3]
            self.rotation = temp_transform[0:3, 0:3]

        temp_pos = self.position

        if self.velocity_estimator is None or dt <= 0:
            self.velocity_estimator = self._app.radar_sensor_scenario.VelocityEstimate()
            self.velocity_estimator.setApproximationOrder(3)  # order of estimate, 3 seems to work best
        ret = self.velocity_estimator.push(
            time,
            np.ascontiguousarray(self.rotation, dtype=np.float64),
            np.ascontiguousarray(temp_pos, dtype=np.float64),
        )
        if not ret:
            raise RuntimeError("Error pushing velocity estimate")

        (_, self.linear_velocity, self.angular_velocity) = self.velocity_estimator.get()
