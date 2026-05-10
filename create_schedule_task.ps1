$Action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c "D:\02_Clone git\01_github\youtube-charts-vn\auto_update_charts.bat"'
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'Update YouTube Charts VN Pages' -Action $Action -Trigger $Trigger -Settings $Settings -Description 'Update static YouTube Charts VN pages and push to GitHub when Windows user logs on' -Force
