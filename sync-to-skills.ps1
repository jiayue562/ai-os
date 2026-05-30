# AI OS - 同步到 .agents/skills/ 技能目录
# 让 opencode 能识别到最新版本
# 使用方法: .\sync-to-skills.ps1

Write-Host "=== 同步 AI OS 到 Agent 技能目录 ===" -ForegroundColor Cyan

$repo = "C:\Users\jia'yue\ai-os"
$target = "C:\Users\jia'yue\.agents\skills\AI龙龟共生伙伴操作系统"

# 确保目标目录存在
if (-not (Test-Path $target)) {
  New-Item -ItemType Directory -Path $target -Force | Out-Null
}

# 同步核心文件
$filesToSync = @(
  "SKILL.md",
  "README.md",
  "LICENSE"
)

foreach ($file in $filesToSync) {
  $src = Join-Path $repo $file
  $dst = Join-Path $target $file
  if (Test-Path $src) {
    Copy-Item -Path $src -Destination $dst -Force
    Write-Host "  ✅ $file" -ForegroundColor Green
  }
}

# 同步 references 目录
$refSrc = Join-Path $repo "references"
$refDst = Join-Path $target "references"
if (Test-Path $refSrc) {
  if (-not (Test-Path $refDst)) {
    New-Item -ItemType Directory -Path $refDst -Force | Out-Null
  }
  Copy-Item -Path "$refSrc\*" -Destination $refDst -Recurse -Force
  Write-Host "  ✅ references/" -ForegroundColor Green
}

# 同步 docs 目录
$docsSrc = Join-Path $repo "docs"
$docsDst = Join-Path $target "docs"
if (Test-Path $docsSrc) {
  if (-not (Test-Path $docsDst)) {
    New-Item -ItemType Directory -Path $docsDst -Force | Out-Null
  }
  Copy-Item -Path "$docsSrc\*" -Destination $docsDst -Recurse -Force
  Write-Host "  ✅ docs/" -ForegroundColor Green
}

Write-Host "`n✅ 同步完成！技能目录已更新" -ForegroundColor Green
Write-Host "技能路径: $target" -ForegroundColor Blue
