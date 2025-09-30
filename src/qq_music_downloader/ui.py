"""现代化的CustomTkinter UI界面"""

from pathlib import Path
from tkinter import TclError, filedialog, messagebox
import tkinter.font as tkfont
from typing import Any
import re
import shutil
import subprocess
import customtkinter as ctk


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


FONT_CACHE_DIR = Path(__file__).resolve().parent / "resources" / "font_cache"
ctk.FontManager.linux_font_path = str(FONT_CACHE_DIR)


def _prepare_font_resources() -> None:
    """在创建 Tk 根窗口之前预加载中文字体并刷新缓存。"""

    font_dir = Path(ctk.FontManager.linux_font_path)
    font_dir.mkdir(parents=True, exist_ok=True)

    resource_dir = Path(__file__).resolve().parent / "resources" / "fonts"
    font_candidates = [
        Path.home() / ".local/share/fonts/NotoSansCJK-Regular.ttc",
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
    ]
    font_candidates.extend(sorted(resource_dir.glob("*.otf")))
    font_candidates.extend(sorted(resource_dir.glob("*.ttf")))

    has_updates = False
    for font_path in font_candidates:
        if not font_path.exists():
            continue
        target_path = font_dir / font_path.name
        if not target_path.exists() or font_path.stat().st_mtime > target_path.stat().st_mtime:
            try:
                shutil.copy2(font_path, target_path)
                has_updates = True
            except OSError:
                continue

    if has_updates:
        try:
            subprocess.run(
                ["fc-cache", "-f", str(font_dir)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.CalledProcessError):
            pass


_prepare_font_resources()


class QQMusicUI:
    """基于CustomTkinter的QQ音乐下载器界面"""

    _UNICODE_ESCAPE_PATTERN = re.compile(r"\\u[0-9a-fA-F]{4}")

    def __init__(self):
        self.root = ctk.CTk()
        try:
            system_encoding = self.root.tk.call("encoding", "system")
            print(f"[UI] Tk system encoding: {system_encoding}")
            if system_encoding.lower() != "utf-8":
                self.root.tk.call("encoding", "system", "utf-8")
                print("[UI] Tk system encoding set to utf-8")
        except TclError as encoding_error:
            print(f"[UI] unable to query Tk encoding: {encoding_error}")
        self.root.title(self._normalize_text("QQ音乐下载器"))
        self.root.geometry("900x750")
        self.root.minsize(800, 700)

        self.app = None
        self.current_songs: list[dict[str, Any]] = []
        self.selected_indices = set()
        self.batch_mode = False

        self.setup_styles()
        self.create_widgets()
        self.center_window()
        self.root.after_idle(self._normalize_all_widget_texts)

    def set_app(self, app):
        """设置应用实例"""
        self.app = app

    def setup_styles(self):
        """设置界面样式"""
        self.colors = {
            "primary": "#3b82f6",
            "success": "#10b981",
            "bg": "#f8fafc",
            "card": "#ffffff",
            "text": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        }

        self.root.configure(fg_color=self.colors["bg"])
        self._load_font_resources()
        self.font_family = self._choose_font_family()
        print(f"[UI] selected font family: {self.font_family}")
        self._font_cache: dict[tuple[int, str], ctk.CTkFont] = {}

    def _normalize_text(self, text: str) -> str:
        """将包含 ``\\uXXXX`` 序列的文本还原为可见中文。"""

        if isinstance(text, str) and self._UNICODE_ESCAPE_PATTERN.search(text):
            try:
                return text.encode("utf-8").decode("unicode_escape")
            except UnicodeDecodeError:
                return text
        return text

    def _normalize_widget_text(self, widget) -> None:
        """尝试纠正某个控件当前的文本内容。"""

        try:
            current = widget.cget("text")
        except (AttributeError, TclError, TypeError, ValueError):
            current = None

        if isinstance(current, str):
            normalized = self._normalize_text(current)
            if "\\u" in current:
                print(
                    f"[UI] normalize {widget.__class__.__name__}: {current!r} -> {normalized!r}"
                )
            if normalized != current:
                try:
                    widget.configure(text=normalized)
                except (AttributeError, TclError, TypeError, ValueError):
                    pass

    def _normalize_widget_tree(self, widget) -> None:
        """递归遍历并修正常见控件的文本。"""

        self._normalize_widget_text(widget)
        try:
            children = widget.winfo_children()
        except (AttributeError, TclError):
            return

        for child in children:
            self._normalize_widget_tree(child)

    def _normalize_all_widget_texts(self) -> None:
        """对当前界面所有控件进行一次文本修正。"""

        self._normalize_widget_tree(self.root)

    def _load_font_resources(self) -> None:
        """加载可用的中文字体文件，提升界面文字显示效果。

        Returns:
            None: 无返回值。
        """

        font_dir = Path(ctk.FontManager.linux_font_path).expanduser()
        font_dir.mkdir(parents=True, exist_ok=True)

        font_candidates = [
            Path.home() / ".local/share/fonts/NotoSansCJK-Regular.ttc",
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/truetype/noto/NotoSansCJKsc-Regular.otf"),
            Path("/usr/share/fonts/truetype/noto/NotoSansSC-Regular.otf"),
            Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
            Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
        ]

        resource_dir = Path(__file__).resolve().parent / "resources" / "fonts"
        font_candidates.extend(sorted(resource_dir.glob("*.otf")))
        font_candidates.extend(sorted(resource_dir.glob("*.ttf")))

        loaded_fonts = []
        for font_path in font_candidates:
            if not font_path.exists():
                continue
            try:
                ctk.FontManager.load_font(str(font_path))
                loaded_fonts.append(font_path.name)
            except OSError:
                continue

        if loaded_fonts:
            print(f"已加载字体: {', '.join(loaded_fonts)}")
        else:
            print("警告: 未能加载任何中文字体")

    def _choose_font_family(self) -> str:
        """选择当前环境可用的中文友好字体.

        Returns:
            str: 匹配到的字体族名称。
        """

        resource_dir = Path(__file__).resolve().parent / "resources" / "fonts"
        font_candidates = [
            resource_dir / "NotoSansSC-Regular.otf",
            resource_dir / "NotoSansSC-Regular.ttf",
            Path.home() / ".local/share/fonts/NotoSansCJK-Regular.ttc",
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
        ]

        for font_path in font_candidates:
            if not font_path.exists():
                continue
            if ctk.FontManager.load_font(str(font_path)):
                print(f"[UI] loaded font file: {font_path.name}")

        try:
            self.root.update_idletasks()
        except TclError:
            pass

        preferred_fonts = [
            "Noto Sans CJK SC",
            "Noto Sans SC",
            "Source Han Sans SC",
            "思源黑体",
            "Microsoft YaHei UI",
            "Microsoft YaHei",
            "微软雅黑",
            "PingFang SC",
            "WenQuanYi Micro Hei",
            "SimHei",
            "Arial Unicode MS",
            "Segoe UI",
        ]

        available = {name.lower(): name for name in tkfont.families(self.root)}
        print(f"[UI] available font count: {len(available)}")
        debug_fonts = [
            name
            for name in available.values()
            if any(keyword in name.lower() for keyword in ["noto", "wqy", "hei", "song", "fang", "yuan"])
        ]
        print(f"[UI] sample fonts: {debug_fonts[:10]}")

        for font_name in preferred_fonts:
            try:
                candidate = tkfont.Font(root=self.root, family=font_name, size=12)
                actual = candidate.actual("family")
                normalized = (actual or "").lower()
                print(f"[UI] probe font: {font_name} -> actual {actual}")
                if normalized and normalized not in {"fixed", "tkdefaultfont"}:
                    return actual
            except TclError as error:
                print(f"[UI] probe failed: {font_name} -> {error}")

        for font_name in preferred_fonts:
            key = font_name.lower()
            if key in available and available[key] not in {"fixed", "tkdefaultfont"}:
                print(f"[UI] using font family from list: {available[key]}")
                return available[key]

        default_font = tkfont.nametofont("TkDefaultFont", root=self.root)
        fallback = default_font.actual("family")
        print(f"[UI] fallback font: {fallback}")
        return fallback

    def get_font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """返回带缓存的字体实例，确保中文显示正常。

        Args:
            size: 字号数值。
            weight: 字重描述，例如 "bold"。

        Returns:
            ctk.CTkFont: 匹配到的字体对象。
        """

        cache_key = (size, weight)
        if cache_key not in self._font_cache:
            self._font_cache[cache_key] = ctk.CTkFont(
                family=self.font_family,
                size=size,
                weight=weight,
            )
        return self._font_cache[cache_key]

    def center_window(self):
        """居中窗口"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """创建所有界面组件"""
        main_container = ctk.CTkScrollableFrame(
            self.root, fg_color="transparent", corner_radius=0
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_header(main_container)
        self.create_cookie_section(main_container)
        self.create_path_section(main_container)
        self.create_search_section(main_container)
        self.create_results_section(main_container)
        self.create_download_section(main_container)
        self.create_status_section(main_container)

    def create_header(self, parent):
        """创建标题区域"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 25))

        raw_title = self._normalize_text("🎵 QQ音乐下载器")
        print(f"[UI] header title -> {raw_title!r}")
        title_label = ctk.CTkLabel(
            header_frame,
            text=raw_title,
            font=self.get_font(32, "bold"),
            text_color=self.colors["text"],
        )
        title_label.pack()

        raw_subtitle = self._normalize_text("高品质音乐下载工具")
        print(f"[UI] header subtitle -> {raw_subtitle!r}")
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text=raw_subtitle,
            font=self.get_font(14),
            text_color=self.colors["text_secondary"],
        )
        subtitle_label.pack(pady=(5, 0))

    def create_cookie_section(self, parent):
        """创建Cookie配置区域"""
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=self.colors["card"])
        card.pack(fill="x", pady=(0, 15))

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            content_frame,
            text=self._normalize_text("账号配置"),
            font=self.get_font(18, "bold"),
            text_color=self.colors["text"],
            anchor="w",
        )
        title.pack(fill="x", pady=(0, 10))

        desc = ctk.CTkLabel(
            content_frame,
            text=self._normalize_text("从 y.qq.com 登录后复制完整的 Cookie 信息"),
            font=self.get_font(12),
            text_color=self.colors["text_secondary"],
            anchor="w",
        )
        desc.pack(fill="x", pady=(0, 10))

        self.cookie_textbox = ctk.CTkTextbox(
            content_frame,
            height=80,
            corner_radius=6,
            border_width=1,
            border_color=self.colors["border"],
        )
        self.cookie_textbox.pack(fill="x", pady=(0, 10))

        self.cookie_button = ctk.CTkButton(
            content_frame,
            text=self._normalize_text("保存并验证"),
            command=self.save_cookie,
            height=35,
            corner_radius=6,
            font=self.get_font(14),
        )
        self.cookie_button.pack(anchor="e")

    def create_path_section(self, parent):
        """创建下载路径设置区域"""
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=self.colors["card"])
        card.pack(fill="x", pady=(0, 15))

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            content_frame,
            text=self._normalize_text("下载目录"),
            font=self.get_font(18, "bold"),
            text_color=self.colors["text"],
            anchor="w",
        )
        title.pack(fill="x", pady=(0, 10))

        path_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        path_frame.pack(fill="x")

        self.path_label = ctk.CTkLabel(
            path_frame,
            text=self._normalize_text("请先配置Cookie"),
            font=self.get_font(12),
            text_color=self.colors["text_secondary"],
            anchor="w",
        )
        self.path_label.pack(side="left", fill="x", expand=True)

        self.path_button = ctk.CTkButton(
            path_frame,
            text=self._normalize_text("选择目录"),
            command=self.choose_path,
            width=100,
            height=30,
            corner_radius=6,
            font=self.get_font(13),
        )
        self.path_button.pack(side="right", padx=(10, 0))

    def create_search_section(self, parent):
        """创建搜索区域"""
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=self.colors["card"])
        card.pack(fill="x", pady=(0, 15))

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            content_frame,
            text=self._normalize_text("搜索音乐"),
            font=self.get_font(18, "bold"),
            text_color=self.colors["text"],
            anchor="w",
        )
        title.pack(fill="x", pady=(0, 10))

        search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        search_frame.pack(fill="x")

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=self._normalize_text("输入歌曲名称或歌手"),
            height=40,
            corner_radius=6,
            border_width=1,
            border_color=self.colors["border"],
            font=self.get_font(14),
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.search_button = ctk.CTkButton(
            search_frame,
            text=self._normalize_text("搜索"),
            command=self.search_songs,
            width=80,
            height=40,
            corner_radius=6,
            font=self.get_font(14, "bold"),
        )
        self.search_button.pack(side="right")

    def create_results_section(self, parent):
        """创建搜索结果区域"""
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=self.colors["card"])
        card.pack(fill="x", pady=(0, 15))

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            header_frame,
            text=self._normalize_text("搜索结果"),
            font=self.get_font(18, "bold"),
            text_color=self.colors["text"],
            anchor="w",
        )
        title.pack(side="left")

        self.batch_switch = ctk.CTkSwitch(
            header_frame,
            text=self._normalize_text("批量模式"),
            command=self.toggle_batch_mode,
            button_color=self.colors["primary"],
            progress_color=self.colors["primary"],
        )
        self.batch_switch.pack(side="right", padx=(10, 0))

        list_frame = ctk.CTkFrame(
            content_frame, corner_radius=6, fg_color=self.colors["bg"], height=250
        )
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        list_frame.pack_propagate(False)

        self.results_frame = ctk.CTkScrollableFrame(
            list_frame, fg_color="transparent", corner_radius=0
        )
        self.results_frame.pack(fill="both", expand=True, padx=1, pady=1)

        self.result_items = []

        tip = ctk.CTkLabel(
            content_frame,
            text=self._normalize_text("点击歌曲可选择，批量模式下支持多选"),
            font=self.get_font(11),
            text_color=self.colors["text_secondary"],
        )
        tip.pack(anchor="w")

    def create_download_section(self, parent):
        """创建下载控制区域"""
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=self.colors["card"])
        card.pack(fill="x", pady=(0, 15))

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            content_frame,
            text=self._normalize_text("下载设置"),
            font=self.get_font(18, "bold"),
            text_color=self.colors["text"],
            anchor="w",
        )
        title.pack(fill="x", pady=(0, 15))

        controls_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=(0, 15))

        format_label = ctk.CTkLabel(
            controls_frame,
            text=self._normalize_text("音质格式"),
            font=self.get_font(13),
            text_color=self.colors["text_secondary"],
        )
        format_label.pack(side="left", padx=(0, 10))

        format_values = [
            self._normalize_text(value)
            for value in ["M4A (128kbps)", "MP3 (320kbps)", "FLAC (无损)"]
        ]

        self.format_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=format_values,
            width=150,
            height=32,
            corner_radius=6,
            font=self.get_font(13),
        )
        self.format_menu.pack(side="left")

        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(anchor="w")

        self.download_button = ctk.CTkButton(
            buttons_frame,
            text=self._normalize_text("开始下载"),
            command=self.start_download,
            width=120,
            height=38,
            corner_radius=6,
            fg_color=self.colors["success"],
            hover_color="#059669",
            font=self.get_font(14, "bold"),
        )
        self.download_button.pack(side="left", padx=(0, 10))

        self.pause_button = ctk.CTkButton(
            buttons_frame,
            text=self._normalize_text("暂停/恢复"),
            command=self.toggle_pause,
            width=120,
            height=38,
            corner_radius=6,
            state="disabled",
            font=self.get_font(14),
        )
        self.pause_button.pack(side="left")

    def create_status_section(self, parent):
        """创建状态显示区域"""
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=self.colors["card"])
        card.pack(fill="x")

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            content_frame,
            text=self._normalize_text("下载进度"),
            font=self.get_font(18, "bold"),
            text_color=self.colors["text"],
            anchor="w",
        )
        title.pack(fill="x", pady=(0, 10))

        self.progress_bar = ctk.CTkProgressBar(
            content_frame,
            height=8,
            corner_radius=4,
            progress_color=self.colors["primary"],
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            content_frame,
            text=self._normalize_text("准备就绪"),
            font=self.get_font(12),
            text_color=self.colors["text_secondary"],
        )
        self.status_label.pack(anchor="w")

    def update_results(self, songs: list[dict[str, Any]]):
        """更新搜索结果列表"""
        for item in self.result_items:
            item.destroy()
        self.result_items.clear()
        self.current_songs = songs
        self.selected_indices.clear()

        for i, song in enumerate(songs):
            item_frame = ctk.CTkFrame(
                self.results_frame,
                corner_radius=6,
                fg_color="transparent",
                cursor="hand2",
            )
            item_frame.pack(fill="x", pady=2)

            checkbox = ctk.CTkCheckBox(
                item_frame,
                text="",
                width=24,
                command=lambda idx=i: self.toggle_selection(idx),
            )
            checkbox.pack(side="left", padx=(10, 5))

            info_text = self._normalize_text(
                f"{i + 1}. {song['name']} - {song['singer']} ({song['album']})"
            )
            info_label = ctk.CTkLabel(
                item_frame,
                text=info_text,
                font=self.get_font(13),
                text_color=self.colors["text"],
                anchor="w",
            )
            info_label.pack(side="left", fill="x", expand=True, padx=5)

            item_frame.bind(
                "<Button-1>", lambda e, idx=i, cb=checkbox: self.on_item_click(idx, cb)
            )
            info_label.bind(
                "<Button-1>", lambda e, idx=i, cb=checkbox: self.on_item_click(idx, cb)
            )

            self.result_items.append(
                {"frame": item_frame, "checkbox": checkbox, "index": i}
            )

    def on_item_click(self, index, checkbox):
        """处理列表项点击"""
        if checkbox.get():
            checkbox.deselect()
        else:
            checkbox.select()
        self.toggle_selection(index)

    def toggle_selection(self, index):
        """切换选中状态"""
        if index in self.selected_indices:
            self.selected_indices.remove(index)
        else:
            if not self.batch_mode:
                self.selected_indices.clear()
                for item in self.result_items:
                    if item["index"] != index:
                        item["checkbox"].deselect()
            self.selected_indices.add(index)

    def toggle_batch_mode(self):
        """切换批量模式"""
        self.batch_mode = self.batch_switch.get()
        if not self.batch_mode:
            if len(self.selected_indices) > 1:
                first_selected = min(self.selected_indices)
                self.selected_indices = {first_selected}
                for item in self.result_items:
                    if item["index"] != first_selected:
                        item["checkbox"].deselect()

    def save_cookie(self):
        """保存Cookie"""
        cookie = self.cookie_textbox.get("1.0", "end-1c").strip()
        if not cookie:
            messagebox.showwarning(
                self._normalize_text("提示"),
                self._normalize_text("请输入Cookie"),
            )
            return

        if self.app:
            self.app.submit_coroutine(self.app.save_cookie_async(cookie))

    def choose_path(self):
        """选择下载路径"""
        path = filedialog.askdirectory(title=self._normalize_text("选择下载目录"))
        if path:
            self.path_label.configure(text=self._normalize_text(path))
            if self.app:
                self.app.update_download_path(path)

    def search_songs(self):
        """搜索歌曲"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning(
                self._normalize_text("提示"),
                self._normalize_text("请输入搜索关键词"),
            )
            return

        if self.app:
            self.app.submit_coroutine(self.app.search_songs_async(keyword))

    def start_download(self):
        """开始下载"""
        if not self.selected_indices:
            messagebox.showwarning(
                self._normalize_text("提示"),
                self._normalize_text("请先选择要下载的歌曲"),
            )
            return

        quality_map = {
            self._normalize_text("M4A (128kbps)"): 1,
            self._normalize_text("MP3 (320kbps)"): 2,
            self._normalize_text("FLAC (无损)"): 3,
        }
        quality = quality_map.get(self.format_menu.get(), 1)

        if self.app:
            self.app.submit_coroutine(
                self.app.start_download_async(list(self.selected_indices), quality)
            )

    def toggle_pause(self):
        """切换暂停状态"""
        if self.app:
            self.app.toggle_pause()

    def set_status(self, text: str):
        """设置状态文本"""
        self.status_label.configure(text=self._normalize_text(text))

    def set_progress(self, value: float):
        """设置进度条值"""
        self.progress_bar.set(value)

    def set_download_path_label(self, path: str):
        """设置路径标签"""
        self.path_label.configure(text=self._normalize_text(path))

    def enable_download_controls(self, enabled: bool):
        """启用/禁用下载控制按钮"""
        state = "normal" if enabled else "disabled"
        self.download_button.configure(state=state)
        self.pause_button.configure(state="normal" if not enabled else "disabled")

    def run(self):
        """运行主界面"""
        self.root.mainloop()
