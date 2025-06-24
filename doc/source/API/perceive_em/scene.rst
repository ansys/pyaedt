Scene
=====

The scene manages all components in a radar simulation scene, including actors and antenna platforms.


.. currentmodule:: ansys.aedt.core.perceive_em.scene.scene_root

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   SceneManager


Examples
--------
>>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
>>> perceive_em = PerceiveEM()
>>> scene_manager = perceive_em.scene


Perceive EM Simulation is defined using the concept of building a scene tree.

The tree is defined through a parent and child relationship of nodes, and properties assigned to each node.
There are two types of nodes: generic and radar nodes.


.. image:: ../_static/perceive_em_workflow.png
  :width: 800
  :alt: Perceive EM scene
