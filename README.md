# CodexSwitch

一键切换 Codex 配置，自动管理 Moon Bridge 进程。

![screenshot](https://img.shields.io/badge/platform-Windows-blue)
![version](https://img.shields.io/badge/version-1.0.6-green)

---

## 简介

CodexSwitch 是一个 Windows 桌面工具，解决在 **OpenAI** 和 **DeepSeek (via Moon Bridge)** 之间频繁切换 Codex 配置的痛点。

| 场景 | 之前（手动） | 现在（一键） |
|------|-------------|-------------|
| 从 OpenAI 切到 DeepSeek | 开 PowerShell → go run Moon Bridge → 新窗口复制 config → 重启 Codex | 点一下按钮，全部自动完成 |
| 从 DeepSeek 切回 OpenAI | 复制 config → 重启 Codex | 点一下按钮 |
| Moon Bridge 管理 | 单独开窗口保持运行 | 后台自动管理，带健康检查 |

---

## 功能

- **一键切换配置**：在 OpenAI 和 DeepSeek 配置间切换，自动备份当前配置
- **Moon Bridge 自动管理**：自动编译 `moonbridge.exe` → 后台启动 → TCP 健康检查 → 一键停止
- **路径发现**：首次使用引导选择 Moon Bridge 目录，验证完整性后永久保存
- **智能切换**：检测 Codex 运行状态，切换配置前提示保存工作，切换后提示手动启动
- **系统托盘**：常驻托盘，左键显示窗口，右键快速操作
- **开机自启**：通过 Windows 注册表实现
- **不依赖 Python 环境**：打包为独立 exe，双击运行

---

## 下载

已编译好的 exe 位于项目目录：

```
F:\VibeCoding\AutoStartCodex\dist\CodexSwitch.exe
```

双击即可运行。所有配置保存在 `~/.codex-switcher/config.yaml`。

---

## 使用方法

### 首次运行

1. 双击 `CodexSwitch.exe`
2. 点击 **Switch to DeepSeek**
3. 如果尚未配置 Moon Bridge 路径，会弹出文件夹选择对话框
4. 选择你的 Moon Bridge 项目目录（包含 `config.yml`、`cmd/moonbridge/`、`go.mod` 的文件夹）
5. 工具会自动编译 `moonbridge.exe` 并启动，切换配置，提示你手动启动 Codex

### 日常使用

| 操作 | 行为 |
|------|------|
| **Switch to OpenAI** | 切换配置 → 提示手动启动 Codex |
| **Switch to DeepSeek** | 启动 Moon Bridge（如需）→ 切换配置 → 提示手动启动 Codex |
| **Stop Moon Bridge** | 停止 Moon Bridge 进程 |
| **窗口 ×** | 隐藏到系统托盘 |
| **Quit 按钮** | 弹窗选择「退出」或「最小化到托盘」 |
| **托盘左键** | 显示窗口 |
| **托盘右键** | 快速切换 / 退出 |

### VPN 注意事项

由于网络环境原因：

```
开 VPN → 启动 Codex（OpenAI 需要）
  ├─ 切 DeepSeek → 关 VPN（直连国内更稳定）
  └─ 保持 OpenAI → 保持 VPN
```

理想方案：在 VPN 客户端设置 split tunneling，仅 `api.openai.com` 走 VPN 隧道。

---

## 截图

```

┌──────────────────────────────────────────────────────┐
│  Codex Config Switcher                               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────┐ ┌──────────────────┐           │
│  │  Switch to       │ │  Switch to       │           │
│  │  OpenAI          │ │  DeepSeek        │           │
│  └──────────────────┘ └──────────────────┘           │
│                                                      │
│  Current: DeepSeek       Moon Bridge: running        │
│                                                      │
│  ┌─ Log ───────────────────────────────────────────┐ │
│  │ [10:00] Switching to DeepSeek ...               │ │
│  │ [10:00] Starting Moon Bridge ...                │ │
│  │ [10:05] Moon Bridge ready (127.0.0.1:38440)     │ │
│  │ [10:05] Configuration switched. Please start    │ │
│  │         Codex manually.                         │ │
│  └──────────────────────────────────────────────────┘ │
│                                                      │
│  ☐ Start on boot    [Set MB path] [Stop MB] [Quit]  │
└──────────────────────────────────────────────────────┘
```

---

## 项目结构

```
CodexSwitch/
├── CodexSwitch.exe         ← 编译好的可执行文件
├── main.py                 ← 入口
│
├── core/
│   ├── models.py           ← 数据模型（ProfileType, MoonBridgeStatus 等）
│   ├── config_manager.py   ← 配置持久化 + 注册表管理
│   ├── config_switcher.py  ← Codex 配置切换
│   ├── moon_bridge.py      ← 编译、启动、停止、健康检查
│   └── codex_launcher.py   ← Codex 进程查找与管理
│
├── app/
│   ├── theme.py            ← 主题系统（LIGHT / DARK）
│   ├── ui.py               ← customtkinter 主窗口
│   └── tray.py             ← 系统托盘
│
├── docs/
│   ├── architecture.md     ← 软件架构说明
│   └── development.md      ← 功能开发说明
│
├── logs/
│   └── changelog.md        ← v1.0.0 ~ v1.0.6 完整变更日志
│
├── requirements.txt
├── config.yaml
└── CodexSwitch.spec        ← PyInstaller 打包配置
```

---

## 自行构建

需要 Python 3.10+：

```powershell
cd F:\VibeCoding\AutoStartCodex
python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m PyInstaller --onefile --windowed --name CodexSwitch `
  --add-data "core;core" --add-data "app;app" main.py
```

输出：`dist\CodexSwitch.exe`

或用 spec 文件（参数已在其中）：
```powershell
python -m PyInstaller CodexSwitch.spec
```

---

## 技术栈

| 组件 | 用途 |
|------|------|
| Python 3.12 | 运行环境 |
| customtkinter | 桌面 GUI |
| pystray | 系统托盘 |
| PyYAML | 配置读写 |
| Pillow | 托盘图标 |
| PyInstaller | 打包为单 exe |
| Go (编译 Moon Bridge) | Moon Bridge 编译 |

---

## 开源协议

MIT