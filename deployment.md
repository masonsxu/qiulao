# 免费部署指南

## 🆓 完全免费的部署选项

### 1. Railway (推荐，无需信用卡)

**优势：**
- ✅ 每月 $5 免费额度
- ✅ 无需信用卡验证
- ✅ 自动从 GitHub 部署
- ✅ 支持自定义域名
- ✅ 自动 HTTPS

**部署步骤：**
1. 访问 https://railway.app
2. 使用 GitHub 账号登录
3. 点击 "New Project"
4. 选择 "Deploy from GitHub repo"
5. 选择 `masonsxu/qiulao` 仓库
6. 设置环境变量：
   ```
   OPENAI_API_KEY=your_api_key
   ENABLE_AI=true
   DEBUG=false
   ```
7. 点击 Deploy

**访问地址：** `https://your-project-name.railway.app`

### 2. PythonAnywhere (真正免费)

**优势：**
- ✅ 完全免费套餐
- ✅ 无需信用卡
- ✅ 支持 Python Web 应用
- ❌ 需要手动部署

**部署步骤：**
1. 注册 https://www.pythonanywhere.com
2. 创建免费账号
3. 上传项目文件
4. 配置 Web 应用
5. 设置 WSGI 配置

### 3. Glitch (适合小型项目)

**优势：**
- ✅ 完全免费
- ✅ 在线编辑器
- ✅ 自动部署
- ❌ 资源限制较大

### 4. Replit (开发友好)

**优势：**
- ✅ 免费套餐
- ✅ 在线 IDE
- ✅ 简单部署
- ❌ 性能限制

### 5. Fly.io (有限免费)

**优势：**
- ✅ 免费额度
- ✅ 全球部署
- ✅ 高性能
- ❌ 需要信用卡验证

## 🎯 推荐方案：Railway

基于你的需求，我强烈推荐 **Railway**：

1. **无需信用卡** - 真正的免费使用
2. **简单部署** - 直接连接 GitHub 仓库
3. **足够额度** - $5/月免费额度足够小型应用
4. **专业功能** - 自动 HTTPS、自定义域名等

## 🚀 一键部署到 Railway

点击下面的按钮直接部署：

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2Fmasonsxu%2Fqiulao)

或者手动部署：

1. 访问 https://railway.app
2. 连接 GitHub 账号
3. 选择 `masonsxu/qiulao` 仓库
4. 设置环境变量
5. 点击 Deploy

## 🔧 环境变量配置

无论选择哪个平台，都需要设置这些环境变量：

```env
OPENAI_API_KEY=your_actual_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-3.5-turbo
DEBUG=false
ENABLE_AI=true
```

## 📱 部署后测试

部署成功后，访问：
- 主页：`https://your-app-url.railway.app`
- API 文档：`https://your-app-url.railway.app/docs`
- 健康检查：`https://your-app-url.railway.app/health`