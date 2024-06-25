=============
API reference
=============

This section describes PyAEDT core classes, methods, and functions
for AEDT apps and modules. Use the search feature or click links
to view API documentation.
The Ansys Electronics Desktop (AEDT) is a platform that enables true electronics system design.
`AEDT <https://www.ansys.com/products/electronics>`_ provides access to the Ansys gold-standard
electro-magnetics simulation solutions such as Ansys HFSS,
Ansys Maxwell, Ansys Q3D Extractor, Ansys Siwave, and Ansys Icepak using electrical CAD (ECAD) and
Mechanical CAD (MCAD) workflows.
In addition, it includes direct links to the complete Ansys portfolio of thermal, fluid,
and Mechanical solvers for comprehensive multiphysics analysis.
Tight integration among these solutions provides unprecedented ease of use for setup and
faster resolution of complex simulations for design and optimization.

.. image:: ../Resources/aedt_2.png
  :width: 800
  :alt: AEDT Applications
  :target: https://www.ansys.com/products/electronics

The PyAEDT API includes classes for apps and modules. You must initialize the
PyAEDT app to get access to all modules and methods. Available apps are:

- `HFSS <https://www.ansys.com/products/electronics/ansys-hfss>`_
- `HFSS 3D Layout <https://www.ansys.com/products/electronics/ansys-hfss>`_
- `Maxwell 3D <https://www.ansys.com/products/electronics/ansys-maxwell>`_
- `Maxwell 2D <https://www.ansys.com/products/electronics/ansys-maxwell>`_
- `Maxwell Circuit <https://www.ansys.com/products/electronics/ansys-maxwell>`_
- `Q3D <https://www.ansys.com/products/electronics/ansys-q3d-extractor>`_
- `Q2D Extractor <https://www.ansys.com/products/electronics/ansys-q3d-extractor>`_
- `Icepak <https://www.ansys.com/products/electronics>`_
- `Mechanical <https://www.ansys.com/products/structures/ansys-mechanical>`_
- RMXprt
- EMIT
- Circuit
- `TwinBuilder <https://www.ansys.com/products/digital-twin/ansys-twin-builder>`_

All other classes and methods are inherited into the app class.
The desktop app is implicitly launched in any of the other applications.
Before accessing a PyAEDT app, the desktop app has to be launched and initialized.
The desktop app can be explicitly or implicitly initialized as shown in the following examples.

Example with ``Desktop`` class explicit initialization:

.. code:: python

    from pyaedt import launch_desktop, Circuit
    d = launch_desktop(specified_version="2023.1",
                       non_graphical=False,
                       new_desktop_session=True,
                       close_on_exit=True,
                       student_version=False):
     circuit = Circuit()
     ...
     # Any error here should be caught by the desktop app.
     ...
     d.release_desktop()

Example with ``Desktop`` class implicit initialization:

.. code:: python

    from pyaedt import Circuit
    circuit = Circuit(specified_version="2023.1",
                      non_graphical=False,
                      new_desktop_session=True,
                      close_on_exit=True,
                      student_version=False):
     circuit = Circuit()
     ...
     # Any error here should be caught by the desktop app.
     ...
     circuit.release_desktop()


.. .. toctree::
..    :maxdepth: 2

