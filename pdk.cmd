@echo off
rem chcp 65001

if [%1] == [] (exit /B)

set oldpwd=%cd%
set cwdir=%~dp0

cd /d %cwdir%

__utils\pydir\python.exe -B -u __utils\pdk.py "[%cwdir%]" %*

cd /d %oldpwd%
