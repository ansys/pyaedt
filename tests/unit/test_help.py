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

"""Tests for the Help utility."""

from urllib.parse import parse_qs
from urllib.parse import urlparse
import webbrowser

import pytest

from ansys.aedt.core.help import Help


def test_base_paths():
    helper = Help(version="stable", silent=True)

    assert helper.base_path.endswith("/version/stable")
    assert helper.examples_base == "https://examples.aedt.docs.pyansys.com"


def test_version_setter_validation():
    helper = Help(version="stable", silent=True)

    with pytest.raises(ValueError):
        helper.version = ""

    helper.version = "dev"
    assert helper.version == "dev"
    assert helper.base_path.endswith("/version/dev")


def test_search_builds_url_and_respects_silent(monkeypatch):
    """Search should return URL and not open browser in silent mode."""

    def _fail_open(*args, **kwargs):
        raise AssertionError("Browser should not be opened in silent mode.")

    monkeypatch.setattr(webbrowser, "open_new_tab", _fail_open)
    monkeypatch.setattr(webbrowser, "open", _fail_open)

    helper = Help(version="stable", silent=True)

    url = helper.search("mesh")

    parsed = urlparse(url)
    assert parsed.path.endswith("/search.html")

    qs = parse_qs(parsed.query)
    assert "q" in qs
    assert qs["q"][0] == "mesh"


def test_search_raises_on_empty_keywords():
    helper = Help(version="stable", silent=True)

    with pytest.raises(ValueError):
        helper.search("")

    with pytest.raises(ValueError):
        helper.search([])


def test_search_multiple_keywords_encoding():
    helper = Help(version="stable", silent=True)

    url = helper.search(["mesh", "heat"])
    q_value = parse_qs(urlparse(url).query)["q"][0]

    assert "mesh" in q_value
    assert "heat" in q_value


@pytest.mark.parametrize(
    ("method_name", "expected_suffix"),
    [
        ("home", "/index.html"),
        ("user_guide", "/User_guide/index.html"),
        ("getting_started", "/Getting_started/index.html"),
        ("installation_guide", "/Getting_started/Installation.html"),
        ("api_reference", "/API/index.html"),
        ("release_notes", "/changelog.html"),
    ],
)
def test_helper_urls_under_base_path(method_name, expected_suffix, monkeypatch):
    """Helper methods should construct URLs under the base path and honor silent mode."""

    def _fail_open(*args, **kwargs):
        raise AssertionError("Browser should not be opened in silent mode.")

    monkeypatch.setattr(webbrowser, "open_new_tab", _fail_open)
    monkeypatch.setattr(webbrowser, "open", _fail_open)

    helper = Help(version="stable", silent=True)
    method = getattr(helper, method_name)

    url = method()
    assert url.startswith(helper.base_path)
    assert url.endswith(expected_suffix)


def test_examples_github_issues_forums_dev_urls(monkeypatch):
    """URLs that are not version-dependent should be fixed."""

    def _fail_open(*args, **kwargs):
        raise AssertionError("Browser should not be opened in silent mode.")

    monkeypatch.setattr(webbrowser, "open_new_tab", _fail_open)
    monkeypatch.setattr(webbrowser, "open", _fail_open)

    helper = Help(silent=True)

    assert helper.examples() == "https://examples.aedt.docs.pyansys.com"
    assert helper.github() == "https://github.com/ansys/pyaedt"
    assert helper.issues() == "https://github.com/ansys/pyaedt/issues"
    assert helper.ansys_forum() == "https://discuss.ansys.com/discussions/tagged/pyaedt"
    assert helper.developer_forum() == "https://developer.ansys.com/"


def test_changelog_with_explicit_release(monkeypatch):
    """changelog(release=...) should build the correct GitHub URL."""

    def _fail_open(*args, **kwargs):
        raise AssertionError("Browser should not be opened in silent mode.")

    monkeypatch.setattr(webbrowser, "open_new_tab", _fail_open)
    monkeypatch.setattr(webbrowser, "open", _fail_open)

    helper = Help(silent=True)

    url = helper.changelog(release="0.7.0")
    assert url == "https://github.com/ansys/pyaedt/releases/tag/v0.7.0"


def test_changelog_default_release_uses_installed_version(monkeypatch):
    """When release is None, changelog should use ansys.aedt.core.__version__."""

    def _fail_open(*args, **kwargs):
        raise AssertionError("Browser should not be opened in silent mode.")

    monkeypatch.setattr(webbrowser, "open_new_tab", _fail_open)
    monkeypatch.setattr(webbrowser, "open", _fail_open)

    monkeypatch.setattr("ansys.aedt.core.__version__", "1.2.3", raising=False)

    helper = Help(silent=True)
    url = helper.changelog()
    assert url == "https://github.com/ansys/pyaedt/releases/tag/v1.2.3"


def test_browser_validation(monkeypatch):
    """Browser setter should validate custom browsers via webbrowser.get."""

    class DummyController:
        def open_new_tab(self, *args, **kwargs):
            return True

        def open(self, *args, **kwargs):
            return True

    def fake_get(name):
        if name == "dummy":
            return DummyController()
        raise webbrowser.Error("No such browser.")

    monkeypatch.setattr(webbrowser, "get", fake_get)

    helper = Help(browser="dummy", silent=True)
    assert helper.browser == "dummy"

    with pytest.raises(ValueError):
        helper.browser = "this-browser-does-not-exist"


def test_non_silent_methods_open_browser(monkeypatch):
    """When silent is False, helper methods should call webbrowser.open_new_tab."""
    opened_urls = []

    class DummyController:
        def open_new_tab(self, url, *args, **kwargs):
            opened_urls.append(url)
            return True

        def open(self, url, *args, **kwargs):
            opened_urls.append(url)
            return True

    def fake_get(name="default"):
        return DummyController()

    monkeypatch.setattr(webbrowser, "get", fake_get)

    helper = Help(version="stable", browser="default", silent=False)

    url = helper.home()
    assert url in opened_urls
    assert url.endswith("/index.html")
