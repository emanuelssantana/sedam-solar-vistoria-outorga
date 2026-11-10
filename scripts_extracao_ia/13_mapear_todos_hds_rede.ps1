# ==============================================================================
# SCRIPT 13: MAPEAMENTO GLOBAL SEGURO DE DISCOS E COMPARTILHAMENTOS
# Utiliza exclusivamente identidades cadastradas no Windows Credential Manager
# Sem argumentos de senhas literais em scripts ou logs
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " MAPEAMENTO SEGURO DE DISCOS E COMPARTILHAMENTOS " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. SEDAM
Write-Host "`n[1/3] Conectando ao Servidor SEDAM (M:\)..." -ForegroundColor Yellow
net use M: "\\172.16.6.10\sedam" /persistent:yes 2>$null

# 2. Notebook Dell G3
Write-Host "`n[2/3] Conectando aos compartilhamentos do Dell G3..." -ForegroundColor Yellow
net use N: "\\100.84.144.1\D_nvmw_sys_Raw_2de2_g3" /persistent:yes 2>$null
net use O: "\\100.84.144.1\C Dell g3" /persistent:yes 2>$null
net use P: "\\100.84.144.1\USB-1TB_5200rpm_E" /persistent:yes 2>$null

# 3. Desktop B550
Write-Host "`n[3/3] Conectando aos compartilhamentos do Desktop B550..." -ForegroundColor Yellow
net use W: "\\R5-5500-5500M\2TB-2026-7200_900gb-USB_1-de2-W" /persistent:yes 2>$null
net use X: "\\R5-5500-5500M\X_ssd_447_workFOTOS_usb" /persistent:yes 2>$null
net use Y: "\\R5-5500-5500M\2TB-2026-7200-USB_800gb_2-de2-Q" /persistent:yes 2>$null
net use Z: "\\R5-5500-5500M\5500-D-107gb-sys" /persistent:yes 2>$null

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " STATUS ATUAL DAS UNIDADES: " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
net use
