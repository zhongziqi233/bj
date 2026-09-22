# 子弹笔记

一个前后端分离的子弹笔记项目，包含标准子弹笔记的主要页面、简单用户管理和管理员用户管理。

技术栈：

- 前端：Vue 3 + Vite + Element Plus + Pinia + Vue Router
- 后端：Flask + Flask-SQLAlchemy + Flask-JWT-Extended
- 数据库：MySQL 8
- 部署：Docker Compose 开发环境 + Docker Compose 生产环境 + Nginx + Gunicorn

## 功能

### 子弹笔记

- One Dark 深色主题：极光背景、玻璃拟态卡片、页面切换和交互光效
- 字体：英文使用 JetBrains Mono，中文使用等距更纱黑体 Slab SC，字体文件已内置到前端项目
- 每日日志：按日期记录任务、事件和笔记
- 快速记录：使用 `•` 任务、`○` 事件、`—` 笔记三种类型
- 自定义子弹：用预设矢量叠加、上传 SVG 或粘贴路径，为任务、事件和笔记设计专属符号
- 状态子弹：任务待办、完成、推迟到明天、迁移到指定日期、安排到未来日志分别使用独立子弹
- 任务状态：待办、已完成、已迁移、已安排、已取消
- 重点标记：给重要记录加星标
- 月度日志：月历查看日期记录，单独维护本月任务列表
- 未来日志：按年份查看 12 个月，把事项安排到目标月份
- 自定义集合：创建阅读清单、旅行计划、项目资料等长期集合
- 任务迁移：把任务迁移到指定日期，并自动在目标日期创建新任务
- 安排到未来日志：把记录安排到目标月份

### 用户管理

- 注册、登录、JWT 鉴权
- 修改自己的密码
- 管理员查看用户列表、搜索用户
- 管理员启用或禁用用户
- 管理员调整用户角色
- 管理员重置用户密码
- 管理员删除用户
- 系统保护：不能取消自己的管理员权限、禁用自己或删除自己

## 项目结构

```text
BulletJournal/
├── backend/                 Flask 后端
│   ├── app/
│   │   ├── models/          用户、集合、记录模型
│   │   ├── routes/          认证、用户、记录、集合接口
│   │   └── utils/           日期、校验、鉴权工具
│   ├── tests/               后端接口测试
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                Vue 3 前端
│   ├── src/
│   │   ├── api/             API 封装
│   │   ├── components/      记录添加、记录列表组件
│   │   ├── layouts/         主布局
│   │   ├── stores/          登录状态
│   │   └── views/           页面
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml       本地开发
├── docker-compose.prod.yml  生产部署
└── .env.example             环境变量示例
```

## Docker 本地开发

请先安装 Docker Desktop，然后在项目根目录执行：

```bash
copy .env.example .env
docker compose up --build
```

启动后访问：

- 前端：http://localhost:5173
- 后端健康检查：http://localhost:5000/api/health
- MySQL：localhost:3306

默认管理员账号来自 `.env`：

```text
用户名：admin
密码：Admin123456
```

第一次启动时后端会自动建表并创建默认管理员。生产环境请务必修改 `.env` 中的密码和密钥。

## Docker 生产部署

1. 准备服务器，安装 Docker 和 Docker Compose
2. 复制环境变量文件并修改所有密钥和密码
3. 启动生产服务

```bash
copy .env.example .env
docker compose -f docker-compose.prod.yml up -d --build
```

生产环境访问：

- 前端：http://服务器地址
- API：http://服务器地址/api

生产环境中的 Nginx 会托管前端构建产物，并把 `/api` 请求转发到 Flask 后端。MySQL 数据保存在 Docker volume `mysql_data` 中。

生产环境建议至少修改：

```text
SECRET_KEY
JWT_SECRET_KEY
MYSQL_PASSWORD
MYSQL_ROOT_PASSWORD
DEFAULT_ADMIN_PASSWORD
CORS_ORIGINS
```

## 不使用 Docker 的本地开发

### 后端

先准备一个 MySQL 8 数据库，并创建数据库和用户。然后执行：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=mysql+pymysql://bullet:bullet_pass@localhost:3306/bullet_journal?charset=utf8mb4
flask --app wsgi:app init-db
flask --app wsgi:app run --debug --port 5000
```

也可以复制根目录的 `.env.example` 为 `.env`，再自行设置环境变量。项目默认会读取 `DATABASE_URL`、`SECRET_KEY`、`JWT_SECRET_KEY`、`DEFAULT_ADMIN_USERNAME`、`DEFAULT_ADMIN_EMAIL` 和 `DEFAULT_ADMIN_PASSWORD`。

### 前端

```bash
cd frontend
npm install
npm run dev
```

开发环境默认把 `/api` 代理到 `http://localhost:5000`。如需修改，参考 `frontend/.env.example`。

## 测试

后端测试默认使用 SQLite 临时数据库，不会连接本机的 MySQL：

```bash
cd backend
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q
```

如果要用真实 MySQL 做集成测试，可以设置 `TEST_DATABASE_URL`。测试会在该数据库中创建和删除测试表，请务必使用专门的测试库：

```powershell
$env:TEST_DATABASE_URL="mysql+pymysql://root:你的密码@127.0.0.1:3306/bullet_journal_test?charset=utf8mb4"
.venv\Scripts\python.exe -m pytest -q
```

前端构建检查：

```bash
cd frontend
npm run build
```

## API 概览

### 认证

- `POST /api/auth/register`：注册
- `POST /api/auth/login`：登录
- `GET /api/auth/me`：当前用户
- `PUT /api/auth/password`：修改密码

### 记录

- `GET /api/entries`：查询记录
  - 每日：`?log_type=daily&date=2026-09-17`
  - 月度：`?log_type=monthly&month=2026-09`
  - 未来：`?log_type=future&year=2026`
  - 集合：`?log_type=collection&collection_id=1`
- `POST /api/entries`：创建记录
- `PATCH /api/entries/<id>`：更新记录
- `DELETE /api/entries/<id>`：删除记录
- `POST /api/entries/<id>/migrate`：迁移任务
- `POST /api/entries/<id>/postpone`：推迟任务到下一天
- `POST /api/entries/<id>/schedule`：安排到未来日志

### 集合

- `GET /api/collections`：集合列表
- `POST /api/collections`：创建集合
- `GET /api/collections/<id>`：集合详情
- `PATCH /api/collections/<id>`：更新集合
- `DELETE /api/collections/<id>`：删除集合

### 自定义子弹

- `GET /api/bullet-style`：获取当前用户的子弹样式
- `PUT /api/bullet-style`：保存子弹样式
- `DELETE /api/bullet-style`：恢复默认子弹样式

### 用户管理

以下接口需要管理员权限：

- `GET /api/users`：用户列表
- `PATCH /api/users/<id>`：修改用户状态或角色
- `POST /api/users/<id>/reset-password`：重置密码
- `DELETE /api/users/<id>`：删除用户

## 后续可以继续扩展

- 记录拖拽排序
- 月度日历事件弹窗
- 数据导入导出
- 邮箱验证和找回密码
- 操作日志和审计
- 数据库迁移版本管理
- 移动端 PWA
