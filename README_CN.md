# CodexSwitch

一键切换 Codex 配置，自动管理 Moon Bridge 进程。

---

## 功能特性

- **一键配置切换**：在 OpenAI 和 DeepSeek 之间一键切换
- **Moon Bridge 自动管理**：编译、启动、健康检查、停止 —— 全自动完成
- **路径发现**：首次运行时引导您选择 Moon Bridge 目录
- **智能切换**：检测 Codex 运行状态，杀死前发出警告，提示手动启动
- **系统托盘**：左键显示窗口，右键快速操作
- **开机自启**：通过 Windows 注册表实现，可在 GUI 中开关
- **无需 Python 环境**：单个便携 exe（PyInstaller 打包）

## 使用方法

### 配置文件

首次运行时，工具会自动在以下路径创建配置：

```
C:\Users\<你的用户名>\.codex-switcher\config.yaml
```

无需手动编辑，所有设置均可通过 GUI 管理。

### 首次运行

1. 双击 CodexSwitch.exe 或运行 python main.py
2. 点击"切换到 DeepSeek"
3. 如果尚未设置 Moon Bridge 路径，将弹出文件夹选择对话框
4. 选择你的 moon-bridge 项目目录
5. 工具将自动编译 moonbridge.exe、启动它，并切换配置

### 快速参考

| 操作 | 行为 |
|------|------|
| 切换到 OpenAI | 切换配置，提示手动启动 Codex |
| 切换到 DeepSeek | 启动 MB，切换配置，提示手动启动 Codex |
| 停止 Moon Bridge | 结束 moonbridge.exe 进程 |
| 关闭窗口 (x) | 隐藏到系统托盘 |
| 退出按钮 | 对话框：退出或最小化到托盘 |
| 托盘左键单击 | 显示窗口 |
| 托盘右键单击 | 快速切换/退出 |

### VPN 提示

VPN 开启 → 启动 Codex（OpenAI 需要 VPN）
  → 切换到 DeepSeek：关闭 VPN 以确保稳定
  → 继续使用 OpenAI：保持 VPN 开启

## 从源码构建

需要 Python 3.10+：

```powershell
cd F:\VibeCoding\CodexSwitch
pip install -r requirements.txt
pip install pyinstaller
pyinstaller CodexSwitch.spec
```

## 技术栈

| 组件 | 用途 |
|------|------|
| Python 3.12 | 运行环境 |
| customtkinter | 桌面 GUI |
| pystray | 系统托盘 |
| PyYAML | 配置持久化 |
| Pillow | 托盘图标 |
| PyInstaller | 打包为单 exe |
| Go | Moon Bridge 编译 |

## 许可证

MIT
