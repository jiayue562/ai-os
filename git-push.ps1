# AI OS - 一键提交并推送到GitHub
# 使用方法: .\git-push.ps1 "feat: 新增xxx功能"

param(
  [Parameter(Mandatory=$true)]
  [string]$Message
)

$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $dir

Write-Host "=== AI OS 提交并推送 ===" -ForegroundColor Cyan

# 检查是否有修改
$status = git status --porcelain
if (-not $status) {
  Write-Host "没有需要提交的修改" -ForegroundColor Yellow
  exit 0
}

# 显示待提交文件
Write-Host "待提交文件:" -ForegroundColor Cyan
git status -s

# 确认提交
Write-Host "`n提交信息: $Message" -ForegroundColor Green

# 执行提交
git add -A
git commit -m $Message
if ($LASTEXITCODE -ne 0) {
  Write-Host "提交失败" -ForegroundColor Red
  exit 1
}

# 推送到GitHub
Write-Host "`n推送到 GitHub..." -ForegroundColor Cyan
git push
if ($LASTEXITCODE -eq 0) {
  Write-Host "✅ 推送成功!" -ForegroundColor Green
  Write-Host "https://github.com/jiayue562/ai-os" -ForegroundColor Blue
} else {
  Write-Host "❌ 推送失败" -ForegroundColor Red
}
