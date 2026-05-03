# zkali_mcp 部署到 Debian 服务器指南

## 前置要求

- Debian 服务器已安装 Python 3.12+
- 服务器已配置 SSH 访问权限
- 本地已安装 scp 或 rsync（Git Bash / WSL 自带）

## 方案 A：使用 tar.gz 打包传输（推荐快速部署）

### 1. 本地打包项目

```powershell
# 进入项目根目录
cd C:\Users\a1575\Desktop\888

# 生成排除列表（不打包虚拟环境、缓存等）
$ExcludeList = @(
    '.venv',
    '__pycache__',
    '*.pyc',
    '.vscode',
    'artifacts',
    '.env'
)

# 创建 tar.gz（保留源代码和依赖声明）
tar.exe -czf zkali_mcp.tar.gz `
  --exclude-vcs `
  --exclude='.venv' `
  --exclude='__pycache__' `
  --exclude='*.pyc' `
  --exclude='.vscode' `
  --exclude='artifacts' `
  src/ .github/ requirements.txt 2>$null

Write-Host "打包完成：zkali_mcp.tar.gz"
```

### 2. 上传到服务器

```powershell
# 替换为你的实际信息
$ServerUser = "user"           # Debian 用户名
$ServerIP = "192.168.x.x"      # 服务器 IP
$ServerPath = "/home/$ServerUser/projects"  # 服务器目标路径

# 使用 scp 上传
scp zkali_mcp.tar.gz "${ServerUser}@${ServerIP}:${ServerPath}/"
```

### 3. 服务器端解包并配置

```bash
# SSH 登录服务器
ssh user@192.168.x.x

# 进入目标路径
cd /home/user/projects

# 解包
tar -xzf zkali_mcp.tar.gz

cd src/zkali_mcp

# 创建虚拟环境
python3.12 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 测试（自检）
python main.py --self-test
```

---

## 方案 B：使用 rsync 增量同步（推荐长期维护）

### 1. 首次同步

```powershell
# 第一次完整同步
rsync -avz --delete `
  --exclude='.venv' `
  --exclude='__pycache__' `
  --exclude='*.pyc' `
  --exclude='.vscode' `
  --exclude='artifacts' `
  C:\Users\a1575\Desktop\888\src\ user@192.168.x.x:/home/user/projects/src/

rsync -avz C:\Users\a1575\Desktop\888\.github\ user@192.168.x.x:/home/user/projects/.github/

rsync -av C:\Users\a1575\Desktop\888\*.txt user@192.168.x.x:/home/user/projects/
```

### 2. 后续更新

```powershell
# 只同步变更的文件
rsync -avz --exclude='.venv' --exclude='__pycache__' `
  C:\Users\a1575\Desktop\888\src\zkali_mcp\ user@192.168.x.x:/home/user/projects/src/zkali_mcp/
```

---

## 方案 C：Git 仓库方式（推荐团队协作）

### 1. 本地初始化 git（可选）

```powershell
# 仅当你想要版本控制时
cd C:\Users\a1575\Desktop\888
git init
git config user.email "your-email@example.com"
git config user.name "Your Name"
git add .
git commit -m "Initial commit: zkali_mcp project"

# 添加远程仓库（如 GitHub）
git remote add origin https://github.com/yourusername/zkali_mcp.git
git push -u origin main
```

### 2. 服务器端克隆

```bash
cd /home/user/projects
git clone https://github.com/yourusername/zkali_mcp.git
cd zkali_mcp
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r src/zkali_mcp/requirements.txt
```

---

## 启动服务（三选一）

### stdio 模式（用于 VS Code 接入）
```bash
cd /home/user/projects/src/zkali_mcp
.venv/bin/python main.py
```

### streamable-http 模式（独立服务）
```bash
cd /home/user/projects/src/zkali_mcp
.venv/bin/python main.py --transport streamable-http --host 0.0.0.0 --port 8000
```

### SSE 模式（HTTP SSE 端点）
```bash
cd /home/user/projects/src/zkali_mcp
.venv/bin/python main.py --transport sse --host 0.0.0.0 --port 8000
```

---

## 使用 systemd 配置后台服务（可选）

### 创建服务文件

```bash
sudo nano /etc/systemd/system/zkali-mcp.service
```

### 输入以下内容

```ini
[Unit]
Description=zkali_mcp MCP Server
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/projects/src/zkali_mcp
ExecStart=/home/user/projects/src/zkali_mcp/.venv/bin/python main.py --transport streamable-http --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable zkali-mcp
sudo systemctl start zkali-mcp

# 查看状态
sudo systemctl status zkali-mcp

# 查看日志
sudo journalctl -u zkali-mcp -f
```

---

## 故障排查

### Python 版本检查
```bash
python3.12 --version
# 若无 python3.12，用 python3 --version 检查
```

### 依赖检查
```bash
source .venv/bin/activate
pip list | grep mcp
```

### 端口测试
```bash
# 检查 8000 端口是否开放
sudo ufw allow 8000
sudo ufw status

# 测试连接
curl -X GET http://127.0.0.1:8000/mcp
```

---

## 快速脚本（一键上传）

### Windows PowerShell 脚本

```powershell
# 保存为 upload-to-debian.ps1

param(
    [string]$ServerUser = "user",
    [string]$ServerIP = "192.168.x.x",
    [string]$ServerPath = "/home/user/projects",
    [string]$Method = "tar"  # tar 或 rsync
)

if ($Method -eq "tar") {
    Write-Host "=> 打包项目..."
    tar.exe -czf zkali_mcp.tar.gz `
      --exclude='.venv' `
      --exclude='__pycache__' `
      --exclude='*.pyc' `
      --exclude='.vscode' `
      --exclude='artifacts' `
      src .github requirements.txt 2>$null
    
    Write-Host "=> 上传 tar.gz..."
    scp zkali_mcp.tar.gz "${ServerUser}@${ServerIP}:${ServerPath}/"
    
    Write-Host "=> 上传完成，请在服务器执行:"
    Write-Host "    cd $ServerPath && tar -xzf zkali_mcp.tar.gz"
}
elseif ($Method -eq "rsync") {
    Write-Host "=> 使用 rsync 同步..."
    rsync -avz --delete `
      --exclude='.venv' `
      --exclude='__pycache__' `
      --exclude='*.pyc' `
      --exclude='.vscode' `
      --exclude='artifacts' `
      src .github requirements.txt "${ServerUser}@${ServerIP}:${ServerPath}/"
    
    Write-Host "=> 同步完成"
}
```

### 用法

```powershell
# 使用 tar 方法
.\upload-to-debian.ps1 -ServerUser "debian_user" -ServerIP "your.server.ip" -Method "tar"

# 使用 rsync 方法
.\upload-to-debian.ps1 -ServerUser "debian_user" -ServerIP "your.server.ip" -Method "rsync"
```

