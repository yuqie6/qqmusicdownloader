# ui.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

class ModernUIStyles:
    """现代化UI样式系统，提供统一的视觉设计标准"""
    
    # 颜色系统定义了应用程序的主要配色方案
    COLORS = {
        'primary': '#2563eb',      # 主题蓝，用于主要按钮和重要元素
        'primary_dark': '#1e40af',  # 深蓝，用于悬停状态
        'secondary': '#4b5563',    # 辅助灰，用于次要文本和图标
        'success': '#10b981',      # 成功绿，用于完成和确认操作
        'warning': '#f59e0b',      # 警告橙，用于需要注意的状态
        'error': '#ef4444',        # 错误红，用于错误提示
        'background': '#f8fafc',   # 主背景色，整体页面背景
        'card': '#ffffff',         # 卡片背景，用于内容区块
        'border': '#e2e8f0',       # 边框色，用于分隔线和边框
        'text': '#1f2937',         # 主文本色，用于主要文字
        'text_secondary': '#6b7280' # 次要文本色，用于辅助文字
    }
    
    # 间距系统确保整个界面有统一的间距规范
    SPACING = {
        'xs': 4,   # 最小间距，用于紧凑元素
        'sm': 8,   # 小间距，用于相关元素
        'md': 16,  # 中等间距，用于一般元素
        'lg': 24,  # 大间距，用于主要分区
        'xl': 32   # 最大间距，用于独立区块
    }

    # 基础卡片样式，用于内容区块
    CARD_STYLE = Pack(
        direction=COLUMN,
        padding=SPACING['md'],
        background_color=COLORS['card'],
        flex=1
    )

    # 标题样式，用于区块标题
    HEADER_STYLE = Pack(
        padding=SPACING['md'],
        font_size=16,
        font_weight='bold',
        color=COLORS['text']
    )

    # 主要按钮样式
    BUTTON_PRIMARY = Pack(
        padding=(SPACING['sm'], SPACING['md']),
        background_color=COLORS['primary'],
        color='white',
        height=36,
        width=120
    )

    # 成功按钮样式
    BUTTON_SUCCESS = Pack(
        padding=(SPACING['sm'], SPACING['md']),
        background_color=COLORS['success'],
        color='white',
        height=36,
        width=120
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
        main_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=self.styles.SPACING['lg'],
            background_color=self.styles.COLORS['background'],
            flex=1
        ))

        # 添加顶部标题区域
        main_box.add(self.create_header_section())

        # 为每个功能区域创建容器并添加间距
        content_sections = [
            self.path_box,
            self.cookie_box,
            self.search_box,
            self.results_table,
            self.control_box,
            self.status_box
        ]

        for section in content_sections:
            container = toga.Box(style=Pack(
                direction=COLUMN,
                padding=(0, 0, self.styles.SPACING['md'], 0)
            ))
            container.add(section)
            main_box.add(container)

        return main_box

    def create_header_section(self):
        """创建应用标题区域"""
        header_box = toga.Box(style=Pack(
            direction=ROW,
            padding=self.styles.SPACING['md'],
            background_color=self.styles.COLORS['primary']
        ))

        title = toga.Label(
            'QQ音乐下载器',
            style=Pack(
                font_size=20,
                font_weight='bold',
                color='white',
                padding=(0, self.styles.SPACING['md'])
            )
        )
        header_box.add(title)
        return header_box

    def create_path_section(self):
        """创建下载路径显示区域"""
        box = toga.Box(style=self.styles.CARD_STYLE)
        
        self.path_label = toga.Label(
            '下载路径将在登录后显示',
            style=Pack(
                padding=(self.styles.SPACING['sm'], 0),
                color=self.styles.COLORS['text']
            )
        )
        box.add(self.path_label)
        return box

    def create_cookie_section(self):
        """创建Cookie设置区域"""
        box = toga.Box(style=self.styles.CARD_STYLE)
        
        # 添加标题
        header = toga.Label(
            'Cookie设置',
            style=self.styles.HEADER_STYLE
        )
        box.add(header)
        
        # Cookie输入框
        self.cookie_input = toga.MultilineTextInput(
            placeholder='请输入QQ音乐Cookie',
            style=Pack(
                height=80,
                padding=(self.styles.SPACING['sm'], 0),
                flex=1
            )
        )
        box.add(self.cookie_input)
        
        # 保存按钮容器
        button_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(self.styles.SPACING['md'], 0, 0, 0)
        ))
        
        self.cookie_button = toga.Button(
            '保存Cookie',
            on_press=self.app.save_cookie,
            style=self.styles.BUTTON_PRIMARY
        )
        button_box.add(self.cookie_button)
        box.add(button_box)
        
        return box

    def create_search_section(self):
        """创建搜索区域"""
        box = toga.Box(style=self.styles.CARD_STYLE)
        
        search_box = toga.Box(style=Pack(
            direction=ROW,
            alignment='center'
        ))
        
        # 搜索输入框
        self.search_input = toga.TextInput(
            placeholder='请输入歌曲名称',
            style=Pack(
                flex=1,
                padding=(0, self.styles.SPACING['md'], 0, 0),
                height=36
            )
        )
        
        # 搜索按钮
        self.search_button = toga.Button(
            '搜索',
            on_press=self.app.search_songs,
            style=self.styles.BUTTON_PRIMARY
        )
        
        search_box.add(self.search_input)
        search_box.add(self.search_button)
        box.add(search_box)
        
        return box

    def create_results_section(self):
        """创建搜索结果显示区域"""
        self.results_table = toga.Table(
            headings=['选择', '序号', '歌曲名', '歌手', '专辑'],
            accessors=['selected', 'index', 'name', 'singer', 'album'],
            data=[],
            style=Pack(
                flex=1,
                padding=self.styles.SPACING['sm'],
                background_color=self.styles.COLORS['card'],
                height=300  # 使用固定高度替代 min_height
            ),
            on_select=self.app.on_table_select
        )
        return self.results_table
    def create_control_section(self):
        """创建下载控制区域"""
        box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=self.styles.SPACING['md'],
            background_color=self.styles.COLORS['card']
        ))

        # 上部分：音质选择和批量模式
        top_controls = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, self.styles.SPACING['md'], 0)
        ))

        # 音质选择组件
        quality_box = toga.Box(style=Pack(
            direction=ROW,
            alignment='center'
        ))
        quality_label = toga.Label(
            '音质选择:',
            style=Pack(
                padding=(0, self.styles.SPACING['sm'], 0, 0),
                color=self.styles.COLORS['text']
            )
        )
        quality_items = ['标准品质 (128kbps)', '高品质 (320kbps)', '无损品质 (FLAC)']
        self.quality_selection = toga.Selection(
            items=quality_items,
            style=Pack(width=200)
        )
        quality_box.add(quality_label)
        quality_box.add(self.quality_selection)

        # 批量模式开关
        self.batch_switch = toga.Switch(
            '批量模式',
            style=Pack(padding=(0, self.styles.SPACING['lg']))
        )
        
        top_controls.add(quality_box)
        top_controls.add(self.batch_switch)
        
        # 下载按钮区域
        button_box = toga.Box(style=Pack(
            direction=ROW,
            alignment='center'
        ))
        
        self.download_button = toga.Button(
            '下载选中歌曲',
            on_press=self.app.start_download,
            style=self.styles.BUTTON_SUCCESS
        )
        
        self.pause_button = toga.Button(
            '暂停下载',
            on_press=self.app.toggle_pause,
            style=self.styles.BUTTON_PRIMARY
        )
        self.pause_button.enabled = False
        
        # 添加按钮间距
        button_box.add(self.download_button)
        button_box.add(toga.Box(style=Pack(width=self.styles.SPACING['md'])))
        button_box.add(self.pause_button)
        
        box.add(top_controls)
        box.add(button_box)
        return box

    def create_status_section(self):
        """创建状态显示区域"""
        box = toga.Box(style=self.styles.CARD_STYLE)
        
        # 进度条
        self.progress_bar = toga.ProgressBar(style=Pack(
            flex=1,
            padding=(self.styles.SPACING['sm'], 0)
        ))
        
        # 状态标签
        self.status_label = toga.Label(
            '准备就绪',
            style=Pack(
                padding=(self.styles.SPACING['sm'], 0),
                color=self.styles.COLORS['text']
            )
        )
        
        box.add(self.progress_bar)
        box.add(self.status_label)
        return box

    # 工具方法，用于更新UI状态
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