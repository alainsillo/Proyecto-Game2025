@echo off
cd /d "c:\Users\Lenovo\Documents\Phyton-Programs\7 Rings Run - Game"
git config core.editor "cmd /c exit"
git merge --abort
git push -u origin main --force
echo Push completed!
pause
