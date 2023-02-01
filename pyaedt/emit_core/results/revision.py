import os

from pyaedt.generic.general_methods import pyaedt_function_handler

class Revision:
    """
    Provides the ``Revision`` object.

    Parameters
    ----------
    Emit_obj :
         ``Emit`` object that this revision is associated with.
    name : str, optional
        Name of the revision to create. The default is ``None``, in which case a
        default name is given.

    Examples
    --------
    Create a ``Revision`` instance.

    >>> aedtapp = Emit()
    >>> rev = Revision(aedtapp, "Revision 1")
    >>> domain = aedtapp.interaction_domain()
    >>> rev.run(domain)
    """

    def __init__(self, emit_obj, name=""):
        subfolder = ""
        for f in os.scandir(emit_obj.results.location):
            if os.path.splitext(f.name)[1].lower() in ".aedtresults":
                subfolder = os.path.join(f.path, "EmitDesign1")
        default_behaviour = not os.path.exists(os.path.join(subfolder, "{}.emit".format(name)))
        if default_behaviour:
            print("The most recently generated revision will be used because the revision specified does not exist.")
        if name == "" or default_behaviour:
            file = max([f for f in os.scandir(subfolder)], key=lambda x: x.stat().st_mtime)
            full = file.path
            name = file.name
        else:
            full = subfolder + "/{}.emit".format(name)
        self.name = name
        """Name of the revision."""

        self.path = full
        """Full path of the revision."""

        self.emit_obj = emit_obj
        """''Emit'' object associated with the revision."""

    @pyaedt_function_handler()
    def run(self, domain):
        """
        Load the revision and then analyze along the given domain.

        Parameters
        ----------
        domain :
            ``InteractionDomain`` object for constraining the analysis parameters.

        Returns
        -------
        interaction:class: `Interaction`
            Interaction object.

        Examples
        ----------
        >>> domain = aedtapp.interaction_domain()
        >>> rev.run(domain)

        """
        self.emit_obj._load_result_set(self.path)
        self.path = self.emit_obj._emit_api.get_project_path()  # making sure format matches
        engine = self.emit_obj._emit_api.get_engine()
        interaction = engine.run(domain)
        return interaction

    @pyaedt_function_handler()
    def get_max_simultaneous_interferers(self):

        """
        Get the number of maximum simultaneous interferers.

        Returns
        -------
        max_interferers : int
            Maximum number of simultaneous interferers associated with engine

        Examples
        ----------
        >>> max_num = aedtapp.results.get_max_simultaneous_interferers()
        """
        self.emit_obj._load_result_set(self.path)
        engine = self.emit_obj._emit_api.get_engine()
        max_interferers = engine.max_simultaneous_interferers
        return max_interferers

    @pyaedt_function_handler()
    def set_max_simultaneous_interferers(self, val):

        """
        Set the number of maximum simultaneous interferers.

        Examples
        ----------
        >>> max_num = aedtapp.results.get_max_simultaneous_interferers()
        """
        self.emit_obj._load_result_set(self.path)
        engine = self.emit_obj._emit_api.get_engine()
        engine.max_simultaneous_interferers = val

    @pyaedt_function_handler()
    def is_domain_valid(self, ret_val, domain):
        """
        Return ``True`` if the given domain is valid for the current Revision

        Examples
        ----------
        >>> domain = aedtapp.interaction_domain()
        >>> aedtapp.results.is_domain_valid(domain)
        True
        """
        self.emit_obj._load_result_set(self.path)
        engine = self.emit_obj._emit_api.get_engine()
        return engine.is_domain_valid(domain)