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
from tkinter import ttk, messagebox, filedialog, PhotoImage
import json

from pathlib import Path

class Pin:
    def __init__(self, name=None, layer=None, x=None, y=None, diameter=None, via_type="Through"):
        self.name = name
        self.layer = layer
        self.x = x
        self.y = y
        self.diameter = diameter
        self.via_type = via_type
    
    def to_dict(self):
        return {
            "name": self.name,
            "layer": self.layer,
            "x": self.x,
            "y": self.y,
            "diameter": self.diameter,
            "via_type": self.via_type
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
            layer=data.get("layer"),
            x=data.get("x"),
            y=data.get("y"),
            diameter=data.get("diameter"),
            via_type=data.get("via_type", "Through")
        )

# 全局变量来管理 pin_map 的表格数据
pin_map_data = []

from PIL import Image
from PIL import ImageTk


def create_pin_map_settings_ui(tab_frame, app_instance):
    style = ttk.Style()
    style.configure("PyAEDT.Treeview", rowheight=25)
    style.map("PyAEDT.Treeview",
              foreground=[('selected', '#000000')],
              background=[('selected', '#CCE4F7')])


    # Pin Map 
    params_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    params_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=(5, 0))

    ttk.Label(params_frame, text="Pitch X", style="PyAEDT.TLabel").grid(row=0, column=0)
    app_instance.pitch_x_entry = ttk.Entry(params_frame, width=15)
    app_instance.pitch_x_entry.insert(0, "1000um")
    app_instance.pitch_x_entry.grid(row=0, column=1)
    
    ttk.Label(params_frame, text="Pitch Y", style="PyAEDT.TLabel").grid(row=0, column=2, padx=5)
    app_instance.pitch_y_entry = ttk.Entry(params_frame, width=15)
    app_instance.pitch_y_entry.insert(0, "1000um")
    app_instance.pitch_y_entry.grid(row=0, column=3)
    
    ttk.Label(params_frame, text="Num of Single Nets", style="PyAEDT.TLabel").grid(row=0, column=4, padx=5)
    app_instance.single_nets_combo = ttk.Combobox(params_frame, width=5, values=list(range(6)))
    app_instance.single_nets_combo.grid(row=0, column=5)
    app_instance.single_nets_combo.set("4")
    
    ttk.Label(params_frame, text="Num of Diff Pairs", style="PyAEDT.TLabel").grid(row=0, column=6, padx=5)
    app_instance.diff_pairs_combo = ttk.Combobox(params_frame, width=5, values=list(range(6)))
    app_instance.diff_pairs_combo.grid(row=0, column=7)
    app_instance.diff_pairs_combo.set("2")
    
    ttk.Label(params_frame, text="Num of Rows", style="PyAEDT.TLabel").grid(row=0, column=8, padx=5)
    app_instance.rows_combo = ttk.Combobox(params_frame, width=5, values=list(range(1, 11)), state="normal")
    app_instance.rows_combo.grid(row=0, column=9)
    app_instance.rows_combo.set("3")
    
    ttk.Label(params_frame, text="Num of Column", style="PyAEDT.TLabel").grid(row=0, column=10, padx=5)
    app_instance.columns_combo = ttk.Combobox(params_frame, width=5, values=list(range(1, 11)), state="normal")
    app_instance.columns_combo.grid(row=0, column=11)
    app_instance.columns_combo.set("3")
    
    ttk.Button(params_frame, text="Generate", command=lambda: generate_pin_map(app_instance), style="PyAEDT.TButton").grid(row=0, column=12, padx=20)


    # Pin Map table
    table_frame = ttk.LabelFrame(tab_frame, style="PyAEDT.TLabelframe")
    table_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=(0, 5))
    tab_frame.grid_rowconfigure(2, weight=1)
    tab_frame.grid_columnconfigure(0, weight=1)
    
    # 创建表格容器
    table_container = ttk.Frame(table_frame, style="PyAEDT.TFrame")
    table_container.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
    table_frame.grid_rowconfigure(1, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    
    # 创建滚动条
    canvas = tk.Canvas(table_container, bg='white')
    scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, style="PyAEDT.TFrame")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # 创建表格头部
    header_frame = ttk.Frame(scrollable_frame, style="PyAEDT.TFrame")
    header_frame.grid(row=0, column=0, sticky='ew', padx=2, pady=2)
    
    # 存储表格头部框架的引用
    app_instance.header_frame = header_frame
    
    # 初始化表格头部
    create_table_headers(app_instance)
    
    # 存储表格数据的容器
    app_instance.pin_grid_frame = ttk.Frame(scrollable_frame, style="PyAEDT.TFrame")
    app_instance.pin_grid_frame.grid(row=1, column=0, sticky='ew', padx=2, pady=2)

    # Bottom button
    button_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=4, column=0, sticky='ew', pady=5)
    
    # Configure button_frame to make it resizable
    button_frame.grid_columnconfigure(3, weight=1)  # Last column takes remaining space
    
    ttk.Button(button_frame, text="Reset", command=lambda: reset_pin_map(app_instance), style="PyAEDT.TButton").grid(row=0, column=0, padx=5, sticky='e')

    # 初始化表格数据存储
    app_instance.pin_grid_data = []
    app_instance.pin_grid_widgets = []
    
    # 初始化表格数据
    update_pin_tree(app_instance)
    

