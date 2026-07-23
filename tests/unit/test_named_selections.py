# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.modeler import NamedSelections

# NOTE: we avoid defining test-local helper classes; tests use MagicMock to
# simulate a user_lists object when needed.


@pytest.fixture
def named_selection_setup(request):
    """Fixture used to provide either a MagicMock NamedSelections or a real instance.

    By default (no indirect param) it yields a MagicMock(spec=NamedSelections).
    To get a real instance, parametrize the fixture with value "real":
        @pytest.mark.parametrize("named_selection_setup", ["real"], indirect=True)
        def test_x(named_selection_setup):
            # named_selection_setup is a real NamedSelections instance
    """
    mode = getattr(request, "param", "mock")
    if mode == "mock":
        with patch("ansys.aedt.core.modeler.cad.modeler.NamedSelections.__init__", lambda x: None):
            mock_instance = MagicMock(spec=NamedSelections)
            yield mock_instance
    elif mode == "real":
        # Create a fake modeler to attach to the real NamedSelections
        fake_modeler = MagicMock()
        fake_modeler.oeditor = MagicMock()
        fake_modeler.user_lists = []
        ns = NamedSelections(fake_modeler, props={}, name="ns_real")
        yield ns
    else:
        raise ValueError(f"Unknown fixture mode: {mode}")


@pytest.mark.parametrize("named_selection_setup", ["real"], indirect=True)
def test_create_and_delete_runs_real_method(named_selection_setup) -> None:
    """Create a real NamedSelections via the fixture and exercise the real delete() method.

    This verifies the delete implementation calls the editor and removes the instance
    from modeler.user_lists.
    """
    ns = named_selection_setup

    # Ensure the real instance has a modeler and is present in user_lists
    ns._modeler.user_lists.append(ns)
    ns._modeler.oeditor.Delete = MagicMock(return_value=None)

    assert ns.delete()

    # Verify the editor Delete was called with the expected arguments
    ns._modeler.oeditor.Delete.assert_called_once_with(
        [
            "NAME:Selections",
            "Selections:=",
            ns.name,
        ]
    )

    # Verify the named selection was removed from the modeler's user_lists
    assert ns not in ns._modeler.user_lists


@pytest.mark.parametrize("named_selection_setup", ["real"], indirect=True)
def test_delete_raises_when_user_lists_remove_fails(named_selection_setup) -> None:
    """Exercise delete() so that the internal removal from modeler.user_lists fails
    and the method raises AEDTRuntimeError("Failed to delete the named selection.").
    """
    ns = named_selection_setup

    # Replace the modeler's user_lists with a MagicMock that iterates over [ns]
    # but whose remove() does nothing, to simulate a failed removal.
    mock_lists = MagicMock()
    mock_lists.__iter__.return_value = iter([ns])
    mock_lists.remove = MagicMock(return_value=None)
    ns._modeler.user_lists = mock_lists

    # Make editor.Delete succeed
    ns._modeler.oeditor.Delete = MagicMock(return_value=None)

    # Now calling delete() should reach the final check and raise AEDTRuntimeError
    with pytest.raises(AEDTRuntimeError, match="Failed to delete the named selection."):
        ns.delete()


class TestNamedSelectionsRename:
    @pytest.mark.parametrize("named_selection_setup", ["real"], indirect=True)
    def test_rename_success(self, named_selection_setup) -> None:
        """Rename succeeds when the new name is not already present.

        Simplified: mock ChangeProperty, ensure rename updates local name and
        ChangeProperty is called.
        """
        ns = named_selection_setup
        new_name = "renamed_ns"

        # Mock ChangeProperty to do nothing
        ns._modeler.oeditor.ChangeProperty = MagicMock(return_value=None)

        # Simulate AEDT having the new named selection present after the rename
        new_ns = MagicMock()
        new_ns.name = new_name
        ns._modeler.user_lists = [new_ns]

        # Call rename and verify it returns True and updates ns.name
        assert ns.rename(new_name)
        assert ns.name == new_name

    @pytest.mark.parametrize("named_selection_setup", ["real"], indirect=True)
    def test_rename_failure_raises(self, named_selection_setup) -> None:
        """Rename raises AEDTRuntimeError when the new name is not present in modeler.user_lists."""
        ns = named_selection_setup
        # Mock ChangeProperty to do nothing
        ns._modeler.oeditor.ChangeProperty = MagicMock(return_value=None)
        # Simulate that ChangeProperty did not update modeler.user_lists: keep only ns
        ns._modeler.user_lists = [ns]

        # Now rename should raise because the new name is not found in user_lists
        with pytest.raises(AEDTRuntimeError, match="Failed to rename the named selection."):
            ns.rename("invalid")
