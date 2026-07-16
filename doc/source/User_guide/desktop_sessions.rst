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
        version = d.aedt_version_id
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
        version = d.aedt_version_id
        hfss = Hfss()
        maxwell = Maxwell3d()
        # Work with an existing AEDT session here.

    # The AEDT session remains open here.

Use ``Desktop`` class directly
------------------------------

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


Session selection precedence
----------------------------

When ``Desktop`` decides whether to connect to an existing AEDT session or to start a new one,
PyAEDT evaluates several inputs in a specific order. The following list describes the exact
checks performed by the library (this order matches the implementation in
``ansys.aedt.core.desktop._validate_port`` and related initialization logic):

- If ``port`` is ``0``: a concrete port is assigned (``_assign_port``) and used.
- If ``new_desktop`` is ``True``: PyAEDT prefers to start a new AEDT instance. If the
  requested port is already in use by any active session, PyAEDT chooses a different
  free port (``_find_free_port``) so the new session can be started.
- If a remote RPyC RPC connection is configured (``settings.remote_rpc_session``): PyAEDT
  uses the remote session and short-circuits further local port checks (``new_desktop`` is
  set to ``False`` and the requested port is used).
- If there is an active session for the same AEDT version and the requested port is used by
  that session, PyAEDT connects to it (reuse).
- If there is an active session for the same AEDT version but the opposite display mode
  (graphical vs non-graphical) using the requested port, PyAEDT flips the ``non_graphical``
  flag and connect to that session.
- If the requested port is in use by a different AEDT version, PyAEDT treats this as a
  conflict and (to avoid attaching to the wrong version) select a new free port and start
  a new session (``new_desktop`` becomes ``True``).
- If none of the above conditions apply, PyAEDT uses the requested port and start a
  new AEDT session.

This precedence ensures predictable behavior: version and the desire to force a new
session (``new_desktop``) govern whether PyAEDT attaches or starts, while port and display
mode determine whether an existing session can be reused or whether a new one must be
created.
