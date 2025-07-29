import tkinter as tk
from tkinter import ttk
import os
import webbrowser

def create_help_tab_ui(tab_frame, app_instance):
    # 创建主Frame
    main_frame = ttk.Frame(tab_frame)
    main_frame.pack(fill='both', expand=True)

    # 文档链接区域
    doc_frame = ttk.LabelFrame(main_frame, text='Documentation')
    doc_frame.pack(fill='x', padx=5, pady=5)

    # 检查PDF文件是否存在
    pdf_path = os.path.join(os.path.dirname(__file__), 'user_manual.pdf')
    
    if os.path.exists(pdf_path):
        # 创建超链接按钮
        def open_pdf():
            webbrowser.open(pdf_path)
            
        link = ttk.Button(doc_frame, 
                         text='Open User Manual (PDF)',
                         command=open_pdf,
                         style='Hyperlink.TButton')
        link.pack(pady=10)
    else:
        ttk.Label(doc_frame, text='PDF documentation not found').pack(pady=10)

    # 下方项目信息区域（保持原有代码不变）
    info_frame = ttk.LabelFrame(main_frame, text='Project Information')
    info_frame.pack(fill='x', padx=5, pady=5)

    # 项目信息内容
    info_content = ttk.Frame(info_frame)
    info_content.pack(fill='both', expand=True, padx=10, pady=5)

    # 使用Grid布局来更好地组织信息
    row = 0
    
    # 版本信息
    ttk.Label(info_content, text='Version:', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=(5,0))
    ttk.Label(info_content, text='0.1').grid(row=row, column=1, sticky='w')
    
    row += 1
    # 作者信息
    ttk.Label(info_content, text='Authors:', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=(15,0))
    authors = ['Hui Zhou - Maintainer', 'Zhen Guo - Maintainer', 'Haiwen Zhang - Maintainer', 'Johnny Feng - Documentation']
    for author in authors:
        row += 1
        ttk.Label(info_content, text=f'• {author}').grid(row=row, column=0, columnspan=2, sticky='w', padx=20)
    
    row += 1
    # 联系方式
    ttk.Label(info_content, text='Contact:', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=(15,0))
    row += 1
    ttk.Label(info_content, text='Email: support@ansy.com').grid(row=row, column=0, columnspan=2, sticky='w', padx=20)
    row += 1
    ttk.Label(info_content, text='Website: https://www.ansys.com').grid(row=row, column=0, columnspan=2, sticky='w', padx=20)
    
    row += 1
    # 版权信息
    ttk.Label(info_content, text='Copyright:', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=(15,0))
    row += 1
    ttk.Label(info_content, text='© 2025 Ansys. All rights reserved.').grid(row=row, column=0, columnspan=2, sticky='w', padx=20)

    # 配置列的权重
    info_content.grid_columnconfigure(1, weight=1)