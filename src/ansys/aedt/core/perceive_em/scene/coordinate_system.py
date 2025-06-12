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


class CoordinateSystem:
    def __init__(self, actor):
        """
        Initialize a CoordSys instance.

        Parameters:
        ------------
        h_node : handle, optional
            The handle for the node.

        h_elem : handle, optional
            The handle for the element.

        parent_h_node : handle, optional
            The handle for the parent node.

        is_radar : bool, optional
            If True, the node is a radar. Defaults to False.
        """
        # Internal property
        self._actor = actor
        self._app = actor._app

        # Private properties
        self._rot = np.eye(3)
        self._pos = np.zeros(3)
        self._lin = np.zeros(3)
        self._ang = np.zeros(3)
        self._transform4x4 = np.eye(4)
        self.dt = 0
        self.time = 0
        self.transforms = None
        self.vel_estimator = None

    def _update_with_transforms(self, time=None):
        self.dt = time - self.time
        self.time = time

        if self.transforms is not None and time is not None:
            temp_transform = self.transforms(np.mod(time, self.transforms.x[-1]))  # account for limited time animations
            self._pos = temp_transform[0:3, 3]
            self._rot = temp_transform[0:3, 0:3]

        temp_pos = self._pos
        if (self.vel_estimator is None) or (self.dt <= 0):
            self.vel_estimator = self._app.radar_sensor_scenario.VelocityEstimate()
            self.vel_estimator.setApproximationOrder(3)  # order of estimate, 3 seems to work best
        ret = self.vel_estimator.push(
            time, np.ascontiguousarray(self._rot, dtype=np.float64), np.ascontiguousarray(temp_pos, dtype=np.float64)
        )
        if not ret:
            raise RuntimeError("error pushing velocity estimate")
        (_, self._lin, self._ang) = self.vel_estimator.get()

    def update(self, time=None):
        if time is not None:
            self._update_with_transforms(time)

        if self._actor.parent_node is None:
            self._app.api.setCoordSysInGlobal(
                self._actor.scene_node,
                np.ascontiguousarray(self._rot, dtype=np.float64),
                np.ascontiguousarray(self._pos, dtype=np.float64),
                np.ascontiguousarray(self._lin, dtype=np.float64),
                np.ascontiguousarray(self._ang, dtype=np.float64),
            )
        else:
            self._app.api.setCoordSysInParent(
                self._actor.scene_node,
                np.ascontiguousarray(self._rot, dtype=np.float64),
                np.ascontiguousarray(self._pos, dtype=np.float64),
                np.ascontiguousarray(self._lin, dtype=np.float64),
                np.ascontiguousarray(self._ang, dtype=np.float64),
            )

    @property
    def transform4x4(self):
        self.update()
        (ret, rot, pos, lin, ang) = self._app.api.coordSysInGlobal(self._actor.scene_node)
        self._transform4x4 = np.concatenate((np.asarray(rot), np.asarray(pos).reshape((-1, 1))), axis=1)
        self._transform4x4 = np.concatenate((self._transform4x4, np.array([[0, 0, 0, 1]])), axis=0)
        return self._transform4x4

    @transform4x4.setter
    def transform4x4(self, value):
        self._pos = value[0:3, 3]
        self._rot = value[0:3, 0:3]
        self.update()

    @property
    def pos(self):
        return np.array(self._pos)

    @pos.setter
    def pos(self, value):
        self._pos = value

    @property
    def rot(self):
        return np.array(self._rot)

    @rot.setter
    def rot(self, value):
        self._rot = value

    @property
    def lin(self):
        return np.array(self._lin)

    @lin.setter
    def lin(self, value):
        self._lin = value

    @property
    def ang(self):
        return np.array(self._ang)

    @ang.setter
    def ang(self, value):
        self._ang = value
