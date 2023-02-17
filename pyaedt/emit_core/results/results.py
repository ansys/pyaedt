import warnings

from pyaedt.emit_core import EMIT_MODULE
from pyaedt.emit_core.results.revision import Revision
from pyaedt.generic.general_methods import pyaedt_function_handler


class Results:
    """
    Provides the ``Results`` object.

    Parameters
    ----------
    emit_obj : emit_obj object
        Emit object used to create the result.

    Examples
    --------
    Create an instance of the ``Result`` object.

    >>> aedtapp.results = Results()
    >>> revision = aedtapp.results.analyze()
    >>> receivers = revision.get_receiver_names()
    """

    def __init__(self, emit_obj):
        self.emit_project = emit_obj
        """Emit project."""

        self.current_revision = None
        """Current active Revision."""

        self.revisions = []
        """List of all result revisions. Only one loaded at a time"""

        self.design = emit_obj.odesktop.GetActiveProject().GetActiveDesign()
        """Active design for the Emit project."""

    @pyaedt_function_handler()
    def _add_revision(self, name=None):
        """Add a new revision.

        Parameters
        ----------
        name : str, optional
            Name for the new revision. If None, it will
            be named the current design revision.

        Returns
        -------
        ``Revision`` object that was created.
        """
        if name == None:
            self.design.AddResult()
            rev_num = self.design.GetRevision()
            name = "Revision {}".format(rev_num)
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
                warnings.warn("{} does not exist".format(revision_name))

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
            domain = EMIT_MODULE.InteractionDomain()
        except NameError:
            raise ValueError("An Emit object must be initialized before any static member of the Results.")
        return domain

    @pyaedt_function_handler
    def _unload_revisions(self):
        """Convenience function to set all revisions
        as ``unloaded``

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

    @pyaedt_function_handler()
    def analyze(self, revision_name=None):
        """
        Analyze the specified design.

        Parameters
        ----------
        revision_name : str
            Revision to analyze. The default is ``None``,in which case the most recent revision
            is loaded if it matches the current design revision.

        Returns
        -------
        rev:class:`pyaedt.modules.Revision`
            Specified ``Revision`` object that was generated.

        Examples
        --------
        >>> rev = aedtapp.results.analyze()
        >>> interferers = rev.get_interferer_names()
        >>> receivers = rev.get_receiver_names()
        """
        if revision_name is None:
            # analyze the current design revision
            if self.current_revision is None:
                self.current_revision = self._add_revision()
            elif (
                self.current_revision.revision_number
                == self.emit_project.odesktop.GetActiveProject().GetActiveDesign().GetRevision()
            ):
                # Revision exists for design rev #, load if it needed
                if not self.current_revision.revision_loaded:
                    self.current_revision._load_revision()
            else:
                # there are changes since the current revision was analyzed, create
                # a new revision
                self.current_revision.revision_loaded = False
                self.current_revision = self._add_revision()
        else:
            rev = [x for x in self.revisions if revision_name == x.name]
            if len(rev) > 0:
                # unload the current revision and load the specified revision
                self.current_revision.revision_loaded = False
                self.current_revision = rev[0]
                self.current_revision._load_revision()
            else:
                print("{} not found.".format(revision_name))
        return self.current_revision
