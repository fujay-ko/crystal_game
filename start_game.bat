@echo off
title Crystal Game

echo ==========================================
echo       Crystal Game (免伺服器版)
echo ==========================================
echo.
echo 正在開啟遊戲...
echo 如果瀏覽器沒有自動開啟，請手動用瀏覽器開啟 index.html
echo （若此方式異常，請改用 start_web.bat 以伺服器模式啟動）
echo.

start "" "%~dp0index.html"
