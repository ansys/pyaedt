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
    """
    Class to manage a coordinate system for a scene actor in the Perceive EM simulation framework.

    This class handles the position, rotation, linear and angular velocity of the associated actor,
    and provides transformation matrix access and velocity estimation over time.
    """

    def __init__(self, actor):
        """
        Initialize a CoordinateSystem instance.

        Parameters
        ----------
            actor: The scene node to which this coordinate system is attached.
        """

        # Internal property

        # Perceive EM API
        self._actor = actor
        self._app = actor._app
        self._api = self._app.api
        self._rss = self._app.radar_sensor_scenario
        self.logger = self._app.logger

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
        """Rotation matrix of the coordinate system.

        Returns
        -------
        numpy.ndarray
            A 3x3 rotation matrix representing the orientation.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.coordinate_system.rotation
        """
        return np.array(self.__rotation)

    @rotation.setter
    def rotation(self, value):
        self.__rotation = value

    @property
    def position(self):
        """Position of the coordinate system in 3D space.

        Returns
        -------
        numpy.ndarray
             A 3-element array representing the position vector.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.coordinate_system.position
        """
        return np.array(self.__position)

    @position.setter
    def position(self, value):
        self.__position = value

    @property
    def linear_velocity(self):
        """Set the linear velocity.

        Returns
        -------
        numpy.ndarray
            A 3-element array representing the new linear velocity.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.coordinate_system.linear_velocity
        """
        return np.array(self.__linear_velocity)

    @linear_velocity.setter
    def linear_velocity(self, value):
        self.__linear_velocity = value

    @property
    def angular_velocity(self):
        """Angular velocity of the coordinate system.

        Returns
        -------
        numpy.ndarray
            A 3-element array representing angular velocity in rad/s.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.coordinate_system.angular_velocity
        """
        return np.array(self.__angular_velocity)

    @angular_velocity.setter
    def angular_velocity(self, value):
        self.__angular_velocity = value

    @property
    def transformation_matrix(self):
        """Full 4x4 transformation matrix in global coordinates.

        Returns
        -------
        numpy.ndarray
            A 4x4 matrix that combines rotation and position for global transformation.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.coordinate_system.transformation_matrix
        """
        self.update()
        (_, rot, pos, _, _) = self._coordinate_system_in_global(self._actor.scene_node)
        self.__transformation_matrix = np.concatenate((np.asarray(rot), np.asarray(pos).reshape((-1, 1))), axis=1)
        self.__transformation_matrix = np.concatenate((self.__transformation_matrix, np.array([[0, 0, 0, 1]])), axis=0)
        return self.__transformation_matrix

    @transformation_matrix.setter
    def transformation_matrix(self, value):
        self.__position = value[0:3, 3]
        self.__rotation = value[0:3, 0:3]
        self.update()

    def update(self, time=None, velocity_estimator_order=3):
        """Update the coordinate system in the simulation environment.

        If the actor has no parent node, the coordinate system is updated in global coordinates.
        Otherwise, it is updated relative to its parent. If a time value is provided, and a transform
        function exists, the transformation is interpolated at that specific time.

        Parameters
        ----------
        time : float, optional
            Simulation time in seconds. If provided, updates position and rotation using the `transforms` function.
        velocity_estimator_order : int, optional
            Velocity estimator order. The default is ``3``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.coordinate_system.update(time=1.0)
        """
        if time is not None:
            self._update_with_transforms(time, velocity_estimator_order)

        return self._set_coordinate_system(
            node=self._actor.scene_node,
            rotation=np.ascontiguousarray(self.rotation, dtype=np.float64),
            position=np.ascontiguousarray(self.position, dtype=np.float64),
            linear_velocity=np.ascontiguousarray(self.linear_velocity, dtype=np.float64),
            angular_velocity=np.ascontiguousarray(self.angular_velocity, dtype=np.float64),
            parent_node=self._actor.scene_node,
        )

    def _update_with_transforms(self, time=0, velocity_estimator_order=3):
        """Internal helper to update position, rotation, and velocities using time-based transforms.

        This method calculates the delta time and uses it to push new data to a velocity estimator.
        It interpolates the transformation at the given time if `self.transforms` is available.

        Parameters
        ----------
        time : float
            Current simulation time in seconds.
        velocity_estimator_order : int, optional
            Velocity estimator order. The default is ``3``.
        """
        dt = time - self._time

        self._time = time

        if self.transforms is not None and time is not None:
            temp_transform = self.transforms(np.mod(time, self.transforms.x[-1]))  # account for limited time animations
            self.position = temp_transform[0:3, 3]
            self.rotation = temp_transform[0:3, 0:3]

        temp_pos = self.position

        if self.velocity_estimator is None or dt <= 0:
            self.velocity_estimator = self._velocity_estimate()
            self._set_approximation_order(velocity_estimator_order)

        ret = self.velocity_estimator.push(
            time,
            np.ascontiguousarray(self.rotation, dtype=np.float64),
            np.ascontiguousarray(temp_pos, dtype=np.float64),
        )
        if not ret:
            raise RuntimeError("Error pushing velocity estimate")

        _, self.linear_velocity, self.angular_velocity = self.velocity_estimator.get()

    # Internal Perceive EM API objects
    @perceive_em_function_handler
    def _coordinate_system_in_global(self, node):
        """
        Retrieve the global coordinate system properties of a scene node.

        This method calls the Perceive EM API to obtain the transformation
        and motion characteristics of a specified scene node in the global reference frame.

        Parameters
        ----------
        node : SceneNode
            The scene node to query.

        Returns
        -------
        tuple
            A tuple of five elements:
            - `ret` (int): API status code (e.g., success or failure).
            - `rot` (ndarray): 3x3 rotation matrix representing orientation in global frame.
            - `pos` (ndarray): 3-element position vector in global coordinates.
            - `lin` (ndarray): 3-element linear velocity vector.
            - `ang` (ndarray): 3-element angular velocity vector.
        """
        return self._api.coordSysInGlobal(node)

    def _set_coordinate_system(self, node, rotation, position, linear_velocity, angular_velocity, parent_node=None):
        """
        Set the global coordinate system for a scene node.

        This method assigns the transformation and motion state of a given node in the global
        coordinate system, including orientation, position, and velocities.

        Parameters
        ----------
        node : SceneNode
            The handle of the scene node to modify.
        rotation : array-like
            A 3x3 rotation matrix representing the node's orientation in the global frame.
        position : array-like
            A 3-element vector specifying the node's global position.
        linear_velocity : array-like
            A 3-element vector representing the node's linear velocity in global coordinates.
        angular_velocity : array-like
            A 3-element vector representing the node's angular velocity in global coordinates.
        parent_node : SceneNode
            Parent scene node.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if parent_node is None:
            return self._set_coordinate_system_in_global(node, rotation, position, linear_velocity, angular_velocity)
        else:
            return self._set_coordinate_system_in_parent(node, rotation, position, linear_velocity, angular_velocity)

    @perceive_em_function_handler
    def _set_coordinate_system_in_global(self, node, rotation, position, linear_velocity, angular_velocity):
        """
        Set the global coordinate system for a scene node.

        This method assigns the transformation and motion state of a given node in the global
        coordinate system, including orientation, position, and velocities.

        Parameters
        ----------
        node : int or SceneNode
            The identifier or handle of the scene node to modify.
        rotation : array-like
            A 3x3 rotation matrix representing the node's orientation in the global frame.
        position : array-like
            A 3-element vector specifying the node's global position.
        linear_velocity : array-like
            A 3-element vector representing the node's linear velocity in global coordinates.
        angular_velocity : array-like
            A 3-element vector representing the node's angular velocity in global coordinates.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self._api.setCoordSysInGlobal(
            node,
            rotation,
            position,
            linear_velocity,
            angular_velocity,
        )
        return True

    @perceive_em_function_handler
    def _set_coordinate_system_in_parent(self, node, rotation, position, linear_velocity, angular_velocity):
        """
        Set the global coordinate system for a scene node.

        This method assigns the transformation and motion state of a given node in the global
        coordinate system, including orientation, position, and velocities.

        Parameters
        ----------
        node : int or SceneNode
            The identifier or handle of the scene node to modify.
        rotation : array-like
            A 3x3 rotation matrix representing the node's orientation in the global frame.
        position : array-like
            A 3-element vector specifying the node's global position.
        linear_velocity : array-like
            A 3-element vector representing the node's linear velocity in global coordinates.
        angular_velocity : array-like
            A 3-element vector representing the node's angular velocity in global coordinates.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        return self._api.setCoordSysInParent(
            node,
            rotation,
            position,
            linear_velocity,
            angular_velocity,
        )

    @perceive_em_function_handler
    def _velocity_estimate(self):
        """
        Get VelocityEstimate object from Perceive EM API.

        Returns
        -------
        VelocityEstimate

        """
        return self._rss.VelocityEstimate()

    @perceive_em_function_handler
    def _set_approximation_order(self, order):
        """
        Set approximation order of VelocityEstimator object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.velocity_estimator is not None:
            return self.velocity_estimator.setApproximationOrder(order)
        self.logger.info("Velocity estimator not set.")
        return False
