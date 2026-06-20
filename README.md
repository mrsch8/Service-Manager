# ⚙️ 服务管理器 Service Manager

> Windows 本地服务可视化管理工具，让服务管理变得简单高效

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010/11-0078d4.svg)](https://windows.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🎨 **现代化界面** | 深色主题，卡片式设计，视觉舒适 |
| ⚡ **快速启停** | 一键启动/停止单个或全部服务 |
| 📊 **实时状态** | 自动检测并显示服务运行状态 |
| 💡 **智能提醒** | 重复操作提示，防止误操作 |
| 🔄 **加载动画** | 操作过程中显示动画，防止误触 |
| 📦 **便携使用** | 打包成单个 exe，无需安装 Python |
| 🔧 **配置灵活** | 通过 JSON 配置文件添加/管理服务 |

---

## 🛠️ 支持的服务

| 服务 | 图标 | 类型 | 说明 |
|------|------|------|------|
| MySQL | 🐬 | 数据库 | 关系型数据库管理系统 |
| Redis | 🔴 | 缓存 | 高性能内存数据库 |
| RabbitMQ | 🐰 | 消息队列 | 开源消息代理软件 |

> 💡 可通过修改 `config.json` 添加更多 Windows 服务

---

## 📦 安装与使用

### 方式一：直接运行源码

**环境要求：**
- Python 3.8 或更高版本
- Windows 10/11

**安装步骤：**

```bash
# 1. 克隆仓库
git clone https://gitee.com/你的用户名/ServiceManager.git
cd ServiceManager

# 2. 安装依赖
pip install customtkinter

# 3. 运行程序（需要管理员权限）
python service_manager.py
```

### 方式二：使用打包后的 exe

1. 从 [Releases](https://gitee.com/你的用户名/ServiceManager/releases) 下载最新版本
2. 解压到任意目录
3. 双击 `服务管理器.exe` 运行

---

## 📁 项目结构

```
ServiceManager/
├── service_manager.py    # 主程序源码
├── service_manager.ico   # 应用图标
├── config.json           # 服务配置文件
├── README.md             # 项目说明
├── .gitignore            # Git 忽略规则
└── LICENSE               # 开源协议
```

---

## ⚙️ 配置说明

编辑 `config.json` 文件可以添加或修改管理的服务：

```json
{
    "window": {
        "title": "服务管理器",
        "width": 600,
        "height": 500
    },
    "services": [
        {
            "name": "MySQL",
            "display_name": "MySQL",
            "description": "关系型数据库",
            "type": "windows",
            "service_name": "MySQL",
            "icon": "🐬"
        },
        {
            "name": "Redis",
            "display_name": "Redis",
            "description": "内存数据库",
            "type": "windows",
            "service_name": "Redis",
            "icon": "🔴"
        },
        {
            "name": "RabbitMQ",
            "display_name": "RabbitMQ",
            "description": "消息队列",
            "type": "windows",
            "service_name": "RabbitMQ",
            "icon": "🐰"
        }
    ]
}
```

### 配置字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 服务唯一标识 |
| `display_name` | string | ✅ | 显示名称 |
| `description` | string | ❌ | 服务描述 |
| `type` | string | ✅ | 服务类型：`windows` |
| `service_name` | string | ✅ | Windows 服务名称 |
| `icon` | string | ❌ | Emoji 图标 |

### 添加新服务示例

```json
{
    "name": "Nginx",
    "display_name": "Nginx",
    "description": "高性能 Web 服务器",
    "type": "windows",
    "service_name": "Nginx",
    "icon": "🌐"
}
```

---

## 🔨 打包为 exe

```bash
# 安装打包工具
pip install pyinstaller

# 打包（在项目目录执行）
pyinstaller --onefile --windowed --icon=service_manager.ico --name "服务管理器" service_manager.py
```

打包完成后，exe 文件位于 `dist` 目录中。

---

## 🖼️ 界面预览

```
┌─────────────────────────────────────────────────┐
│  ⚙️ 服务管理器                                   │
├─────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────┐ │
│ │  🐬  MySQL      ● 运行中     [启动] [停止]  │ │
│ │      关系型数据库                             │ │
│ ├─────────────────────────────────────────────┤ │
│ │  🔴  Redis      ○ 已停止     [启动] [停止]  │ │
│ │      内存数据库                               │ │
│ ├─────────────────────────────────────────────┤ │
│ │  🐰  RabbitMQ   ● 运行中     [启动] [停止]  │ │
│ │      消息队列                                 │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│  运行中: 2/3            [全部启动] [全部停止]    │
└─────────────────────────────────────────────────┘
```

---

## ❓ 常见问题

### Q: 启动服务时提示"拒绝访问"？

**A:** 需要以管理员身份运行程序。程序会自动请求管理员权限，请在弹出的 UAC 对话框中点击"是"。

### Q: 如何查看服务是否安装为 Windows 服务？

**A:** 打开命令提示符，执行：
```bash
sc query 服务名
```
例如：`sc query MySQL`

### Q: 如何添加新的服务？

**A:** 编辑 `config.json` 文件，在 `services` 数组中添加新的服务配置即可。

### Q: Redis 启动失败怎么办？

**A:** 确保 Redis 已安装为 Windows 服务。可以使用以下命令安装：
```bash
redis-server --service-install
```

---

## 🤝 贡献指南

欢迎贡献代码、提交 Issue 或 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

---

## 📝 更新日志

### v1.0 (2026-06-20)
- ✨ 全新 UI 设计，深色主题
- ⚡ 批量启停功能
- 🔄 加载动画
- 💡 智能提示
- 📦 支持打包成 exe

---

## 📮 联系方式

- 邮箱：2385598433@qq.com

---

## ⭐ 支持项目

如果这个项目对你有帮助，请给个 Star 支持一下！
