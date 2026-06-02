param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

# lock 파일 있으면 먼저 제거 (VS Code git 충돌 방지)
Remove-Item "$PSScriptRoot\.git\index.lock" -ErrorAction SilentlyContinue
Remove-Item "$PSScriptRoot\.git\HEAD.lock" -ErrorAction SilentlyContinue

$date = Get-Date -Format "yyyy-MM-dd"
git add .
git commit -m "$date : $Message"
git push
Write-Host "✅ Pushed: $date : $Message" -ForegroundColor Green