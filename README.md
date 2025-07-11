# 求捞 (Qiulao) - AI Resume Optimization System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)

一个基于 FastAPI 的智能简历优化系统，帮助用户根据岗位 HC (Hiring Criteria) 自动优化简历。

[English](#english) | [中文](#中文)

## 功能特性

- 📝 **Markdown 简历解析** - 智能解析 Markdown 格式简历
- 🎯 **关键字匹配** - 基于岗位 HC 的关键字提取和匹配
- ✨ **AI 辅助优化** - 使用 OpenAI API 进行智能简历编辑和完善
- 🎨 **专业渲染** - 输出格式化的 HTML 简历
- 🔒 **安全可靠** - 不编造虚假信息，仅基于真实内容优化
- 🌐 **Web 界面** - 提供直观的 Web 操作界面

## 快速开始

### 环境要求

- Python 3.13+
- OpenAI API Key (可选，设置 `ENABLE_AI=False` 可无 API 运行)

### 安装

#### 方式 1: 使用 UV (推荐)

```bash
# 克隆项目
git clone https://github.com/your-username/qiulao.git
cd qiulao

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows
uv pip install -r requirements.txt
```

#### 方式 2: 使用 pip

```bash
# 克隆项目
git clone https://github.com/your-username/qiulao.git
cd qiulao

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，配置你的 API 密钥：
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-3.5-turbo
DEBUG=False
ENABLE_AI=True
```

### 运行

```bash
# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用简化命令
python main.py
```

访问 http://localhost:8000 查看 Web 界面，或访问 http://localhost:8000/docs 查看 API 文档。

## 使用方式

### Web 界面

1. 在浏览器打开 http://localhost:8000
2. 上传 Markdown 格式的简历
3. 输入目标岗位的 HC (职位描述)
4. 点击优化，获得优化后的简历

### API 调用

```python
import requests

# 完整优化流程
response = requests.post("http://localhost:8000/api/v1/optimize-resume", json={
    "markdown_content": "# 你的简历内容...",
    "job_hc": "前端开发工程师，要求熟悉React、Vue等..."
})

result = response.json()
print(result["optimized_content"])
```

### 命令行测试

```bash
# 运行完整测试管道
python test_pipeline.py
```

## 项目架构

```
qiulao/
├── app/
│   ├── api/          # API 路由
│   ├── core/         # 核心配置
│   ├── models/       # 数据模型
│   ├── services/     # 业务逻辑
│   └── main.py       # FastAPI 应用
├── static/           # 静态文件
├── templates/        # HTML 模板
├── tests/            # 测试文件
├── *.md             # 示例简历
└── requirements.txt  # 依赖文件
```

### 核心服务

- **ResumeParserService**: 解析 Markdown 简历
- **KeywordExtractorService**: 提取和匹配关键字
- **ResumeEditorService**: AI 辅助内容优化
- **ResumeRendererService**: 格式化输出

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t qiulao .

# 运行容器
docker run -p 8000:8000 --env-file .env qiulao
```

### 云平台部署

项目支持部署到多个云平台：

- **Render**: 一键部署 (推荐)
- **Railway**: 快速部署
- **Vercel**: 静态部署
- **Heroku**: 传统部署

详见 [部署指南](docs/deployment.md)

## 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md)。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 支持

- 🐛 [报告问题](https://github.com/your-username/qiulao/issues)
- 💡 [功能建议](https://github.com/your-username/qiulao/discussions)
- 📖 [查看文档](docs/)

---

## English

An AI-powered resume optimization system built with FastAPI that helps users optimize their resumes based on job descriptions (Hiring Criteria).

### Features

- 📝 **Markdown Resume Parsing** - Intelligent parsing of Markdown format resumes
- 🎯 **Keyword Matching** - Extract and match keywords based on job descriptions
- ✨ **AI-Powered Optimization** - Smart resume editing using OpenAI API
- 🎨 **Professional Rendering** - Output formatted HTML resumes
- 🔒 **Safe & Reliable** - No fabricated information, only factual optimization
- 🌐 **Web Interface** - Intuitive web-based operation

### Quick Start

1. Clone and setup:
```bash
git clone https://github.com/your-username/qiulao.git
cd qiulao
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

3. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Visit http://localhost:8000 for the web interface or http://localhost:8000/docs for API documentation.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.