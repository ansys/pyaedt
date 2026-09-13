.. _ref_security_consideration:

Security considerations
=======================

This section provides information on security considerations for the use
of PyAEDT. It is important to understand the capabilities which PyAEDT
provides, especially when using it to build applications or scripts that
accept untrusted input.

If a function displays a warning that redirects to this page, it indicates
that the function may expose security risks when used improperly.
In such cases, it is essential to pay close attention to:

- **Function arguments**: Ensure that arguments passed to the function are
  properly validated and do not contain untrusted content such as arbitrary
  file paths, shell commands, or serialized data.
- **Environment variables**: Be cautious of environment variables that can
  influence the behavior of the function, particularly if they are user-defined
  or inherited from an untrusted execution context.
- **Global settings (`settings`)**: PyAEDT settings control various aspects of
  runtime behavior such as AEDT features, use of LSF cluster or remote server
  connections. Review these settings to avoid unexpected side effects or security
  vulnerabilities.

Always validate external input, avoid executing arbitrary commands or code,
and follow the principle of least privilege when developing with PyAEDT.

.. _security_launch_aedt:

Launching AEDT
--------------

The :py:func:`.launch_aedt` and :py:func:`.launch_aedt_in_lsf` functions can be used
to launch AEDT. The executable which is launched is configured with the function
parameters, environment variables and the
`settings <https://aedt.docs.pyansys.com/version/stable/User_guide/settings.html>`_.
This may allow an attacker to launch arbitrary executables on the system. When
exposing the launch function to untrusted users, it is important to validate that
the executable path, environment variables (for example ``ANSYSEM_ROOT``,
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
``ANSYSEM_ROOT``, ``ANSYSEM_PY_CLIENT_ROOT`` and ``ANSYSEMSV_ROOT`` are safe.
Otherwise, hard-code them in the application.

