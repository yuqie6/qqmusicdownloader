# ui.py
import toga
from toga.style import Pack


class ModernUIStyles:
    COLORS = {
        "primary": "#6366f1",
        "primary_dark": "#4f46e5",
        "secondary": "#6b7280",
        "success": "#10b981",
        "background": "#f8fafc",
        "card": "#ffffff",
        "border": "#e2e8f0",
        "text": "#1f2937",
        "text_secondary": "#6b7280",
    }

    SPACING = {
        "xs": 2,  # 减小间距
        "sm": 4,
        "md": 8,
        "lg": 12,
        "xl": 16,
    }

    CARD_STYLE = Pack(
        direction="column",
        padding=SPACING["sm"],  # 减小padding
        background_color=COLORS["card"],
        flex=1,
    )

    HEADER_STYLE = Pack(
        padding=SPACING["sm"],
        font_size=16,  # 减小字体
        font_weight="bold",
        color=COLORS["text"],
    )

    BUTTON_PRIMARY = Pack(
        padding=(SPACING["xs"], SPACING["sm"]),
        background_color=COLORS["primary"],
        color="white",
        height=32,  # 减小按钮高度
        width=100,  # 减小按钮宽度
    )

    BUTTON_SUCCESS = Pack(
        padding=(SPACING["xs"], SPACING["sm"]),
        background_color=COLORS["success"],
        color="white",
        height=32,
        width=100,
    )


class QQMusicDownloaderUI:
    """QQ音乐下载器的UI实现，采用现代化设计"""

    def __init__(self, app):
        self.app = app
        self.styles = ModernUIStyles()
        self.setup_ui_components()

    def setup_ui_components(self):
        """初始化所有UI组件"""
        self.path_box = self.create_path_section()
        self.cookie_box = self.create_cookie_section()
        self.search_box = self.create_search_section()
        self.results_table = self.create_results_section()
        self.control_box = self.create_control_section()
        self.status_box = self.create_status_section()

    def create_main_box(self):
        """创建主容器，采用现代化布局"""
        main_box = toga.Box(
            style=Pack(
                direction="column",
                padding=self.styles.SPACING["lg"],
                background_color=self.styles.COLORS["background"],
                flex=1,
            )
        )

        # 添加顶部标题区域
        main_box.add(self.create_header_section())

        # 为每个功能区域创建容器并添加间距
        content_sections = [
            self.path_box,
            self.cookie_box,
            self.search_box,
            self.results_table,
            self.control_box,
            self.status_box,
        ]

        for section in content_sections:
            container = toga.Box(
                style=Pack(
                    direction="column", padding=(0, 0, self.styles.SPACING["md"], 0)
                )
            )
            container.add(section)
            main_box.add(container)

        return main_box

    def create_header_section(self):
        header_box = toga.Box(
            style=Pack(
                direction="row",
                padding=self.styles.SPACING["sm"],
                background_color="#2c3e50",
            )
        )

        title = toga.Label(
            "极简音乐下载器",
            style=Pack(
                font_size=16,
                font_weight="bold",
                color="#2ecc71",
                padding=(0, self.styles.SPACING["sm"]),
            ),
        )

        header_box.add(title)
        return header_box

    def create_path_section(self):
        box = toga.Box(style=self.styles.CARD_STYLE)

        path_container = toga.Box(
            style=Pack(
                direction="row",
                padding=(self.styles.SPACING["xs"], 0),
                alignment="center",
            )
        )

        self.path_label = toga.Label("下载路径将在登录后显示", style=Pack(flex=1))

        self.choose_path_button = toga.Button(
            "选择路径",
            on_press=self.app.choose_download_path,
            style=self.styles.BUTTON_PRIMARY,
        )

        path_container.add(self.path_label)
        path_container.add(self.choose_path_button)
        box.add(path_container)
        return box

    def create_cookie_section(self):
        box = toga.Box(style=self.styles.CARD_STYLE)

        self.cookie_input = toga.MultilineTextInput(
            placeholder="请输入QQ音乐Cookie",
            style=Pack(
                height=60,  # 减小高度
                padding=(self.styles.SPACING["xs"], 0),
                flex=1,
            ),
        )

        self.cookie_button = toga.Button(
            "保存Cookie",
            on_press=self.app.save_cookie,
            style=self.styles.BUTTON_PRIMARY,
        )

        box.add(self.cookie_input)
        box.add(self.cookie_button)
        return box

    def create_search_section(self):
        box = toga.Box(style=self.styles.CARD_STYLE)

        search_box = toga.Box(style=Pack(direction="row", alignment="center"))

        self.search_input = toga.TextInput(
            placeholder="输入歌曲名称搜索", style=Pack(flex=1, height=32)
        )

        self.search_button = toga.Button(
            "搜索", on_press=self.app.search_songs, style=self.styles.BUTTON_PRIMARY
        )

        search_box.add(self.search_input)
        search_box.add(self.search_button)
        box.add(search_box)
        return box

    def create_results_section(self):
        self.results_table = toga.Table(
            headings=["选择", "序号", "歌曲名", "歌手", "专辑"],
            accessors=["selected", "index", "name", "singer", "album"],
            data=[],
            style=Pack(
                flex=1,
                padding=self.styles.SPACING["xs"],
                background_color=self.styles.COLORS["card"],
                height=200,  # 减小表格高度
            ),
            on_select=self.app.on_table_select,
        )
        return self.results_table

    def create_control_section(self):
        box = toga.Box(style=self.styles.CARD_STYLE)

        controls = toga.Box(style=Pack(direction="row", alignment="center"))

        format_box = toga.Box(style=Pack(direction="row", alignment="center"))

        self.format_selection = toga.Selection(
            items=["M4A", "MP3", "FLAC"], style=Pack(width=100)
        )

        self.batch_switch = toga.Switch(
            "批量下载", style=Pack(padding=(0, self.styles.SPACING["md"]))
        )

        format_box.add(self.format_selection)
        format_box.add(self.batch_switch)
        controls.add(format_box)

        button_box = toga.Box(style=Pack(direction="row", alignment="center"))

        self.download_button = toga.Button(
            "下载", on_press=self.app.start_download, style=self.styles.BUTTON_SUCCESS
        )

        self.pause_button = toga.Button(
            "暂停下载", on_press=self.app.toggle_pause, style=self.styles.BUTTON_PRIMARY
        )
        self.pause_button.enabled = False

        button_box.add(self.download_button)
        button_box.add(toga.Box(style=Pack(width=self.styles.SPACING["sm"])))
        button_box.add(self.pause_button)

        box.add(controls)
        box.add(button_box)
        return box

    def create_status_section(self):
        box = toga.Box(style=self.styles.CARD_STYLE)

        self.progress_bar = toga.ProgressBar(
            style=Pack(flex=1, padding=(self.styles.SPACING["xs"], 0))
        )

        self.status_label = toga.Label(
            "准备就绪", style=Pack(padding=(self.styles.SPACING["xs"], 0))
        )

        box.add(self.progress_bar)
        box.add(self.status_label)
        return box

    def update_table_data(self, data):
        """更新表格数据"""
        self.results_table.data = data

    def set_path_label(self, text):
        """更新路径标签文本"""
        self.path_label.text = text

    def set_status_label(self, text):
        """更新状态标签文本"""
        self.status_label.text = text

    def update_progress(self, value):
        """更新进度条值"""
        self.progress_bar.value = value