# Create table headers based on column count
def create_table_headers(app_instance):
    # Clear existing headers
    for widget in app_instance.header_frame.winfo_children():
        widget.destroy()
    
    # Get number of columns from the combo box
    try:
        num_columns = int(app_instance.columns_combo.get())
        num_columns = len(app_instance.config_model.pin_map[0])
    except (ValueError, AttributeError):
        num_columns = 10  # Default to 10 columns
    
    # Generate column names: Index + A, B, C, ...
    columns = ['Index']
    for i in range(num_columns):
        columns.append(chr(ord('A') + i))
    
    # Create header labels
    for i, col in enumerate(columns):
        width = 6 if col == 'Index' else 10
        label = ttk.Label(app_instance.header_frame, text=col, style="PyAEDT.TLabel", width=width, anchor='center')
        label.grid(row=0, column=i, padx=1, pady=1, sticky='ew')
        if col != 'Index':
            app_instance.header_frame.grid_columnconfigure(i, weight=1)

# Update table display
def update_pin_tree(app_instance, use_config_data=True):
    # 更新表格头部
    create_table_headers(app_instance)
    
    # 清空现有的控件和数据
    for widget_row in app_instance.pin_grid_widgets:
        for widget in widget_row:
            widget.destroy()
    app_instance.pin_grid_widgets.clear()
    app_instance.pin_grid_data.clear()
    
    # Get number of columns from the combo box
    try:
        num_columns = int(app_instance.columns_combo.get())
    except (ValueError, AttributeError):
        num_columns = 3  # Default to 3 columns
    
    # Get number of rows from the combo box
    try:
        num_rows = int(app_instance.rows_combo.get())
    except (ValueError, AttributeError):
        num_rows = 3  # Default to 3 rows
    
    # 动态生成下拉框选项
    pin_options = ["VSS", "VDD", "GND"]  # 基础选项
    
    # 从pin_map_data中提取生成的引脚名称
    if pin_map_data:
        generated_pin_names = [pin.name for pin in pin_map_data]
        pin_options.extend(generated_pin_names)
    
    # 如果存在config_model.pin_map，也添加其中的选项
    config_pin_map = None
    if use_config_data:
        try:
            if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'pin_map'):
                config_pin_map = app_instance.config_model.pin_map
                if config_pin_map:
                    # 从配置数据中提取所有唯一的引脚名称
                    for row in config_pin_map:
                        for pin_name in row:
                            if pin_name not in pin_options:
                                pin_options.append(pin_name)
        except AttributeError:
            pass
    
    # 去重并保持顺序
    pin_options = list(dict.fromkeys(pin_options))
    
    # 只在初始化时使用配置数据的行列数
    if use_config_data and config_pin_map:
        num_rows = len(config_pin_map)
        num_columns = len(config_pin_map[0]) if config_pin_map else num_columns
        # 更新combo box的值以反映实际数据
        app_instance.rows_combo.set(str(num_rows))
        app_instance.columns_combo.set(str(num_columns))
    
    # 创建指定行数的数据
    for row_idx in range(num_rows):
        # 创建行数据
        if config_pin_map and row_idx < len(config_pin_map):
            # 使用配置数据
            row_data = config_pin_map[row_idx][:num_columns]  # 确保不超过列数
            # 如果配置数据列数不足，用默认值填充
            while len(row_data) < num_columns:
                row_data.append("VSS")
        else:
            # 使用默认数据
            row_data = ["VSS"] * num_columns
        
        app_instance.pin_grid_data.append(row_data)
        
        # 创建行控件
        row_widgets = []
        
        # Index列（标签）
        index_label = ttk.Label(app_instance.pin_grid_frame, text=str(row_idx + 1), 
                               style="PyAEDT.TLabel", width=6, anchor='center')
        index_label.grid(row=row_idx, column=0, padx=1, pady=1, sticky='ew')
        row_widgets.append(index_label)
        
        # 动态列（下拉框）
        for col_idx in range(num_columns):
            combo = ttk.Combobox(app_instance.pin_grid_frame, values=pin_options, 
                               width=8, style="PyAEDT.TCombobox", state="readonly")
            # 设置实际值
            combo.set(row_data[col_idx])
            combo.grid(row=row_idx, column=col_idx + 1, padx=1, pady=1, sticky='ew')
            
            # 绑定值变化事件
            def on_combo_change(event, r=row_idx, c=col_idx):
                app_instance.pin_grid_data[r][c] = event.widget.get()
            combo.bind('<<ComboboxSelected>>', on_combo_change)
            
            row_widgets.append(combo)
            # 设置列权重
            app_instance.pin_grid_frame.grid_columnconfigure(col_idx + 1, weight=1)
        
        app_instance.pin_grid_widgets.append(row_widgets)


