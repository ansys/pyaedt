Security considerations
=======================

This section provides information on security considerations for the use
of PyAEDT. It is important to understand the capabilities which PyAEDT
provides, especially when using it to build applications or scripts that
accept untrusted input.

.. _security_launch_aedt:

Launching AEDT
--------------

The :py:func:`.launch_aedt` and :py:func:`.launch_aedt_in_lsf` functions can be used
to launch AEDT. The executable which is launched is configured with the function
parameters, environment variables and the
`settings <https://aedt.docs.pyansys.com/version/stable/User_guide/settings.html>`_.
This may allow an attacker to launch arbitrary executables on the system. When
exposing the launch function to untrusted users, it is important to validate that
the executable path, environment variables (for example ``"ANSYSEM_ROOT"``,
``ANSYSEM_PY_CLIENT_ROOT`` and ``ANSYSEMSV_ROOT``) and PyAEDT settings are safe.
Otherwise, hard-code them in the application.

.. _security_ansys_cloud:

Retrieving Ansys Cloud information
----------------------------------

The :py:func:`.get_cloud_job_info` and :py:func:`.get_available_cloud_config`
functions can be used to retrieve information related to Ansys Cloud.
The executable which is launched is configured with the function
parameters and the AEDT installation that is detected. Since finding the AEDT
installation path is based of environment variables, this may allow an attacker
to launch arbitrary executables on the system. When exposing the launch function
to untrusted users, it is important to validate that environment variables like
``"ANSYSEM_ROOT"``, ``ANSYSEM_PY_CLIENT_ROOT`` and ``ANSYSEMSV_ROOT`` are safe.
Otherwise, hard-code them in the application.

