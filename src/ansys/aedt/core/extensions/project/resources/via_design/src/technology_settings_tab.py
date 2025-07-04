import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

def create_technology_settings_ui(tab_frame, app_instance):
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

    # --- 原有的UI元素现在都放置在 scrollable_frame 中 ---

    # 单位选择区域
    unit_frame = ttk.Frame(scrollable_frame) # 修改父控件为 scrollable_frame
    unit_frame.pack(fill='x', padx=5, pady=5)
    ttk.Label(unit_frame, text="Length Unit:").pack(side='left')
    app_instance.length_unit = ttk.Combobox(unit_frame, width=5, values=['mm', 'um'])
    app_instance.length_unit.set('um')
    app_instance.length_unit.pack(side='left', padx=5)
    ttk.Label(unit_frame, text="Angle Unit:").pack(side='left', padx=5)
    app_instance.angle_unit = ttk.Combobox(unit_frame, width=5, values=['deg'])
    app_instance.angle_unit.set('deg')
    app_instance.angle_unit.pack(side='left')
    ttk.Label(unit_frame, text="Freq Unit:").pack(side='left', padx=5)
    app_instance.freq_unit = ttk.Combobox(unit_frame, width=5, values=['GHz'])
    app_instance.freq_unit.set('GHz')
    app_instance.freq_unit.pack(side='left')

    # 文件选择区域
    file_frame = ttk.Frame(scrollable_frame) # 修改父控件为 scrollable_frame
    file_frame.pack(fill='x', padx=5, pady=5)
    ttk.Label(file_frame, text="Tech File").grid(row=0, column=0, sticky='w')
    ttk.Entry(file_frame).grid(row=0, column=1, sticky='ew', padx=5)
    ttk.Button(file_frame, text="Browse").grid(row=0, column=2) # 命令未定义
    ttk.Button(file_frame, text="Import").grid(row=0, column=3, padx=5) # 命令未定义
    file_frame.grid_columnconfigure(1, weight=1)
    
    # 主设置区域的框架不再需要 settings_frame，直接将 trace_setting_frame 等 pack 到 scrollable_frame
    
    # Trace Settings
    trace_setting_frame = ttk.LabelFrame(scrollable_frame, text="Trace Settings:") 
    trace_setting_frame.pack(fill='x', expand=True, padx=5, pady=5)
    # 创建左右布局的容器
    trace_container_frame = ttk.Frame(trace_setting_frame)
    trace_container_frame.pack(fill='both', expand=True)
    # 左侧参数设置
    trace_params_frame = ttk.Frame(trace_container_frame)
    trace_params_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    app_instance.show_diff_trace = tk.BooleanVar(value=True)
    ttk.Checkbutton(trace_params_frame, text="Show Diff Trace Parameters", 
                   variable=app_instance.show_diff_trace).pack(anchor='w')
    # Trace Settings部分的参数设置
    params = [
        ("Diff Traces Primary Width", "30um"),
        ("Diff Traces Primary Gap", "70um"),
        ("Diff Coupled Traces to Shape Spacing", "70um")
    ]
    for text, default in params:
        frame = ttk.Frame(trace_params_frame)
        frame.pack(fill='x', pady=2)
        ttk.Label(frame, text=text).pack(side='left')
        entry = ttk.Entry(frame, width=15)
        entry.insert(0, default)
        entry.pack(side='right')

    # Diff Trace Gather Type radio buttons
    gather_frame = ttk.Frame(trace_params_frame)
    gather_frame.pack(fill='x', pady=2)
    app_instance.gather_type = tk.IntVar(value=2)
    ttk.Radiobutton(gather_frame, text="Diff Trace Gather Type 1: Short Preferred", 
                   variable=app_instance.gather_type, value=1).pack(anchor='w')
    
    # Diff Trace Width Over Voids (只在Type 1被选中时可用)
    void_width_frame = ttk.Frame(trace_params_frame)
    void_width_frame.pack(fill='x', pady=2)
    ttk.Label(void_width_frame, text="Diff Trace Width Over Voids").pack(side='left')
    void_width_entry = ttk.Entry(void_width_frame, width=15)
    void_width_entry.insert(0, "75um")
    void_width_entry.pack(side='right')
    
    # 添加联动功能
    def update_void_width_state(*args):
        if app_instance.gather_type.get() == 1:
            void_width_entry.configure(state='normal')
        else:
            void_width_entry.configure(state='disabled')
    
    app_instance.gather_type.trace_add('write', update_void_width_state)
    # 初始化状态
    update_void_width_state()
    
    ttk.Radiobutton(gather_frame, text="Diff Trace Gather Type 2: Coupled Preferred", 
                   variable=app_instance.gather_type, value=2).pack(anchor='w')

    extend_frame = ttk.Frame(trace_params_frame)
    extend_frame.pack(fill='x', pady=2)
    ttk.Label(extend_frame, text="Diff Traces Extend Length").pack(side='left')
    app_instance.extend_auto = tk.BooleanVar(value=True)
    ttk.Radiobutton(extend_frame, text="Auto", variable=app_instance.extend_auto, 
                   value=True).pack(side='left', padx=5)
    ttk.Radiobutton(extend_frame, text="Manual", variable=app_instance.extend_auto, 
                   value=False).pack(side='left')
    extend_entry = ttk.Entry(extend_frame, width=10)
    extend_entry.insert(0, "100um")
    extend_entry.pack(side='right')
    
    # 添加联动功能
    def update_extend_entry_state(*args):
        if app_instance.extend_auto.get():
            extend_entry.configure(state='disabled')
        else:
            extend_entry.configure(state='normal')
    
    app_instance.extend_auto.trace_add('write', update_extend_entry_state)
    # 初始化状态
    update_extend_entry_state()

    # Single Trace Parameters
    single_trace_frame = ttk.Frame(trace_params_frame)
    single_trace_frame.pack(fill='x', pady=5)
    app_instance.show_single_trace = tk.BooleanVar(value=False)
    ttk.Checkbutton(single_trace_frame, text="Show Single Trace Parameters", 
                   variable=app_instance.show_single_trace).pack(anchor='w')
    ttk.Label(single_trace_frame, text="Min Trace to Shape Spacing").pack(side='left')
    single_trace_entry = ttk.Entry(single_trace_frame, width=15)
    single_trace_entry.insert(0, "50um")
    single_trace_entry.pack(side='right')

    # 右侧图片区域
    image_frame = ttk.Frame(trace_container_frame)
    image_frame.pack(side='right', fill='both', padx=5, pady=5)
    try:
        script_dir = os.path.dirname(__file__) 
        trace_image_path = os.path.join(script_dir, "trace_setting_demo.png")
        trace_image_pil = Image.open(trace_image_path)
        app_instance.trace_image_tk = ImageTk.PhotoImage(trace_image_pil)
        trace_image_label = ttk.Label(image_frame, image=app_instance.trace_image_tk)
        trace_image_label.image = app_instance.trace_image_tk 
        trace_image_label.pack(expand=True)
    except FileNotFoundError:
        ttk.Label(image_frame, text="图片占位 (trace_setting_demo.png 未找到)").pack(expand=True)
    except Exception as e:
        ttk.Label(image_frame, text=f"加载图片错误: {e}").pack(expand=True)
    
    # Via Settings
    via_settings_frame = ttk.LabelFrame(scrollable_frame, text="Via Settings:") 
    via_settings_frame.pack(fill='x', expand=True, padx=5, pady=5)
    
    # 创建左右布局的容器
    via_container_frame = ttk.Frame(via_settings_frame)
    via_container_frame.pack(fill='both', expand=True)
    
    # 左侧参数设置
    via_params_frame = ttk.Frame(via_container_frame)
    via_params_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    
    # 基本参数
    via_params = [
        ("Drill Outer Diameter", "65um"),
        ("Regular Pad Diameter", "95um"),
        ("Core Layer Pad Diameter", "125um")
    ]
    
    for text, default in via_params:
        frame = ttk.Frame(via_params_frame)
        frame.pack(fill='x', pady=2)
        ttk.Label(frame, text=text).pack(side='left')
        entry = ttk.Entry(frame, width=15)
        entry.insert(0, default)
        entry.pack(side='right')
    
    # 添加Max Metal Layers per Padstack
    max_layers_frame = ttk.Frame(via_params_frame)
    max_layers_frame.pack(fill='x', pady=2)
    ttk.Label(max_layers_frame, text="Max Metal Layers per Padstack").pack(side='left')
    ttk.Combobox(max_layers_frame, width=5, values=list(range(1, 11))).pack(side='right')
    
    # 添加Diff Via参数设置
    ttk.Checkbutton(via_params_frame, text="Show Diff Via Parameters").pack(anchor='w', pady=5)
    
    # Diff Upper Via Routing Angle
    angle_frame = ttk.Frame(via_params_frame)
    angle_frame.pack(fill='x', pady=2)
    ttk.Label(angle_frame, text="Diff Upper Via Routing Angle(deg)").pack(side='left')
    
    # Auto/Manual radio buttons
    radio_frame = ttk.Frame(angle_frame)
    radio_frame.pack(side='right')
    auto_var = tk.BooleanVar(value=True)
    ttk.Radiobutton(radio_frame, text="Auto", variable=auto_var, value=True).pack(side='left')
    ttk.Radiobutton(radio_frame, text="Manual", variable=auto_var, value=False).pack(side='left')
    angle_entry = ttk.Entry(radio_frame, width=5)
    angle_entry.pack(side='left')
    
    # 添加联动功能
    def update_angle_entry_state(*args):
        if auto_var.get():
            angle_entry.configure(state='disabled')
        else:
            angle_entry.configure(state='normal')
    
    auto_var.trace_add('write', update_angle_entry_state)
    # 初始化状态
    update_angle_entry_state()
    
    # Diff Via Void Spacing
    void_frame = ttk.Frame(via_params_frame)
    void_frame.pack(fill='x', pady=2)
    ttk.Label(void_frame, text="Diff Via Void Spacing").pack(side='left')
    void_entry = ttk.Entry(void_frame, width=15)
    void_entry.insert(0, "50um")
    void_entry.pack(side='right')
    
    # Diff Void Layers
    layers_frame = ttk.Frame(via_params_frame)
    layers_frame.pack(fill='x', pady=2)
    ttk.Label(layers_frame, text="Diff Void Layers(Including Pad Layer)").pack(side='left')
    ttk.Combobox(layers_frame, width=15, values=['Auto']).pack(side='right')
    
    # 添加Single Via参数设置
    ttk.Checkbutton(via_params_frame, text="Show Single Via Parameters").pack(anchor='w', pady=5)
    
    # Single Net Routing Angle
    single_angle_frame = ttk.Frame(via_params_frame)
    single_angle_frame.pack(fill='x', pady=2)
    ttk.Label(single_angle_frame, text="Single Net Routing Angle(deg)").pack(side='left')
    single_angle_entry = ttk.Entry(single_angle_frame, width=15)
    single_angle_entry.insert(0, "45")
    single_angle_entry.pack(side='right')
    
    # Single Via Void Spacing
    single_void_frame = ttk.Frame(via_params_frame)
    single_void_frame.pack(fill='x', pady=2)
    ttk.Label(single_void_frame, text="Single Via Void Spacing").pack(side='left')
    single_void_entry = ttk.Entry(single_void_frame, width=15)
    single_void_entry.insert(0, "50um")
    single_void_entry.pack(side='right')
    
    # Single Void Layers
    single_layers_frame = ttk.Frame(via_params_frame)
    single_layers_frame.pack(fill='x', pady=2)
    ttk.Label(single_layers_frame, text="Single Void Layers(Including Pad Layer)").pack(side='left')
    ttk.Combobox(single_layers_frame, width=5, values=list(range(1, 11))).pack(side='right')
    
    # 右侧图片区域 TODO: 以后添加Ansys示意图
    # via_image_frame = ttk.Frame(via_container_frame)
    # via_image_frame.pack(side='right', fill='both', padx=5, pady=5)
    # try:
    #     script_dir = os.path.dirname(__file__) 
    #     via_image_path = os.path.join(script_dir, "via_settings.png")
    #     via_image_pil = Image.open(via_image_path)
    #     app_instance.via_image_tk = ImageTk.PhotoImage(via_image_pil)
    #     via_image_label = ttk.Label(via_image_frame, image=app_instance.via_image_tk)
    #     via_image_label.image = app_instance.via_image_tk 
    #     via_image_label.pack(expand=True)
    # except FileNotFoundError:
    #     ttk.Label(via_image_frame, text="图片占位 (via_setting.png 未找到)").pack(expand=True)
    # except Exception as e:
    #     ttk.Label(via_image_frame, text=f"加载图片错误: {e}").pack(expand=True)

    # Core Via Settings
    core_via_settings_frame = ttk.LabelFrame(scrollable_frame, text="Core Via Settings:") 
    core_via_settings_frame.pack(fill='x', expand=True, padx=5, pady=5)
    
    # 创建左右布局的容器
    core_via_container_frame = ttk.Frame(core_via_settings_frame)
    core_via_container_frame.pack(fill='both', expand=True)
    
    # 左侧参数设置
    core_via_params_frame = ttk.Frame(core_via_container_frame)
    core_via_params_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    
    # 基本参数
    core_via_params = [
        ("Drill Outer Diameter", "150um"),
        ("Pad Diameter", "250um")
    ]
    
    for text, default in core_via_params:
        frame = ttk.Frame(core_via_params_frame)
        frame.pack(fill='x', pady=2)
        ttk.Label(frame, text=text).pack(side='left')
        entry = ttk.Entry(frame, width=15)
        entry.insert(0, default)
        entry.pack(side='right')
    
    # Show Diff Pair Core Via Parameters
    app_instance.show_diff_core_via = tk.BooleanVar(value=True)
    ttk.Checkbutton(core_via_params_frame, text="Show Diff Pair Core Via Parameters", 
                   variable=app_instance.show_diff_core_via).pack(anchor='w', pady=5)
    
    # Diff Pair Core Via Distance
    distance_frame = ttk.Frame(core_via_params_frame)
    distance_frame.pack(fill='x', pady=2)
    ttk.Label(distance_frame, text="Diff Pair Core Via Distance").pack(side='left')
    distance_entry = ttk.Entry(distance_frame, width=15)
    distance_entry.insert(0, "500um")
    distance_entry.pack(side='right')
    
    # Void Parameters
    void_type_frame = ttk.Frame(core_via_params_frame)
    void_type_frame.pack(fill='x', pady=2)
    app_instance.core_via_void_type = tk.StringVar(value="spacing")
    ttk.Radiobutton(void_type_frame, text="Diff Pair Core Via Void Parameter", 
                   variable=app_instance.core_via_void_type, value="parameter").pack(anchor='w')
    
    # Void Length and Width
    void_size_frame = ttk.Frame(core_via_params_frame)
    void_size_frame.pack(fill='x', padx=20)
    ttk.Label(void_size_frame, text="Void Length(Horizontal)").pack(side='left')
    void_length_entry = ttk.Entry(void_size_frame, width=15)
    void_length_entry.insert(0, "400um")
    void_length_entry.pack(side='right')
    
    void_width_frame = ttk.Frame(core_via_params_frame)
    void_width_frame.pack(fill='x', padx=20)
    ttk.Label(void_width_frame, text="Void Width(Vertical)").pack(side='left')
    void_width_entry = ttk.Entry(void_width_frame, width=15)
    void_width_entry.insert(0, "700um")
    void_width_entry.pack(side='right')
    
    # Void by Spacing
    ttk.Radiobutton(core_via_params_frame, text="Diff Pair Core Via Void by Spacing", 
                   variable=app_instance.core_via_void_type, value="spacing").pack(anchor='w')
    
    # Spacing Parameters
    spacing_frame = ttk.Frame(core_via_params_frame)
    spacing_frame.pack(fill='x', padx=20)
    ttk.Label(spacing_frame, text="Diff Pair Core Via Void Spacing").pack(side='left')
    spacing_entry = ttk.Entry(spacing_frame, width=15)
    spacing_entry.insert(0, "50um")
    spacing_entry.pack(side='right')
    
    # Set Different Horizontal/Vertical Spacing
    diff_spacing_frame = ttk.Frame(core_via_params_frame)
    diff_spacing_frame.pack(fill='x', padx=20)
    app_instance.diff_spacing = tk.BooleanVar(value=False)
    ttk.Checkbutton(diff_spacing_frame, text="Set Different Horizontal/Vertical Spacing", 
                   variable=app_instance.diff_spacing).pack(anchor='w')
    
    # Horizontal and Vertical Spacing
    h_spacing_frame = ttk.Frame(core_via_params_frame)
    h_spacing_frame.pack(fill='x', padx=20)
    ttk.Label(h_spacing_frame, text="Diff Pair Core Via Void Horizontal Spacing").pack(side='left')
    h_spacing_entry = ttk.Entry(h_spacing_frame, width=15)
    h_spacing_entry.insert(0, "50um")
    h_spacing_entry.pack(side='right')
    
    v_spacing_frame = ttk.Frame(core_via_params_frame)
    v_spacing_frame.pack(fill='x', padx=20)
    ttk.Label(v_spacing_frame, text="Diff Pair Core Via Void Verticall Spacing").pack(side='left')
    v_spacing_entry = ttk.Entry(v_spacing_frame, width=15)
    v_spacing_entry.insert(0, "50um")
    v_spacing_entry.pack(side='right')
    
    # Void Layers
    layers_frame = ttk.Frame(core_via_params_frame)
    layers_frame.pack(fill='x', pady=2)
    ttk.Label(layers_frame, text="Diff Pair Core Via Void Layers(Including Pad Layer)").pack(side='left')
    layers_combo = ttk.Combobox(layers_frame, width=15, values=['Auto'])
    layers_combo.set('Auto')
    layers_combo.pack(side='right')
    
    # Return Core Via Settings
    return_signal_frame = ttk.Frame(core_via_params_frame)
    return_signal_frame.pack(fill='x', pady=2)
    ttk.Label(return_signal_frame, text="Diff Pair Return Core Via to Signal Core Via").pack(side='left')
    app_instance.return_signal_auto = tk.BooleanVar(value=True)
    ttk.Radiobutton(return_signal_frame, text="Auto", variable=app_instance.return_signal_auto, 
                   value=True).pack(side='left', padx=5)
    ttk.Radiobutton(return_signal_frame, text="Manual", variable=app_instance.return_signal_auto, 
                   value=False).pack(side='left')
    return_signal_entry = ttk.Entry(return_signal_frame, width=10)
    return_signal_entry.insert(0, "350um")
    return_signal_entry.pack(side='right')
    
    return_return_frame = ttk.Frame(core_via_params_frame)
    return_return_frame.pack(fill='x', pady=2)
    ttk.Label(return_return_frame, text="Diff Pair Return Core Via to Return Core Via").pack(side='left')
    app_instance.return_return_auto = tk.BooleanVar(value=True)
    ttk.Radiobutton(return_return_frame, text="Auto", variable=app_instance.return_return_auto, 
                   value=True).pack(side='left', padx=5)
    ttk.Radiobutton(return_return_frame, text="Manual", variable=app_instance.return_return_auto, 
                   value=False).pack(side='left')
    return_return_entry = ttk.Entry(return_return_frame, width=10)
    return_return_entry.insert(0, "350um")
    return_return_entry.pack(side='right')
    
    # Show Single Net Core Via Parameters
    app_instance.show_single_core_via = tk.BooleanVar(value=False)
    ttk.Checkbutton(core_via_params_frame, text="Show Single Net Core Via Parameters", 
                   variable=app_instance.show_single_core_via).pack(anchor='w', pady=5)
    
    # Min Ground Via to Signal Via Spacing
    min_spacing_frame = ttk.Frame(core_via_params_frame)
    min_spacing_frame.pack(fill='x', pady=2)
    ttk.Label(min_spacing_frame, text="Min Ground Via to Signal Via Spacing").pack(side='left')
    min_spacing_entry = ttk.Entry(min_spacing_frame, width=15)
    min_spacing_entry.insert(0, "50um")
    min_spacing_entry.pack(side='right')
    
    # 右侧图片区域
    core_via_image_frame = ttk.Frame(core_via_container_frame)
    core_via_image_frame.pack(side='right', fill='both', padx=5, pady=5)
    try:
        script_dir = os.path.dirname(__file__) 
        core_via_image_path = os.path.join(script_dir, "core_via_settings.png")
        core_via_image_pil = Image.open(core_via_image_path)
        app_instance.core_via_image_tk = ImageTk.PhotoImage(core_via_image_pil)
        core_via_image_label = ttk.Label(core_via_image_frame, image=app_instance.core_via_image_tk)
        core_via_image_label.image = app_instance.core_via_image_tk 
        core_via_image_label.pack(expand=True)
    except FileNotFoundError:
        ttk.Label(core_via_image_frame, text="图片占位 (core_via_settings.png 未找到)").pack(expand=True)
    except Exception as e:
        ttk.Label(core_via_image_frame, text=f"加载图片错误: {e}").pack(expand=True)

    # Diff Pair Return Vias Pattern
    return_vias_frame = ttk.LabelFrame(scrollable_frame, text="Diff Pair Return Vias Pattern:") 
    return_vias_frame.pack(fill='x', expand=True, padx=5, pady=5)
    
    # 创建水平排列的容器
    pattern_container = ttk.Frame(return_vias_frame)
    pattern_container.pack(fill='x', expand=True, padx=5, pady=5)
    
    # 定义所有模式
    patterns = [
        ("0: No Return Via", 0, "diff_pair_return_vias_pattern_0.png"),
        ("1: One Return Via", 1, "diff_pair_return_vias_pattern_1.png"),
        ("2: Two Return Vias", 2, "diff_pair_return_vias_pattern_2.png"),
        ("3: Surrounding Return Vias - A", 3, "diff_pair_return_vias_pattern_3.png")
        # ("4: Surrounding Return Vias - B", 4, "diff_pair_return_vias_pattern_4.png")
    ]
    
    app_instance.return_via_pattern = tk.IntVar(value=0)
    app_instance.pattern_images = []
    
    # 为每个模式创建一个容器，包含radio和图片
    for text, value, image_file in patterns:
        # 创建一个容器来包含radio和图片
        group_frame = ttk.Frame(pattern_container)
        group_frame.pack(side='left', padx=5)
        
        # 添加radio按钮
        radio = ttk.Radiobutton(group_frame, text=text, value=value,
                              variable=app_instance.return_via_pattern)
        radio.pack(anchor='w', pady=(0, 5))
        
        try:
            # 加载并调整图片大小
            image_path = os.path.join(os.path.dirname(__file__), image_file)
            image = Image.open(image_path)
            
            # 设置固定宽度并保持宽高比
            target_width = 300
            width_percent = (target_width / float(image.size[0]))
            target_height = int((float(image.size[1]) * float(width_percent)))
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # 创建PhotoImage并保存引用
            photo = ImageTk.PhotoImage(image)
            app_instance.pattern_images.append(photo)
            
            # 添加图片标签
            label = ttk.Label(group_frame, image=photo)
            label.pack()
        except Exception as e:
            ttk.Label(group_frame, text=f"无法加载图片: {e}").pack()


    # BGA Pad Settings
    bga_settings_frame = ttk.LabelFrame(scrollable_frame, text="BGA Pad Settings:")
    bga_settings_frame.pack(fill='x', expand=True, padx=5, pady=5)
    
    # 创建左右布局的容器
    bga_container_frame = ttk.Frame(bga_settings_frame)
    bga_container_frame.pack(fill='both', expand=True)
    
    # 左侧参数设置
    bga_params_frame = ttk.Frame(bga_container_frame)
    bga_params_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    
    # Circle/Rectangle Pad选择
    app_instance.pad_type = tk.StringVar(value='circle')
    ttk.Radiobutton(bga_params_frame, text="Circle Pad", 
                   variable=app_instance.pad_type, value='circle').pack(anchor='w')
    
    # Circle Pad Diameter
    circle_frame = ttk.Frame(bga_params_frame)
    circle_frame.pack(fill='x', pady=2)
    ttk.Label(circle_frame, text="Pad Diameter").pack(side='left')
    circle_entry = ttk.Entry(circle_frame, width=15)
    circle_entry.insert(0, "600um")
    circle_entry.pack(side='right')
    
    # Rectangle Pad选项
    ttk.Radiobutton(bga_params_frame, text="Rectangle Pad", 
                   variable=app_instance.pad_type, value='rectangle').pack(anchor='w')
    
    # Rectangle Pad参数
    rect_params = [
        ("Pad Length(Horizontal)", "580um"),
        ("Pad Width(Vertical)", "700um"),
        ("Pad Fillet", "150um"),
        ("Pad Rotation", "0")
    ]
    
    for text, default in rect_params:
        frame = ttk.Frame(bga_params_frame)
        frame.pack(fill='x', pady=2)
        ttk.Label(frame, text=text).pack(side='left')
        entry = ttk.Entry(frame, width=15)
        entry.insert(0, default)
        entry.pack(side='right')
    
    # Diff Pair BGA Pad Parameters
    app_instance.show_diff_bga = tk.BooleanVar(value=True)
    diff_bga_check = ttk.Checkbutton(bga_params_frame, text="Show Diff Pair BGA Pad Parameters", 
                                    variable=app_instance.show_diff_bga)
    diff_bga_check.pack(anchor='w', pady=5)
    
    # 创建一个Frame来容纳所有差分对参数
    diff_bga_frame = ttk.Frame(bga_params_frame)
    diff_bga_frame.pack(fill='x', pady=2)
    
    # Common Void Parameter选项
    app_instance.void_type = tk.StringVar(value='parameter')
    ttk.Radiobutton(diff_bga_frame, text="Diff Pair Common Void Parameter", 
                   variable=app_instance.void_type, value='parameter').pack(anchor='w')
    
    # Common Void参数
    void_params = [
        ("Diff Pair Common Void Length(Horizontal)", "1350um"),
        ("Diff Pair Common Void Width(Vertical)", "800um")
    ]
    
    for text, default in void_params:
        frame = ttk.Frame(diff_bga_frame)
        frame.pack(fill='x', pady=2)
        ttk.Label(frame, text=text).pack(side='left')
        entry = ttk.Entry(frame, width=15)
        entry.insert(0, default)
        entry.pack(side='right')
    
    # Common Void by Spacing选项
    ttk.Radiobutton(diff_bga_frame, text="Diff Pair Common Void by Spacing", 
                   variable=app_instance.void_type, value='spacing').pack(anchor='w')
    
    # Spacing参数
    spacing_frame = ttk.Frame(diff_bga_frame)
    spacing_frame.pack(fill='x', pady=2)
    ttk.Label(spacing_frame, text="Diff Pair BGA Pad to Shape Spacing").pack(side='left')
    spacing_entry = ttk.Entry(spacing_frame, width=15)
    spacing_entry.insert(0, "50um")
    spacing_entry.pack(side='right')
    
    # Different Horizontal/Vertical Spacing选项
    app_instance.diff_spacing = tk.BooleanVar(value=False)
    diff_spacing_check = ttk.Checkbutton(diff_bga_frame, text="Set Different Horizontal/Vertical Spacing", 
                                        variable=app_instance.diff_spacing)
    diff_spacing_check.pack(anchor='w', padx=20)
    
    # Horizontal/Vertical Spacing参数
    hv_spacing_params = [
        ("Diff Pair BGA Pad to Shape Horizontal Spacing", "50um"),
        ("Diff Pair BGA Pad to Shape Vertical Spacing", "50um")
    ]
    
    for text, default in hv_spacing_params:
        frame = ttk.Frame(diff_bga_frame)
        frame.pack(fill='x', pady=2, padx=20)
        ttk.Label(frame, text=text).pack(side='left')
        entry = ttk.Entry(frame, width=15)
        entry.insert(0, default)
        entry.pack(side='right')
    
    # Void Layers
    void_layers_frame = ttk.Frame(diff_bga_frame)
    void_layers_frame.pack(fill='x', pady=2)
    ttk.Label(void_layers_frame, text="Diff Pair Common Void Layers(Including Pad Layer)").pack(side='left')
    void_layers_combo = ttk.Combobox(void_layers_frame, width=15, values=['Auto'])
    void_layers_combo.set('Auto')
    void_layers_combo.pack(side='right')
    
    # Individual Voids Parameter选项
    ttk.Radiobutton(diff_bga_frame, text="Diff Pair Individual Voids Parameter", 
                   variable=app_instance.void_type, value='individual').pack(anchor='w')
    
    # Individual Voids参数
    individual_params = [
        ("Diff Pair Individual Void Length(Horizontal)", "680um"),
        ("Diff Pair Individual Void Width(Vertical)", "800um"),
        ("Diff Pair Manual Individual Void Fillet", "150um"),
        ("Diff Pair Manual Individual Void Rotation", "0")
    ]
    
    for text, default in individual_params:
        frame = ttk.Frame(diff_bga_frame)
        frame.pack(fill='x', pady=2)
        ttk.Label(frame, text=text).pack(side='left')
        entry = ttk.Entry(frame, width=15)
        entry.insert(0, default)
        entry.pack(side='right')
    
    # Individual Voids by Spacing选项
    ttk.Radiobutton(diff_bga_frame, text="Diff Pair Individual Voids by Spacing", 
                   variable=app_instance.void_type, value='individual_spacing').pack(anchor='w')
    
    # Individual Spacing参数
    ind_spacing_frame = ttk.Frame(diff_bga_frame)
    ind_spacing_frame.pack(fill='x', pady=2)
    ttk.Label(ind_spacing_frame, text="Diff Pair BGA Pad to Shape Spacing").pack(side='left')
    ind_spacing_entry = ttk.Entry(ind_spacing_frame, width=15)
    ind_spacing_entry.insert(0, "50um")
    ind_spacing_entry.pack(side='right')
    
    # Different Individual Horizontal/Vertical Spacing选项
    app_instance.ind_diff_spacing = tk.BooleanVar(value=False)
    ind_diff_spacing_check = ttk.Checkbutton(diff_bga_frame, text="Set Different Horizontal/Vertical Spacing", 
                                            variable=app_instance.ind_diff_spacing)
    ind_diff_spacing_check.pack(anchor='w', padx=20)
    
    # Individual Horizontal/Vertical Spacing参数
    ind_hv_spacing_params = [
        ("Diff BGA Pad to Shape Horizontal Spacing", "50um"),
        ("Diff BGA Pad to Shape Vertical Spacing", "50um")
    ]
    
    for text, default in ind_hv_spacing_params:
        frame = ttk.Frame(diff_bga_frame)
        frame.pack(fill='x', pady=2, padx=20)
        ttk.Label(frame, text=text).pack(side='left')
        entry = ttk.Entry(frame, width=15)
        entry.insert(0, default)
        entry.pack(side='right')
    
    # Individual Void Layers
    ind_void_layers_frame = ttk.Frame(diff_bga_frame)
    ind_void_layers_frame.pack(fill='x', pady=2)
    ttk.Label(ind_void_layers_frame, text="Diff Pair Individual Voids Layers(Including Pad Layer)").pack(side='left')
    ind_void_layers_combo = ttk.Combobox(ind_void_layers_frame, width=15, values=['5'])
    ind_void_layers_combo.set('5')
    ind_void_layers_combo.pack(side='right')
    
    # Single Net BGA Pad Parameters
    app_instance.show_single_bga = tk.BooleanVar(value=True)
    single_bga_check = ttk.Checkbutton(bga_params_frame, text="Show Single Net BGA Pad Parameters", 
                                      variable=app_instance.show_single_bga)
    single_bga_check.pack(anchor='w', pady=5)
    
    # 创建一个Frame来容纳所有单端参数
    single_bga_frame = ttk.Frame(bga_params_frame)
    single_bga_frame.pack(fill='x', pady=2)
    
    # Single Net Spacing参数
    single_spacing_frame = ttk.Frame(single_bga_frame)
    single_spacing_frame.pack(fill='x', pady=2)
    ttk.Label(single_spacing_frame, text="Single Net BGA Pad to Shape Spacing").pack(side='left')
    single_spacing_entry = ttk.Entry(single_spacing_frame, width=15)
    single_spacing_entry.insert(0, "50um")
    single_spacing_entry.pack(side='right')
    
    # Different Single Horizontal/Vertical Spacing选项
    app_instance.single_diff_spacing = tk.BooleanVar(value=False)
    single_diff_spacing_check = ttk.Checkbutton(single_bga_frame, text="Set Different Horizontal/Vertical Spacing", 
                                               variable=app_instance.single_diff_spacing)
    single_diff_spacing_check.pack(anchor='w', padx=20)
    
    # Single Horizontal/Vertical Spacing参数
    single_hv_spacing_params = [
        ("Single Net BGA Pad to Shape Horizontal Spacing", "50um"),
        ("Single Net BGA Pad to Shape Vertical Spacing", "50um")
    ]
    
    for text, default in single_hv_spacing_params:
        frame = ttk.Frame(single_bga_frame)
        frame.pack(fill='x', pady=2, padx=20)
        ttk.Label(frame, text=text).pack(side='left')
        entry = ttk.Entry(frame, width=15)
        entry.insert(0, default)
        entry.pack(side='right')
    
    # Single Void Layers
    single_void_layers_frame = ttk.Frame(single_bga_frame)
    single_void_layers_frame.pack(fill='x', pady=2)
    ttk.Label(single_void_layers_frame, text="Single Net Void Layers(Including Pad Layer)").pack(side='left')
    single_void_layers_combo = ttk.Combobox(single_void_layers_frame, width=15, values=['Auto'])
    single_void_layers_combo.set('Auto')
    single_void_layers_combo.pack(side='right')
    
    # 添加差分对参数显示联动功能
    def update_diff_bga_state(*args):
        state = 'normal' if app_instance.show_diff_bga.get() else 'disabled'
        for child in diff_bga_frame.winfo_children():
            if isinstance(child, (ttk.Entry, ttk.Combobox)):
                child.configure(state=state)
            elif isinstance(child, ttk.Radiobutton):
                child['state'] = state
            elif isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, (ttk.Entry, ttk.Combobox)):
                        subchild.configure(state=state)
                    elif isinstance(subchild, ttk.Radiobutton):
                        subchild['state'] = state
                    elif isinstance(subchild, ttk.Checkbutton):
                        subchild['state'] = state
                    else:
                        try:
                            subchild.configure(state=state)
                        except:
                            pass
            else:
                try:
                    child.configure(state=state)
                except:
                    pass
    
    app_instance.show_diff_bga.trace_add('write', update_diff_bga_state)
    update_diff_bga_state()
    
    # 添加单端参数显示联动功能
    def update_single_bga_state(*args):
        state = 'normal' if app_instance.show_single_bga.get() else 'disabled'
        for child in single_bga_frame.winfo_children():
            if isinstance(child, (ttk.Entry, ttk.Combobox)):
                child.configure(state=state)
            elif isinstance(child, ttk.Radiobutton):
                child['state'] = state
            elif isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, (ttk.Entry, ttk.Combobox)):
                        subchild.configure(state=state)
                    elif isinstance(subchild, ttk.Radiobutton):
                        subchild['state'] = state
                    elif isinstance(subchild, ttk.Checkbutton):
                        subchild['state'] = state
                    else:
                        try:
                            subchild.configure(state=state)
                        except:
                            pass
            else:
                try:
                    child.configure(state=state)
                except:
                    pass
    
    app_instance.show_single_bga.trace_add('write', update_single_bga_state)
    update_single_bga_state()
    
    # 右侧图片区域
    image_frame = ttk.Frame(bga_container_frame)
    image_frame.pack(side='right', fill='both', padx=5, pady=5)
    try:
        script_dir = os.path.dirname(__file__)
        bga_image_path = os.path.join(script_dir, "bga_pad_settings.png")
        bga_image_pil = Image.open(bga_image_path)
        app_instance.bga_image_tk = ImageTk.PhotoImage(bga_image_pil)
        bga_image_label = ttk.Label(image_frame, image=app_instance.bga_image_tk)
        bga_image_label.image = app_instance.bga_image_tk
        bga_image_label.pack(expand=True)
    except FileNotFoundError:
        ttk.Label(image_frame, text="图片占位 (bga_pad_settings.png 未找到)").pack(expand=True)
    except Exception as e:
        ttk.Label(image_frame, text=f"加载图片错误: {e}").pack(expand=True)
    # 确保 scrollable_frame 宽度适应 canvas
    scrollable_frame.update_idletasks() # 更新内部组件的尺寸
    canvas.config(scrollregion=canvas.bbox("all"))

    
    # Solderball Settings
    solderball_settings_frame = ttk.LabelFrame(scrollable_frame, text="Solderball Settings:") 
    solderball_settings_frame.pack(fill='x', expand=True, padx=5, pady=5)
    
    # 创建左右布局的容器
    solderball_container_frame = ttk.Frame(solderball_settings_frame)
    solderball_container_frame.pack(fill='both', expand=True)
    
    # 左侧参数设置
    solderball_params_frame = ttk.Frame(solderball_container_frame)
    solderball_params_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    
    # Solderball Material and Segments
    material_frame = ttk.Frame(solderball_params_frame)
    material_frame.pack(fill='x', pady=2)
    ttk.Label(material_frame, text="Solderball Material").pack(side='left')
    material_combo = ttk.Combobox(material_frame, width=15, values=['Solder63'])
    material_combo.set('Solder63')
    material_combo.pack(side='left', padx=5)
    
    ttk.Label(material_frame, text="Solderball Segments").pack(side='left', padx=5)
    segments_combo = ttk.Combobox(material_frame, width=15, values=['8'])
    segments_combo.set('8')
    segments_combo.pack(side='left')
    
    # Size by Ratio to BGA Pad
    app_instance.size_type = tk.StringVar(value='ratio')
    ratio_radio = ttk.Radiobutton(solderball_params_frame, text="Size by Ratio to BGA Pad", 
                                variable=app_instance.size_type, value='ratio')
    ratio_radio.pack(anchor='w', pady=5)
    
    # Ratio Parameters
    ratio_frame = ttk.Frame(solderball_params_frame)
    ratio_frame.pack(fill='x', padx=20)
    
    diameter_ratio_frame = ttk.Frame(ratio_frame)
    diameter_ratio_frame.pack(fill='x', pady=2)
    ttk.Label(diameter_ratio_frame, text="Diameter Ratio to Pad").pack(side='left')
    diameter_ratio_entry = ttk.Entry(diameter_ratio_frame, width=15)
    diameter_ratio_entry.insert(0, "0.8")
    diameter_ratio_entry.pack(side='right')
    
    height_ratio_frame = ttk.Frame(ratio_frame)
    height_ratio_frame.pack(fill='x', pady=2)
    ttk.Label(height_ratio_frame, text="Height Ratio to Diameter").pack(side='left')
    height_ratio_entry = ttk.Entry(height_ratio_frame, width=15)
    height_ratio_entry.insert(0, "1")
    height_ratio_entry.pack(side='right')
    
    # Manual Size
    manual_radio = ttk.Radiobutton(solderball_params_frame, text="Manual Size", 
                                 variable=app_instance.size_type, value='manual')
    manual_radio.pack(anchor='w', pady=5)
    
    # Manual Parameters
    manual_frame = ttk.Frame(solderball_params_frame)
    manual_frame.pack(fill='x', padx=20)
    
    diameter_frame = ttk.Frame(manual_frame)
    diameter_frame.pack(fill='x', pady=2)
    ttk.Label(diameter_frame, text="Diameter").pack(side='left')
    diameter_entry = ttk.Entry(diameter_frame, width=15)
    diameter_entry.insert(0, "500um")
    diameter_entry.pack(side='right')
    
    height_frame = ttk.Frame(manual_frame)
    height_frame.pack(fill='x', pady=2)
    ttk.Label(height_frame, text="Height").pack(side='left')
    height_entry = ttk.Entry(height_frame, width=15)
    height_entry.insert(0, "400um")
    height_entry.pack(side='right')
    
    # 添加联动功能
    def update_size_entry_state(*args):
        if app_instance.size_type.get() == 'ratio':
            # 启用比例输入框
            diameter_ratio_entry.configure(state='normal')
            height_ratio_entry.configure(state='normal')
            # 禁用手动输入框
            diameter_entry.configure(state='disabled')
            height_entry.configure(state='disabled')
        else:
            # 禁用比例输入框
            diameter_ratio_entry.configure(state='disabled')
            height_ratio_entry.configure(state='disabled')
            # 启用手动输入框
            diameter_entry.configure(state='normal')
            height_entry.configure(state='normal')
    
    app_instance.size_type.trace_add('write', update_size_entry_state)
    update_size_entry_state()
    
    # 右侧图片区域
    solderball_image_frame = ttk.Frame(solderball_container_frame)
    solderball_image_frame.pack(side='right', fill='both', padx=5, pady=5)
    try:
        script_dir = os.path.dirname(__file__)
        solderball_image_path = os.path.join(script_dir, "solderball_settings.png")
        solderball_image_pil = Image.open(solderball_image_path)
        app_instance.solderball_image_tk = ImageTk.PhotoImage(solderball_image_pil)
        solderball_image_label = ttk.Label(solderball_image_frame, image=app_instance.solderball_image_tk)
        solderball_image_label.image = app_instance.solderball_image_tk
        solderball_image_label.pack(expand=True)
    except FileNotFoundError:
        ttk.Label(solderball_image_frame, text="图片占位 (solderball_settings.png 未找到)").pack(expand=True)
    except Exception as e:
        ttk.Label(solderball_image_frame, text=f"加载图片错误: {e}").pack(expand=True)

    # Plane Settings
    plane_settings_frame = ttk.LabelFrame(scrollable_frame, text="Plane Settings:") 
    plane_settings_frame.pack(fill='x', expand=True, padx=5, pady=5)
    
    # 创建参数设置框架
    plane_params_frame = ttk.Frame(plane_settings_frame)
    plane_params_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    # 添加四个 Extend Size 参数
    plane_params = [
        ("Extend Size X+", "BGA_Pad_Diameter * 2"),
        ("Extend Size X-", "BGA_Pad_Diameter * 2"),
        ("Extend Size Y+", "BGA_Pad_Diameter * 2"),
        ("Extend Size Y-", "BGA_Pad_Diameter * 2")
    ]
    
    for text, default in plane_params:
        frame = ttk.Frame(plane_params_frame)
        frame.pack(fill='x', pady=2)
        ttk.Label(frame, text=text).pack(side='left')
        entry = ttk.Entry(frame, width=25)
        entry.insert(0, default)
        entry.pack(side='right')

    # 绑定鼠标滚轮事件 (可选, 增强用户体验)
    def _on_mousewheel(event):
        # 根据操作系统调整滚动方向和单位
        if os.name == 'nt': # Windows
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif os.name == 'posix': # Linux/macOS
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
    
    # 绑定到 Canvas 和其子控件，以便在任何地方滚动都有效
    canvas.bind_all("<MouseWheel>", _on_mousewheel) # Windows, some Linux
    canvas.bind_all("<Button-4>", _on_mousewheel)   # Linux (scroll up)
    canvas.bind_all("<Button-5>", _on_mousewheel)   # Linux (scroll down)
