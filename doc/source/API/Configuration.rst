Configuration files
~~~~~~~~~~~~~~~~~~~
This module contains all methods to export project settings to a JSON file
and import and apply settings to a new design. Currently the configuration
cover the following apps:
* HFSS
* Q2D and Q3D Extractor
* Maxwell
* Icepak
* Mechanical

The sections covered are:

* Variables
* Mesh Operations
* Setup and Optimetrics
* Material Properties
* Object Properties
* Boundaries and Excitations

When a boundary is attached to a face, the tool tries to match it with a
FaceByPosition on the same object name on the target design. If, for any
reason, this face position has changed or the object name in the target design has changed,
the boundary fails to apply.


.. currentmodule:: pyaedt.generic.configurations

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Configurations
   ConfigurationsOptions
   ImportResults


.. code:: python

    from pyaedt import Hfss
    app = Hfss(project_name="original_project", specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    conf_file = self.aedtapp.configurations.export_config()

    app2 = Hfss(projec_name='newproject')
    app2.modeler.import_3d_cad(file_path)
    out = app2.configurations.import_config(conf_file)
    app2.configurations.results.global_import_success

    ...
