@echo off
call :treeProcess
goto :eof

:treeProcess
for %%f in (*.rar) do 7z -y -r e "%%f"
for %%f in (*.zip) do 7z -y -r e "%%f"
for %%f in (*.7z) do 7z -y -r e "%%f"

del *.rar *.zip *.7z

for /D %%d in (*) do (
    cd %%d
    call :treeProcess
    cd ..
)
exit /b