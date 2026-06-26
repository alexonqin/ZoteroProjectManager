@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================
::  ZPM 打包脚本 - Windows 文件夹模式
::  用法：双击 build.bat 即可
::  输出：../{APP_NAME_NO_SPACE}_release/ 目录下的 ZIP 文件
:: ============================================================

:: 1. 从 config.py 读取 APP_NAME, APP_ABBR, APP_VERSION
echo [0/7] 读取配置信息...
set APP_NAME=
set APP_ABBR=
set APP_VERSION=

for /f "delims=" %%i in ('findstr /c:"APP_NAME" src\models\config.py') do set _line=%%i
if defined _line (
    for /f tokens^=2^ delims^=^" %%i in ("%_line%") do set APP_NAME=%%i
)

for /f "delims=" %%i in ('findstr /c:"APP_ABBR" src\models\config.py') do set _line=%%i
if defined _line (
    for /f tokens^=2^ delims^=^" %%i in ("%_line%") do set APP_ABBR=%%i
)

for /f "delims=" %%i in ('findstr /c:"APP_VERSION" src\models\config.py') do set _line=%%i
if defined _line (
    for /f tokens^=2^ delims^=^" %%i in ("%_line%") do set APP_VERSION=%%i
)

if not defined APP_NAME (
    echo [警告] 无法从 config.py 读取 APP_NAME，使用默认值
    set APP_NAME=ZoteroProjectManager
)
if not defined APP_ABBR (
    echo [警告] 无法从 config.py 读取 APP_ABBR，使用默认值
    set APP_ABBR=ZPM
)
if not defined APP_VERSION (
    echo [警告] 无法从 config.py 读取 APP_VERSION，使用默认值
    set APP_VERSION=v0.1.7-beta
)

echo [APP_NAME] %APP_NAME%
echo [APP_ABBR] %APP_ABBR%
echo [APP_VERSION] %APP_VERSION%
echo.

:: 去除 APP_NAME 中的空格（生成无空格版本）
set APP_NAME_NO_SPACE=!APP_NAME: =!

:: 设置输出目录和文件名（使用无空格的 APP_NAME）
set RELEASE_DIR=..\%APP_NAME_NO_SPACE%_release
set ZIP_NAME=%APP_NAME_NO_SPACE%_%APP_VERSION%_Win64.zip
set EXE_NAME=%APP_NAME_NO_SPACE%

echo ============================================================
echo   %APP_NAME% 打包工具
echo   版本: %APP_VERSION%
echo   缩写: %APP_ABBR%
echo   模式: 文件夹模式 (--onedir)
echo   输出: %RELEASE_DIR%\%ZIP_NAME%
echo ============================================================
echo.

:: 2. 清理旧构建
echo [1/7] 清理旧构建...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo       完成
echo.

:: 3. 执行 PyInstaller 打包
echo [2/7] 正在打包，请稍候...
pyinstaller ^
    --onedir ^
    --windowed ^
    --name %EXE_NAME% ^
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
    --hidden-import win32com ^
    --hidden-import win32com.client ^
    --hidden-import win32api ^
    --hidden-import win32file ^
    --hidden-import pythoncom ^
    --hidden-import pywintypes ^
    --collect-all pywin32 ^
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
echo [3/7] 正在压缩为 ZIP...
if exist "%ZIP_NAME%" del /q "%ZIP_NAME%"

powershell -command "Compress-Archive -Path 'dist\%EXE_NAME%' -DestinationPath '%ZIP_NAME%' -Force"

if errorlevel 1 (
    echo.
    echo [错误] 压缩失败！请检查 PowerShell 是否可用。
    pause
    exit /b 1
)
echo       完成
echo.

:: 5. 移动 ZIP 到发布目录
echo [4/7] 移动 ZIP 到发布目录...
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"
move /y "%ZIP_NAME%" "%RELEASE_DIR%\" >nul
echo       完成
echo.

:: 6. 清理构建缓存（保留 ZIP 即可）
echo [5/7] 清理构建缓存...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo       完成
echo.

:: 7. 显示结果并自动打开文件夹
echo [6/7] 生成发布信息...
echo.
echo ============================================================
echo   输出文件：
echo   %RELEASE_DIR%\%ZIP_NAME%
echo ============================================================
echo.
echo [7/7] 打包完成！
echo.
echo 正在打开输出文件夹...
start "" "%RELEASE_DIR%"

echo.
echo 按任意键退出...
pause >nul