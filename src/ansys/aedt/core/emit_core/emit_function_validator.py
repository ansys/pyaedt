# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""EMIT function validator for restricted math expressions."""

import ast

from ansys.aedt.core.emit_core.emit_constants import EMIT_FN_ALLOWED_FUNCS
from ansys.aedt.core.emit_core.emit_constants import EMIT_FN_ALLOWED_VARS


class FunctionValidator(ast.NodeVisitor):
    """AST validator for a restricted math expression grammar.

    This class validates mathematical expressions using an Abstract Syntax Tree (AST)
    visitor pattern. It enforces a restricted grammar that only allows specific
    operations, functions, and variables.

    Allowed operations and elements:
        - Binary operators: +, -, *, /
        - Numbers: integers and floats
        - Variables: RF, IF, LO
        - Function calls: abs(x), trunc(x)
        - Parentheses: via AST grouping
    """

    def visit_Module(self, node: ast.Module) -> None:
        """Visit a Module node.

        Parameters
        ----------
        node : ast.Module
            The Module node to visit. Expected to contain a single expression
            when using mode="eval".
        """
        for stmt in node.body:
            self.visit(stmt)

    def visit_Expr(self, node: ast.Expr) -> None:
        """Visit an Expr node.

        Parameters
        ----------
        node : ast.Expr
            The Expr node to visit.
        """
        self.visit(node.value)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Visit a BinOp node.

        Only allows addition, subtraction, multiplication, and division operators.

        Parameters
        ----------
        node : ast.BinOp
            The BinOp node to visit.

        Raises
        ------
        ValueError
            If the operator is not one of +, -, *, /.
        """
        if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            raise ValueError("Only +, -, *, / are allowed")
        self.visit(node.left)
        self.visit(node.right)

    def visit_Call(self, node: ast.Call) -> None:
        """Visit a Call node.

        Only allows simple function calls with bare function names (e.g., abs(), trunc()).
        Functions must be in the allowed list and accept exactly one positional argument.

        Parameters
        ----------
        node : ast.Call
            The Call node to visit.

        Raises
        ------
        ValueError
            If the function call is not a simple function name, if the function is not
            in the allowed list, if keyword arguments are used, or if the number of
            arguments is not exactly one.
        """
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls are allowed")
        func_name = node.func.id
        if func_name not in EMIT_FN_ALLOWED_FUNCS:
            raise ValueError(f"Function not allowed: {func_name}")
        if len(node.keywords) != 0:
            raise ValueError("Keyword arguments are not allowed")
        if len(node.args) != 1:
            raise ValueError("Only one positional argument allowed")
        self.visit(node.args[0])

    def visit_Name(self, node: ast.Name) -> None:
        """Visit a Name node.

        Only allows specific variable names defined in the allowed variables list.

        Parameters
        ----------
        node : ast.Name
            The Name node to visit.

        Raises
        ------
        ValueError
            If the variable name is not in the allowed list.
        """
        if node.id not in EMIT_FN_ALLOWED_VARS:
            raise ValueError(f"Unknown variable: {node.id}")

    def visit_Constant(self, node: ast.Constant) -> None:
        """Visit a Constant node.

        Only allows numeric constants (integers and floats).

        Parameters
        ----------
        node : ast.Constant
            The Constant node to visit.

        Raises
        ------
        ValueError
            If the constant is not a numeric type (int or float).
        """
        if not isinstance(node.value, (int, float)):
            raise ValueError("Only numeric constants allowed")

    def generic_visit(self, node: ast.AST) -> None:
        """Visit any other node type.

        This method is called for node types not explicitly handled by other
        visit methods. It delegates to the parent class implementation.

        Parameters
        ----------
        node : ast.AST
            The AST node to visit.
        """
        return super().generic_visit(node)
