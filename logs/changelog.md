# CodexSwitch 更新日志

## v1.0.1 (2026-06-02)

### 变更

- **移除 Codex 自动启动**：自动启动 Codex 在 Windows App Store 版下不可靠，切换配置后改为弹窗提示用户手动启动
- **切换流程重新设计**：
  - 切换前检查 Codex 是否正在运行
  - 如果正在运行且需要切换配置，弹出确认对话框，让用户保存工作
  - 用户确认后关闭 Codex → 切换配置 → 提示手动启动
  - 如果 Codex 未运行，直接切换配置并提示手动启动
  - 如果已经是目标配置，只管理 Moon Bridge，不动 Codex

### 新增

- **Codex 运行状态检测**：`_do_switch()` 在执行任何操作前先检查 `codex.is_running()`
- **关闭确认对话框**：当 Codex 正在运行且需要切换配置时，弹出 `Toplevel` 对话框警告用户保存工作，提供"关闭 Codex 并切换"/"取消"按钮
- **手动启动提示**：配置切换后，`_show_manual_start_dialog()` 显示提示对话框

### 移除

- 移除了 `_switch_sync` 中的 `self.codex.restart()` 调用，所有自动启动逻辑删除，关闭逻辑保留但只在用户确认后执行

### 清理

- **移除根目录 `config.yaml`**：根目录的 `config.yaml` 是过时模板，实际配置在首次运行时自动生成于 `~/.codex-switcher/config.yaml`

### 构建

- **首个发布版本**：`CodexSwitch.exe`（约 37 MB）使用 PyInstaller 6.6.1 构建，位于 `dist/`，单文件便携可执行文件，无外部依赖

---

## 开发历史（按功能整理）

### v0.9 系列 — 最终打磨

- **Moon Bridge 重连阻塞修复**：停止后再启动时，`_wait_for_ready` 不再阻塞等待 stdout 输出，改为后台守护线程读取 stdout，轮询端口和进程状态
- **退出逻辑修复**：修复了 `self._on_quit` 属性与方法同名的问题，退出时现在总是先停止 Moon Bridge
- **退出对话框**：点击退出按钮显示自定义对话框，提供"退出"（停止 MB + 退出）和"最小化到托盘"两个选项；窗口关闭按钮直接隐藏到托盘
- **系统托盘退出**：托盘右键退出直接调用 `_handle_quit()`，不弹对话框

### v0.8 系列 — 稳定性和可靠性

- **编解码崩溃修复**：Moon Bridge 进程输出原使用 `text=true`，在中文 Windows 上默认 GBK 编码导致崩溃，改为二进制读取 + UTF-8 解码
- **Codex 启动失败处理**：`codex` 命令在 Codex 已运行时返回退出码 1，改为通过 `tasklist` 检查进程表而非退出码
- **Moon Bridge 停止可靠性**：`stop()` 现在同时通过进程名执行 `taskkill /f /im moonbridge.exe`，等待端口关闭后才返回
- **同配置跳过重启**：已在 DeepSeek 时点击"切换到 DeepSeek"只管理 Moon Bridge，不碰配置和 Codex
- **启动失败对话框**：自动启动失败时弹窗提示手动启动

### v0.7 系列 — 架构优化

- **UI 线程不阻塞**：移除 tkinter 主线程中所有 socket 检查，Moon Bridge 健康检查在专用守护线程中运行，添加 2 秒结果缓存
- **关闭行为**：窗口关闭按钮隐藏到系统托盘而非退出，Moon Bridge 保持后台运行
- **新增退出按钮**：完全退出应用并停止 Moon Bridge 进程
- **停止 Moon Bridge 按钮**：停止 Moon Bridge 但不退出应用
- **界面布局**：窗口调整为横屏布局
- **亮色主题**：默认主题改为白色，主题系统提取到 `app/theme.py`
- **后台健康检查**：周期性 Moon Bridge 状态检查移入后台守护线程

### v0.6 系列 — 基础功能完善

- **Codex 启动修复**：优先使用 `codex` shell 命令（App Execution Alias）而非直接二进制路径，绕过 WindowsApps 权限限制
- **线程安全修复**：修复 Moon Bridge 路径未设置时的双重清理 bug，添加 `_switch_aborted` 标志位
- **Moon Bridge 后台运行**：改为隐藏后台进程，不再需要可见的 PowerShell 窗口

### 初始功能

- **OpenAI / DeepSeek 配置切换**：一键切换，自动备份当前配置
- **Moon Bridge 自动管理**：路径检测、编译、启动、健康检查
- **Moon Bridge 路径发现**：首次使用弹窗选择目录并验证，持久化保存
- **Codex 自动重启**：切换配置后杀死并重新启动 Codex
- **开机自启**：通过 Windows 注册表实现，GUI 中开关
- **GUI 主窗口**：customtkinter 深色主题，状态显示、按钮、日志、设置
- **系统托盘**：pystray 右键菜单快速切换
- **操作日志面板**：GUI 内实时日志
- **源码变更检测**：当 .go 文件更新时自动重新编译 moonbridge.exe
- **配置验证**：检查目标配置文件是否存在且格式正确

### 技术栈

- Python 3.12 + customtkinter + pystray + PyYAML + Pillow
- Go（Moon Bridge 编译）
- Windows 注册表（开机自启）
