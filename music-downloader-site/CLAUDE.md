[根目录](../../CLAUDE.md) > **music-downloader-site**

# 前端网站模块

## 模块职责

提供 QQ 音乐下载器的官方展示网站，包含产品介绍、使用指南、FAQ 等内容。基于 React 和 Tailwind CSS 构建的现代化 Web 界面。

## 入口与启动

### 主入口：`src/App.js`
- **框架**：React 18.3.1
- **路由**：React Router DOM
- **部署**：GitHub Pages

### 启动命令
```bash
# 开发模式
npm start

# 构建
npm run build

# 部署到 GitHub Pages
npm run deploy
```

## 对外接口

### 页面路由
- `/` - 首页 (`LandingPage`)
- `/guide` - 使用指南 (`GuidePage`)
- `/faq` - 常见问题 (`FAQPage`)
- `/contact` - 联系方式 (`ContactPage`)

### 主要组件
- `LandingPage.js` - 主页展示
- `GuidePage.js` - 使用指南
- `FAQPage.js` - 常见问题
- `ContactPage.js` - 联系页面

## 关键依赖与配置

### package.json 依赖
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^7.0.1",
    "lucide-react": "^0.462.0"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.15",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49",
    "gh-pages": "^6.2.0"
  }
}
```

### 构建配置
- **Create React App** 标准配置
- **Tailwind CSS** 样式框架
- **GitHub Pages** 自动部署

## 数据模型

### 静态内容
- 产品介绍和功能特点
- 使用指南和截图
- FAQ 内容
- 联系信息

### 无后端依赖
- 纯静态网站
- 无需 API 接口
- 内容通过 Markdown 或 JSON 配置

## 测试与质量

### 测试框架
- **Jest** - 单元测试
- **React Testing Library** - 组件测试
- **Web Vitals** - 性能监控

### 代码质量
- **ESLint** - 代码检查
- **Prettier** - 代码格式化
- **Create React App** 内置规则

## 常见问题 (FAQ)

### Q: 如何本地开发？
A: 使用 `npm start` 启动开发服务器，默认端口 3000。

### Q: 如何部署？
A: 运行 `npm run deploy` 自动部署到 GitHub Pages。

### Q: 如何修改样式？
A: 使用 Tailwind CSS 类名，编辑 `src/index.css`。

## 相关文件清单

### 核心文件
- `src/App.js` - 应用主入口 (25行)
- `src/components/LandingPage.js` - 首页组件
- `src/index.js` - React 渲染入口
- `public/index.html` - HTML 模板

### 配置文件
- `package.json` - 项目配置
- `tailwind.config.js` - Tailwind 配置
- `postcss.config.js` - PostCSS 配置

### 构建文件
- `package-lock.json` - 依赖锁定文件
- `build/` - 构建输出目录

## 变更记录 (Changelog)

### 2025-10-02
- 🆕 创建模块文档
- 📝 补充组件说明和配置信息
- 🔧 整理依赖关系和构建流程

---

*最后更新：2025-10-02*