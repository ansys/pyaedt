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

from typing import Iterable
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import quote_plus
import webbrowser

from ansys.aedt.core.generic.general_methods import PyAedtBase


class Help(PyAedtBase):  # pragma: no cover
    """Utility class to open PyAEDT documentation and related resources.

    This class provides convenience methods to open documentation, examples,
    GitHub pages, and community resources for PyAEDT.

    Features
    --------
    - Browser control.
    - Silent mode: return URLs without launching a browser.
    - Advanced search helper.
    - Helper methods for frequently accessed documentation pages.
    """

    _DOCS_ROOT = "https://aedt.docs.pyansys.com"
    _DEFAULT_VERSION = "stable"
    _EXAMPLES_ROOT = "https://examples.aedt.docs.pyansys.com"
    _GITHUB_ROOT = "https://github.com/ansys/pyaedt"

    def __init__(
        self,
        version: Optional[str] = None,
        browser: str = "default",
        silent: bool = False,
    ) -> None:
        """Initialize the Help utility.

        Parameters
        ----------
        version : str, optional
            Documentation version to use. The default is ``"stable"``.
        browser : str, optional
            Browser name recognized by :mod:`webbrowser`. Use ``"default"``
            to rely on the system default browser. The browser name is
            validated using :func:`webbrowser.get`.
        silent : bool, optional
            If ``True``, no browser windows are opened. All public methods
            only return URLs. The default is ``False``.
        """
        self._version = version or self._DEFAULT_VERSION
        self._browser = "default"  # will be validated by setter below
        self.browser = browser

        self._silent = bool(silent)

    @property
    def version(self) -> str:
        """Documentation version currently configured."""
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        """Set the documentation version."""
        if not value:
            raise ValueError("Version cannot be an empty string.")
        self._version = value

    @property
    def base_path(self) -> str:
        """Base URL of the PyAEDT documentation for the selected version."""
        return f"{self._DOCS_ROOT}/version/{self._version}"

    @property
    def examples_base(self) -> str:
        """Base URL of the PyAEDT examples site."""
        return self._EXAMPLES_ROOT

    @property
    def browser(self) -> str:
        """Browser currently configured for URL launching."""
        return self._browser

    @browser.setter
    def browser(self, value: str) -> None:
        """Set the browser used to open URLs.

        Parameters
        ----------
        value : str
            Browser name recognized by :mod:`webbrowser`, or ``"default"``.

        Raises
        ------
        ValueError
            If a non-default browser name is provided and
            :func:`webbrowser.get` cannot resolve it.
        """
        if value != "default":
            try:
                webbrowser.get(value)
            except webbrowser.Error as exc:  # type: ignore[attr-defined]
                raise ValueError(f"Invalid browser: {value!r}") from exc
        self._browser = value

    @property
    def silent(self) -> bool:
        """Whether URL opening is suppressed.

        If ``True``, URL-opening methods do not open the browser and only
        return the constructed URLs.
        """
        return self._silent

    @silent.setter
    def silent(self, value: bool) -> None:
        """Enable or disable silent mode."""
        self._silent = bool(value)

    def _launch_url(
        self,
        url: str,
        new_tab: bool = True,
    ) -> None:
        """Open a URL in the configured browser unless silent mode is enabled.

        Parameters
        ----------
        url : str
            URL to open.
        new_tab : bool, optional
            Whether to open the URL in a new browser tab. The default is
            ``True``.
        """
        if self.browser != "default":
            web_controller = webbrowser.get(self.browser)
        else:
            web_controller = webbrowser

        if new_tab:
            web_controller.open_new_tab(url)
        else:
            web_controller.open(url)

    @staticmethod
    def _build_search_query(
        keywords: Union[str, Iterable[str]],
    ) -> str:
        """Build a Sphinx-style search query string.

        Parameters
        ----------
        keywords : str or iterable of str
            One or more search terms.

        Returns
        -------
        str
            Search query.
        """
        if isinstance(keywords, str):
            keywords_list: List[str] = [keywords]
        else:
            keywords_list = list(keywords)

        keywords_list = [k.strip() for k in keywords_list if k and k.strip()]
        if not keywords_list:
            raise ValueError("At least one keyword is required for search.")

        query = " ".join(keywords_list)

        return quote_plus(query)

    def search(
        self,
        keywords: Union[str, Iterable[str]],
    ) -> str:
        """Search the PyAEDT documentation.

        Parameters
        ----------
        keywords : str or iterable of str
            One or more search terms.

        Returns
        -------
        str
            The constructed search URL.
        """
        query = self._build_search_query(keywords=keywords)
        url = f"{self.base_path}/search.html?q={query}"
        if not self.silent:
            self._launch_url(url)
        return url

    def home(self) -> str:
        """Open the top-level documentation page for the selected version.

        Returns
        -------
        str
            URL of the page.
        """
        url = f"{self.base_path}/index.html"
        if not self.silent:
            self._launch_url(url)
        return url

    def user_guide(self) -> str:
        """Open the PyAEDT User Guide.

        Returns
        -------
        str
            URL of the User Guide.
        """
        url = f"{self.base_path}/User_guide/index.html"
        if not self.silent:
            self._launch_url(url)
        return url

    def getting_started(self) -> str:
        """Open the PyAEDT Getting Started guide.

        Returns
        -------
        str
            URL of the Getting Started guide.
        """
        url = f"{self.base_path}/Getting_started/index.html"
        if not self.silent:
            self._launch_url(url)
        return url

    def installation_guide(self) -> str:
        """Open the PyAEDT installation instructions.

        Returns
        -------
        str
            URL of the Installation Guide.
        """
        url = f"{self.base_path}/Getting_started/Installation.html"
        if not self.silent:
            self._launch_url(url)
        return url

    def api_reference(self) -> str:
        """Open the PyAEDT API Reference page.

        Returns
        -------
        str
            URL of the API Reference.
        """
        url = f"{self.base_path}/API/index.html"
        if not self.silent:
            self._launch_url(url)
        return url

    def release_notes(self) -> str:
        """Open the PyAEDT release notes page.

        Returns
        -------
        str
            URL of the release notes page.
        """
        url = f"{self.base_path}/changelog.html"
        if not self.silent:
            self._launch_url(url)
        return url

    def examples(self) -> str:
        """Open the official PyAEDT examples website.

        Returns
        -------
        str
            URL of the examples site.
        """
        url = self.examples_base
        if not self.silent:
            self._launch_url(url)
        return url

    def github(self) -> str:
        """Open the PyAEDT GitHub repository.

        Returns
        -------
        str
            URL of the GitHub repository.
        """
        url = self._GITHUB_ROOT
        if not self.silent:
            self._launch_url(url)
        return url

    def changelog(
        self,
        release: Optional[str] = None,
    ) -> str:
        """Open the GitHub changelog page for a specific release.

        Parameters
        ----------
        release : str, optional
            Version tag. If omitted, the currently installed PyAEDT version is used.

        Returns
        -------
        str
            URL of the release notes page for the specified version.
        """
        if release is None:
            from ansys.aedt.core import __version__ as release

        url = f"{self._GITHUB_ROOT}/releases/tag/v{release}"
        if not self.silent:
            self._launch_url(url)
        return url

    def issues(self) -> str:
        """Open the PyAEDT GitHub issues page.

        Returns
        -------
        str
            URL of the issues page.
        """
        url = f"{self._GITHUB_ROOT}/issues"
        if not self.silent:
            self._launch_url(url)
        return url

    def ansys_forum(self) -> str:
        """Open the Ansys forum filtered to the PyAEDT tag.

        Returns
        -------
        str
            URL of the forum page.
        """
        url = "https://discuss.ansys.com/discussions/tagged/pyaedt"
        if not self.silent:
            self._launch_url(url)
        return url

    def developer_forum(self) -> str:
        """Open the Ansys Developer portal.

        Returns
        -------
        str
            URL of the developer portal.
        """
        url = "https://developer.ansys.com/"
        if not self.silent:
            self._launch_url(url)
        return url


online_help = Help()