..    Application
..    MaterialManagement
..    Primitives3D
..    Primitives2D
..    Primitive_Objects
..    Primitives3DLayout
..    PrimitivesCircuit
..    Boundaries
..    Mesh
..    Setup
..    Post
..    DesktopMessenger
..    Optimetrics
..    Variables
..    Constants
..    Configuration
..    SetupTemplates
..    CableModeling
.. toctree::
   :titlesonly:
   :maxdepth: 3

   <span class="nf nf-md-package"></span> pyaedt.misc.misc</api/pyaedt/misc/misc/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.pdf</api/pyaedt/generic/pdf/index>
   <span class="nf nf-md-package"></span> pyaedt.modeler.cad</api/pyaedt/modeler/cad/index>
   <span class="nf nf-md-package"></span> pyaedt.modeler.pcb</api/pyaedt/modeler/pcb/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.plot</api/pyaedt/generic/plot/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.Mesh</api/pyaedt/modules/Mesh/index>
   <span class="nf nf-md-package"></span> pyaedt.sbrplus.plot</api/pyaedt/sbrplus/plot/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.q2d</api/pyaedt/workflows/q2d/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.q3d</api/pyaedt/workflows/q3d/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.spisim</api/pyaedt/generic/spisim/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.misc</api/pyaedt/workflows/misc/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.emit</api/pyaedt/workflows/emit/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.hfss</api/pyaedt/workflows/hfss/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.settings</api/pyaedt/generic/settings/index>
   <span class="nf nf-md-package"></span> pyaedt.modeler.circuits</api/pyaedt/modeler/circuits/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.Boundary</api/pyaedt/modules/Boundary/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.Material</api/pyaedt/modules/Material/index>
   <span class="nf nf-md-package"></span> pyaedt.rpc.local_server</api/pyaedt/rpc/local_server/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.icepak</api/pyaedt/workflows/icepak/index>
   <span class="nf nf-md-package"></span> pyaedt.emit_core.results</api/pyaedt/emit_core/results/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.constants</api/pyaedt/generic/constants/index>
   <span class="nf nf-md-package"></span> pyaedt.modeler.modeler2d</api/pyaedt/modeler/modeler2d/index>
   <span class="nf nf-md-package"></span> pyaedt.modeler.modeler3d</api/pyaedt/modeler/modeler3d/index>
   <span class="nf nf-md-package"></span> pyaedt.modeler.schematic</api/pyaedt/modeler/schematic/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.solutions</api/pyaedt/modules/solutions/index>
   <span class="nf nf-md-package"></span> pyaedt.rpc.rpyc_services</api/pyaedt/rpc/rpyc_services/index>
   <span class="nf nf-md-package"></span> pyaedt.sbrplus.hdm_utils</api/pyaedt/sbrplus/hdm_utils/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.circuit</api/pyaedt/workflows/circuit/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.project</api/pyaedt/workflows/project/index>
   <span class="nf nf-md-package"></span> pyaedt.application.Design</api/pyaedt/application/Design/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.clr_module</api/pyaedt/generic/clr_module/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.compliance</api/pyaedt/generic/compliance/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.filesystem</api/pyaedt/generic/filesystem/index>
   <span class="nf nf-md-package"></span> pyaedt.modeler.modelerpcb</api/pyaedt/modeler/modelerpcb/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.MeshIcepak</api/pyaedt/modules/MeshIcepak/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.SolveSetup</api/pyaedt/modules/SolveSetup/index>
   <span class="nf nf-md-package"></span> pyaedt.sbrplus.hdm_parser</api/pyaedt/sbrplus/hdm_parser/index>
   <span class="nf nf-md-package"></span> pyaedt.emit_core.Couplings</api/pyaedt/emit_core/Couplings/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.ibis_reader</api/pyaedt/generic/ibis_reader/index>
   <span class="nf nf-md-package"></span> pyaedt.modeler.calculators</api/pyaedt/modeler/calculators/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.MaterialLib</api/pyaedt/modules/MaterialLib/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.SolveSweeps</api/pyaedt/modules/SolveSweeps/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.installer</api/pyaedt/workflows/installer/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.maxwell2d</api/pyaedt/workflows/maxwell2d/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.maxwell3d</api/pyaedt/workflows/maxwell3d/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.templates</api/pyaedt/workflows/templates/index>
   <span class="nf nf-md-package"></span> pyaedt.application.Analysis</api/pyaedt/application/Analysis/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.DataHandlers</api/pyaedt/generic/DataHandlers/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.design_types</api/pyaedt/generic/design_types/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.LoadAEDTFile</api/pyaedt/generic/LoadAEDTFile/index>
   <span class="nf nf-md-package"></span> pyaedt.modeler.advanced_cad</api/pyaedt/modeler/advanced_cad/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.LayerStackup</api/pyaedt/modules/LayerStackup/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.Mesh3DLayout</api/pyaedt/modules/Mesh3DLayout/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.mechanical</api/pyaedt/workflows/mechanical/index>
   <span class="nf nf-md-package"></span> pyaedt.application.Variables</api/pyaedt/application/Variables/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.CableModeling</api/pyaedt/modules/CableModeling/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.PostProcessor</api/pyaedt/modules/PostProcessor/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.twinbuilder</api/pyaedt/workflows/twinbuilder/index>
   <span class="nf nf-md-package"></span> pyaedt.application.Analysis3D</api/pyaedt/application/Analysis3D/index>
   <span class="nf nf-md-package"></span> pyaedt.application.JobManager</api/pyaedt/application/JobManager/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.com_parameters</api/pyaedt/generic/com_parameters/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.configurations</api/pyaedt/generic/configurations/index>
   <span class="nf nf-md-package"></span> pyaedt.misc.create_remote_dir</api/pyaedt/misc/create_remote_dir/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.monitor_icepak</api/pyaedt/modules/monitor_icepak/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.SetupTemplates</api/pyaedt/modules/SetupTemplates/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.hfss3dlayout</api/pyaedt/workflows/hfss3dlayout/index>
   <span class="nf nf-md-package"></span> pyaedt.application.analysis_hf</api/pyaedt/application/analysis_hf/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.general_methods</api/pyaedt/generic/general_methods/index>
   <span class="nf nf-md-package"></span> pyaedt.application.aedt_objects</api/pyaedt/application/aedt_objects/index>
   <span class="nf nf-md-package"></span> pyaedt.emit_core.emit_constants</api/pyaedt/emit_core/emit_constants/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.desktop_sessions</api/pyaedt/generic/desktop_sessions/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.CircuitTemplates</api/pyaedt/modules/CircuitTemplates/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.DesignXPloration</api/pyaedt/modules/DesignXPloration/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.report_templates</api/pyaedt/modules/report_templates/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.near_field_import</api/pyaedt/generic/near_field_import/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.python_optimizers</api/pyaedt/generic/python_optimizers/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.touchstone_parser</api/pyaedt/generic/touchstone_parser/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.fields_calculator</api/pyaedt/modules/fields_calculator/index>
   <span class="nf nf-md-package"></span> pyaedt.application.AnalysisNexxim</api/pyaedt/application/AnalysisNexxim/index>
   <span class="nf nf-md-package"></span> pyaedt.application.AnalysisRMxprt</api/pyaedt/application/AnalysisRMxprt/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.report_file_parser</api/pyaedt/generic/report_file_parser/index>
   <span class="nf nf-md-package"></span> pyaedt.modeler.geometry_operators</api/pyaedt/modeler/geometry_operators/index>
   <span class="nf nf-md-package"></span> pyaedt.application.Analysis3DLayout</api/pyaedt/application/Analysis3DLayout/index>
   <span class="nf nf-md-package"></span> pyaedt.application.design_solutions</api/pyaedt/application/design_solutions/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.OptimetricsTemplates</api/pyaedt/modules/OptimetricsTemplates/index>
   <span class="nf nf-md-package"></span> pyaedt.generic.grpc_plugin_dll_class</api/pyaedt/generic/grpc_plugin_dll_class/index>
   <span class="nf nf-md-package"></span> pyaedt.modules.AdvancedPostProcessing</api/pyaedt/modules/AdvancedPostProcessing/index>
   <span class="nf nf-md-package"></span> pyaedt.application.AnalysisTwinBuilder</api/pyaedt/application/AnalysisTwinBuilder/index>
   <span class="nf nf-md-package"></span> pyaedt.application.AEDT_File_Management</api/pyaedt/application/AEDT_File_Management/index>
   <span class="nf nf-md-package"></span> pyaedt.application.AnalysisMaxwellCircuit</api/pyaedt/application/AnalysisMaxwellCircuit/index>
   <span class="nf nf-md-package"></span> pyaedt.workflows.customize_automation_tab</api/pyaedt/workflows/customize_automation_tab/index>
   <span class="nf nf-md-package"></span> pyaedt.misc.spisim_com_configuration_files</api/pyaedt/misc/spisim_com_configuration_files/index>




