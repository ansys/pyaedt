import os

import ansys.aedt.core
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog  # 如果需要为浏览按钮添加功能


def create_stackup_settings_ui(tab_frame,
                               app_instance):
    # 文件选择区域
    file_frame = ttk.Frame(tab_frame)
    file_frame.pack(fill='x')

    ttk.Label(file_frame, text="Material Model File").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    ttk.Entry(file_frame).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
    ttk.Button(file_frame, text="Browse").grid(row=0, column=2, padx=2, pady=5)

    ttk.Label(file_frame, text="Stackup Settings File").grid(row=1, column=0, sticky='w', padx=5, pady=5)
    ttk.Entry(file_frame).grid(row=1, column=1, sticky='ew', padx=5, pady=5)
    ttk.Button(file_frame, text="Browse").grid(row=1, column=2, padx=2, pady=5)
    ttk.Button(file_frame, text="Import").grid(row=1, column=3, padx=5, pady=5)
    file_frame.grid_columnconfigure(1, weight=1)

    # 参数设置区域
    params_frame = ttk.Frame(tab_frame)
    params_frame.pack(fill='x')

    # 第一行参数
    ttk.Label(params_frame, text="PP Thickness(um)").grid(row=0, column=0, padx=(5, 5), pady=5, sticky='w')
    ttk.Entry(params_frame, width=15).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="PP Material").grid(row=0, column=2, padx=5, pady=5, sticky='w')
    ttk.Combobox(params_frame, width=12).grid(row=0, column=3, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="Core Thickness(um)").grid(row=0, column=4, padx=5, pady=5, sticky='w')
    ttk.Entry(params_frame, width=15).grid(row=0, column=5, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="Core Material").grid(row=0, column=6, padx=5, pady=5, sticky='w')
    ttk.Combobox(params_frame, width=12).grid(row=0, column=7, sticky='ew', padx=5, pady=5)

    # 第二行参数
    ttk.Label(params_frame, text="Metal Thickness(um)").grid(row=1, column=0, padx=(5, 5), pady=5, sticky='w')
    ttk.Entry(params_frame, width=15).grid(row=1, column=1, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="Metal Material").grid(row=1, column=2, padx=5, pady=5, sticky='w')
    ttk.Combobox(params_frame, width=12).grid(row=1, column=3, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="Soldermask Thickness(um)").grid(row=1, column=4, padx=5, pady=5, sticky='w')
    ttk.Entry(params_frame, width=15).grid(row=1, column=5, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="Soldermask Material").grid(row=1, column=6, padx=5, pady=5, sticky='w')
    ttk.Combobox(params_frame, width=12).grid(row=1, column=7, sticky='ew', padx=5, pady=5)

    for i in [1, 3, 5, 7]:
        params_frame.grid_columnconfigure(i, weight=1)

    # 层数选择和生成按钮
    layer_frame = ttk.Frame(tab_frame)
    layer_frame.pack(fill='x')
    ttk.Label(layer_frame, text="Number Of Metal Layers").pack(side='left', padx=5, pady=5)
    ttk.Combobox(layer_frame, width=5, values=[2, 4, 6, 8, 10, 12]).pack(side='left', padx=5, pady=5)
    ttk.Button(layer_frame, text="Generate").pack(side='left', padx=20, pady=5)

    # 表格区域
    # 创建一个水平布局的Frame来容纳表格和图片
    table_image_frame = ttk.Frame(tab_frame)
    table_image_frame.pack(fill='both', expand=True, pady=(5, 0))

    # 表格区域 - 占据75%的宽度
    table_frame = ttk.Frame(table_image_frame)
    table_frame.pack(side='left', fill='both', expand=True, padx=(0, 2))

    image_frame = ttk.Frame(table_image_frame)
    image_frame.pack(side='right', fill='both', padx=(2, 0))

    try:
        script_dir = os.path.dirname(__file__)
        image_path = os.path.join(script_dir, "stackup_table_demo.png")  # 假设图片名为stackup_diagram.png
        image = Image.open(image_path)
        app_instance.stackup_tree = ImageTk.PhotoImage(image)
        image_label = ttk.Label(table_frame, image=app_instance.stackup_tree)
        image_label.pack(expand=True)
    except FileNotFoundError:
        ttk.Label(image_frame, text="图片未找到\n(stackup_diagram.png)").pack(expand=True)
    except Exception as e:
        ttk.Label(image_frame, text=f"加载图片错误:\n{str(e)}").pack(expand=True)

    # # 创建表格
    # columns = ('Layer Name', 'Thickness(um)', 'Metal Material', 'Dielectric Material', 'Via Routing', 'Trace Routing')
    # app_instance.stackup_tree = ttk.Treeview(table_frame, columns=columns, show='headings')

    # # 设置列标题
    # for col in columns:
    #     app_instance.stackup_tree.heading(col, text=col)
    #     app_instance.stackup_tree.column(col, width=100)

    # app_instance.stackup_tree.pack(fill='both', expand=True)

    # 图片区域 - 占据25%的宽度

    try:
        script_dir = os.path.dirname(__file__)
        image_path = os.path.join(script_dir, "stackup_demo.png")  # 假设图片名为stackup_diagram.png
        image = Image.open(image_path)
        app_instance.diagram_image = ImageTk.PhotoImage(image)
        image_label = ttk.Label(image_frame, image=app_instance.diagram_image)
        image_label.pack(expand=True)
    except FileNotFoundError:
        ttk.Label(image_frame, text="图片未找到\n(stackup_diagram.png)").pack(expand=True)
    except Exception as e:
        ttk.Label(image_frame, text=f"加载图片错误:\n{str(e)}").pack(expand=True)

    # 底部按钮
    button_frame = ttk.Frame(tab_frame)
    button_frame.pack(fill='x', pady=5, side='bottom')
    ttk.Button(button_frame, text="Reset").pack(side='right', padx=5)
    ttk.Button(button_frame, text="Apply").pack(side='right')
