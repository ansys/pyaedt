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

from ansys.aedt.core.modules.variation import Variation

def parse_profile_key(profile_key):
    """Split the profile key.

    Split the profile key into the setup name
    and variation.

    Parameters
    ----------
    profile_key : str
        String of the format "SetupName - variation". For example
        "MySetup - l_dipole='10.1cm' wire_rad='1mm'".

    Returns
    -------
    setup_name : string
    variation : Variation (dict-like)

    """
    setup, variation_string = profile_key.split('-')
    setup_name = setup.strip()
    variation = Variation(variation_string)
    return setup_name, variation

class ProfileData(object):
    """ Simple interface to solver Profile data.
    """

    def __init__(self, profile_data):
        """

        Parameters
        ----------
        profile_data : BinaryTreeNode
            The full profile data.

        """

        for group_name, process_group in profile_data.children.items():
            for process_name, process_data in process_group.children.items():
                if process_name == "HPC Group":
                    pass
                elif process_name == "Design Validation":
                    pass
                elif process_name == "Frequency Sweep Group":
                    pass
                elif process_name == "Simulation Summary Group":
                    pass





class Profile(object):
    """Provide a simple interface to view and parse the solver profile.

    """

    def __init__(self, profile_dict):
        if type(profile_dict) is dict:
            self._profile_dict = profile_dict
        else:
            raise TypeError('Profile must be a dictionary.')
        for key, value in profile_dict.items():
            self.setup_name, self.variation = parse_profile_key(key)
            self._profile_data = ProfileData(value)

