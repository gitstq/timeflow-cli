# 🕐 TimeFlow CLI

<p align="center">
  <strong>智能命令行时间追踪工具</strong><br>
  <strong>A Smart Command-Line Time Tracking Tool with Pomodoro Support</strong><br>
  <strong>智慧型命令列時間追蹤工具</strong>
</p>

<p align="center">
  <a href="#简体中文">简体中文</a> •
  <a href="#繁體中文">繁體中文</a> •
  <a href="#english">English</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
</p>

---

<a name="简体中文"></a>
# 🎉 简体中文

## ✨ 核心特性

- ⏱️ **简单高效的时间追踪** - 一键开始/停止任务计时
- 🍅 **番茄钟工作法** - 内置25/5分钟专注工作循环
- 📊 **多维度统计报表** - 日/周/月视图，直观了解时间分配
- 📁 **项目管理** - 按项目组织任务，清晰分类
- 🏷️ **智能分类** - 开发、会议、学习等多种预设分类
- 📤 **灵活导出** - 支持 JSON、CSV、Markdown 格式导出
- 🎨 **精美终端界面** - 使用 Rich 库打造优雅的命令行体验
- 💾 **本地数据存储** - SQLite 数据库，数据安全可靠

## 🚀 快速开始

### 安装

```bash
# 使用 pip 安装
pip install timeflow-cli

# 或使用源码安装
git clone https://github.com/gitstq/timeflow-cli.git
cd timeflow-cli
pip install -e .
```

### 基础用法

```bash
# 开始追踪一个任务
timeflow start "编写代码" --project myapp --category development

# 查看当前状态
timeflow status

# 停止追踪
timeflow stop

# 查看今日报告
timeflow report today

# 查看本周报告
timeflow report week
```

### 🍅 番茄钟模式

```bash
# 启动番茄钟（25分钟专注 + 5分钟休息）
timeflow pomodoro start "专注工作" --project study

# 查看番茄钟状态
timeflow pomodoro status

# 停止番茄钟
timeflow pomodoro stop
```

## 📖 详细使用指南

### 任务管理

```bash
# 列出所有任务
timeflow task list

# 添加新任务
timeflow task add "学习Python" --project study --category learning

# 删除任务
timeflow task delete 1
```

### 项目管理

```bash
# 列出所有项目
timeflow project list

# 添加新项目
timeflow project add "个人学习" --description "我的学习计划"
```

### 数据导出

```bash
# 导出为 JSON
timeflow report export -f json

# 导出为 CSV
timeflow report export -f csv -o ~/timeflow.csv

# 导出为 Markdown 报告
timeflow report export -f md -s 2025-01-01 -e 2025-01-31
```

### 查看历史

```bash
# 查看最近20条记录
timeflow history

# 查看特定项目的记录
timeflow history --project myapp
```

## 💡 设计思路

TimeFlow CLI 的设计理念是**简单、专注、高效**。我们相信：

- **最小化干扰** - 命令行工具不会打扰你的工作流
- **数据所有权** - 所有数据存储在本地，你完全掌控
- **灵活分类** - 项目和分类系统适应不同工作方式
- **番茄工作法** - 科学的专注时间管理方法

## 📦 技术栈

- **Python 3.8+** - 现代 Python 语法
- **Click** - 强大的命令行框架
- **Rich** - 精美的终端输出
- **SQLite** - 轻量级本地数据库

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加某个特性'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---

<a name="繁體中文"></a>
# 🎉 繁體中文

## ✨ 核心特性

- ⏱️ **簡單高效的時間追蹤** - 一鍵開始/停止任務計時
- 🍅 **番茄鐘工作法** - 內置25/5分鐘專注工作循環
- 📊 **多維度統計報表** - 日/週/月視圖，直觀了解時間分配
- 📁 **專案管理** - 按專案組織任務，清晰分類
- 🏷️ **智慧分類** - 開發、會議、學習等多種預設分類
- 📤 **靈活匯出** - 支援 JSON、CSV、Markdown 格式匯出
- 🎨 **精美終端介面** - 使用 Rich 庫打造優雅的命令列體驗
- 💾 **本地資料儲存** - SQLite 資料庫，資料安全可靠

## 🚀 快速開始

### 安裝

```bash
# 使用 pip 安裝
pip install timeflow-cli

# 或使用原始碼安裝
git clone https://github.com/gitstq/timeflow-cli.git
cd timeflow-cli
pip install -e .
```

### 基礎用法

```bash
# 開始追蹤一個任務
timeflow start "編寫程式碼" --project myapp --category development

# 查看目前狀態
timeflow status

# 停止追蹤
timeflow stop

# 查看今日報告
timeflow report today

# 查看本週報告
timeflow report week
```

### 🍅 番茄鐘模式

