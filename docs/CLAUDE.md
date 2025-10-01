[根目录](../../CLAUDE.md) > **docs**

# 文档模块

## 模块职责

存储项目的研究文档、API 探测结果、测试数据和技术分析。主要用于开发和维护过程中的技术研究和问题解决。

## 入口与启动

### 主要目录：`research/`
- **内容类型**：JSON 响应数据、JavaScript 分析文件
- **用途**：QQ 音乐 API 分析和加密算法研究
- **访问方式**：直接文件查看

## 对外接口

### 文档分类
- **API 响应分析**：musics_response_headers.json、musics_response_decrypted.json
- **测试载荷**：test_payload_*.json
- **现场测试**：live_*/ 目录
- **JavaScript 分析**：module_*.js、*.js 文件

### 关键研究内容
- QQ 音乐 API 请求/响应格式
- 加密算法分析
- Cookie 和认证机制
- 下载链接生成逻辑

## 关键依赖与配置

### 文件格式
- **JSON**：API 响应数据和测试结果
- **JavaScript**：QQ 音乐网页分析
- **Headers**：HTTP 请求头信息

### 忽略规则
根据 `.gitignore` 配置，research 目录被忽略，不包含在版本控制中。

## 数据模型

### API 响应结构
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "songname": "歌曲名称",
        "singername": "歌手名称",
        "albumname": "专辑名称",
        "songmid": "歌曲ID"
      }
    ]
  }
}
```

### 测试载荷格式
- 请求参数配置
- 响应数据样本
- 解密结果对比

## 研究发现

### QQ 音乐 API 特点
1. **加密传输**：请求和响应都使用加密算法
2. **Cookie 认证**：需要有效的用户认证信息
3. **参数验证**：复杂的时间戳和签名机制
4. **音质控制**：不同音质需要不同的请求参数

### 加密算法
- 使用 JavaScript 实现的加密算法
- 需要 Node.js 环境运行
- 涉及多个 JavaScript 模块的协作

## 常见问题 (FAQ)

### Q: 如何查看研究数据？
A: 直接查看 `docs/research/` 目录下的 JSON 文件。

### Q: 如何更新研究数据？
A: 运行 API 探测脚本，将结果保存到相应目录。

### Q: 为何 research 目录被忽略？
A: 包含敏感的 API 响应数据和个人 Cookie 信息。

## 相关文件清单

### API 响应分析
- `musics_response_headers.json` - HTTP 响应头
- `musics_response_decoded.json` - 解码后的响应
- `musics_response_decrypted.json` - 解密后的响应

### 测试数据
- `test_payload_*.json` - 各种 API 的测试载荷
- `live_*/` - 现场测试结果
- `sample_plain.json` - 明文样本

### JavaScript 分析
- `module_*.js` - QQ 音乐网页模块分析
- `vendor.js` - 第三方库分析
- `runtime.js` - 运行时分析

## 研究缺口与建议

### 待深入研究的方向
1. **加密算法优化**
   - 提高解密效率
   - 减少对 Node.js 的依赖

2. **API 接口稳定性**
   - 监控接口变化
   - 建立自动化检测机制

3. **错误处理机制**
   - 网络异常处理
   - API 限制应对

### 建议的研究工具
- 自动化 API 探测脚本
- 加密算法测试工具
- 性能监控和分析

## 变更记录 (Changelog)

### 2025-10-02
- 🆕 创建文档模块文档
- 📊 整理研究数据分类
- 🔧 明确研究缺口和方向

---

*最后更新：2025-10-02*