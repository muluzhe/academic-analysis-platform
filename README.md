# 学术内容智能分析平台

一个专为研究生和科研人员设计的全能型学术内容智能分析助手，支持论文分析、公众号文章分析、PDF解析等功能。

## 项目概述

本平台基于前后端分离架构，集成 DeepSeek AI 大模型，提供以下核心能力：

- **论文深度分析**：支持 arXiv 链接、PDF 上传、文本粘贴，自动生成结构化的学术分析报告
- **公众号文章解析**：支持微信公众号链接和文本粘贴，提取关键信息并生成资源清单
- **智能内容提取**：自动识别论文中的创新点、实验数据、资源链接等关键信息
- **结构化输出**：采用 Markdown 格式，包含表格、列表、分级标题，易于阅读和理解

## 功能特点

### 1. 多模式分析

- **快速摘要**：1-2句话概括核心内容
- **标准分析**：包含背景、方法、实验、结论的完整分析
- **完整分析**：深度解析 + 复现路线图 + 行动建议

### 2. 多输入方式

- **论文链接**：支持 arXiv、DOI、Semantic Scholar 链接
- **PDF 上传**：自动解析 PDF 全文内容
- **文本粘贴**：直接粘贴论文摘要或全文
- **公众号链接**：支持微信公众号文章链接

### 3. 结构化输出

- 清晰的 Markdown 格式
- 表格展示对比数据
- 分级标题组织内容
- 重要性等级标注（★★★）

### 4. 资源提取

- 自动识别论文、代码仓库、数据集、模型工具
- 提供资源检索方案
- 生成行动建议清单

## 技术架构

### 前端

- **框架**：React 18 + Vite
- **样式**：Tailwind CSS
- **组件**：Lucide React 图标库
- **Markdown 渲染**：ReactMarkdown + Remark GFM

### 后端

- **框架**：FastAPI（Python）
- **AI 模型**：DeepSeek API（支持 deepseek-v4-flash 等模型）
- **PDF 解析**：PyMuPDF
- **数据存储**：SQLite（可选）

## 环境要求

### 必需环境

- **Node.js**：>= 18.0.0
- **Python**：>= 3.9
- **Git**：用于版本控制

### 可选环境

- **NVIDIA GPU**：如需本地部署大模型（当前使用云端 API，无需 GPU）

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/academic-analysis-platform.git
cd academic-analysis-platform
```

### 2. 后端安装

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入你的 DeepSeek API 密钥
```

### 3. 前端安装

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 或者使用 yarn
yarn install
```

## 使用方法

### 1. 启动后端服务

```bash
cd backend

# 激活虚拟环境（如果未激活）
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将运行在：`http://localhost:8000`

### 2. 启动前端服务

```bash
cd frontend

# 启动开发服务器
npm run dev
```

前端服务将运行在：`http://localhost:3000`

### 3. 访问平台

打开浏览器，访问 `http://localhost:3000`，即可使用平台。

### 4. 配置 AI API

1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/) 注册账号
2. 创建 API Key
3. 编辑 `backend/.env` 文件：

```env
AI_API_KEY=sk-your-api-key-here
AI_API_BASE=https://api.deepseek.com
AI_MODEL=deepseek-v4-flash
```

1. 重启后端服务使配置生效

## 功能使用指南

### 论文分析

1. 选择"论文分析"标签
2. 选择分析模式（快速摘要/标准分析/完整分析）
3. 输入方式三选一：
   - 粘贴 arXiv 链接（如 `https://arxiv.org/abs/2510.10274`）
   - 上传 PDF 文件
   - 粘贴论文内容
4. 点击"开始分析"按钮
5. 等待分析完成，查看结构化报告

### 公众号文章分析

1. 选择"公众号分析"标签
2. 选择分析模式
3. 输入方式二选一：
   - 粘贴公众号文章链接（如 `https://mp.weixin.qq.com/s/xxxxx`）
   - 粘贴文章内容
4. 点击"开始分析"按钮

### 历史记录

- 所有分析结果自动保存到历史记录
- 可以查看、导出、删除历史记录
- 支持导出为 Markdown 格式

## 项目结构

```
academic-analysis-platform/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置和提示词
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 入口文件
│   ├── .env                # 环境变量配置
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── services/       # API 服务
│   │   └── App.jsx         # 主应用
│   ├── package.json        # Node.js 依赖
│   └── vite.config.js      # Vite 配置
└── README.md               # 项目说明
```

## 常见问题解决

### 1. 后端启动失败

**问题**：`ModuleNotFoundError: No module named 'xxx'`

**解决**：

```bash
# 确保在虚拟环境中
venv\Scripts\activate

# 重新安装依赖
pip install -r requirements.txt
```

### 2. 前端启动失败

**问题**：`'npm' 不是内部或外部命令`

**解决**：

- 安装 Node.js：<https://nodejs.org/>
- 或使用包管理器安装：`winget install OpenJS.NodeJS.LTS`

### 3. AI 分析返回 401 错误

**问题**：`AI服务请求失败 (HTTP 401)`

**解决**：

1. 检查 `.env` 文件中的 `AI_API_KEY` 是否正确
2. 确认 API 密钥未过期
3. 检查 `AI_API_BASE` 地址是否正确（DeepSeek: `https://api.deepseek.com`）

### 4. 输出格式混乱

**问题**：分析结果混在一起，没有正确分段

**解决**：

1. 刷新页面重新分析
2. 检查网络连接是否稳定
3. 尝试切换分析模式（快速/标准/完整）

### 5. PDF 解析失败

**问题**：上传 PDF 后无法解析内容

**解决**：

1. 确保 PDF 是文本格式（非扫描版图片）
2. 检查 PDF 是否加密
3. 尝试直接粘贴论文内容代替上传

### 6. 公众号链接获取失败

**问题**：`Failed to fetch` 或 `429 Unknown Error`

**解决**：

1. 检查网络连接
2. 尝试直接粘贴文章内容代替链接
3. 等待几分钟后重试（可能被限流）

## 开发计划

- [ ] 支持更多 AI 模型（OpenAI、Claude 等）
- [ ] 添加用户认证和权限管理
- [ ] 支持批量分析多个文档
- [ ] 添加导出为 PDF/Word 功能
- [ ] 支持自定义分析模板
- [ ] 添加协作和分享功能

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至：3598510361\@qq.com

## 致谢

- [DeepSeek](https://deepseek.com/) 提供 AI 能力支持
- [FastAPI](https://fastapi.tiangolo.com/) 提供后端框架
- [React](https://react.dev/) 提供前端框架
- [Tailwind CSS](https://tailwindcss.com/) 提供样式支持

***

**注意**：本项目仅供学术研究和学习使用，请遵守相关服务条款和法律法规。