def save_pin_map_to_config(app_instance):
    """保存当前表格区域的数据为二维数组到config_model.pin_map"""
    try:
        if hasattr(app_instance, 'config_model'):
            # 确保config_model有pin_map属性
            if not hasattr(app_instance.config_model, 'pin_map'):
                app_instance.config_model.pin_map = []
            
            # 将当前表格的pin_grid_data保存为二维数组
            app_instance.config_model.pin_map = [row[:] for row in app_instance.pin_grid_data]  # 深拷贝
    except Exception as e:
        print(f"Error saving pin map to config: {e}")


# Generate pin map based on parameters
def generate_pin_map(app_instance):
    try:
        # 获取参数值
        pitch_x = app_instance.pitch_x_entry.get()
        pitch_y = app_instance.pitch_y_entry.get()
        num_rows = int(app_instance.rows_combo.get())
        num_cols = int(app_instance.columns_combo.get())
        num_single_nets = int(app_instance.single_nets_combo.get())
        num_diff_pairs = int(app_instance.diff_pairs_combo.get())
        # arrangement_type = app_instance.arrangement_var.get()
        
        # 清空现有的引脚
        pin_map_data.clear()
        
        # 计算引脚位置
        pin_count = 0
        default_diameter = "500um"
        default_layer = "Signal"
        
        # 根据排列方式计算引脚位置
        for row in range(num_rows):
            for col in range(num_cols):
                # 基础位置计算
                x_pos = f"{col * float(pitch_x.replace('um', '')):.2f}um"
                y_pos = f"{row * float(pitch_y.replace('um', '')):.2f}um"
                
                # 创建引脚
                pin_count += 1
                
                # 确定引脚类型和名称
                if pin_count <= num_single_nets:
                    pin_name = f"SIG_{pin_count}"
                    pin_type = "Through"
                elif pin_count <= num_single_nets + num_diff_pairs * 2:
                    diff_pair_num = (pin_count - num_single_nets - 1) // 2 + 1
                    is_positive = (pin_count - num_single_nets) % 2 == 1
                    pin_name = f"SIG_{diff_pair_num}_{'P' if is_positive else 'N'}"
                    pin_type = "Through"
                else:
                    # 如果超出了指定的引脚数量，就停止生成
                    break
                
                # 添加引脚
                pin = Pin(
                    name=pin_name,
                    layer=default_layer,
                    x=x_pos,
                    y=y_pos,
                    diameter=default_diameter,
                    via_type=pin_type
                )
                pin_map_data.append(pin)
        
        # 更新表格显示（不使用config数据，按用户设置的行列数）
        update_pin_tree(app_instance, use_config_data=False)
        
        # Generate完成后，保存当前表格数据到config_model
        save_pin_map_to_config(app_instance)
        
        messagebox.showinfo("Success", f"Generated {len(pin_map_data)} pins")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate pin map: {str(e)}")


def reset_pin_map(app_instance):
    """Reset the pin map configuration to default values from config_model.
    
    Args:
        app_instance: The main application instance containing pin map data
    """
    confirmation_msg = "Are you sure you want to reset the pin map? All changes will be lost."
    if messagebox.askyesno("Confirmation", confirmation_msg):
        # 从config_model.pin_map读取默认值并更新表格
        update_pin_tree(app_instance, use_config_data=True)
