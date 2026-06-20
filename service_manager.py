"""
服务管理器 v2 - 美观版
支持配置文件扩展，现代化界面设计
"""

import customtkinter as ctk
import subprocess
import threading
import json
import os
import sys
import ctypes
from pathlib import Path
from tkinter import messagebox


class ToastManager:
    """内置 Toast 管理器 - 显示在窗口内部"""

    def __init__(self, master):
        """
        初始化 Toast 管理器
        master: 主窗口
        """
        self.master = master
        self.toast_container = None
        self.toast_label = None
        self.toast_icon = None
        self.hide_job = None
        self.toast_queue = []  # 消息队列

    def show(self, message, toast_type="info", duration=2500):
        """
        显示 Toast 提示
        message: 提示内容
        toast_type: 类型 (success/error/info)
        duration: 显示时长(毫秒)
        """
        # 如果已有 Toast，加入队列
        if self.toast_container:
            self.toast_queue.append((message, toast_type, duration))
            return

        self._show_toast(message, toast_type, duration)

    def _show_toast(self, message, toast_type, duration):
        """实际显示 Toast"""
        # 颜色配置
        colors = {
            "success": ("#198754", "#d4edda", "✓"),
            "error": ("#dc3545", "#f8d7da", "✗"),
            "info": ("#0d6efd", "#cce5ff", "ℹ"),
        }
        text_color, bg_color, icon = colors.get(toast_type, colors["info"])

        # 创建 Toast 容器（先不显示）
        self.toast_container = ctk.CTkFrame(
            self.master,
            fg_color=bg_color,
            corner_radius=10,
            border_width=1,
            border_color=text_color,
        )

        # 内容
        frame = ctk.CTkFrame(self.toast_container, fg_color="transparent")
        frame.pack(padx=15, pady=10)

        # 图标
        self.toast_icon = ctk.CTkLabel(
            frame,
            text=icon,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=text_color,
        )
        self.toast_icon.pack(side="left", padx=(0, 8))

        # 消息
        self.toast_label = ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=text_color,
        )
        self.toast_label.pack(side="left")

        # 先用 grid 隐藏，等大小确定后再显示
        self.toast_container.grid_remove()

        # 强制计算大小
        self.toast_container.update_idletasks()

        # 计算位置（窗口顶部居中）
        toast_width = self.toast_container.winfo_reqwidth()
        master_width = self.master.winfo_width()
        x = (master_width - toast_width) // 2

        # 使用 place 定位并显示
        self.toast_container.place(x=x, y=20)

        # 自动隐藏
        self.hide_job = self.master.after(duration, self.hide)

    def hide(self):
        """隐藏 Toast"""
        if self.hide_job:
            self.master.after_cancel(self.hide_job)
            self.hide_job = None

        if self.toast_container:
            self.toast_container.destroy()
            self.toast_container = None
            self.toast_label = None
            self.toast_icon = None

        # 显示队列中的下一个 Toast
        if self.toast_queue:
            next_toast = self.toast_queue.pop(0)
            self.master.after(100, lambda: self._show_toast(*next_toast))


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def request_admin():
    """请求管理员权限重新启动"""
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        except:
            pass
        sys.exit(0)

# 设置主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def get_app_dir():
    """获取应用程序所在目录（兼容打包后的 .exe）"""
    if getattr(sys, 'frozen', False):
        # 打包后的 .exe 运行
        return Path(sys.executable).parent
    else:
        # 源代码运行
        return Path(__file__).parent.absolute()


import sys

# 获取脚本所在目录
SCRIPT_DIR = get_app_dir()
CONFIG_FILE = SCRIPT_DIR / "config.json"
ICON_FILE = SCRIPT_DIR / "service_manager.ico"


