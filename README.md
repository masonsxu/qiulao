# 求捞 - AI简历优化系统

一个基于FastAPI的智能简历优化系统，帮助用户根据岗位HC自动优化简历。

## 功能特性

- 📝 Markdown简历解析
- 🎯 基于岗位HC的关键字提取
- ✨ AI辅助简历编辑和完善
- 🎨 简历渲染和格式化输出

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API文档

启动服务后访问 http://localhost:8000/docs 查看完整API文档。

## 项目结构

```
qiulao/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── models/
│   └── services/
├── tests/
├── docs/
└── requirements.txt
```