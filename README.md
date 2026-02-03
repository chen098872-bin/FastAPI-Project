# 智能多场景命名系统 (LLM Chat)

## 项目概述

这是一个基于FastAPI构建的智能多场景命名系统，提供个人姓名、企业名称、产品名称的AI生成服务。

**版本**: v2.0.1
**技术栈**: FastAPI + SQLAlchemy + MySQL + AI服务集成

## 🚀 最新特性

### v2.0.1 更新 (2025-01-XX)
- ✅ **统一收藏API架构** - 解决多进程冲突导致的404错误
- 🔧 **重构收藏仓库** - 实现多类型历史记录自动识别
- 🎯 **简化前端集成** - 统一使用 `/api/v1/favorite/*` 系列API
- 📊 **增强收藏列表** - 支持类型标识和排序
- 🛠️ **优化错误处理** - 完善ResponseValidationError处理机制

## 📁 项目结构

```
llm-chat/
├── app/                    # 主应用目录
│   ├── api/v1/            # API路由层
│   ├── core/              # 核心业务逻辑
│   ├── models/            # 数据模型
│   ├── repositories/      # 数据访问层
│   └── schemas/           # 数据验证层
├── static/                # 静态文件
├── logs/                  # 日志文件
├── API接口文档.md         # API文档
├── 项目架构设计说明.md     # 架构文档
├── FastAPI精通指南.md     # FastAPI指南
├── test_main.http         # API测试文件
└── requirements.txt       # Python依赖
```

## 🛠️ 安装与运行

### 环境要求
- Python 3.11+
- MySQL 8.0+
- Redis (可选)

### 快速开始

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd llm-chat
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp env.example .env
   # 编辑 .env 文件，设置数据库和AI服务配置
   ```

4. **启动服务**
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **访问API文档**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📚 API 接口

### 认证接口
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/code` - 获取邮箱验证码

### 命名生成接口
- `POST /api/v1/name` - 生成个人姓名
- `POST /api/v1/name/company` - 生成企业名称
- `POST /api/v1/name/product` - 生成产品名称

### 收藏管理接口
- `POST /api/v1/favorite/add` - 添加收藏
- `POST /api/v1/favorite/remove` - 移除收藏
- `GET /api/v1/favorite/list` - 获取收藏列表

## 🎯 核心特性

### 多类型命名支持
- **个人姓名**: 基于生辰八字、五行相生等生成
- **企业名称**: 基于行业特性、文化内涵等生成
- **产品名称**: 基于产品功能、目标群体等生成

### 统一收藏系统
- 支持所有类型的历史记录收藏
- 自动类型识别和分类显示
- 统一的收藏管理API

### AI服务集成
- DeepSeek AI (主要服务)
- Alibaba AI (备用服务)
- 智能负载均衡和故障转移

## 📖 文档

- [API接口文档](./API接口文档.md) - 完整的API接口说明
- [项目架构设计说明](./项目架构设计说明.md) - 系统架构和技术实现
- [FastAPI精通指南](./FastAPI精通指南.md) - FastAPI框架深度指南

## 🧪 测试

使用 `test_main.http` 文件进行API测试：

```bash
# 使用IntelliJ HTTP Client或其他HTTP客户端
# 运行 test_main.http 中的请求
```

## 🔧 开发

### 代码规范
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 mypy 进行类型检查

### 数据库迁移
```bash
# 生成迁移文件
alembic revision --autogenerate -m "migration message"

# 执行迁移
alembic upgrade head
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目仅用于毕业设计演示。

---

**注意**: 请在生产环境中配置适当的环境变量，特别是AI服务的API密钥。
