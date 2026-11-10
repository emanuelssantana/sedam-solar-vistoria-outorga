@echo off
chcp 65001 >nul
title CONEXAO TOTAL AO STORAGE SEDAM (172.16.6.10)
echo ======================================================================
echo    CONEXAO PRIORITARIA A TODOS OS COMPARTILHAMENTOS DA SEDAM (172.16.6.10)
echo ======================================================================
echo.

echo [1/4] Gravando credenciais oficiais SEDAM\22255613972 no Windows...
cmdkey /add:172.16.6.10 /user:SEDAM\22255613972 /pass:AnaePenina@2024
cmdkey /add:sedam /user:SEDAM\22255613972 /pass:AnaePenina@2024
echo [OK] Credenciais salvas.

echo.
echo [2/4] Mapeando Volumes Principais da SEDAM...
net use M: "\\172.16.6.10\SEDAM" /persistent:yes
net use K: "\\172.16.6.10\ZONEAMENTO" /persistent:yes
net use S: "\\172.16.6.10\TREINAMENTO SEI" /persistent:yes
net use L: "\\172.16.6.10\lemaf" /persistent:yes
net use B: "\\172.16.6.10\BACKUPS" /persistent:yes

echo.
echo [3/4] Mapeando Volumes de Midias, Documentos e Apoio...
net use I: "\\172.16.6.10\MIDIAS" /persistent:yes
net use O: "\\172.16.6.10\OFFICE" /persistent:yes
net use T: "\\172.16.6.10\SUPORTE" /persistent:yes
net use J: "\\172.16.6.10\LOGS" /persistent:yes

echo.
echo ======================================================================
echo    STATUS DAS UNIDADES MAPEADAS:
echo ======================================================================
net use
echo.
echo Concluido! Pressione qualquer tecla para sair.
pause >nul
