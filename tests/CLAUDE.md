[根目录](../../CLAUDE.md) > **tests**

# 测试模块

## 模块职责

提供 QQ 音乐下载器的测试套件，确保核心功能的正确性和稳定性。目前以基础测试框架为主，需要进一步扩展测试覆盖。

## 入口与启动

### 主入口：`test_app.py`
- **测试框架**：pytest
- **运行命令**：`pytest tests/`
- **覆盖率**：基础框架已建立

### 启动命令
```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_app.py

# 生成覆盖率报告
pytest --cov=src/qqmusicdownloader tests/
```

## 对外接口

### 测试类和函数
- `test_first()` - 基础测试示例
- `unit/test_download_service.py` - 下载服务单元测试样例
- `qqmusicdownloader.py` - 集成测试入口脚本
- `__init__.py` - 测试包初始化

### 测试覆盖范围
- ✅ 基础测试框架
- ❌ API 接口测试 (待补充)
- ❌ 下载功能测试 (待补充)
- ❌ UI 交互测试 (待补充)
- ❌ 加密解密测试 (待补充)

## 关键依赖与配置

### 测试依赖
```python
# pyproject.toml
dependencies = [
    "pytest>=8.4.2",
    "pytest-asyncio>=0.23.6",
    # 其他依赖...
]
```

### 测试配置
- 使用 pytest 标准配置
- 建议添加覆盖率检查
- 建议添加 CI/CD 集成

## 数据模型

### 测试数据
- 模拟 Cookie 数据
- 测试歌曲信息
- API 响应样本

### Mock 对象
- HTTP 请求模拟
- 文件系统操作模拟
- Node.js 进程模拟

## 测试与质量

### 当前测试策略
- **单元测试**：覆盖下载服务核心逻辑
- **集成测试**：API 接口测试 (待开发)
- **端到端测试**：完整下载流程测试 (待开发)

### 建议扩展
```python
# 建议添加的测试
class TestQQMusicAPI:
    def test_cookie_validation(self):
        """测试 Cookie 验证功能"""
        pass

    def test_song_search(self):
        """测试歌曲搜索功能"""
        pass

    def test_download_url_generation(self):
        """测试下载链接生成"""
        pass

class TestQQMusicApp:
    def test_ui_initialization(self):
        """测试 TUI 界面初始化"""
        pass
```

## 常见问题 (FAQ)

### Q: 如何运行测试？
A: 使用 `pytest tests/` 命令运行所有测试。

### Q: 如何添加新测试？
A: 在 `tests/` 目录下创建新的测试文件，以 `test_` 开头。

### Q: 如何生成覆盖率报告？
A: 使用 `pytest --cov=src/qqmusicdownloader tests/`。

## 相关文件清单

### 测试文件
- `test_app.py` - 应用基础测试 (4行)
- `qqmusicdownloader.py` - 集成测试文件
- `__init__.py` - 测试包初始化

### 配置文件
- `pytest.ini` - pytest 配置 (建议添加)
- `.coveragerc` - 覆盖率配置 (建议添加)

## 测试缺口与建议

### 急需补充的测试
1. **API 接口测试**
   - Cookie 验证逻辑
   - 歌曲搜索功能
   - 下载链接生成

2. **核心功能测试**
   - 加密解密算法
   - 文件下载流程
   - 错误处理机制

3. **UI 交互测试**
   - TUI 界面响应
   - 用户输入处理
   - 状态管理

### 建议的测试结构
```
tests/
├── unit/
│   ├── test_api.py
│   ├── test_downloader.py
│   └── test_crypto.py
├── integration/
│   ├── test_download_flow.py
│   └── test_ui_flow.py
├── fixtures/
│   ├── sample_responses.json
│   └── mock_cookies.txt
└── conftest.py
```

## 变更记录 (Changelog)

### 2025-10-02
- 🆕 创建测试模块文档
- 📊 分析当前测试覆盖率
- 📝 制定测试扩展计划

---

*最后更新：2025-10-02*
