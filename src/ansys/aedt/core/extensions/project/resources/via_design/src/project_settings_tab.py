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

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk


def browse_project_file_action(entry_widget):
    """打开文件对话框选择项目保存路径并更新Entry"""
    filename = filedialog.asksaveasfilename(
        title="保存项目文件", filetypes=[("HFSS3DLayout项目文件", "*.via"), ("所有文件", "*.*")]
    )
    if filename:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filename)


def create_project_settings_ui(tab_frame, app_instance):
    # 项目设置区域
    project_main_frame = ttk.LabelFrame(tab_frame, text="Project")  # Renamed to avoid conflict
    project_main_frame.pack(fill="x", padx=5, pady=5)

    # 项目文件保存路径
    file_frame = ttk.Frame(project_main_frame)
    file_frame.pack(fill="x", padx=5, pady=5)
    ttk.Label(file_frame, text="Save Project File").pack(side="left")

    app_instance.project_path_entry = ttk.Entry(file_frame)
    app_instance.project_path_entry.insert(0, "D:\\AnsysChina\\HFSS3DLayoutPkgViaWizard\\output\\HFSS3DLayout_pkg_via")
    app_instance.project_path_entry.pack(side="left", expand=True, fill="x", padx=5)

    # Use lambda to pass the specific entry widget to the action
    browse_button = ttk.Button(
        file_frame, text="Browse", command=lambda: browse_project_file_action(app_instance.project_path_entry)
    )
    browse_button.pack(side="left")
    ttk.Button(file_frame, text="Save").pack(side="left", padx=5)  # 命令未定义

    # 运行脚本按钮
    run_frame = ttk.Frame(project_main_frame)
    run_frame.pack(fill="x", padx=5, pady=5)
    ttk.Button(run_frame, text="Run Scripts in HFSS3DLayout").pack(side="right")  # 命令未定义

    # 输出信息区域
    output_frame = ttk.LabelFrame(tab_frame, text="Output")  # Parent is tab_frame
    output_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # 创建文本框用于显示输出信息
    app_instance.output_text_widget = tk.Text(output_frame, wrap="word", height=10)  # Reduced height for example
    app_instance.output_text_widget.pack(fill="both", expand=True, padx=5, pady=5)

    # 添加示例输出
    sample_output = "[YYYY-MM-DD HH:MM:SS]: Importing PCB Stackup from file: 'path\\to\\file.csv'\n"
    sample_output += "[YYYY-MM-DD HH:MM:SS]: Import PCB Stackup completed."
    sample_output = "==> Involk Ansys Electronics Desktop 2025 R1...\n==> Generating project...\n==> Running..."
    app_instance.output_text_widget.insert("1.0", sample_output)
    app_instance.output_text_widget.config(state="disabled")  # 设置为只读

    # 底部按钮
    bottom_button_frame = ttk.Frame(tab_frame)  # Changed parent to tab_frame
    bottom_button_frame.pack(fill="x", padx=5, pady=5, side="bottom")
    ttk.Button(bottom_button_frame, text="Reset").pack(side="right", padx=5)  # 命令未定义
    ttk.Button(bottom_button_frame, text="Apply").pack(side="right")  # 命令未定义
