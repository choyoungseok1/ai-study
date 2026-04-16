param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

$date = Get-Date -Format "yyyy-MM-dd"
git add .
git commit -m "$date : $Message"
git push
Write-Host "✅ Pushed: $date : $Message" -ForegroundColor Green
