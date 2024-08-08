EMIT modeler
============
The ``EMIT Modeling`` module includes several classes to enable
modeling in EMIT:


* ``modeler`` to return the schematic modeler for an EMIT design.
* ``couplings`` to return a list of all linked couplings within an EMIT design.
* ``version`` to provide the EMIT version information.
* ``set_units`` to set the units globally for the EMIT design.
* ``get_units`` to get the value of the current EMIT design global units.

EMIT version check and set units example:

.. code:: python

    import pyaedt
    from pyaedt import Emit

    emit = Emit(pyaedt.generate_unique_project_name(),
                specified_version="2024.2", non_graphical=False,
                new_desktop_session=True, close_on_exit=True)

    # This call returns detailed version info for EMIT
    ver = emit.version(detailed=True)

    # This call sets the global units for EMIT
    unit_types = ["Power", "Frequency", "Length", "Time"]
    unit_vals = ["kW", "kHz", "meter", "ns"]
    emit.set_units(unit_types, unit_vals)

    # This call gets all the global units for the EMIT design
    all_units = emit.get_units()

    # This call gets the global Frequency units for the EMIT design
    freq_units = emit.get_units("Frequency")

    # Close AEDT
    emit.release_desktop(close_projects=True, close_desktop=True)

EMIT-HFSS link creation example:

.. code:: python

    import os
    import pyaedt
    from pyaedt import Emit
    from pyaedt.generic.filesystem import Scratch

    scratch_path = pyaedt.generate_unique_folder_name()
    temp_folder = os.path.join(scratch_path, ("EmitHFSSExample"))
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)

    # Launch AEDT
    aedtapp = pyaedt.launch_desktop(specified_version="2024.2", non_graphical=False,
                                    new_desktop_session=True, close_on_exit=True)

    # Verify the ``Cell Phone RFT Defense`` example exists
    example_name = "Cell Phone RFI Desense"
    example_aedt = example_name + ".aedt"
    example_results = example_name + ".aedtresults"
    example_lock = example_aedt + ".lock"
    example_pdf_file = example_name + " Example.pdf"

    example_dir = os.path.join(aedtapp.install_path, "Examples\\EMIT")
    example_project = os.path.join(example_dir, example_aedt)
    example_results_folder = os.path.join(example_dir, example_results)
    example_pdf = os.path.join(example_dir, example_pdf_file)

    # If the ``Cell Phone RFT Defense`` example is not
    # in the installation directory, exit from this example.
    if not os.path.exists(example_project):
        exit()

    # Copy the project to a temp directory
    my_project = os.path.join(temp_folder, example_aedt)
    my_results_folder = os.path.join(temp_folder, example_results)
    my_project_lock = os.path.join(temp_folder, example_lock)
    my_project_pdf = os.path.join(temp_folder, example_pdf_file)

    if os.path.exists(my_project):
        os.remove(my_project)

    if os.path.exists(my_project_lock):
        os.remove(my_project_lock)

    with Scratch(scratch_path) as local_scratch:
        local_scratch.copyfile(example_project, my_project)
        local_scratch.copyfolder(example_results_folder, my_results_folder)
        if os.path.exists(example_pdf):
            local_scratch.copyfile(example_pdf, my_project_pdf)

    emit = Emit(my_project)

    # Remove all existing links
    for link in emit.couplings.coupling_names:
        emit.couplings.delete_link(link)

    # Add the HFSS design as a coupling in EMIT
    for link in emit.couplings.linkable_design_names:
        emit.couplings.add_link(link)

    # Get all the antennas in the EMIT design
    antennas = emit.couplings.antenna_nodes
    for ant in antennas:
        print(ant)

    # Close AEDT
    emit.release_desktop(close_projects=True, close_desktop=True)

Create and Analyze an EMIT project:

.. code:: python

    import pyaedt
    from pyaedt import Emit
    from pyaedt.emit_core.emit_constants import TxRxMode, ResultType

    emit = Emit(pyaedt.generate_unique_project_name(),
                specified_version="2024.2", non_graphical=False,
                new_desktop_session=True, close_on_exit=True)

    # Create a radio and connect an antenna to it
    rad1 = emit.modeler.components.create_component("New Radio")
    ant1 = emit.modeler.components.create_component("Antenna")
    if rad1 and ant1:
        ant1.move_and_connect_to(rad1)

    # Quickly create 2 more radios with antennas automatically
    # connected to them
    rad2, ant2 = emit.modeler.components.create_radio_antenna("GPS Receiver")
    rad3, ant3 = emit.modeler.components.create_radio_antenna("Bluetooth Low Energy (LE)", "Bluetooth")

    # Create a new ``Revision``
    rev = emit.results.analyze()

    # Get the receive bands enabled for the GPS Rx
    rx_bands = rev.get_band_names(rad2.name, TxRxMode.RX)

    # Get the transmit bands enabled for the Bluetooth radio
    tx_bands = rev.get_band_names(rad3.name, TxRxMode.TX)

    # Configure the interaction domain that will be analyzed
    domain = emit.results.interaction_domain()
    domain.set_receiver(rad2.name, rx_bands[0], -1)
    domain.set_interferer(rad3.name,tx_bands[0])

    # Analzye the domain and get the worst case interference
    interaction = rev.run(domain)
    worst = interaction.get_worst_instance(ResultType.EMI)
    emi = worst.get_value(ResultType.EMI)
    print("Worst case interference is: {} dB".format(emi))

    # Close AEDT
    emit.release_desktop(close_projects=True, close_desktop=True)