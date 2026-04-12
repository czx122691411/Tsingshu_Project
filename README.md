# 会员管理系统

基于 Django + Vue 3 的前后端分离会员管理系统。

## 技术栈

### 后端
- Django 4.2
- Django REST Framework
- JWT 认证
- SQLite 数据库

### 前端
- Vue 3
- Element Plus
- Pinia
- Vue Router
- Axios

## 功能模块

- 用户认证与权限管理
- 会员管理（新增/编辑/删除/续费/状态筛选）
- 借阅管理（借书/还书/逾期检测）
- 书籍管理（库存管理）
- 数据统计仪表盘

## 快速开始

### 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 初始化数据（创建管理员和示例数据）
python init_db.py

# 启动开发服务器
python manage.py runserver
```

后端服务运行在 http://localhost:8000

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务运行在 http://localhost:5173

## 默认账号

- 管理员: `admin` / `admin123`
- 工作人员: `staff` / `staff123`

## 项目结构

```
member-management/
├── backend/                    # Django后端
│   ├── member_system/          # 主项目配置
│   ├── apps/
│   │   ├── users/              # 用户模块
│   │   ├── members/            # 会员模块
│   │   └── borrows/            # 借阅模块
│   ├── manage.py
│   └── requirements.txt
│
└── frontend/                   # Vue前端
    ├── src/
    │   ├── api/                # API接口
    │   ├── components/         # 组件
    │   ├── views/              # 页面
    │   ├── router/             # 路由
    │   └── stores/             # 状态管理
    └── package.json
```

## API接口

### 认证
- POST `/api/auth/login/` - 登录
- GET `/api/auth/me/` - 获取当前用户
- POST `/api/auth/logout/` - 登出

### 会员
- GET `/api/members/` - 会员列表
- POST `/api/members/` - 创建会员
- PUT `/api/members/{id}/` - 更新会员
- DELETE `/api/members/{id}/` - 删除会员
- POST `/api/members/{id}/renew/` - 续费

### 借阅
- GET `/api/borrows/` - 借阅列表
- POST `/api/borrows/` - 创建借阅
- POST `/api/borrows/{id}/return_book/` - 归还

### 书籍
- GET `/api/books/` - 书籍列表
- POST `/api/books/` - 创建书籍
- PUT `/api/books/{id}/` - 更新书籍
- DELETE `/api/books/{id}/` - 删除书籍

### 统计
- GET `/api/stats/` - 仪表盘数据
