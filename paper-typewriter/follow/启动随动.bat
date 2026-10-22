@echo off
chcp 65001 >nul
rem ============================================================
rem  纸面随光标移动 —— 一键启动
rem  1) 以调试端口启动 Typora（不改 Typora 本体）
rem  2) 注入 paper-follow.js
rem  注意：Typora 是单实例应用，若它已在运行，请先完全退出
rem        （托盘图标右键 → 退出），否则新启动参数不会生效。
rem ============================================================
setlocal
set PORT=9333
set HERE=%~dp0
set TYPORA=%TYPORA_PATH%
if "%TYPORA%"=="" set TYPORA=D:\ProgramFiles\Typora\Typora.exe
if not exist "%TYPORA%" set TYPORA=%LOCALAPPDATA%\Programs\Typora\Typora.exe

rem --- 端口是否已就绪 ---
powershell -NoProfile -Command "try{Invoke-WebRequest -UseBasicParsing http://127.0.0.1:%PORT%/json/version -TimeoutSec 1 ^| Out-Null; exit 0}catch{exit 1}" >nul 2>&1
if errorlevel 1 (
  if not exist "%TYPORA%" (
    echo [x] 找不到 Typora.exe，请设置环境变量 TYPORA_PATH 指向安装目录
    pause & exit /b 1
  )
  echo [1/2] 以调试端口 %PORT% 启动 Typora ...
  start "" "%TYPORA%" --remote-debugging-port=%PORT% --remote-allow-origins=*
  timeout /t 7 >nul
) else (
  echo [1/2] Typora 已在调试端口上运行
)

rem --- 注入 ---
set PY=
if exist "%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe" (
  set PY=%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe
) else (
  set PY=python
)
echo [2/2] 注入随动脚本 ...
"%PY%" "%HERE%inject.py" %PORT%
echo.
pause