```bash
# 啟動番茄鐘（25分鐘專注 + 5分鐘休息）
timeflow pomodoro start "專注工作" --project study

# 查看番茄鐘狀態
timeflow pomodoro status

# 停止番茄鐘
timeflow pomodoro stop
```

## 📖 詳細使用指南

### 任務管理

```bash
# 列出所有任務
timeflow task list

# 新增新任務
timeflow task add "學習Python" --project study --category learning

# 刪除任務
timeflow task delete 1
```

### 專案管理

```bash
# 列出所有專案
timeflow project list

# 新增新專案
timeflow project add "個人學習" --description "我的學習計畫"
```

### 資料匯出

```bash
# 匯出為 JSON
timeflow report export -f json

# 匯出為 CSV
timeflow report export -f csv -o ~/timeflow.csv

# 匯出為 Markdown 報告
timeflow report export -f md -s 2025-01-01 -e 2025-01-31
```

### 查看歷史

```bash
# 查看最近20筆記錄
timeflow history

# 查看特定專案的記錄
timeflow history --project myapp
```

## 💡 設計理念

TimeFlow CLI 的設計理念是**簡單、專注、高效**。我們相信：

- **最小化干擾** - 命令列工具不會打擾你的工作流
- **資料所有權** - 所有資料儲存在本地，你完全掌控
- **靈活分類** - 專案和分類系統適應不同工作方式
- **番茄工作法** - 科學的專注時間管理方法

## 📦 技術架構

- **Python 3.8+** - 現代 Python 語法
- **Click** - 強大的命令列框架
- **Rich** - 精美的終端輸出
- **SQLite** - 輕量級本地資料庫

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 本倉庫
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加某個特性'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 建立 Pull Request

## 📄 開源協議

本專案採用 [MIT](LICENSE) 協議開源。

---

<a name="english"></a>
# 🎉 English

## ✨ Core Features

- ⏱️ **Simple & Efficient Time Tracking** - One-click start/stop task timing
- 🍅 **Pomodoro Technique** - Built-in 25/5 minute focus work cycles
- 📊 **Multi-dimensional Reports** - Day/week/month views for time allocation insights
- 📁 **Project Management** - Organize tasks by projects with clear categorization
- 🏷️ **Smart Categories** - Development, meetings, learning, and more preset categories
- 📤 **Flexible Export** - Export to JSON, CSV, and Markdown formats
- 🎨 **Beautiful Terminal UI** - Elegant command-line experience with Rich library
- 💾 **Local Data Storage** - SQLite database for secure and reliable data

## 🚀 Quick Start

### Installation

```bash
# Install via pip
pip install timeflow-cli

# Or install from source
git clone https://github.com/gitstq/timeflow-cli.git
cd timeflow-cli
pip install -e .
```

### Basic Usage

```bash
# Start tracking a task
timeflow start "Coding" --project myapp --category development

# Check current status
timeflow status

# Stop tracking
timeflow stop

# View today's report
timeflow report today

# View weekly report
timeflow report week
```

### 🍅 Pomodoro Mode

```bash
# Start Pomodoro (25min focus + 5min break)
timeflow pomodoro start "Focus Work" --project study

# Check Pomodoro status
timeflow pomodoro status

# Stop Pomodoro
timeflow pomodoro stop
```

## 📖 Detailed Usage Guide

### Task Management

```bash
# List all tasks
timeflow task list

# Add new task
timeflow task add "Learn Python" --project study --category learning

# Delete task
timeflow task delete 1
```

### Project Management

```bash
# List all projects
timeflow project list

# Add new project
timeflow project add "Personal Study" --description "My learning plan"
```

### Data Export

```bash
# Export as JSON
timeflow report export -f json

# Export as CSV
timeflow report export -f csv -o ~/timeflow.csv

# Export as Markdown report
timeflow report export -f md -s 2025-01-01 -e 2025-01-31
```

### View History

```bash
# View recent 20 entries
timeflow history

# View entries for specific project
timeflow history --project myapp
```

## 💡 Design Philosophy

TimeFlow CLI is designed with **simplicity, focus, and efficiency** in mind. We believe:

- **Minimal Distraction** - CLI tools won't interrupt your workflow
- **Data Ownership** - All data stored locally, you have full control
- **Flexible Categorization** - Project and category system adapts to different workflows
- **Pomodoro Technique** - Scientific time management for focused work

## 📦 Tech Stack

- **Python 3.8+** - Modern Python syntax
- **Click** - Powerful CLI framework
- **Rich** - Beautiful terminal output
- **SQLite** - Lightweight local database

## 🤝 Contributing

Contributions are welcome! Please feel free to submit Issues and Pull Requests.

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add some feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the [MIT](LICENSE) License.

---

<p align="center">
  Made with ❤️ by TimeFlow Team
</p>
