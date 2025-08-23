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

from PIL import Image
from PIL import ImageTk


def create_pin_map_settings_ui(tab_frame, app_instance):
    # 文件选择区域
    file_frame = ttk.Frame(tab_frame)
    file_frame.pack(fill="x", padx=5, pady=5)

    ttk.Label(file_frame, text="Pin Map File").grid(row=0, column=0, sticky="w")
    ttk.Entry(file_frame).grid(row=0, column=1, sticky="ew", padx=5)
    ttk.Button(file_frame, text="Browse").grid(row=0, column=2, padx=2)  # 命令未定义
    ttk.Button(file_frame, text="Import").grid(row=0, column=3, padx=2)  # 命令未定义
    file_frame.grid_columnconfigure(1, weight=1)

    # Pin Map 参数设置区域
    params_frame = ttk.Frame(tab_frame)
    params_frame.pack(fill="x", padx=5, pady=5)

    # 第一行参数
    ttk.Label(params_frame, text="Pitch X").grid(row=0, column=0)
    app_instance.pitch_x_entry = ttk.Entry(params_frame, width=15)
    app_instance.pitch_x_entry.insert(0, "1000um")
    app_instance.pitch_x_entry.grid(row=0, column=1)

    ttk.Label(params_frame, text="Pitch Y").grid(row=0, column=2, padx=5)
    app_instance.pitch_y_entry = ttk.Entry(params_frame, width=15)
    app_instance.pitch_y_entry.insert(0, "1000um")
    app_instance.pitch_y_entry.grid(row=0, column=3)

    ttk.Label(params_frame, text="Num of Single Nets").grid(row=0, column=4, padx=5)
    ttk.Combobox(params_frame, width=5, values=list(range(11))).grid(row=0, column=5)

    ttk.Label(params_frame, text="Num of Diff Pairs").grid(row=0, column=6, padx=5)
    ttk.Combobox(params_frame, width=5, values=list(range(1, 11))).grid(row=0, column=7)

    # Note: Original code has "Num of Rows" twice. Assuming this is intentional.
    ttk.Label(params_frame, text="Num of Rows").grid(row=0, column=8, padx=5)  # First "Num of Rows"
    ttk.Combobox(params_frame, width=5, values=list(range(1, 11))).grid(row=0, column=9)

    ttk.Label(params_frame, text="Num of Rows").grid(row=0, column=10, padx=5)  # Second "Num of Rows"
    ttk.Combobox(params_frame, width=5, values=list(range(1, 11))).grid(row=0, column=11)

    ttk.Button(params_frame, text="Generate").grid(row=0, column=12, padx=20)  # 命令未定义

    # 排列方式选择和示意图显示区域
    arrangement_frame = ttk.Frame(tab_frame)
    arrangement_frame.pack(fill="x", padx=5, pady=5)

    arrangements = [
        ("In Line", "in_line", "pin_map_01.png"),
        ("Staggered - Odd Rows", "stag_odd_rows", "pin_map_02.png"),
        ("Staggered - Even Rows", "stag_even_rows", "pin_map_03.png"),
        ("Staggered - Odd Columns", "stag_odd_cols", "pin_map_04.png"),
        ("Staggered - Even Columns", "stag_even_cols", "pin_map_05.png"),
    ]

    app_instance.arrangement_var = tk.StringVar(value="in_line")
    app_instance.demo_images = []

    # 为每个排列方式创建一个容器，包含radio和图片
    for text, value, image_file in arrangements:
        # 创建一个容器来包含radio和图片
        group_frame = ttk.Frame(arrangement_frame)
        group_frame.pack(side="left", padx=5)

        # 添加radio按钮
        radio = ttk.Radiobutton(group_frame, text=text, value=value, variable=app_instance.arrangement_var)
        radio.pack(anchor="w", pady=(0, 5))  # 将anchor改为'w'以实现左对齐

        try:
            # 加载并调整图片大小
            image_path = os.path.join(os.path.dirname(__file__), image_file)
            image = Image.open(image_path)

            # 设置固定宽度并保持宽高比
            target_width = 240
            width_percent = target_width / float(image.size[0])
            target_height = int((float(image.size[1]) * float(width_percent)))
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

            # 创建PhotoImage并保存引用
            photo = ImageTk.PhotoImage(image)
            app_instance.demo_images.append(photo)

            # 添加图片标签
            label = ttk.Label(group_frame, image=photo)
            label.pack()
        except Exception as e:
            ttk.Label(group_frame, text=f"无法加载图片: {e}").pack()

    # 预览区域
    preview_frame = ttk.Frame(tab_frame)
    preview_frame.pack(fill="both", expand=True, padx=5, pady=5)

    table_frame = ttk.Frame(preview_frame)
    table_frame.pack(side="left", fill="both", expand=True, padx=(0, 2))

    try:
        src_dir = app_instance.EXTENSION_RESOURCES_PATH
        image_path = src_dir / "image/pin_map_table_demo.png"  # 假设图片名为stackup_diagram.png
        image = Image.open(image_path)
        app_instance.pin_map_table_tk = ImageTk.PhotoImage(image)
        image_label = ttk.Label(table_frame, image=app_instance.pin_map_table_tk)
        image_label.pack(expand=True, anchor="w", fill="both")  # 添加anchor参数
    except FileNotFoundError:
        raise
        # ttk.Label(image_frame, text="图片未找到\n(stackup_diagram.png)").pack(expand=True)
    except Exception:
        raise
        # ttk.Label(image_frame, text=f"加载图片错误:\n{str(e)}").pack(expand=True)

    # # 创建画布用于显示引脚排列预览
    # app_instance.preview_canvas = tk.Canvas(preview_frame, bg='white')
    # app_instance.preview_canvas.pack(fill='both', expand=True)

    # 底部按钮
    button_frame = ttk.Frame(tab_frame)
    button_frame.pack(fill="x", padx=5, pady=5, side="bottom")  # side='bottom' added
    ttk.Button(button_frame, text="Reset").pack(side="right", padx=5)  # 命令未定义
    ttk.Button(button_frame, text="Apply").pack(side="right")  # 命令未定义
