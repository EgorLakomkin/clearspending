@echo off
call :treeProcess
goto :eof

:treeProcess
for %%f in (*.*) do java -jar tika-app-1.5.jar -t "%%f" > "%%f.__tika.txt"


for /D %%d in (*) do (
    cd %%d
    call :treeProcess
    cd ..
)
exit /b