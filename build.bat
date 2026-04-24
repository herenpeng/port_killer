@echo off
chcp 65001 >nul

echo ========================================
echo    Port Killer 打包工具
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.6+
    pause
    exit /b 1
)

echo [1/4] 检查 PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [信息] 正在安装 PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败
        pause
        exit /b 1
    )
) else (
    echo [信息] PyInstaller 已安装
)

echo.
echo [2/4] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist PortKiller.spec del /q PortKiller.spec

echo.
echo [3/4] 开始打包...
python -m PyInstaller --clean build.spec

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo [4/4] 打包完成！
echo.
echo ========================================
echo    可执行文件位置: dist\PortKiller.exe
echo ========================================
echo.

:: 检查是否生成成功
if exist dist\PortKiller.exe (
    echo [成功] PortKiller.exe 已生成
    echo    文件大小: 
    for %%A in (dist\PortKiller.exe) do echo    %%~zA 字节
    echo.
) else (
    echo [警告] 未找到生成的 exe 文件
)

echo 按任意键退出...
pause >nul