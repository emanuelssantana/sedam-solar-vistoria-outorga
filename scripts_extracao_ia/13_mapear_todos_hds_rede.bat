@echo off
chcp 65001 >nul
echo ==========================================================
echo  MAPEAMENTO SEGURO DE DISCOS E COMPARTILHAMENTOS
echo ==========================================================

echo [1/3] Mapeando Servidor SEDAM (M:)...
net use M: "\\172.16.6.10\sedam" /persistent:yes 2>nul

echo [2/3] Mapeando Compartilhamentos Dell G3...
net use N: "\\100.84.144.1\D_nvmw_sys_Raw_2de2_g3" /persistent:yes 2>nul
net use O: "\\100.84.144.1\C Dell g3" /persistent:yes 2>nul
net use P: "\\100.84.144.1\USB-1TB_5200rpm_E" /persistent:yes 2>nul

echo [3/3] Mapeando Compartilhamentos Desktop B550...
net use W: "\\R5-5500-5500M\2TB-2026-7200_900gb-USB_1-de2-W" /persistent:yes 2>nul
net use X: "\\R5-5500-5500M\X_ssd_447_workFOTOS_usb" /persistent:yes 2>nul
net use Y: "\\R5-5500-5500M\2TB-2026-7200-USB_800gb_2-de2-Q" /persistent:yes 2>nul
net use Z: "\\R5-5500-5500M\5500-D-107gb-sys" /persistent:yes 2>nul

echo.
net use
echo.
pause