class ServiceCard(ctk.CTkFrame):
    """单个服务卡片组件"""

    def __init__(self, master, service_config, main_window, on_status_change=None):
        super().__init__(master, height=90, corner_radius=12)
        self.pack_propagate(False)

        self.service_config = service_config
        self.main_window = main_window  # 主窗口引用
        self.on_status_change = on_status_change
        self.is_running = False

        self.create_widgets()

    def create_widgets(self):
        # 左侧：图标和信息
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.pack(side="left", fill="y", padx=15, pady=10)

        # 图标和名称
        icon_label = ctk.CTkLabel(
            left_frame,
            text=self.service_config.get("icon", "⚙️"),
            font=ctk.CTkFont(size=28),
        )
        icon_label.pack(side="left", padx=(0, 10))

        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="y")

        name_label = ctk.CTkLabel(
            info_frame,
            text=self.service_config["display_name"],
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        name_label.pack(anchor="w")

        desc_label = ctk.CTkLabel(
            info_frame,
            text=self.service_config.get("description", ""),
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            anchor="w",
        )
        desc_label.pack(anchor="w")

        # 中间：状态指示器
        middle_frame = ctk.CTkFrame(self, fg_color="transparent")
        middle_frame.pack(side="left", fill="y", padx=10)

        self.status_indicator = ctk.CTkLabel(
            middle_frame,
            text="●",
            font=ctk.CTkFont(size=24),
            text_color="gray50",
        )
        self.status_indicator.pack(pady=25)

        # 右侧：状态文本和操作按钮
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right", fill="y", padx=15, pady=10)

        self.status_label = ctk.CTkLabel(
            right_frame,
            text="检测中...",
            font=ctk.CTkFont(size=13),
            width=80,
        )
        self.status_label.pack(pady=(5, 8))

        # 按钮容器
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack()

        # 加载动画标签（隐藏）
        self.loading_label = ctk.CTkLabel(
            btn_frame,
            text="⏳",
            font=ctk.CTkFont(size=16),
            text_color="#ffc107",
            width=30,
        )

        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="启动",
            width=70,
            height=28,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color="#198754",
            hover_color="#157347",
            command=self.start_service,
        )
        self.start_btn.pack(side="left", padx=3)

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="停止",
            width=70,
            height=28,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color="#dc3545",
            hover_color="#bb2d3b",
            command=self.stop_service,
        )
        self.stop_btn.pack(side="left", padx=3)

        # 动画状态
        self.is_loading = False
        self.loading_frames = ["⏳", "⏳", "⏳", "⏳"]
        self.loading_index = 0

    def check_status(self):
        """检查服务状态"""
        try:
            service_name = self.service_config.get("service_name", self.service_config["name"])
            result = subprocess.run(
                ["sc", "query", service_name],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return "RUNNING" in result.stdout
        except Exception:
            return False

    def update_status(self):
        """更新状态显示"""
        self.is_running = self.check_status()

        if self.is_running:
            self.status_indicator.configure(text_color="#198754")
            self.status_label.configure(text="运行中", text_color="#198754")
        else:
            self.status_indicator.configure(text_color="#dc3545")
            self.status_label.configure(text="已停止", text_color="#dc3545")

    def start_loading(self, status_text="处理中..."):
        """开始加载动画"""
        self.is_loading = True
        self.loading_index = 0

        # 隐藏按钮，显示加载动画
        self.start_btn.pack_forget()
        self.stop_btn.pack_forget()

        self.loading_label.configure(text=status_text)
        self.loading_label.pack(side="left", padx=3)
        self.status_label.configure(text="处理中...", text_color="#ffc107")

        # 开始动画
        self.animate()

    def stop_loading(self):
        """停止加载动画"""
        self.is_loading = False
        self.loading_label.pack_forget()

        # 恢复按钮
        self.start_btn.pack(side="left", padx=3)
        self.stop_btn.pack(side="left", padx=3)

    def animate(self):
        """动画效果"""
        if not self.is_loading:
            return

        # 旋转动画符号
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading_index = (self.loading_index + 1) % len(spinners)
        self.loading_label.configure(text=spinners[self.loading_index])

        # 每 100ms 更新一次
        if self.is_loading:
            self.after(100, self.animate)

    def start_service(self):
        """启动服务"""
        # 检查是否已在运行
        if self.check_status():
            self.status_label.configure(text="已运行", text_color="#198754")
            self.main_window.toast_manager.show(f"{self.service_config['display_name']} 已在运行中", "info")
            return

        self.start_loading("启动中")

        def _start():
            try:
                service_name = self.service_config.get("service_name", self.service_config["name"])
                subprocess.run(
                    ["net", "start", service_name],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                self.after(0, lambda: self.main_window.toast_manager.show(f"{self.service_config['display_name']} 启动成功", "success"))
            except Exception as e:
                self.after(0, lambda: self.main_window.toast_manager.show(f"启动失败: {str(e)}", "error"))

            self.after(200, self._on_complete)

        threading.Thread(target=_start, daemon=True).start()

    def stop_service(self):
        """停止服务"""
        # 检查是否已停止
        if not self.check_status():
            self.status_label.configure(text="已停止", text_color="#dc3545")
            self.main_window.toast_manager.show(f"{self.service_config['display_name']} 已停止", "info")
            return

        self.start_loading("停止中")

        def _stop():
            try:
                service_name = self.service_config.get("service_name", self.service_config["name"])
                subprocess.run(
                    ["net", "stop", service_name],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                self.after(0, lambda: self.main_window.toast_manager.show(f"{self.service_config['display_name']} 已停止", "success"))
            except Exception as e:
                self.after(0, lambda: self.main_window.toast_manager.show(f"停止失败: {str(e)}", "error"))

            self.after(200, self._on_complete)

        threading.Thread(target=_stop, daemon=True).start()

    def set_buttons_state(self, state):
        """设置按钮状态"""
        self.start_btn.configure(state=state)
        self.stop_btn.configure(state=state)

    def _on_complete(self):
        """操作完成回调"""
        self.stop_loading()
        self.update_status()
        if self.on_status_change:
            self.on_status_change()


class ServiceManager(ctk.CTk):
    """服务管理器主窗口"""

    def __init__(self):
        super().__init__()

        # 加载配置
        self.config = self.load_config()

        # 窗口配置
        window_config = self.config.get("window", {})
        self.title(window_config.get("title", "服务管理器"))
        width = window_config.get('width', 600)
        height = window_config.get('height', 500)
        self.geometry(f"{width}x{height}")
        self.minsize(500, 400)

        # 窗口居中显示 - 使用 after 确保窗口已显示
        self.after(10, self.center_window)

        # 设置窗口图标
        if ICON_FILE.exists():
            self.iconbitmap(ICON_FILE)

        # 初始化 Toast 管理器
        self.toast_manager = ToastManager(self)

        self.service_cards = []
        self.create_widgets()
        self.refresh_all_status()

    def center_window(self):
        """窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"+{x}+{y}")

    def load_config(self):
        """加载配置文件"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"services": [], "window": {}}

    def save_config(self):
        """保存配置文件"""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def create_widgets(self):
        # 主容器
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # 顶部标题栏
        self.create_header(main_frame)

        # 服务列表
        self.create_service_list(main_frame)

        # 底部控制栏
        self.create_footer(main_frame)

    def create_header(self, parent):
        """创建顶部标题"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(
            header_frame,
            text="⚙️ 服务管理器",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.pack(side="left")

    def create_service_list(self, parent):
        """创建服务列表"""
        # 滚动容器
        scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color="gray40",
            scrollbar_button_hover_color="gray50",
        )
        scroll_frame.pack(fill="both", expand=True)

        # 为每个服务创建卡片
        for service in self.config.get("services", []):
            card = ServiceCard(
                scroll_frame,
                service_config=service,
                main_window=self,  # 传入主窗口引用
                on_status_change=self.update_footer_status,
            )
            card.pack(fill="x", pady=5)
            self.service_cards.append(card)

    def create_footer(self, parent):
        """创建底部控制栏"""
        footer_frame = ctk.CTkFrame(parent, corner_radius=10)
        footer_frame.pack(fill="x", pady=(15, 0))

        # 左侧：状态统计
        self.status_summary = ctk.CTkLabel(
            footer_frame,
            text="就绪",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
        )
        self.status_summary.pack(side="left", padx=15, pady=12)

        # 右侧：批量操作按钮
        btn_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=15, pady=10)

        self.start_all_btn = ctk.CTkButton(
            btn_frame,
            text="▶ 全部启动",
            width=100,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#198754",
            hover_color="#157347",
            command=self.start_all_services,
        )
        self.start_all_btn.pack(side="left", padx=5)

        self.stop_all_btn = ctk.CTkButton(
            btn_frame,
            text="⏹ 全部停止",
            width=100,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#dc3545",
            hover_color="#bb2d3b",
            command=self.stop_all_services,
        )
        self.stop_all_btn.pack(side="left", padx=5)

    def refresh_all_status(self):
        """刷新所有服务状态"""
        self.status_summary.configure(text="正在检测...")
        self.after(100, self._do_refresh)

    def _do_refresh(self):
        def _refresh():
            for card in self.service_cards:
                card.update_status()
            self.after(0, self.update_footer_status)

        threading.Thread(target=_refresh, daemon=True).start()

    def update_footer_status(self):
        """更新底部状态统计"""
        running = sum(1 for card in self.service_cards if card.is_running)
        total = len(self.service_cards)
        self.status_summary.configure(text=f"运行中: {running}/{total}")

    def start_all_services(self):
        """启动所有服务"""
        self.set_all_buttons_state("disabled")
        self.set_all_cards_buttons_state("disabled")  # 禁用所有卡片按钮
        self.toast_manager.show("正在启动所有服务...", "info", 1500)

        def _start_all():
            try:
                for card in self.service_cards:
                    if not card.is_running:
                        service_name = card.service_config.get("service_name", card.service_config["name"])
                        subprocess.run(
                            ["net", "start", service_name],
                            capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW,
                        )
                self.after(0, lambda: self.toast_manager.show("所有服务启动完成", "success"))
            except Exception as e:
                self.after(0, lambda: self.toast_manager.show(f"启动失败: {str(e)}", "error"))

            self.after(1500, self._on_all_complete)

        threading.Thread(target=_start_all, daemon=True).start()

    def stop_all_services(self):
        """停止所有服务"""
        self.set_all_buttons_state("disabled")
        self.set_all_cards_buttons_state("disabled")  # 禁用所有卡片按钮
        self.toast_manager.show("正在停止所有服务...", "info", 1500)

        def _stop_all():
            try:
                for card in self.service_cards:
                    if card.is_running:
                        service_name = card.service_config.get("service_name", card.service_config["name"])
                        subprocess.run(
                            ["net", "stop", service_name],
                            capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW,
                        )
                self.after(0, lambda: self.toast_manager.show("所有服务已停止", "success"))
            except Exception as e:
                self.after(0, lambda: self.toast_manager.show(f"停止失败: {str(e)}", "error"))

            self.after(1500, self._on_all_complete)

        threading.Thread(target=_stop_all, daemon=True).start()

    def set_all_buttons_state(self, state):
        """设置底部按钮状态"""
        self.start_all_btn.configure(state=state)
        self.stop_all_btn.configure(state=state)

    def set_all_cards_buttons_state(self, state):
        """设置所有卡片按钮状态"""
        for card in self.service_cards:
            card.set_buttons_state(state)

    def _on_all_complete(self):
        """所有操作完成回调"""
        self.set_all_buttons_state("normal")
        self.set_all_cards_buttons_state("normal")  # 恢复卡片按钮
        self.refresh_all_status()


if __name__ == "__main__":
    # 检查并请求管理员权限
    request_admin()

    app = ServiceManager()
    app.mainloop()
