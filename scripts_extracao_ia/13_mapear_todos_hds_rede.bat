@echo off
chcp 65001 >nul
echo ==========================================================
echo  MAPEAMENTO GLOBAL DE TODOS OS HDS DA REDE TRIANGULAR
echo ==========================================================

echo [1/4] Registrando credenciais de rede no Windows...
cmdkey /add:dell_macbook_note /user:dell_macbook_note\rede_dell /pass:@ManuCompartilha2026
cmdkey /add:100.84.144.1 /user:dell_macbook_note\rede_dell /pass:@ManuCompartilha2026
cmdkey /add:172.16.6.10 /user:SEDAM\22255613972 /pass:Sedam@2026

echo [2/4] Mapeando Servidor SEDAM (M:)...
net use M: "\\172.16.6.10\sedam" /persistent:yes

echo [3/4] Mapeando HDs e SSDs do Notebook Dell G3...
net use N: "\\100.84.144.1\D_nvmw_sys_Raw_2de2_g3" /persistent:yes
net use O: "\\100.84.144.1\C Dell g3" /persistent:yes
net use P: "\\100.84.144.1\USB-1TB_5200rpm_E" /persistent:yes

echo [4/4] Mapeando HDs do Desktop B550 (se ativo)...
net use W: "\\R5-5500-5500M\2TB-2026-7200_900gb-USB_1-de2-W" /persistent:yes
net use X: "\\R5-5500-5500M\X_ssd_447_workFOTOS_usb" /persistent:yes
net use Y: "\\R5-5500-5500M\2TB-2026-7200-USB_800gb_2-de2-Q" /persistent:yes
net use Z: "\\R5-5500-5500M\5500-D-107gb-sys" /persistent:yes

echo.
echo ==========================================================
echo  STATUS DAS UNIDADES DE REDE:
echo ==========================================================
net use
echo.
echo Concluido!
