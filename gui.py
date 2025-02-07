import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import subprocess
import threading
import queue
from pathlib import Path
import sys
import platform
import random
from datetime import datetime

class YuEGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YuE Music Generator")
        # 主要設定頁面
        style = ttk.Style()
        #style.configure("TFrame", background="gray6")
        # 建立樣式 要設為clam 有些UI才能改
        style.theme_use("clam")
        # 設定全螢幕
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        # 設定DPI縮放
        self.root.tk.call('tk', 'scaling', 1.2)
        
        # 深色主題顏色定義
        self.colors = {
            'bg_dark': '#1A1A1A',        # 主背景色 (更深沉)
            'bg_darker': '#212121',       # 更深的背景色 (稍微調亮)
            'bg_light': '#2A2A2A',        # 較淺的背景色
            'text': '#E0E0E0',            # 主要文字顏色 (更明亮)
            'text_bright': '#FFFFFF',      # 亮色文字
            'accent': '#2C7A7B',          # 強調色 (更柔和的青綠色)
            'accent_hover': '#38B2B2',    # 強調色懸停 (更鮮明)
            'danger': '#CF3B49',          # 危險色 (更柔和的紅色)
            'danger_hover': '#E64C5C',    # 危險色懸停
            'border': '#383838',          # 邊框顏色 (稍微調亮)
            'button_bg': '#404040',       # 按鈕背景色 (更明顯)
            'button_hover': '#4D4D4D',    # 按鈕懸停色
            'frame_bg': '#2A2A2A'         # 框架背景色
        }
        
        # 設定全局樣式
        self.style = ttk.Style()
        
        # 設定全局字體和顏色
        self.default_font = ('Microsoft JhengHei UI', 14)
        self.title_font = ('Microsoft JhengHei UI', 16, 'bold')
        
        # 設定主題顏色
        self.style.configure('.',
                      font=self.default_font,
                      background=self.colors['bg_dark'],
                      foreground=self.colors['text'])
        
        # 框架樣式
        self.style.configure('TFrame',
                      background=self.colors['bg_darker'])
        
        self.style.configure('TLabelframe',
                      padding=12,
                      relief="solid",
                      background=self.colors['bg_darker'],
                      bordercolor=self.colors['border'])
        
        self.style.configure('TLabelframe.Label',
                      font=self.title_font,
                      foreground=self.colors['text_bright'],
                      background=self.colors['bg_darker'])
        
        # 基本按鈕樣式
        self.style.configure('TButton',
                      padding=(10, 6),     # 加大按鈕內邊距
                      font=self.default_font,
                      background=self.colors['button_bg'],
                      foreground=self.colors['text_bright'],
                      borderwidth=1,       # 添加細邊框
                      relief='solid')      # 改為實線邊框
        
        self.style.map('TButton',
                 background=[('active', self.colors['button_hover']),
                             ('!active', self.colors['button_bg']),  # 明確設定正常狀態
                             ('disabled', self.colors['bg_dark'])],
                 foreground=[('active', self.colors['text_bright']),
                             ('!active', self.colors['text_bright']),  # 文字顏色始終亮色
                             ('disabled', self.colors['text'])])
        
        # 主要按鈕樣式加強
        self.style.configure('Primary.TButton',
                      padding=(14, 8),     # 更大的內邊距
                      font=(self.default_font[0], self.default_font[1]+2, 'bold'),  # 更大字體
                      background=self.colors['accent'],
                      foreground=self.colors['text_bright'],
                      borderwidth=0,       # 移除邊框
                      relief='flat')       # 扁平化設計
        
        self.style.map('Primary.TButton',
                 background=[('active', self.colors['accent_hover']),
                             ('disabled', self.colors['bg_dark'])],
                 relief=[('active', 'sunken')])
        
        # 危險按鈕樣式加強
        self.style.configure('Danger.TButton',
                      padding=(12, 6),
                      font=(self.default_font[0], self.default_font[1]+1, 'bold'),
                      background=self.colors['danger'],
                      foreground=self.colors['text_bright'],
                      borderwidth=2,
                      relief='raised')
        
        self.style.map('Danger.TButton',
                 background=[('active', self.colors['danger_hover']),
                             ('disabled', self.colors['bg_dark'])],
                 relief=[('active', 'sunken')])
        
        # 輸入框樣式
        self.style.configure('TEntry',
                      fieldbackground=self.colors['bg_darker'],
                      foreground=self.colors['text'],
                      insertcolor=self.colors['text_bright'])
        
        # 在 style 設定中添加
        self.style.configure('Custom.TEntry',
                      fieldbackground=self.colors['bg_darker'],
                      foreground=self.colors['text'],
                      insertcolor=self.colors['text_bright'])
        
        # 設定根窗口背景色
        self.root.configure(bg=self.colors['bg_dark'])
        
        # 載入配置
        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self.load_config()
        
        # 添加虛擬環境路徑設定
        if "venv_path" not in self.config:
            self.config["venv_path"] = "F:/project/AI/YuE/YuE-for-windows/YuEGP/YuE-exllamav2/myevnv"  # 設定默認虛擬環境路徑
            if platform.system() == "Windows":
                self.config["python_cmd"] = "python"
            else:
                self.config["python_cmd"] = "python3"
            self.save_config()
        
        # 載入音樂風格標籤
        tags_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),  # 回到YuE-exllamav2目錄
            "top_200_tags.json"
        )
        try:
            with open(tags_path, "r", encoding="utf-8") as f:
                self.genre_tags = json.load(f)
        except FileNotFoundError:
            self.genre_tags = []
            print(f"Warning: {tags_path} not found")
        
        # 在建立主要框架之前，先初始化 command_text
        self.command_text = None
        
        # 建立主要框架
        self.create_main_frame()
        
        # 只保留一個視窗狀態設定
        if platform.system() == "Windows":
            self.root.state('zoomed')
        else:
            self.root.attributes('-zoomed', True)
        
        # 用於存儲生成進程
        self.process = None
        self.subprocess = None  # 添加用於存儲子進程的變數
        self.output_queue = queue.Queue()
        
        # 添加計時器相關變數
        self.timer_id = None
        self.start_time = None
        
        # Notebook 樣式設定
        self.style.configure('TNotebook',
                          background=self.colors['bg_darker'],
                          borderwidth=0)

        self.style.configure('TNotebook.Tab',
                          padding=(10, 5),
                          background=self.colors['bg_darker'],
                          foreground=self.colors['text'],
                          borderwidth=1,
                          relief='flat')

        # 分類 Notebook 專用樣式
        self.style.configure('Genre.TNotebook',
                          background=self.colors['bg_darker'],
                          borderwidth=0)

        self.style.configure('Genre.TNotebook.Tab',
                          padding=(10, 5),
                          background=self.colors['button_bg'],
                          foreground=self.colors['text'],
                          borderwidth=0)

        # 分類 Notebook Tab 的狀態映射
        self.style.map('Genre.TNotebook.Tab',
                     background=[('selected', self.colors['accent']),
                                 ('!selected', self.colors['button_bg']),
                                 ('active', self.colors['button_hover'])],
                                 foreground=[('selected', self.colors['text_bright']),
                                             ('!selected', self.colors['text']),
                                             ('active', self.colors['text_bright'])])
        
    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "models": {
                    "stage1_model": "F:/project/AI/YuE/YuE-for-windows/YuEGP/YuE-exllamav2/Model/YuE-s1-7B-anneal-en-cot-exl2",
                    "stage2_model": "F:/project/AI/YuE/YuE-for-windows/YuEGP/YuE-exllamav2/Model/YuE-s2-1B-general-exl2",
                    "stage1_use_exl2": True,
                    "stage2_use_exl2": True
                },
                "environment": {
                    "venv_path": "F:/project/AI/YuE/YuE-for-windows/YuEGP/YuE-exllamav2/myevnv",
                    "python_cmd": "python",
                    "output_dir": "outputs"
                },
                "generation": {
                    "max_new_tokens": 3000,
                    "run_n_segments": 2,
                    "stage2_batch_size": 4,
                    "stage1_cache_size": 16384,
                    "stage2_cache_size": 32768,
                    "seed": -1
                },
                "audio_prompt": {
                    "use_audio_prompt": False,
                    "audio_prompt_path": "",
                    "prompt_start_time": 0.0,
                    "prompt_end_time": 30.0
                },
                "output": {
                    "output_filename": ""
                },
                "recommended_settings": {
                    "default": {
                        "stage2_cache_size": 32768,
                        "stage1_cache_size": 16384
                    },
                    "low_vram": {
                        "stage2_cache_size": 16384,
                        "stage1_cache_size": 8192
                    },
                    "high_quality": {
                        "stage2_cache_size": 65536,
                        "stage1_cache_size": 32768
                    }
                }
            }
            self.save_config()
            
    def save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)
            
    def create_main_frame(self):
        # 主要設定頁面
        style = ttk.Style()
        style.configure("TFrame", background="gray6")
        # 建立樣式
        #style.theme_use("clam")

        # 將 ttk.PanedWindow 改為 tk.PanedWindow
        main_container = tk.PanedWindow(self.root, orient="horizontal", bg=self.colors['bg_dark'])
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # 建立左右面板時直接指定最小尺寸
        left_panel = tk.Frame(main_container, bg=self.colors['frame_bg'])
        right_panel = tk.Frame(main_container, bg=self.colors['frame_bg'])
        
        # 使用 tkinter 原生方法添加面板
        main_container.add(left_panel, minsize=400, stretch='always')  # 左側最小寬度400
        main_container.add(right_panel, minsize=400, stretch='always')  # 右側最小寬度400
        
        # 修改延遲設定方法
        def configure_panes():
            # 改用 tkinter 原生的 paneconfig
            main_container.paneconfig(left_panel, minsize=400)
            main_container.paneconfig(right_panel, minsize=400)
            # 設定初始分割位置為中間
            main_container.sash_place(0, int(main_container.winfo_width()/2), 0)
        
        # 配置根視窗縮放
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 左側Notebook設定
        self.notebook = ttk.Notebook(left_panel)
        self.notebook.pack(fill='both', expand=True)
        
        
        # 2. 修改 Tab 樣式
        style.configure("CustomNotebook.TNotebook.Tab", 
                         background="gray20", foreground="white",
                         padding=[10, 5])
        style.map("CustomNotebook.TNotebook.Tab",
                  background=[("selected", "darkred")])


        # 套用自訂樣式
        self.notebook.configure(style="CustomNotebook.TNotebook")

        # 建立 Frame 並加入 Notebook
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="主要設定")

        self.notebook.pack(expand=True, fill="both")
        
        # 在可捲動框架中添加內容
        input_frame = ttk.LabelFrame(main_frame, text="輸入")
        input_frame.pack(fill="x", expand=True, padx=5, pady=5)
        
        # 風格輸入
        genre_frame = ttk.LabelFrame(input_frame, text="音樂風格")
        genre_frame.pack(fill="x", padx=5, pady=5)
        
        # 風格文本輸入
        self.genre_text = scrolledtext.ScrolledText(
            genre_frame, 
            height=2,
            font=self.default_font,
            padx=10,
            pady=10,
            background=self.colors['bg_darker'],
            foreground=self.colors['text'],
            insertbackground=self.colors['text_bright'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['text_bright'],
            undo=True  # 啟用撤銷功能
        )
        self.genre_text.pack(fill="x", pady=5)
        
        # 風格按鈕區域
        genre_buttons_frame = ttk.Frame(genre_frame)
        genre_buttons_frame.pack(fill="x", expand=True)
        
        # 建立分類notebook
        genre_notebook = ttk.Notebook(genre_buttons_frame, style='Genre.TNotebook')
        genre_notebook.pack(fill="both", expand=True)
        
        # 為每個類型創建一個頁面
        for category, tags in self.genre_tags.items():
            category_frame = tk.Frame(genre_notebook, bg=self.colors['bg_darker'])
            genre_notebook.add(category_frame, text=category)
            self.create_scrollable_buttons(category_frame, tags)
        
        # 清除和隨機按鈕框架
        button_frame = ttk.Frame(genre_frame)
        button_frame.pack(fill="x", pady=5)
        
        tk.Button(
            button_frame,
            text="清除風格",
            command=lambda: self.genre_text.delete(1.0, tk.END),
            bg=self.colors['button_bg'],
            fg=self.colors['text_bright'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text_bright'],
            relief='flat',
            font=self.default_font
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="隨機選擇",
            command=self.random_genre,
            bg=self.colors['button_bg'],
            fg=self.colors['text_bright'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text_bright'],
            relief='flat',
            font=self.default_font
        ).pack(side="left", padx=5)
        
        # 歌詞輸入
        lyrics_frame = ttk.LabelFrame(input_frame, text="歌詞")
        lyrics_frame.pack(fill="both", expand=True, pady=5)
        
        self.lyrics_text = scrolledtext.ScrolledText(
            lyrics_frame, 
            height=12,
            font=self.default_font,
            padx=10,
            pady=10,
            wrap=tk.WORD,
            background=self.colors['bg_darker'],
            foreground=self.colors['text'],
            insertbackground=self.colors['text_bright'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['text_bright'],
            undo=True  # 啟用撤銷功能
        )
        self.lyrics_text.pack(fill="both", expand=True)
        
        # === 右側輸出日誌 ===
        right_panel.grid_rowconfigure(0, weight=0)  # 音頻提示設定
        right_panel.grid_rowconfigure(1, weight=0)  # 執行指令設定
        right_panel.grid_rowconfigure(2, weight=2)  # 日誌區域 (增加權重)
        right_panel.grid_rowconfigure(3, weight=1)  # 控制面板
        right_panel.grid_columnconfigure(0, weight=1)
        
        # 音頻提示設定
        prompt_frame = ttk.LabelFrame(right_panel, text="音頻提示設定")
        prompt_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 第一行：勾選框和音頻選擇
        prompt_top_frame = ttk.Frame(prompt_frame)
        prompt_top_frame.pack(fill="x", pady=2)
        
        # 使用音頻提示選項
        self.use_audio_prompt = tk.BooleanVar(value=False)
        ttk.Checkbutton(prompt_top_frame, 
                       text="使用音頻提示", 
                       variable=self.use_audio_prompt,
                       command=self.toggle_audio_prompt
                       ).pack(side="left", padx=5)
        
        # 音頻文件選擇
        self.audio_prompt_path = ttk.Entry(
            prompt_top_frame,
            width=40,
            state="disabled",
            style='Custom.TEntry'
        )
        self.audio_prompt_path.pack(side="left", fill="x", expand=True, padx=5)
        
        self.browse_audio_btn = tk.Button(
            prompt_top_frame, 
            text="瀏覽", 
            command=lambda: self.browse_path("audio_prompt_path"),
            state="disabled",
            bg=self.colors['button_bg'],
            fg=self.colors['text_bright'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text_bright'],
            relief='flat',
            font=self.default_font
        )
        self.browse_audio_btn.pack(side="left", padx=5)
        
        # 第二行：時間範圍設定
        time_frame = ttk.Frame(prompt_frame)
        time_frame.pack(fill="x", pady=5)
        
        # 使用Grid佈局來對齊時間設定
        ttk.Label(time_frame, text="開始時間:").grid(row=0, column=0, padx=5)
        self.prompt_start_time = ttk.Entry(
            time_frame,
            width=8,
            state="disabled",
            style='Custom.TEntry'
        )
        self.prompt_start_time.grid(row=0, column=1, padx=2)
        self.prompt_start_time.insert(0, "0.0")  # 設置默認值
        
        ttk.Label(time_frame, text="秒").grid(row=0, column=2, padx=2)
        
        ttk.Label(time_frame, text="結束時間:").grid(row=0, column=3, padx=5)
        self.prompt_end_time = ttk.Entry(
            time_frame,
            width=8,
            state="disabled",
            style='Custom.TEntry'
        )
        self.prompt_end_time.grid(row=0, column=4, padx=2)
        self.prompt_end_time.insert(0, "30.0")  # 設置默認值
        
        ttk.Label(time_frame, text="秒").grid(row=0, column=5, padx=2)
        
        # 輸出日誌
        log_frame = ttk.LabelFrame(right_panel, text="輸出日誌")
        log_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # 建立日誌捲動容器
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # 建立文本框和捲軸
        self.output_text = scrolledtext.ScrolledText(
            log_container,
            height=6,
            font=('Consolas', 12),
            padx=10,
            pady=10,
            background=self.colors['bg_darker'],
            foreground=self.colors['text'],
            insertbackground=self.colors['text_bright'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['text_bright']
        )
        self.output_text.pack(fill="both", expand=True)
        
        # 控制區域
        control_frame = ttk.LabelFrame(right_panel, text="控制面板")
        control_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        control_frame.configure(style='Control.TLabelframe')  # 使用自定義樣式
        
        # 生成控制
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill="both", expand=True, padx=5, pady=5)  # 使用 both 而不是 x
        
        # 左側按鈕
        button_left_frame = ttk.Frame(button_frame)
        button_left_frame.pack(side="left", fill="x", expand=True)
        
        # 生成和中斷按鈕並排
        button_row = ttk.Frame(button_left_frame)
        button_row.pack(fill="x", expand=True)
        
        self.run_button = tk.Button(
            button_row,
            text="生成音樂",
            command=self.run_generation,
            bg=self.colors['accent'],
            fg=self.colors['text_bright'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['text_bright'],
            relief='raised',
            font=(self.default_font[0], self.default_font[1]+1, 'bold')
        )
        self.run_button.pack(side="left", padx=5)
        
        self.stop_button = tk.Button(
            button_row,
            text="停止",
            command=self.stop_generation,
            bg=self.colors['danger'],
            fg=self.colors['text_bright'],
            activebackground=self.colors['danger_hover'],
            activeforeground=self.colors['text_bright'],
            relief='raised',
            font=(self.default_font[0], self.default_font[1]+1, 'bold'),
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)
        
        # 新增預覽和打開目錄按鈕
        self.preview_button = tk.Button(
            button_row,
            text="預覽音樂",
            command=self.play_latest_preview,
            bg=self.colors['accent'],
            fg=self.colors['text_bright'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['text_bright'],
            relief='raised',
            font=self.default_font,
            state="disabled"  # 初始時禁用
        )
        self.preview_button.pack(side="left", padx=5)
        
        self.open_dir_button = tk.Button(
            button_row,
            text="打開目錄",
            command=self.open_latest_dir,
            bg=self.colors['button_bg'],
            fg=self.colors['text_bright'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text_bright'],
            relief='raised',
            font=self.default_font,
            state="disabled"  # 初始時禁用
        )
        self.open_dir_button.pack(side="left", padx=5)
        
        # 進度條和計時器在下方
        status_frame = ttk.Frame(button_frame)
        status_frame.pack(fill="x", expand=True, pady=(5,0))
        
        # 進度條樣式設定
        self.style.configure("Custom.Horizontal.TProgressbar",
                           troughcolor=self.colors['bg_darker'],
                           background=self.colors['accent'],
                           bordercolor=self.colors['border'],
                           lightcolor=self.colors['accent_hover'],
                           darkcolor=self.colors['accent'])
        
        # 進度條
        self.progress = ttk.Progressbar(
            status_frame, 
            mode="indeterminate",
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(side="left", fill="x", expand=True, padx=5)
        
        # 計時器
        timer_frame = ttk.Frame(status_frame)
        timer_frame.pack(side="right", padx=5)
        
        ttk.Label(timer_frame, 
                 text="用時:", 
                 font=('Microsoft JhengHei UI', 12, 'bold')  # 加大字體
                 ).pack(side="left")
        
        self.timer_label = ttk.Label(
            timer_frame, 
            text="00:00",
            font=('Consolas', 14, 'bold'),  # 加大字體
            foreground=self.colors['accent']  # 使用強調色
        )
        self.timer_label.pack(side="left", padx=5)
        
        # === 進階設定頁面 ===
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="進階設定")
        
        # 建立進階設定頁面的捲動容器
        self.adv_canvas = tk.Canvas(advanced_frame, bg=self.colors['frame_bg'])  # 改為實例變數
        adv_scrollbar = ttk.Scrollbar(advanced_frame, orient="vertical", command=self.adv_canvas.yview)
        adv_scrollable_frame = ttk.Frame(self.adv_canvas)  # 移除 bg 參數
        
        # 配置捲動
        adv_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.adv_canvas.configure(scrollregion=self.adv_canvas.bbox("all"))
        )
        
        self.adv_canvas.create_window((0, 0), window=adv_scrollable_frame, anchor="nw")
        self.adv_canvas.configure(yscrollcommand=adv_scrollbar.set)
        
        # 配置Canvas和Scrollbar的佈局
        self.adv_canvas.pack(side="left", fill="both", expand=True)
        adv_scrollbar.pack(side="right", fill="y")
        
        # 主要設定頁面的捲動容器
        self.main_canvas = tk.Canvas(main_frame, bg=self.colors['frame_bg'])  # 改為實例變數
        main_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.main_canvas.yview)
        main_scrollable_frame = ttk.Frame(self.main_canvas)
        
        # 修改滑鼠滾輪事件處理
        def _on_mousewheel(event):
            current_tab = self.notebook.index(self.notebook.select())
            if current_tab == 0:  # 主要設定頁面
                self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif current_tab == 1:  # 進階設定頁面
                self.adv_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # 綁定事件到root而非canvas
        self.root.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 模型設定區域
        model_frame = ttk.LabelFrame(adv_scrollable_frame, text="模型設定", padding=10)
        model_frame.pack(fill="x", padx=10, pady=5)
        
        # Stage1 模型路徑
        ttk.Label(model_frame, text="Stage1 模型路徑:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.stage1_path = ttk.Entry(model_frame, width=50)
        self.stage1_path.insert(0, self.config["models"]["stage1_model"])
        self.stage1_path.grid(row=0, column=1, padx=5)
        tk.Button(
            model_frame,
            text="瀏覽",
            command=lambda: self.browse_path("stage1_model"),
            bg=self.colors['button_bg'],
            fg=self.colors['text_bright'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text_bright'],
            relief='flat',
            font=self.default_font
        ).grid(row=0, column=2)
        
        # Stage2 模型路徑
        ttk.Label(model_frame, text="Stage2 模型路徑:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.stage2_path = ttk.Entry(model_frame, width=50)
        self.stage2_path.insert(0, self.config["models"]["stage2_model"])
        self.stage2_path.grid(row=1, column=1, padx=5)
        tk.Button(
            model_frame,
            text="瀏覽",
            command=lambda: self.browse_path("stage2_model"),
            bg=self.colors['button_bg'],
            fg=self.colors['text_bright'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text_bright'],
            relief='flat',
            font=self.default_font
        ).grid(row=1, column=2)
        
        # 虛擬環境設定
        env_frame = ttk.LabelFrame(adv_scrollable_frame, text="環境設定", padding=10)
        env_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(env_frame, text="虛擬環境路徑:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.venv_path = ttk.Entry(env_frame, width=50)
        self.venv_path.insert(0, self.config["environment"]["venv_path"])
        self.venv_path.grid(row=0, column=1, padx=5)
        tk.Button(
            env_frame,
            text="瀏覽",
            command=lambda: self.browse_path("venv_path"),
            bg=self.colors['button_bg'],
            fg=self.colors['text_bright'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text_bright'],
            relief='flat',
            font=self.default_font
        ).grid(row=0, column=2)
        
        # 性能設定
        perf_frame = ttk.LabelFrame(adv_scrollable_frame, text="性能設定", padding=10)
        perf_frame.pack(fill="x", padx=10, pady=5)
        
        # Cache大小設定
        ttk.Label(perf_frame, text="Stage2 Cache Size:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.stage2_cache_size = ttk.Entry(perf_frame, width=10)
        self.stage2_cache_size.insert(0, str(self.config["generation"]["stage2_cache_size"]))
        self.stage2_cache_size.grid(row=0, column=1, sticky="w", padx=5)
        
        # 性能配置選擇
        ttk.Label(perf_frame, text="性能配置:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.preset_var = tk.StringVar(value="default")
        preset_combo = ttk.Combobox(perf_frame, 
                                   textvariable=self.preset_var,
                                   values=["default", "low_vram", "high_quality"],
                                   width=15,
                                   state="readonly")
        preset_combo.grid(row=1, column=1, sticky="w", padx=5)
        ttk.Button(perf_frame, text="套用配置", 
                  command=self.apply_preset).grid(row=1, column=2, padx=5)
        
        # 生成參數設定
        gen_frame = ttk.LabelFrame(adv_scrollable_frame, text="生成參數", padding=10)
        gen_frame.pack(fill="x", padx=10, pady=5)
        
        # 最大生成token數
        ttk.Label(gen_frame, text="最大生成Token數:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.max_new_tokens = ttk.Entry(gen_frame, width=10)
        self.max_new_tokens.insert(0, str(self.config["generation"]["max_new_tokens"]))
        self.max_new_tokens.grid(row=0, column=1, sticky="w", padx=5)
        
        # 生成段數
        ttk.Label(gen_frame, text="生成段數:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.run_n_segments = ttk.Entry(gen_frame, width=10)
        self.run_n_segments.insert(0, str(self.config["generation"]["run_n_segments"]))
        self.run_n_segments.grid(row=1, column=1, sticky="w", padx=5)
        
        # Stage2批次大小
        ttk.Label(gen_frame, text="Stage2批次大小:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.stage2_batch_size = ttk.Entry(gen_frame, width=10)
        self.stage2_batch_size.insert(0, str(self.config["generation"]["stage2_batch_size"]))
        self.stage2_batch_size.grid(row=2, column=1, sticky="w", padx=5)
        
        # Stage1 Cache大小
        ttk.Label(gen_frame, text="Stage1 Cache大小:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.stage1_cache_size = ttk.Entry(gen_frame, width=10)
        self.stage1_cache_size.insert(0, str(self.config["generation"]["stage1_cache_size"]))
        self.stage1_cache_size.grid(row=3, column=1, sticky="w", padx=5)
        
        # 隨機種子
        seed_frame = ttk.Frame(gen_frame)
        seed_frame.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        ttk.Label(seed_frame, text="隨機種子:").pack(side="left", padx=(0,5))
        
        # 種子模式選擇
        self.seed_mode = tk.StringVar(value="random")
        random_mode = ttk.Radiobutton(seed_frame, text="隨機", variable=self.seed_mode, 
                                    value="random", command=self.update_seed_state)
        specific_mode = ttk.Radiobutton(seed_frame, text="指定", variable=self.seed_mode, 
                                      value="specific", command=self.update_seed_state)
        random_mode.pack(side="left", padx=5)
        specific_mode.pack(side="left", padx=5)
        
        # 種子輸入框和生成按鈕
        self.seed = ttk.Entry(seed_frame, width=10)
        self.seed.insert(0, str(self.config["generation"]["seed"]))
        self.seed.pack(side="left", padx=5)
        
        self.generate_seed_btn = tk.Button(
            seed_frame,
            text="生成種子",
            command=self.generate_random_seed,
            bg=self.colors['button_bg'],
            fg=self.colors['text_bright'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text_bright'],
            relief='flat',
            font=self.default_font
        )
        self.generate_seed_btn.pack(side="left", padx=5)
        
        # 初始化種子輸入框狀態
        self.update_seed_state()
        
        # 在創建完所有 Entry 後設定其樣式
        def configure_entries():
            # 設定所有 Entry 的樣式
            for entry in [self.audio_prompt_path, self.output_filename, 
                         self.prompt_start_time, self.prompt_end_time,
                         self.stage1_path, self.stage2_path, self.venv_path]:
                entry.configure(
                    background=self.colors['bg_darker'],
                    foreground=self.colors['text']
                )
        
        # 延遲執行設定
        self.root.after(100, configure_entries)
        
        # 建立顯示執行指令的框架
        command_frame = ttk.LabelFrame(right_panel, text="執行指令")
        command_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # 建立顯示執行指令的文本框
        self.command_text = scrolledtext.ScrolledText(
            command_frame,
            height=4,
            font=('Consolas', 12),
            wrap=tk.WORD,
            background=self.colors['bg_darker'],
            foreground=self.colors['text'],
            insertbackground=self.colors['text_bright'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['text_bright']
        )
        self.command_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 為兩個文本框綁定常用的複製/貼上快捷鍵
        def bind_text_shortcuts(widget):
            """綁定文本框的複製/貼上快捷鍵"""
            def copy(event):
                widget.event_generate("<<Copy>>")
                return "break"
            
            def paste(event):
                widget.event_generate("<<Paste>>")
                return "break"
            
            def cut(event):
                widget.event_generate("<<Cut>>")
                return "break"
            
            def select_all(event):
                widget.tag_add(tk.SEL, "1.0", tk.END)
                return "break"
            
            # Windows/Linux 快捷鍵
            widget.bind('<Control-c>', copy)
            widget.bind('<Control-v>', paste)
            widget.bind('<Control-x>', cut)
            widget.bind('<Control-a>', select_all)
            
            # macOS 快捷鍵
            widget.bind('<Command-c>', copy)
            widget.bind('<Command-v>', paste)
            widget.bind('<Command-x>', cut)
            widget.bind('<Command-a>', select_all)

        # 為兩個文本框綁定快捷鍵
        bind_text_shortcuts(self.genre_text)
        bind_text_shortcuts(self.lyrics_text)
        
    def browse_path(self, key):
        if key.endswith('_path'):
            path = filedialog.askopenfilename()
        else:
            path = filedialog.askdirectory()
        if path:
            if key == "stage1_model":
                self.stage1_path.delete(0, tk.END)
                self.stage1_path.insert(0, path)
                # 更新配置中的模型路徑
                self.config["models"]["stage1_model"] = path
            elif key == "stage2_model":
                self.stage2_path.delete(0, tk.END)
                self.stage2_path.insert(0, path)
                # 更新配置中的模型路徑
                self.config["models"]["stage2_model"] = path
            elif key == "audio_prompt_path":
                self.audio_prompt_path.delete(0, tk.END)
                self.audio_prompt_path.insert(0, path)
                self.config["audio_prompt"]["audio_prompt_path"] = path
            elif key == "venv_path":
                self.venv_path.delete(0, tk.END)
                self.venv_path.insert(0, path)
                self.config["environment"]["venv_path"] = path
            # 儲存更新後的配置
            self.save_config()
    
    def update_output(self):
        try:
            while True:
                line = self.output_queue.get_nowait()
                if line.startswith("progress_update:"):
                    # 進度更新行
                    progress_line = line.replace("progress_update:", "")
                    # 找到最後一個進度行並刪除
                    content = self.output_text.get("1.0", tk.END)
                    lines = content.split('\n')
                    # 從後往前找最後一個進度行
                    for i in range(len(lines)-1, -1, -1):
                        if "|" in lines[i] and "[A" in lines[i]:
                            # 保留該行之前的所有內容
                            new_content = '\n'.join(lines[:i])
                            self.output_text.delete("1.0", tk.END)
                            if new_content:
                                self.output_text.insert(tk.END, new_content + "\n")
                            break
                    # 添加新的進度行
                    self.output_text.insert(tk.END, progress_line + "\n")
                elif line.startswith("normal:"):
                    # 一般訊息
                    normal_line = line.replace("normal:", "")
                    self.output_text.insert(tk.END, normal_line + "\n")
                self.output_text.see(tk.END)
        except queue.Empty:
            if self.process and self.process.is_alive():
                self.root.after(100, self.update_output)
            else:
                # 統一狀態恢復點
                self.progress.stop()
                self.run_button.configure(
                    bg=self.colors['accent'],
                    fg=self.colors['text_bright'],
                    state="normal",
                    text="生成音樂"
                )
                self.stop_button.configure(state="disabled")
                self.stop_timer()
                
                # 生成完成後，檢查是否有生成的音樂文件
                output_dir = os.path.join(
                    self.config["environment"]["output_dir"],
                    self.config["output"]["output_filename"]
                )
                mixed_file = os.path.join(output_dir, "mixed.mp3")
                
                if os.path.exists(mixed_file):
                    # 儲存最新的文件路徑
                    self.latest_mixed_file = mixed_file
                    self.latest_output_dir = output_dir
                    
                    # 輸出歌詞和風格到文本文件
                    with open(os.path.join(output_dir, "genre.txt"), "w", encoding="utf-8") as f:
                        f.write(self.genre_text.get("1.0", tk.END).strip())
                    with open(os.path.join(output_dir, "lyrics.txt"), "w", encoding="utf-8") as f:
                        f.write(self.lyrics_text.get("1.0", tk.END).strip())
                    
                    # 啟用預覽和打開目錄按鈕
                    self.preview_button.configure(state="normal")
                    self.open_dir_button.configure(state="normal")
                    
                    # 在輸出中顯示生成完成的路徑
                    self.output_text.insert(tk.END, f"\n=== 生成完成 ===\n")
                    self.output_text.insert(tk.END, f"輸出目錄: {output_dir}\n")
                    self.output_text.insert(tk.END, f"音樂文件: {mixed_file}\n")
                    self.output_text.see(tk.END)

    def play_preview(self, audio_file):
        """預覽音樂文件"""
        if platform.system() == "Windows":
            os.startfile(audio_file)
        else:
            import subprocess
            opener = "open" if platform.system() == "Darwin" else "xdg-open"
            subprocess.call([opener, audio_file])

    def open_output_dir(self, dir_path):
        """打開輸出目錄"""
        if platform.system() == "Windows":
            os.startfile(dir_path)
        else:
            import subprocess
            opener = "open" if platform.system() == "Darwin" else "xdg-open"
            subprocess.call([opener, dir_path])

    def get_python_cmd(self):
        """獲取Python執行命令"""
        if platform.system() == "Windows":
            if self.config["venv_path"]:
                return os.path.join(self.config["venv_path"], "Scripts", "python.exe")
            return "python"
        else:
            if self.config["venv_path"]:
                return os.path.join(self.config["venv_path"], "bin", "python3")
            return "python3"
    
    def run_generation(self):
        try:
            # 自動使用時間檔名
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"YuE_generated_{current_time}"
            self.config["output"]["output_filename"] = output_filename
            
            # 更新生成按鈕外觀
            self.run_button.configure(
                bg=self.colors['accent'],  # 保持原顏色
                fg=self.colors['text_bright'],
                state="disabled",  # 僅禁用按鈕
                text="生成中..."
            )
            self.stop_button.configure(state="normal")  # 啟用中斷按鈕
            
            # 設定進度條速度和大小
            self.progress.configure(maximum=100)
            self.progress.configure(mode="indeterminate")
            self.progress.start(10)  # 調整速度
            
            # 更新配置
            self.config["generation"].update({
                "max_new_tokens": int(self.max_new_tokens.get()),
                "run_n_segments": int(self.run_n_segments.get()),
                "stage2_batch_size": int(self.stage2_batch_size.get()),
                "stage1_cache_size": int(self.stage1_cache_size.get()),
                "stage2_cache_size": int(self.stage2_cache_size.get()),
                "seed": int(self.seed.get())
            })
            
            # 處理音頻提示時間設定
            start_time = self.prompt_start_time.get().strip()
            end_time = self.prompt_end_time.get().strip()
            
            self.config["audio_prompt"].update({
                "use_audio_prompt": self.use_audio_prompt.get(),
                "audio_prompt_path": self.audio_prompt_path.get(),
                "prompt_start_time": float(start_time) if start_time else 0.0,
                "prompt_end_time": float(end_time) if end_time else 30.0
            })
            
            self.save_config()
            
            # 檢查輸入
            if not self.genre_text.get("1.0", tk.END).strip():
                raise ValueError("請輸入音樂風格！")
            if not self.lyrics_text.get("1.0", tk.END).strip():
                raise ValueError("請輸入歌詞！")
            
            # 修改記錄顯示位置
            self.command_text.delete(1.0, tk.END)
            self.command_text.insert(tk.END, "=== 開始生成音樂 ===\n")
            self.command_text.insert(tk.END, f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.command_text.insert(tk.END, "\n=== 生成參數 ===\n")
            self.command_text.insert(tk.END, f"最大Token數: {self.config['generation']['max_new_tokens']}\n")
            self.command_text.insert(tk.END, f"生成段數: {self.config['generation']['run_n_segments']}\n")
            self.command_text.insert(tk.END, f"Stage2批次大小: {self.config['generation']['stage2_batch_size']}\n")
            self.command_text.insert(tk.END, f"Stage1 Cache大小: {self.config['generation']['stage1_cache_size']}\n")
            self.command_text.insert(tk.END, f"Stage2 Cache大小: {self.config['generation']['stage2_cache_size']}\n")
            if self.config['generation']['seed'] >= 0:
                self.command_text.insert(tk.END, f"隨機種子: {self.config['generation']['seed']}\n")
            
            if self.config['audio_prompt']['use_audio_prompt']:
                self.command_text.insert(tk.END, "\n=== 音頻提示設定 ===\n")
                self.command_text.insert(tk.END, f"音頻檔案: {self.config['audio_prompt']['audio_prompt_path']}\n")
                self.command_text.insert(tk.END, f"時間範圍: {self.config['audio_prompt']['prompt_start_time']} - {self.config['audio_prompt']['prompt_end_time']}\n")
            
            self.command_text.insert(tk.END, "\n=== 輸入內容 ===\n")
            self.command_text.insert(tk.END, f"音樂風格: {self.genre_text.get('1.0', tk.END).strip()}\n")
            self.command_text.insert(tk.END, f"歌詞內容:\n{self.lyrics_text.get('1.0', tk.END).strip()}\n")
            
            # 準備命令，使用虛擬環境的Python
            python_cmd = self.get_python_cmd()
            script_path = os.path.join(os.path.dirname(__file__), "infer.py")
            
            # 修改命令生成部分
            cmd = [
                python_cmd,
                script_path,
                "--stage1_model", self.config["models"]["stage1_model"],
                "--stage2_model", self.config["models"]["stage2_model"],
                "--stage1_use_exl2",
                "--stage2_use_exl2",
                "--stage2_cache_size", str(self.config["generation"]["stage2_cache_size"]),
                "--max_new_tokens", str(self.config["generation"]["max_new_tokens"]),
                "--run_n_segments", str(self.config["generation"]["run_n_segments"]),
                "--stage2_batch_size", str(self.config["generation"]["stage2_batch_size"]),
                "--stage1_cache_size", str(self.config["generation"]["stage1_cache_size"])
            ]
            
            if self.config["generation"]["seed"] >= 0:
                cmd.extend(["--seed", str(self.config["generation"]["seed"])])
            
            if self.config["audio_prompt"]["use_audio_prompt"]:
                cmd.extend([
                    "--use_audio_prompt",
                    "--audio_prompt_path", self.config["audio_prompt"]["audio_prompt_path"],
                    "--prompt_start_time", str(self.config["audio_prompt"]["prompt_start_time"]),
                    "--prompt_end_time", str(self.config["audio_prompt"]["prompt_end_time"])
                ])
            
            # 儲存輸入到臨時文件
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            
            genre_path = temp_dir / "genre.txt"
            lyrics_path = temp_dir / "lyrics.txt"
            
            with open(genre_path, "w", encoding="utf-8") as f:
                f.write(self.genre_text.get("1.0", tk.END))
            with open(lyrics_path, "w", encoding="utf-8") as f:
                f.write(self.lyrics_text.get("1.0", tk.END))
            
            cmd.extend(["--genre_txt", str(genre_path), "--lyrics_txt", str(lyrics_path)])
            
            # 如果設定了輸出目錄
            if self.config["output"]["output_filename"]:
                output_dir = os.path.join(self.config["environment"]["output_dir"], self.config["output"]["output_filename"])
                cmd.extend(["--output_dir", output_dir])
            
            # 在執行命令前,將完整指令顯示在指令文本框中
            cmd_str = " ".join(cmd)
            self.command_text.insert(tk.END, "\n=== 執行指令 ===\n")
            self.command_text.insert(tk.END, f"{cmd_str}\n")
            self.command_text.insert(tk.END, "\n=== 執行輸出 ===\n")
            
            # 移除原本在 output_text 中的記錄
            self.output_text.delete(1.0, tk.END)
            
            # 開始執行
            self.run_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.progress.start()
            self.start_timer()  # 開始計時
            
            def run_process():
                try:
                    # 設置環境變數
                    env = os.environ.copy()
                    if self.config["venv_path"]:
                        if platform.system() == "Windows":
                            env["PATH"] = os.path.join(self.config["venv_path"], "Scripts") + os.pathsep + env["PATH"]
                        else:
                            env["PATH"] = os.path.join(self.config["venv_path"], "bin") + os.pathsep + env["PATH"]
                    
                    self.subprocess = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        env=env
                    )
                    
                    for line in self.subprocess.stdout:
                        if hasattr(self.process, 'stopped'):
                            break
                        
                        # 檢查是否為進度更新行
                        if "|" in line and "[A" in line:
                            # 清空隊列
                            while not self.output_queue.empty():
                                self.output_queue.get_nowait()
                            # 只保留最新的進度行
                            self.output_queue.put("progress_update:" + line.strip())
                        else:
                            # 一般訊息
                            self.output_queue.put("normal:" + line.strip())
                        
                    self.subprocess.wait()
                except Exception as e:

                    error_msg = f"錯誤: {str(e)}"
                    self.output_queue.put(error_msg)
            

            self.process = threading.Thread(target=run_process)
            self.process.start()
            self.root.after(100, self.update_output)
            
        except Exception as e:
            # 新增完整的按鈕狀態恢復
            self.run_button.configure(
                bg=self.colors['accent'],
                fg=self.colors['text_bright'],
                state="normal",
                text="生成音樂"
            )
            self.stop_button.configure(state="disabled")
            self.progress.stop()
            self.stop_timer()
            self.output_text.insert(tk.END, f"\n錯誤: {str(e)}\n")
            self.output_text.see(tk.END)
            messagebox.showerror("錯誤", str(e))
            return

    def apply_preset(self):
        """套用性能配置預設"""
        preset = self.preset_var.get()
        settings = self.config["recommended_settings"][preset]
        
        # 更新界面顯示
        self.stage2_cache_size.delete(0, tk.END)
        self.stage2_cache_size.insert(0, str(settings["stage2_cache_size"]))
        self.stage1_cache_size.delete(0, tk.END)
        self.stage1_cache_size.insert(0, str(settings["stage1_cache_size"]))
        
        # 更新配置
        self.config["generation"]["stage2_cache_size"] = settings["stage2_cache_size"]
        self.config["generation"]["stage1_cache_size"] = settings["stage1_cache_size"]
        self.save_config()
        
        messagebox.showinfo("成功", f"已套用{preset}配置")

    def add_genre_tag(self, tag):
        """添加風格標籤到輸入框"""
        current_text = self.genre_text.get("1.0", tk.END).strip()
        if current_text:
            # 檢查標籤是否已存在
            tags = current_text.split(", ")
            if tag not in tags:
                self.genre_text.delete(1.0, tk.END)
                self.genre_text.insert("1.0", current_text + ", " + tag)
        else:
            self.genre_text.insert("1.0", tag)

    def random_genre(self):
        """隨機選擇風格標籤"""
        # 從所有類別中選擇 5-5 個不同的類別
        categories = [cat for cat in self.genre_tags.keys() if "冷門" not in cat]
        if not categories:
            return
        
        num_categories = random.randint(5, 5)
        selected_categories = random.sample(categories, min(num_categories, len(categories)))
        
        # 從每個選中的類別中隨機選擇 1-1 個標籤
        selected_tags = []
        for category in selected_categories:
            tags = self.genre_tags[category]
            if tags:
                num_tags = random.randint(1, 1)
                category_tags = random.sample(tags, min(num_tags, len(tags)))
                for tag in category_tags:
                    # 處理標籤可能是元組/列表的情況
                    if isinstance(tag, (tuple, list)):
                        selected_tags.append(tag[1])  # 使用實際值
                    else:
                        selected_tags.append(tag)
        
        # 確保至少有一個標籤被選中
        if not selected_tags and categories:
            category = random.choice(categories)
            tags = self.genre_tags[category]
            if tags:
                tag = random.choice(tags)
                # 處理標籤可能是元組/列表的情況
                if isinstance(tag, (tuple, list)):
                    selected_tags.append(tag[1])  # 使用實際值
                else:
                    selected_tags.append(tag)
        
        # 清除現有文本並插入新的標籤
        if selected_tags:
            self.genre_text.delete(1.0, tk.END)
            self.genre_text.insert(1.0, ", ".join(selected_tags))

    def stop_generation(self):
        """中斷生成過程"""
        if self.process and self.process.is_alive():
            self.process.stopped = True
            if self.subprocess:
                if platform.system() == "Windows":
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.subprocess.pid)])
                else:
                    self.subprocess.terminate()
            self.progress.stop()
            
            # 修改這裡：正確恢復按鈕狀態
            self.run_button.configure(
                bg=self.colors['accent'],
                fg=self.colors['text_bright'],
                state="normal",
                text="生成音樂"
            )
            self.stop_button.configure(state="disabled")
            self.stop_timer()
            self.output_queue.put("生成過程已中斷")

    def toggle_audio_prompt(self):
        """切換音頻提示相關控件的狀態"""
        state = "normal" if self.use_audio_prompt.get() else "disabled"
        self.audio_prompt_path.configure(state=state)
        self.browse_audio_btn.configure(state=state)
        self.prompt_start_time.configure(state=state)
        self.prompt_end_time.configure(state=state)
        
        # 如果啟用音頻提示且時間欄位為空，則設置默認值
        if self.use_audio_prompt.get():
            if not self.prompt_start_time.get().strip():
                self.prompt_start_time.delete(0, tk.END)
                self.prompt_start_time.insert(0, "0.0")
            if not self.prompt_end_time.get().strip():
                self.prompt_end_time.delete(0, tk.END)
                self.prompt_end_time.insert(0, "30.0")

    def start_timer(self):
        """開始計時"""
        self.start_time = datetime.now()
        self.update_timer()
    
    def update_timer(self):
        """更新計時器顯示"""
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            minutes = int(elapsed.total_seconds() // 60)
            seconds = int(elapsed.total_seconds() % 60)
            self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")
            self.timer_id = self.root.after(1000, self.update_timer)
    
    def stop_timer(self):
        """停止計時"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            minutes = int(elapsed.total_seconds() // 60)
            seconds = int(elapsed.total_seconds() % 60)
            self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")
            self.start_time = None

    def create_scrollable_buttons(self, category_frame, tags):
        """創建可捲動的按鈕區域"""
        # 建立畫布和捲軸
        btn_canvas = tk.Canvas(
            category_frame,
            bg=self.colors['bg_darker'],  # 畫布背景色
            height=80,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            category_frame,
            orient="vertical",
            command=btn_canvas.yview,
            style='Vertical.TScrollbar'
        )
        
        # 建立按鈕容器時指定背景色
        btn_frame = tk.Frame(btn_canvas, bg=self.colors['bg_darker'])  # 修改這行
        
        # 配置捲動
        btn_canvas.configure(yscrollcommand=scrollbar.set)
        btn_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 創建視窗
        btn_canvas.create_window((0,0), window=btn_frame, anchor="nw")
        
        # 更新捲動區域的函數
        def update_scroll_region(event=None):
            btn_canvas.configure(scrollregion=btn_canvas.bbox("all"))
            canvas_height = max(80, min(btn_frame.winfo_reqheight(), 200))
            btn_canvas.configure(height=canvas_height)
        
        # 綁定更新函數
        btn_frame.bind("<Configure>", update_scroll_region)
        
        # 建立按鈕
        max_cols = 4
        row = col = 0
        for tag_pair in tags:
            # 檢查標籤是否為元組/列表（顯示文字和實際值）
            if isinstance(tag_pair, (tuple, list)):
                display_text, actual_tag = tag_pair
            else:
                display_text = actual_tag = tag_pair
                
            btn = tk.Button(
                btn_frame,
                text=display_text,  # 顯示文字
                command=lambda t=actual_tag: self.add_genre_tag(t),  # 實際添加的標籤
                width=18,
                bg=self.colors['button_bg'],
                fg=self.colors['text_bright'],
                activebackground=self.colors['button_hover'],
                activeforeground=self.colors['text_bright'],
                relief='flat',
                font=self.default_font
            )
            btn.grid(row=row, column=col, padx=3, pady=2, sticky="ew")
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def play_latest_preview(self):
        """預覽最新生成的音樂"""
        if hasattr(self, 'latest_mixed_file') and os.path.exists(self.latest_mixed_file):
            self.play_preview(self.latest_mixed_file)

    def open_latest_dir(self):
        """打開最新生成的目錄"""
        if hasattr(self, 'latest_output_dir') and os.path.exists(self.latest_output_dir):
            self.open_output_dir(self.latest_output_dir)

    def update_seed_state(self):
        """更新種子輸入框和按鈕的狀態"""
        if self.seed_mode.get() == "random":
            self.seed.configure(state="disabled")
            self.generate_seed_btn.configure(state="disabled")
            self.seed.delete(0, tk.END)
            self.seed.insert(0, "-1")  # 隨機模式使用 -1
        else:
            self.seed.configure(state="normal")
            self.generate_seed_btn.configure(state="normal")
            if self.seed.get() == "-1":  # 如果是 -1，清空輸入框
                self.seed.delete(0, tk.END)
    
    def generate_random_seed(self):
        """生成隨機種子"""
        random_seed = random.randint(0, 2**32-1)  # 生成 32 位正整數
        self.seed.delete(0, tk.END)
        self.seed.insert(0, str(random_seed))

def main():
    root = tk.Tk()
    app = YuEGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 