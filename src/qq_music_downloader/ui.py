# ui.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

class ModernUIStyles:
    """现代化UI样式系统，提供统一的视觉设计标准"""
    
    COLORS = {
        'primary': '#6366f1',      # Indigo, more modern than blue
        'primary_dark': '#4f46e5', # Darker indigo for hover
        'secondary': '#6b7280',    # Cool gray
        'success': '#10b981',      # Emerald green
        'background': '#f8fafc',   # Light background
        'card': '#ffffff',         # White for cards
        'border': '#e2e8f0',       # Subtle border
        'text': '#1f2937',         # Dark text
        'text_secondary': '#6b7280' # Secondary text
    }
    
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32
    }

    # 现代化卡片样式
    CARD_STYLE = Pack(
        direction=COLUMN,
        padding=SPACING['md'],
        background_color=COLORS['card'],
        flex=1
    )

    # 更大更醒目的标题样式
    HEADER_STYLE = Pack(
        padding=SPACING['lg'],
        font_size=18,
        font_weight='bold',
        color=COLORS['text']
    )

    # 主按钮样式
    BUTTON_PRIMARY = Pack(
        padding=(SPACING['sm'], SPACING['md']),
        background_color=COLORS['primary'],
        color='white',
        height=40,  # 稍微更高的按钮
        width=130
    )

    # 成功按钮样式
    BUTTON_SUCCESS = Pack(
        padding=(SPACING['sm'], SPACING['md']),
        background_color=COLORS['success'],
        color='white',
        height=40,
        width=130
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
        """创建应用标题区域 - 这次绝对不会躲猫猫了！"""
        header_box = toga.Box(style=Pack(
            direction=ROW,
            padding=self.styles.SPACING['md'],
            background_color='#2c3e50'  # 深蓝灰色底色
        ))

        # 装饰条现在用padding来定位
        accent_box = toga.Box(style=Pack(
            width=4,
            background_color='#00ff00',  # 亮绿色装饰条
            padding=(0, self.styles.SPACING['md'], 0, 0)
        ))

        title_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 0, self.styles.SPACING['md']),
            background_color='#2ecc71'  # 保持和header_box一致
        ))

        title = toga.Label(
            '极简音乐下载器',
            style=Pack(
                font_size=20,
                font_weight='bold',
                color='#2ecc71',  # 清晰的浅色文字
                padding=(0, self.styles.SPACING['md'])
            )
        )
    
        title_box.add(title)
        header_box.add(accent_box)
        header_box.add(title_box)
        return header_box

    def create_path_section(self):
        """创建带选择按钮的下载路径显示区域"""
        box = toga.Box(style=self.styles.CARD_STYLE)
        
        # 创建路径选择的容器
        path_container = toga.Box(style=Pack(
            direction=ROW,
            padding=(self.styles.SPACING['sm'], 0),
            alignment='center'
        ))
        
        # 路径显示标签
        self.path_label = toga.Label(
            '下载路径将在登录后显示',
            style=Pack(
                padding=(0, self.styles.SPACING['sm'], 0, 0),
                color=self.styles.COLORS['text'],
                flex=1
            )
        )
        
        # 选择路径按钮
        self.choose_path_button = toga.Button(
            '选择路径',
            on_press=self.app.choose_download_path,
            style=Pack(
                padding=(0, self.styles.SPACING['sm']),
                background_color=self.styles.COLORS['secondary'],
                color='white',
                height=36,
                width=100
            )
        )
        
        path_container.add(self.path_label)
        path_container.add(self.choose_path_button)
        box.add(path_container)
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
        """创建更现代的搜索区域"""
        box = toga.Box(style=self.styles.CARD_STYLE)
        
        search_box = toga.Box(style=Pack(
            direction=ROW,
            alignment='center',
            padding=(self.styles.SPACING['sm'], 0)
        ))
        
        # 搜索输入框 - 更大更醒目
        self.search_input = toga.TextInput(
            placeholder='输入歌曲名称搜索',
            style=Pack(
                flex=1,
                padding=(0, self.styles.SPACING['md'], 0, 0),
                height=40  # 更高的输入框
            )
        )
        
        # 搜索按钮 - 更现代的样式
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
        """创建更现代的搜索结果显示区域"""
        self.results_table = toga.Table(
            headings=['选择', '序号', '歌曲名', '歌手', '专辑'],
            accessors=['selected', 'index', 'name', 'singer', 'album'],
            data=[],
            style=Pack(
                flex=1,
                padding=self.styles.SPACING['sm'],
                background_color=self.styles.COLORS['card'],
                height=350  # 稍微增加表格高度
            ),
            on_select=self.app.on_table_select
        )
        return self.results_table
  
    def create_control_section(self):
        """创建下载控制区域，使用格式选择替代音质选择"""
        box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=self.styles.SPACING['md'],
            background_color=self.styles.COLORS['card']
        ))

        # 上部分：格式选择和批量模式
        top_controls = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, self.styles.SPACING['md'], 0)
        ))

        # 格式选择组件
        format_box = toga.Box(style=Pack(
            direction=ROW,
            alignment='center'
        ))
        format_label = toga.Label(
            '格式选择:',
            style=Pack(
                padding=(0, self.styles.SPACING['sm'], 0, 0),
                color=self.styles.COLORS['text']
            )
        )
        format_items = ['M4A','MP3', 'FLAC']
        self.format_selection = toga.Selection(
            items=format_items,
            style=Pack(width=150)
        )
        format_box.add(format_label)
        format_box.add(self.format_selection)

        hint_label = toga.Label(
            '注：受限于QQ音乐API，实际下载可能均为M4A格式',
            style=Pack(
                padding=(self.styles.SPACING['sm'], 0),
                color=self.styles.COLORS['text_secondary'],
                font_size=12
            )
        )
        format_box.add(hint_label)
        # 批量模式开关 - 使用更现代的样式
        self.batch_switch = toga.Switch(
            '批量下载',
            style=Pack(
                padding=(0, self.styles.SPACING['lg']),
                color=self.styles.COLORS['primary']
            )
        )
        
        top_controls.add(format_box)
        top_controls.add(self.batch_switch)
        
        # 下载按钮区域 - 更现代的布局
        button_box = toga.Box(style=Pack(
            direction=ROW,
            alignment='center',
            padding=(self.styles.SPACING['md'], 0, 0, 0)
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