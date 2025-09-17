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

import warnings

from ansys.aedt.core import emit_core
from ansys.aedt.core.emit_core.results.revision import Revision
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class Results:
    """
    Provides the ``Results`` object.

    Parameters
    ----------
    emit_obj : emit_obj object
        EMIT object used to create the result.

    Examples
    --------
    Create an instance of the ``Result`` object.

    >>> aedtapp.results = Results()
    >>> revision = aedtapp.results.analyze()
    >>> receivers = revision.get_receiver_names()
    """

    def __init__(self, emit_obj):
        self.emit_project = emit_obj
        """EMIT project."""

        self.current_revision = None
        """Current active Revision."""

        self.revisions = []
        """List of all result revisions. Only one loaded at a time"""

        self.design = emit_obj.desktop_class.active_design(emit_obj.odesktop.GetActiveProject())
        """Active design for the EMIT project."""

        self.aedt_version = int(self.emit_project.aedt_version_id[-3:])

    @pyaedt_function_handler()
    def _add_revision(self, name=None):
        """Add a new revision or get the current revision if it already exists.

        Parameters
        ----------
        name : str, optional
            Name for the new revision, if created. The default is ``None``, in which
            case the name of the current design revision is used.

        Raises
        ------
        RuntimeError if the name given is not the name of an existing result set and a current result set already
        exists.

        Returns
        -------
        ``Revision`` object that was created.
        """
        if self.aedt_version > 251 and name is None:
            current_revision = None
            current_revisions = [revision for revision in self.revisions if revision.name == "Current"]

            # Remove existing Current revisions
            for revision in current_revisions:
                self.delete_revision("Current")

            # Create and return an updated Current revision
            current_revision = Revision(self, self.emit_project, name)
            self.revisions.append(current_revision)
            return current_revision
        else:
            revision = Revision(self, self.emit_project, name)
            self.revisions.append(revision)
            return revision

    @pyaedt_function_handler()
    def delete_revision(self, revision_name):
        """Delete the specified revision from the results.

        Parameters
        ----------
        revision_name : str
            Name of the revision.

        Returns
        -------
        None

        Examples
        --------
        >>> aedtapp.results.delete_revision("Revision 10")
        """
        if self.aedt_version > 251:
            if revision_name in self.design.GetKeptResultNames():
                self.design.DeleteKeptResult(revision_name)
                if self.current_revision.name == revision_name and self.current_revision.revision_loaded:
                    self.emit_project._emit_api.close()
                    self.current_revision = None
            for rev in self.revisions:
                if revision_name in rev.name:
                    self.revisions.remove(rev)
                    break
        else:
            if revision_name in self.design.GetResultList():
                self.design.DeleteResult(revision_name)
                if self.current_revision.name == revision_name and self.current_revision.revision_loaded:
                    self.emit_project._emit_api.close()
                    self.current_revision = None
                for rev in self.revisions:
                    if revision_name in rev.name:
                        self.revisions.remove(rev)
                        break
                else:
                    warnings.warn(f"{revision_name} does not exist")

    @staticmethod
    def interaction_domain():
        """
        Get an ``InteractionDomain`` object.

        Returns
        -------
        :class:`Emit.InteractionDomain`
            Defines a set of interacting interferers and receivers.

        Examples
        --------
        >>> domain = Emit.results.InteractionDomain()

        """
        try:
            domain = emit_core.emit_api_python().InteractionDomain()
        except NameError:
            raise ValueError("An EMIT object must be initialized before any static member of the Results.")
        return domain

    @pyaedt_function_handler
    def _unload_revisions(self):
        """Convenience function to set all revisions as ``unloaded``

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        for rev in self.revisions:
            rev.revision_loaded = False

    @pyaedt_function_handler()
    def revision_names(self):
        """
        Return a list of all the revision names.

        Parameters
        ----------
        None

        Returns
        -------
        revision_names : list str
            List of all revision names.
        """
        return [rev.name for rev in self.revisions]

    @pyaedt_function_handler
    def get_revision(self, revision_name=None):
        """
        Load the specified revision.

        Parameters
        ----------
        revision_name : str, optional
            Revision to load. The default is  ``None`` in which
            case the latest revision will be returned.

        Returns
        -------
        rev:class:`ansys.aedt.core.modules.revision`
            Specified ``Revision`` object that was loaded.

        Examples
        --------
        >>> rev = aedtapp.results.get_revision("Revision 15")
        >>> interferers = rev.get_interferer_names()
        >>> receivers = rev.get_receiver_names()
        """
        # no revisions to load, create a new one
        if len(self.revisions) == 0:
            return self.analyze()
        # retrieve the latest revision if nothing specified
        if revision_name is None:
            if self.aedt_version > 251:
                return self.current_revision

            # unload the current revision and load the latest
            self.current_revision.revision_loaded = False
            self.current_revision = self.revisions[-1]
            self.current_revision._load_revision()
        else:
            rev = [x for x in self.revisions if revision_name == x.name]
            if len(rev) > 0:
                # unload the current revision and load the specified revision
                self.current_revision.revision_loaded = False
                self.current_revision = rev[0]
                self.current_revision._load_revision()
            else:
                # might be an old revision that was never loaded by pyaedt
                aedt_result_list = self.design.GetKeptResultNames()
                rev = [x for x in aedt_result_list if revision_name == x]
                if len(rev) > 0:
                    # unload the current revision and load the specified revision
                    self.current_revision.revision_loaded = False
                    self.current_revision = self._add_revision(rev[0])
                else:
                    warnings.warn(f"{revision_name} not found.")
        return self.current_revision

    @pyaedt_function_handler()
    def analyze(self):
        """Analyze the current revision or create a new revision if the design has changed.

        Returns
        -------
        rev:class:`ansys.aedt.core.modules.revision`
            Specified ``Revision`` object that was generated.

        Examples
        --------
        >>> rev = aedtapp.results.analyze()
        >>> interferers = rev.get_interferer_names()
        >>> receivers = rev.get_receiver_names()
        """
        if self.aedt_version > 251:
            if self.current_revision:
                self.current_revision.revision_loaded = False

            self.current_revision = self._add_revision()
            return self.current_revision
        else:
            # No revisions exist, add one
            if self.current_revision is None:
                self.current_revision = self._add_revision()
            # no changes since last created revision, load it
            elif (
                self.revisions[-1].revision_number
                == self.emit_project.desktop_class.active_design(
                    self.emit_project.desktop_class.active_project()
                ).GetRevision()
            ):
                self.get_revision(self.revisions[-1].name)
            else:
                # there are changes since the current revision was analyzed, create
                # a new revision
                self.current_revision.revision_loaded = False
                self.current_revision = self._add_revision()

            return self.current_revision
