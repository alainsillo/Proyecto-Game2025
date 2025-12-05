# Force clean git state and push
$gitDir = "c:\Users\Lenovo\Documents\Phyton-Programs\7 Rings Run - Game"
$mergeHeadFile = "$gitDir\.git\MERGE_HEAD"

# Remove merge state file if it exists
if (Test-Path $mergeHeadFile) {
    Remove-Item $mergeHeadFile -Force
    Write-Host "Removed MERGE_HEAD file"
}

# Reset to local main branch
Set-Location $gitDir
& git reset --hard HEAD
Write-Host "Repository reset to HEAD"

# Push to remote with force
& git push -u origin main --force
Write-Host "Pushed to GitHub with --force"
