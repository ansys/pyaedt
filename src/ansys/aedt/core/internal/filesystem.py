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

import os
from pathlib import Path
import secrets
import shutil
import string

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.file_utils import _uname


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
    return [Path(i).absolute() for i in Path(dirname).glob(pattern)]


def my_location():
    """ """
    return Path(__file__).parent.resolve(strict=False)


class Scratch(PyAedtBase):
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
        name = "".join(secrets.choice(char_set) for _ in range(6))
        self._scratch_path = (Path(local_path) / ("scratch" + name)).resolve(strict=False)
        if self._scratch_path.exists():
            try:
                self.remove()
            except Exception:
                self._cleaned = False
        if self._cleaned:
            try:
                self.path.mkdir(parents=True, exist_ok=True)
                os.chmod(self.path, permission)
            except FileNotFoundError as fnf_error:  # Raise error if folder doesn't exist.
                print(fnf_error)

    def remove(self):
        """ """
        try:
            shutil.rmtree(self._scratch_path, ignore_errors=True)
        except Exception:
            logger.error(f"An error occurred while removing {self._scratch_path}")

    def copyfile(self, src_file, dst_filename=None):
        """Copy a file to the scratch directory.

        The target filename is optional. If omitted, the target file name is identical to the source file name.

        Parameters
        ----------
        src_file : str or :class:`pathlib.Path`
            Source file with fullpath.
        dst_filename : str or :class:`pathlib.Path`, optional
            Destination filename with the extension. The default is ``None``,
            in which case the destination file is given the same name as the
            source file.

        Returns
        -------
        dst_file : str
            Full path and file name of the copied file.
        """
        if dst_filename:
            dst_file = self.path / dst_filename
        else:
            dst_file = self.path / Path(src_file).name
        if dst_file.exists():
            try:
                dst_file.unlink()
            except OSError:  # pragma: no cover
                pass
        try:
            shutil.copy2(src_file, dst_file)
        except FileNotFoundError as fnf_error:
            print(fnf_error)

        return str(dst_file)

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

    def create_sub_folder(self, name: str = "") -> str:
        """Create a subfolder.

        Parameters
        ----------
        name : str, optional

        Return
        ------
        str
            Full path to the created subfolder. If no name is provided, a random name is generated.
        """
        sub_folder = Path(self.path) / _uname(name)
        sub_folder.mkdir(parents=True, exist_ok=True)
        return str(sub_folder)


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


def is_safe_path(path, allowed_extensions=None):
    """Validate if a path is safe to use."""
    # Ensure path is an existing file or directory
    path = Path(path)
    if not path.exists() or not path.is_file():
        return False

    # # Restrict to allowed file extensions:
    if allowed_extensions:
        if path.suffix not in allowed_extensions:
            return False

    # # Ensure path does not contain dangerous characters
    if any(char in str(path) for char in (";", "|", "&", "$", "<", ">", "`")):
        return False

    return True
