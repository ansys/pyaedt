# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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


def post_processor(app=None, project=None, design=None, version=None):
    """PostProcessor.

    Returns
    -------
    :class:`ansys.aedt.core.visualization.post.post_common_3d.PostProcessor3D` or
    :class:`ansys.aedt.core.visualization.post.post_icepak.PostProcessorIcepak` or
    :class:`ansys.aedt.core.visualization.post.post_circuit.PostProcessorCircuit`
        PostProcessor object.
    """
    if not app:
        from ansys.aedt.core.generic.design_types import get_pyaedt_app
        from ansys.aedt.core.generic.desktop_sessions import _desktop_sessions

        if not _desktop_sessions:
            from ansys.aedt.core.desktop import Desktop

            d = Desktop(version=version, non_graphical=True)
        else:
            d = _desktop_sessions.values()[0]
        app = get_pyaedt_app(project_name=project, design_name=design, desktop=d)
    app.logger.reset_timer()
    PostProcessor = None
    if app:
        if app.design_type == "Icepak":
            from ansys.aedt.core.visualization.post.post_icepak import PostProcessorIcepak as PostProcessor
        elif app.design_type in ["Twin Builder", "RMxprt", "RMxprtSolution", "Circuit Design", "Circuit Netlist"]:
            from ansys.aedt.core.visualization.post.post_circuit import PostProcessorCircuit as PostProcessor
        else:
            from ansys.aedt.core.visualization.post.post_common_3d import PostProcessor3D as PostProcessor
    if PostProcessor:
        _post = PostProcessor(app)
        app.logger.info_timer("Post class has been initialized!")
        return _post
    app.logger.error("Failed to initialize Post Processor!")
    return None
