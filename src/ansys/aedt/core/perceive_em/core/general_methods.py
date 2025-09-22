# ruff: noqa: E402

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

import numpy as np

from ansys.aedt.core.aedt_logger import pyaedt_logger


def perceive_em_function_handler(func):
    """
    Decorator for handling function calls to the Perceive EM API.

    This decorator wraps methods that interact with the Perceive EM API and handles
    common error and warning cases. It logs any errors or warnings encountered during
    the API call and raises exceptions when necessary.

    The decorator attempts to determine the appropriate `radar_sensor_scenario` and `api`
    references based on standard naming conventions used in Perceive EM objects.

    Logging is handled through the PyAEDT logger.

    Examples
    --------
    >>> from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
    >>> class MyClass:
    >>>     def __init__(self, api, scenario):
    >>>         self.api = api
    >>>     @perceive_em_function_handler
    >>>     def do_something(self):
    >>>         return self._api.someCall()
    """

    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
        except Exception:
            pyaedt_logger.error(self._api.getLastError())
            raise Exception("Perceive EM API call failed.")

        if hasattr(self, "radar_sensor_scenario"):
            rss = self.radar_sensor_scenario
        elif hasattr(self, "_rss"):
            rss = self._rss
        elif hasattr(self, "_app") and hasattr(self._app, "radar_sensor_scenario"):
            rss = self._app.radar_sensor_scenario
        else:
            pyaedt_logger.error("Radar scenario module not found.")
            raise Exception

        if hasattr(self, "api"):
            api = self.api
        elif hasattr(self, "_api"):
            api = self._api
        elif hasattr(self, "_app") and hasattr(self._app, "api"):
            api = self._app.api
        else:
            pyaedt_logger.error("Radar scenario API not loaded.")
            raise Exception

        result_return = True
        if isinstance(result, tuple) and len(result) == 2:
            result_return = result[1]
            result = result[0]
        elif isinstance(result, np.ndarray):
            return result

        if isinstance(result, bool):
            return result

        if result == rss.RGpuCallStat.OK:
            return result_return
        elif result == rss.RGpuCallStat.RGPU_WARNING:
            pyaedt_logger.warning(api.getLastWarnings())
            return result_return
        elif result == rss.RGpuCallStat.RGPU_ERROR:
            pyaedt_logger.error(api.getLastError())
            raise Exception
        else:
            return result

    return wrapper
