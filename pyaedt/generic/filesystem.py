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

import os
import random
import shutil
import string

from pyaedt.aedt_logger import pyaedt_logger as logger


def search_files(dirname, pattern="*"):
    """Search for files inside a directory given a specific pattern.

    Parameters
    ----------
    dirname : str
    pattern :str, optional

    Returns
    -------
    list
    """
    from pyaedt.generic.general_methods import is_ironpython

    if is_ironpython:
        import glob

        return list(glob.glob(os.path.join(dirname, pattern)))
    else:
        import pathlib

        return [os.path.abspath(i) for i in pathlib.Path(dirname).glob(pattern)]


def my_location():
    """ """
    return os.path.normpath(os.path.dirname(__file__))


class Scratch:
    """ """

    @property
    def path(self):
        """ """
        return self._scratch_path

    @property
    def is_empty(self):
        """ """
        return self._cleaned

    def __init__(self, local_path, permission=0o777, volatile=False):
        self._volatile = volatile
        self._cleaned = True
        char_set = string.ascii_uppercase + string.digits
        self._scratch_path = os.path.normpath(os.path.join(local_path, "scratch" + "".join(random.sample(char_set, 6))))
        if os.path.exists(self._scratch_path):
            try:
                self.remove()
            except Exception:
                self._cleaned = False
        if self._cleaned:
            try:
                os.mkdir(self.path)
                os.chmod(self.path, permission)
            except FileNotFoundError as fnf_error:  # Raise error if folder doesn't exist.
                print(fnf_error)

    def remove(self):
        """ """
        try:
            # TODO check why on Anaconda 3.7 get errors with os.path.exists
            shutil.rmtree(self._scratch_path, ignore_errors=True)
        except Exception:
            logger.error("An error occurred while removing {}".format(self._scratch_path))

    def copyfile(self, src_file, dst_filename=None):
        """
        Copy a file to the scratch directory. The target filename is optional.
        If omitted, the target file name is identical to the source file name.

        Parameters
        ----------
        src_file : str
            Source file with fullpath.
        dst_filename : str, optional
            Destination filename with the extension. The default is ``None``,
            in which case the destination file is given the same name as the
            source file.


        Returns
        -------
        dst_file : str
            Full path and file name of the copied file.

        """
        if dst_filename:
            dst_file = os.path.join(self.path, dst_filename)
        else:
            dst_file = os.path.join(self.path, os.path.basename(src_file))
        if os.path.exists(dst_file):
            try:
                os.unlink(dst_file)
            except OSError:  # pragma: no cover
                pass
        try:
            shutil.copy2(src_file, dst_file)
        except FileNotFoundError as fnf_error:
            print(fnf_error)

        return dst_file

    def copyfolder(self, src_folder, destfolder):
        """

        Parameters
        ----------
        src_folder :

        destfolder :


        Returns
        -------

        """
        shutil.copytree(src_folder, destfolder, dirs_exist_ok=True)
        return True

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type or self._volatile:
            self.remove()


def get_json_files(start_folder):
    """
    Get the absolute path to all *.json files in start_folder.

    Parameters
    ----------
    start_folder, str
        Path to the folder where the json files are located.

    Returns
    -------
    """
    return [y for x in os.walk(start_folder) for y in search_files(x[0], "*.json")]
