# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""Miscellaneous Methods for PyAEDT."""

import os
import warnings


def list_installed_ansysem():
    """Return a list of installed AEDT versions on ``ANSYSEM_ROOT``."""
    aedt_env_var_prefix = "ANSYSEM_ROOT"
    version_list = sorted([x for x in os.environ if x.startswith(aedt_env_var_prefix)], reverse=True)
    aedt_env_var_prefix = "ANSYSEM_PY_CLIENT_ROOT"
    version_list += sorted([x for x in os.environ if x.startswith(aedt_env_var_prefix)], reverse=True)
    aedt_env_var_sv_prefix = "ANSYSEMSV_ROOT"
    version_list += sorted([x for x in os.environ if x.startswith(aedt_env_var_sv_prefix)], reverse=True)

    if not version_list:
        warnings.warn(
            "No installed versions of AEDT are found in the system environment variables ``ANSYSEM_ROOTxxx``."
        )

    return version_list


def installed_versions():
    """Get the installed AEDT versions.

    This method returns a dictionary, with version as the key and installation path
    as the value."""

    return_dict = {}
    version_list = list_installed_ansysem()
    client = False
    for version_env_var in version_list:
        if "ANSYSEMSV_ROOT" in version_env_var:
            current_version_id = version_env_var.replace("ANSYSEMSV_ROOT", "")
            student = True
        elif "ANSYSEM_ROOT" in version_env_var:
            current_version_id = version_env_var.replace("ANSYSEM_ROOT", "")
            student = False
        else:
            current_version_id = version_env_var.replace("ANSYSEM_PY_CLIENT_ROOT", "")
            student = False
            client = True
        try:
            version = int(current_version_id[0:2])
            release = int(current_version_id[2])
            if version < 20:
                if release < 3:
                    version -= 1
                else:
                    release -= 2
            if student:
                v_key = "20{0}.{1}SV".format(version, release)
            elif client:
                v_key = "20{0}.{1}CL".format(version, release)
            else:
                v_key = "20{0}.{1}".format(version, release)
            return_dict[v_key] = os.environ[version_env_var]
        except Exception:  # pragma: no cover
            pass
    return return_dict


def current_version():
    """Get the current AEDT version."""
    try:
        return list(installed_versions().keys())[0]
    except (NameError, IndexError):
        return ""


def current_student_version():
    """Get the current AEDT student version."""
    for version_key in installed_versions():
        if "SV" in version_key:
            return version_key
    return ""


def is_safe_path(path, allowed_extensions=None):
    """Validate if a path is safe to use."""
    # Ensure path is an existing file or directory
    if not os.path.exists(path) or not os.path.isfile(path):
        return False

    # Restrict to allowed file extensions:
    if allowed_extensions:
        if not any(path.endswith(extension) for extension in allowed_extensions):
            return False

    # Ensure path does not contain dangerous characters
    if any(char in path for char in (";", "|", "&", "$", "<", ">", "`")):
        return False

    return True
