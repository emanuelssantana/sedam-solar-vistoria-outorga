@echo off
chcp 65001 >nul
title CONEXAO SEGURA AO STORAGE SEDAM (172.16.6.10)
echo ======================================================================
echo    CONEXAO A COMPARTILHAMENTOS DA SEDAM (172.16.6.10) - SEM SENHAS EM TEXTO
echo ======================================================================
echo.

echo [1/2] Mapeando Volumes Principais da SEDAM (usando credencial do Windows)...
net use M: "\\172.16.6.10\SEDAM" /persistent:yes 2>nul
net use K: "\\172.16.6.10\ZONEAMENTO" /persistent:yes 2>nul
net use S: "\\172.16.6.10\TREINAMENTO SEI" /persistent:yes 2>nul
net use L: "\\172.16.6.10\lemaf" /persistent:yes 2>nul
net use B: "\\172.16.6.10\BACKUPS" /persistent:yes 2>nul

echo.
echo [2/2] Mapeando Volumes de Apoio...
net use I: "\\172.16.6.10\MIDIAS" /persistent:yes 2>nul
net use O: "\\172.16.6.10\OFFICE" /persistent:yes 2>nul
net use T: "\\172.16.6.10\SUPORTE" /persistent:yes 2>nul
net use J: "\\172.16.6.10\LOGS" /persistent:yes 2>nul

echo.
echo ======================================================================
echo    STATUS DAS UNIDADES:
echo ======================================================================
net use
echo.
pause
