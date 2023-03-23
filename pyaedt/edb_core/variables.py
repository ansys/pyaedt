class Variable:
    """Manages EDB methods for variable accessible from `Edb.Utility.VariableServer` property."""

    @property
    def _is_design_varible(self):
        """Determines whether this variable is a design variable."""
        if self.name.startswith("$"):
            return False
        else:
            return True

    @property
    def _var_server(self):
        if self._is_design_varible:
            return self._pedb.active_cell.GetVariableServer()
        else:
            return self._pedb.db.GetVariableServer()

    @property
    def name(self):
        """Get the name of this variable."""
        return self._name

    @property
    def value(self):
        """Get the value of this variable."""
        return self._var_server.GetVariableValue(self.name)[1].ToDouble()

    @value.setter
    def value(self, value):
        self._var_server.SetVariableValue(self.name, self._pedb.edb_value(value))

    @property
    def description(self):
        """Get the description of this variable."""
        return self._var_server.GetVariableDescription(self.name)

    @description.setter
    def description(self, value):
        self._var_server.SetVariableDescription(self.name, value)

    @property
    def is_parameter(self):
        """Determine whether this variable is a parameter."""
        return self._var_server.IsVariableParameter(self.name)

    @property
    def value_str(self):
        """Get the value of this variable in string."""
        return self._var_server.GetVariableValue(self.name)[1].ToString()

    def __init__(self, pedb, name):
        self._pedb = pedb
        self._name = name
        pass

    def delete(self):
        """Delete this variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edb = Edb()
        >>> edb.variables.["new_variable"].delete()
        """
        return self._var_server.DeleteVariable(self.name)


class Variables:
    """Manages variables accessible from `Edb.variables`"""

    def __getitem__(self, item):
        return self.variables[item]

    @property
    def _design_var_server(self):
        return self._pedb.active_cell.GetVariableServer()

    @property
    def _project_var_server(self):
        return self._pedb.db.GetVariableServer()

    @property
    def design_variables(self):
        """Get all design variables."""
        d_var = dict()
        for i in self._design_var_server.GetAllVariableNames():
            d_var[i] = Variable(self._pedb, i)
        return d_var

    @property
    def project_variables(self):
        """Get all project variables."""
        p_var = dict()
        for i in self._project_var_server.GetAllVariableNames():
            p_var[i] = Variable(self._pedb, i)
        return p_var

    @property
    def variables(self):
        """Get all variables."""
        all_vars = dict()
        for i, j in self.project_variables.items():
            all_vars[i] = j
        for i, j in self.design_variables.items():
            all_vars[i] = j
        return all_vars

    def __init__(self, pedb):
        self._pedb = pedb
        pass

    def add(self, name, value, is_parameter=False):
        """Add a new variable.

        Parameters
        ----------
        name: str
            The name of this variable.
        value: int, float, str
            The value of this variable.
        is_parameter: bool
            Whether this variable is a parameter. The default value is ``False``

        Returns
        -------
        :class: `pyaedt.edb_core.variables.Variable`

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edb = Edb()
        >>> edb.variables.add("new_variable", 1e-3)
        """
        if name.startswith("$"):
            var_server = self._project_var_server
        else:
            var_server = self._design_var_server

        var_server.AddVariable(name, self._pedb.edb_value(value), is_parameter)
        return self.variables[name]
