@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================
::  ZPL 打包脚本 - Windows 文件夹模式
::  用法：双击 build.bat 即可
::  输出：../ZoteroProjectLauncher_release/ 目录下的 ZIP 文件
:: ============================================================

:: 1. 从 config.py 读取 APP_VERSION
echo [0/6] 读取版本号...
set VERSION=
for /f "delims=" %%i in ('findstr /c:"APP_VERSION" src\models\config.py') do set _line=%%i
if defined _line (
    for /f tokens^=2^ delims^=^" %%i in ("%_line%") do set VERSION=%%i
)
if not defined VERSION (
    echo [警告] 无法从 config.py 读取版本号，使用默认值 v0.1.6-beta
    set VERSION=v0.1.6-beta
)
echo [版本] %VERSION%
echo.

set RELEASE_DIR=..\ZoteroProjectLauncher_release
set ZIP_NAME=ZoteroProjectLauncher_%VERSION%_Win64.zip

echo ============================================================
echo   ZPL 打包工具
echo   版本: %VERSION%
echo   模式: 文件夹模式 (--onedir)
echo   输出: %RELEASE_DIR%\%ZIP_NAME%
echo ============================================================
echo.

:: 2. 清理旧构建
echo [1/6] 清理旧构建...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo       完成
echo.

:: 3. 执行 PyInstaller 打包
echo [2/6] 正在打包，请稍候...
pyinstaller ^
    --onedir ^
    --windowed ^
    --name ZoteroProjectLauncher ^
    --add-data "src;src" ^
    --add-data "src/resources/languages.json;src/resources" ^
    --hidden-import json ^
    --hidden-import configparser ^
    --hidden-import dataclasses ^
    --hidden-import typing ^
    --hidden-import datetime ^
    --hidden-import re ^
    --hidden-import zipfile ^
    --hidden-import shutil ^
    --hidden-import subprocess ^
    --hidden-import pathlib ^
    --hidden-import sqlite3 ^
    --clean ^
    --noconfirm ^
    src/main.py

:: 检查打包是否成功
if errorlevel 1 (
    echo.
    echo [错误] 打包失败！请检查 Python 环境和依赖。
    pause
    exit /b 1
)
echo       完成
echo.

:: 4. 压缩为 ZIP（打包整个文件夹，保持目录结构）
echo [3/6] 正在压缩为 ZIP...
if exist "%ZIP_NAME%" del /q "%ZIP_NAME%"

powershell -command "Compress-Archive -Path 'dist\ZoteroProjectLauncher' -DestinationPath '%ZIP_NAME%' -Force"

if errorlevel 1 (
    echo.
    echo [错误] 压缩失败！请检查 PowerShell 是否可用。
    pause
    exit /b 1
)
echo       完成
echo.

:: 5. 移动 ZIP 到发布目录
echo [4/6] 移动 ZIP 到发布目录...
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"
move /y "%ZIP_NAME%" "%RELEASE_DIR%\" >nul
echo       完成
echo.

:: 6. 清理构建缓存（保留 ZIP 即可）
echo [5/6] 清理构建缓存...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo       完成
echo.

:: 7. 显示结果并自动打开文件夹
echo [6/6] 打包完成！
echo.
echo ============================================================
echo   输出文件：
echo   %RELEASE_DIR%\%ZIP_NAME%
echo ============================================================
echo.
echo 正在打开输出文件夹...
start "" "%RELEASE_DIR%"

echo.
echo 按任意键退出...
pause >nul