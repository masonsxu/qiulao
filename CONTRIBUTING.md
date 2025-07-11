# 贡献指南

感谢您对求捞项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议：

1. 查看 [Issues](https://github.com/your-username/qiulao/issues) 是否已有相关问题
2. 如果没有，请创建新的 Issue，详细描述：
   - 问题的具体表现
   - 复现步骤
   - 预期行为
   - 运行环境信息

### 提交代码

1. **Fork 项目**
   ```bash
   # Fork 后克隆到本地
   git clone https://github.com/your-username/qiulao.git
   cd qiulao
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **开发环境设置**
   ```bash
   # 使用 UV 管理依赖
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   
   # 配置环境变量
   cp .env.example .env
   # 编辑 .env 文件
   ```

4. **编写代码**
   - 遵循现有代码风格
   - 添加必要的注释
   - 确保代码安全性

5. **测试**
   ```bash
   # 运行测试
   python test_pipeline.py
   
   # 启动服务测试
   uvicorn app.main:app --reload
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 描述更改内容
   - 说明解决的问题
   - 添加相关测试结果

## 代码规范

### Python 代码风格

- 遵循 PEP 8 规范
- 使用有意义的变量名和函数名
- 添加适当的类型注解
- 保持函数简洁，职责单一

### 提交信息格式

使用语义化提交信息：

```
type(scope): 简短描述

详细描述（可选）

Closes #issue-number
```

类型（type）：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 安全要求

- **绝不提交敏感信息**（API 密钥、密码等）
- 确保用户输入验证
- 遵循最小权限原则
- 不编造虚假的简历内容

## 开发指南

### 项目架构

```
app/
├── api/          # API 路由层
├── core/         # 核心配置
├── models/       # 数据模型
└── services/     # 业务逻辑层
```

### 添加新功能

1. **API 端点**：在 `app/api/` 中添加路由
2. **业务逻辑**：在 `app/services/` 中实现服务
3. **数据模型**：在 `app/models/schemas.py` 中定义
4. **测试**：添加相应的测试用例

### 测试要求

- 新功能必须包含测试
- 确保现有测试通过
- 测试覆盖主要功能路径

## 发布流程

项目维护者会定期发布新版本：

1. 更新版本号（`pyproject.toml`）
2. 更新 CHANGELOG
3. 创建 Git tag
4. 发布到 GitHub Releases

## 联系方式

- GitHub Issues: [项目问题讨论](https://github.com/your-username/qiulao/issues)
- GitHub Discussions: [功能建议和讨论](https://github.com/your-username/qiulao/discussions)

## 行为准则

请遵循开源社区的基本准则：

- 保持友善和专业
- 尊重不同观点
- 专注于技术讨论
- 帮助新贡献者

感谢您的贡献！