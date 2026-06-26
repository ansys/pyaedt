Desktop sessions
================

PyAEDT can use ``Desktop`` either to start a new AEDT session or to connect to an
existing one. The ``close_on_exit`` argument controls whether that AEDT session is
closed when leaving a context manager or when the Python interpreter session ends.

When ``close_on_exit`` is not explicitly provided, PyAEDT chooses the behavior automatically:

- Inside a context manager (``with Desktop(...)``), ``close_on_exit`` is treated as ``True``.
- Outside a context manager:

  - if PyAEDT starts a new AEDT session, ``close_on_exit`` behaves as ``True``
  - if PyAEDT connects to an existing AEDT session, ``close_on_exit`` behaves as ``False``

When ``close_on_exit`` is explicitly set to ``True`` or ``False``, the user choice is always respected.

Behavior summary
----------------

The following table summarizes the most common behavior combinations:

.. list-table::
   :header-rows: 1
   :widths: 35 35

   * - Usage
     - Result on exit
   * - ``with Desktop(close_on_exit=True)`` or ``with Desktop()``
     - AEDT closes when leaving the context manager
   * - ``with Desktop(close_on_exit=False)``
     - AEDT remains open when leaving the context manager
   * - ``Desktop(new_desktop=True)``
     - AEDT closes when the interpreter session ends
   * - ``Desktop(new_desktop=False)``
     - PyAEDT connected to an existing session. AEDT remains open when the interpreter session ends
   * - ``Desktop(close_on_exit=True)``
     - AEDT closes when the interpreter session ends
   * - ``Desktop(close_on_exit=False)``
     - AEDT remains open when the interpreter session ends

Use a context manager
---------------------

Use a context manager when you want deterministic cleanup at the end of a block:

.. code:: python

    from ansys.aedt.core import Desktop, Hfss, Maxwell3d

    with Desktop(
        version="2026.1",
        non_graphical=True,
        new_desktop=True,
    ) as d:
        hfss = Hfss()
        maxwell = Maxwell3d()
        # ...
        # Work with AEDT here.
        # ...

    # AEDT is automatically closed here.

If needed, you can still override the default behavior explicitly:

.. code:: python

    from ansys.aedt.core import Desktop, Hfss, Maxwell3d

    with Desktop(
        version="2026.1",
        non_graphical=True,
        new_desktop=False,
        close_on_exit=False,
    ) as d:
        hfss = Hfss()
        maxwell = Maxwell3d()
        # Work with an existing AEDT session here.

    # The AEDT session remains open here.

Use ``Desktop`` class directly
--------------------

When ``Desktop`` is used directly, the default behavior depends on whether PyAEDT starts
or attaches to AEDT. You can also release the desktop explicitly for finer control:

.. code:: python

    import ansys.aedt.core

    d = ansys.aedt.core.Desktop(
        version="2026.1",
        non_graphical=False,
        new_desktop=False,
    )

    hfss = ansys.aedt.core.Hfss()
    # Work with AEDT here.

    d.release_desktop(close_projects=False, close_desktop=False)

Recommendations
---------------

- Use ``with Desktop(...)`` when you want predictable cleanup.
- Use direct ``Desktop(...)`` construction when you need more manual control over the AEDT session lifecycle.
- When attaching to an existing AEDT session, consider leaving ``close_on_exit`` unset or setting it explicitly to ``True`` if you do want PyAEDT to close that session.
