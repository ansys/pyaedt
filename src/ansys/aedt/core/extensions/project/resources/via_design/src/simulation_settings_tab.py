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

import os
import tkinter as tk
from tkinter import ttk


def create_simulation_settings_ui(tab_frame, app_instance):
    # 创建一个主 Canvas 用于滚动
    canvas = tk.Canvas(tab_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 创建一个垂直滚动条
    scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 配置 Canvas
    canvas.configure(yscrollcommand=scrollbar.set)

    # 创建一个 Frame 放置在 Canvas 中，所有内容将在这个 Frame 里
    scrollable_frame = ttk.Frame(canvas)

    # 将 scrollable_frame 添加到 canvas 窗口
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # 当 scrollable_frame 的大小改变时，更新 canvas 的滚动区域
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    # 当 Canvas 大小改变时，调整 scrollable_frame 的宽度
    def on_canvas_configure(event):
        # 更新 scrollable_frame 的宽度以匹配 canvas
        canvas.itemconfig(canvas_window, width=event.width)

    scrollable_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    # 将原有的 sweep_frame 改为 scrollable_frame 的子控件
    sweep_frame = ttk.Frame(scrollable_frame)
    sweep_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # 以下是原有的所有组件代码，父控件改为 sweep_frame
    # 频率扫描设置

    # 扫描名称和启用选项
    name_frame = ttk.Frame(sweep_frame)
    name_frame.pack(fill="x", padx=5, pady=2)
    ttk.Label(name_frame, text="Sweep Name:").pack(side="left")
    sweep_name = ttk.Entry(name_frame, width=30)
    sweep_name.insert(0, "SweepHfss")
    sweep_name.pack(side="left", padx=5)
    enabled_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(name_frame, text="Enabled", variable=enabled_var).pack(side="left", padx=20)
    use_q3d_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(name_frame, text="Use Q3D to solve DC point", variable=use_q3d_var).pack(side="left")

    # 扫描类型
    type_frame = ttk.Frame(sweep_frame)
    type_frame.pack(fill="x", padx=5, pady=2)
    ttk.Label(type_frame, text="Sweep Type:").pack(side="left")
    sweep_type = ttk.Combobox(type_frame, width=20, values=["Interpolating", "Discrete", "Broadband Fast"])
    sweep_type.set("Interpolating")
    sweep_type.pack(side="left", padx=5)

    # 频率扫描表格
    table_frame = ttk.LabelFrame(sweep_frame, text="Frequency Sweep")
    table_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # 创建表格
    columns = ("Type", "Start", "End", "Step size")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # 添加示例数据
    tree.insert("", "end", values=("Linear Step", "0GHz", "10GHz", "0.05GHz"))

    # 添加滚动条
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 按钮组
    button_frame = ttk.Frame(table_frame)
    button_frame.pack(fill="x", padx=5, pady=5)
    ttk.Button(button_frame, text="Add Above").pack(side="left", padx=2)
    ttk.Button(button_frame, text="Add Below").pack(side="left", padx=2)
    ttk.Button(button_frame, text="Delete Selection").pack(side="left", padx=2)
    ttk.Button(button_frame, text="Preview...").pack(side="left", padx=2)

    # 时域计算按钮
    ttk.Button(table_frame, text="Time Domain Calculation...").pack(side="right", padx=5, pady=5)

    # 选项设置
    options_frame = ttk.LabelFrame(sweep_frame, text="Options")
    options_frame.pack(fill="x", padx=5, pady=5)
    save_fields_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(options_frame, text="Save fields", variable=save_fields_var).pack(anchor="w", padx=5)
    save_rad_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(options_frame, text="Save radiated fields only", variable=save_rad_var).pack(anchor="w", padx=25)

    # S矩阵求解设置
    matrix_frame = ttk.LabelFrame(sweep_frame, text="S-Matrix Only Solve")
    matrix_frame.pack(fill="x", padx=5, pady=5)
    solve_type = tk.StringVar(value="auto")
    ttk.Radiobutton(matrix_frame, text="Auto", variable=solve_type, value="auto").pack(anchor="w", padx=5)
    ttk.Radiobutton(matrix_frame, text="Manual", variable=solve_type, value="manual").pack(anchor="w", padx=5)

    freq_frame = ttk.Frame(matrix_frame)
    freq_frame.pack(fill="x", padx=25, pady=2)
    ttk.Label(freq_frame, text="Allow for frequencies above").pack(side="left")
    freq_entry = ttk.Entry(freq_frame, width=10)
    freq_entry.insert(0, "1")
    freq_entry.pack(side="left", padx=5)
    ttk.Combobox(freq_frame, width=5, values=["MHz"]).pack(side="left")

    # 创建Setup Name和Enabled选项
    setup_frame = ttk.Frame(sweep_frame)
    setup_frame.pack(fill="x", padx=5, pady=2)
    ttk.Label(setup_frame, text="Setup Name:").pack(side="left")
    setup_name = ttk.Entry(setup_frame, width=20)
    setup_name.insert(0, "HFSS Setup 1")
    setup_name.pack(side="left", padx=5)
    setup_enabled = tk.BooleanVar(value=True)
    ttk.Checkbutton(setup_frame, text="Enabled", variable=setup_enabled).pack(side="left", padx=5)

    # 自适应求解设置
    adaptive_frame = ttk.LabelFrame(sweep_frame, text="Adaptive Solutions")
    adaptive_frame.pack(fill="x", padx=5, pady=5)

    # 求解频率选项
    freq_type = tk.StringVar(value="single")
    ttk.Label(adaptive_frame, text="Solution Frequency:").pack(anchor="w", padx=5, pady=2)
    freq_options_frame = ttk.Frame(adaptive_frame)
    freq_options_frame.pack(fill="x", padx=25)
    ttk.Radiobutton(freq_options_frame, text="Single", variable=freq_type, value="single").pack(side="left")
    ttk.Radiobutton(freq_options_frame, text="Multi-Frequencies", variable=freq_type, value="multi").pack(
        side="left", padx=20
    )
    ttk.Radiobutton(freq_options_frame, text="Broadband", variable=freq_type, value="broadband").pack(side="left")

    # 频率设置
    freq_frame = ttk.Frame(adaptive_frame)
    freq_frame.pack(fill="x", padx=25, pady=2)
    ttk.Label(freq_frame, text="Frequency").pack(side="left")
    freq_entry = ttk.Entry(freq_frame, width=15)
    freq_entry.insert(0, "8")
    freq_entry.pack(side="left", padx=5)
    freq_unit = ttk.Combobox(freq_frame, width=5, values=["GHz"])
    freq_unit.set("GHz")
    freq_unit.pack(side="left")

    # 最大迭代次数
    iter_frame = ttk.Frame(adaptive_frame)
    iter_frame.pack(fill="x", padx=25, pady=2)
    ttk.Label(iter_frame, text="Maximum Number of").pack(side="left")
    iter_entry = ttk.Entry(iter_frame, width=15)
    iter_entry.insert(0, "20")
    iter_entry.pack(side="left", padx=5)

    # 收敛条件选择
    conv_type = tk.StringVar(value="delta_s")
    ttk.Radiobutton(adaptive_frame, text="Maximum Delta S", variable=conv_type, value="delta_s").pack(
        anchor="w", padx=25
    )
    delta_frame = ttk.Frame(adaptive_frame)
    delta_frame.pack(fill="x", padx=45)
    delta_entry = ttk.Entry(delta_frame, width=15)
    delta_entry.insert(0, "0.02")
    delta_entry.pack(side="left")

    ttk.Radiobutton(adaptive_frame, text="Use Matrix Convergence", variable=conv_type, value="matrix").pack(
        anchor="w", padx=25
    )
    ttk.Button(adaptive_frame, text="Set Magnitude and Phase...").pack(anchor="w", padx=45)

    # 字段设置
    fields_frame = ttk.LabelFrame(sweep_frame, text="Fields")
    fields_frame.pack(fill="x", padx=5, pady=5)
    save_fields = tk.BooleanVar(value=False)
    ttk.Checkbutton(fields_frame, text="Save fields", variable=save_fields).pack(anchor="w", padx=5)
    save_rad = tk.BooleanVar(value=False)
    ttk.Checkbutton(fields_frame, text="Save radiated fields only", variable=save_rad).pack(anchor="w", padx=25)

    # 底部按钮
    bottom_frame = ttk.Frame(sweep_frame)
    bottom_frame.pack(fill="x", padx=5, pady=5)
    ttk.Button(bottom_frame, text="Use Defaults").pack(side="left")
    ttk.Button(bottom_frame, text="HPC and Analysis Options...").pack(side="right")

    # 初始网格选项
    mesh_frame = ttk.LabelFrame(sweep_frame, text="Initial Mesh Options")
    mesh_frame.pack(fill="x", padx=5, pady=5)

    # Lambda细化选项
    lambda_var = tk.BooleanVar(value=True)
    lambda_frame = ttk.Frame(mesh_frame)
    lambda_frame.pack(fill="x", padx=5, pady=2)
    ttk.Checkbutton(lambda_frame, text="Do Lambda Refinement", variable=lambda_var).pack(side="left")
    lambda_entry = ttk.Entry(lambda_frame, width=15)
    lambda_entry.insert(0, "0.66667")
    lambda_entry.pack(side="left", padx=5)
    default_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(lambda_frame, text="Use Default Value", variable=default_var).pack(side="left", padx=5)

    # 自适应选项
    adaptive_options_frame = ttk.LabelFrame(sweep_frame, text="Adaptive Options")
    adaptive_options_frame.pack(fill="x", padx=5, pady=5)

    # 最大细化设置
    max_refine_frame = ttk.Frame(adaptive_options_frame)
    max_refine_frame.pack(fill="x", padx=5, pady=2)
    ttk.Label(max_refine_frame, text="Maximum Refinement Per Pass:").pack(side="left")
    max_refine_entry = ttk.Entry(max_refine_frame, width=15)
    max_refine_entry.insert(0, "30")
    max_refine_entry.pack(side="left", padx=5)
    ttk.Label(max_refine_frame, text="%").pack(side="left")

    # 最大细化限制
    max_refine_limit_frame = ttk.Frame(adaptive_options_frame)
    max_refine_limit_frame.pack(fill="x", padx=5, pady=2)
    max_limit_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(max_refine_limit_frame, text="Maximum Refinement:", variable=max_limit_var).pack(side="left")
    max_limit_entry = ttk.Entry(max_refine_limit_frame, width=15)
    max_limit_entry.insert(0, "1000000")
    max_limit_entry.pack(side="left", padx=5)

    # 最小通过次数
    min_pass_frame = ttk.Frame(adaptive_options_frame)
    min_pass_frame.pack(fill="x", padx=5, pady=2)
    ttk.Label(min_pass_frame, text="Minimum Number of Passes:").pack(side="left")
    min_pass_entry = ttk.Entry(min_pass_frame, width=15)
    min_pass_entry.insert(0, "1")
    min_pass_entry.pack(side="left", padx=5)

    # 最小收敛通过次数
    min_conv_frame = ttk.Frame(adaptive_options_frame)
    min_conv_frame.pack(fill="x", padx=5, pady=2)
    ttk.Label(min_conv_frame, text="Minimum Converged Passes:").pack(side="left")
    min_conv_entry = ttk.Entry(min_conv_frame, width=15)
    min_conv_entry.insert(0, "1")
    min_conv_entry.pack(side="left", padx=5)

    # 求解选项
    solution_frame = ttk.LabelFrame(sweep_frame, text="Solution Options")
    solution_frame.pack(fill="x", padx=5, pady=5)

    # 基函数顺序
    basis_frame = ttk.Frame(solution_frame)
    basis_frame.pack(fill="x", padx=5, pady=2)
    ttk.Label(basis_frame, text="Order of Basis Functions:").pack(side="left")
    basis_combo = ttk.Combobox(basis_frame, width=15, values=["Mixed Order"])
    basis_combo.set("Mixed Order")
    basis_combo.pack(side="left", padx=5)

    # 求解器选择
    solver_var = tk.StringVar(value="direct")
    ttk.Radiobutton(solution_frame, text="Auto Select Direct/Iterative", variable=solver_var, value="auto").pack(
        anchor="w", padx=5
    )
    ttk.Radiobutton(solution_frame, text="Direct Solver", variable=solver_var, value="direct").pack(anchor="w", padx=5)
    ttk.Radiobutton(solution_frame, text="Iterative Solver", variable=solver_var, value="iterative").pack(
        anchor="w", padx=5
    )

    # 相对残差
    residual_frame = ttk.Frame(solution_frame)
    residual_frame.pack(fill="x", padx=25, pady=2)
    ttk.Label(residual_frame, text="Relative Residual:").pack(side="left")
    residual_entry = ttk.Entry(residual_frame, width=15)
    residual_entry.insert(0, "0.0001")
    residual_entry.pack(side="left", padx=5)

    # 底部按钮
    button_frame = ttk.Frame(sweep_frame)
    button_frame.pack(fill="x", padx=5, pady=5, side="bottom")
    ttk.Button(button_frame, text="Apply").pack(side="right", padx=5)
    ttk.Button(button_frame, text="Cancel").pack(side="right")

    # 绑定鼠标滚轮事件 (可选, 增强用户体验)
    def _on_mousewheel(event):
        # 根据操作系统调整滚动方向和单位
        if os.name == "nt":  # Windows
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif os.name == "posix":  # Linux/macOS
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

    # 绑定到 Canvas 和其子控件，以便在任何地方滚动都有效
    canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows, some Linux
    canvas.bind_all("<Button-4>", _on_mousewheel)  # Linux (scroll up)
    canvas.bind_all("<Button-5>", _on_mousewheel)  # Linux (scroll down)
