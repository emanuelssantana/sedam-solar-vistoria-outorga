# ==============================================================================
# SCRIPT 13: MAPEAMENTO GLOBAL DE TODOS OS HDS E COMPARTILHAMENTOS DA MALHA
# Executar no A320MH (e adaptável para Dell G3 / B550)
# Mapeia: SEDAM M:\, Notebook Dell G3, Desktop B550 e Discos Locais
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " INICIANDO MAPEAMENTO DE TODOS OS HDS DA REDE TRIANGULAR " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# ------------------------------------------------------------------------------
# 1. CREDENCIAIS NO GERENCIADOR DO WINDOWS (CMDKEY)
# ------------------------------------------------------------------------------
Write-Host "`n[1/4] Registrando credenciais de rede..." -ForegroundColor Yellow

# Credenciais do Dell G3 (Conta rede_dell)
cmdkey /add:dell_macbook_note /user:dell_macbook_note\rede_dell /pass:@ManuCompartilha2026
cmdkey /add:100.84.144.1 /user:dell_macbook_note\rede_dell /pass:@ManuCompartilha2026
cmdkey /add:192.168.1.194 /user:dell_macbook_note\rede_dell /pass:@ManuCompartilha2026

# Credenciais do Servidor SEDAM ERGAS
cmdkey /add:172.16.6.10 /user:SEDAM\22255613972 /pass:Sedam@2026
cmdkey /add:sedam /user:SEDAM\22255613972 /pass:Sedam@2026

# ------------------------------------------------------------------------------
# 2. MAPEAMENTO DO SERVIDOR SEDAM (M:\)
# ------------------------------------------------------------------------------
Write-Host "`n[2/4] Conectando ao Servidor SEDAM (M:\)..." -ForegroundColor Yellow
try {
    net use M: "\\172.16.6.10\sedam" /persistent:yes
    Write-Host "  [OK] Unidade M:\ mapeada para \\172.16.6.10\sedam" -ForegroundColor Green
} catch {
    Write-Host "  [AVISO] Servidor 172.16.6.10 nao alcancado diretamente. Verifique se a ponte Tailscale esta ativa." -ForegroundColor Yellow
}

# ------------------------------------------------------------------------------
# 3. MAPEAMENTO DOS HDS DO NOTEBOOK DELL G3
# ------------------------------------------------------------------------------
Write-Host "`n[3/4] Conectando aos HDs e SSDs do Notebook Dell G3..." -ForegroundColor Yellow

# N: NVMe Secundario Dell G3
net use N: "\\100.84.144.1\D_nvmw_sys_Raw_2de2_g3" /persistent:yes
# O: SSD Windows 11 Dell G3
net use O: "\\100.84.144.1\C Dell g3" /persistent:yes
# P: HD Mecanico USB 1TB Dell G3
net use P: "\\100.84.144.1\USB-1TB_5200rpm_E" /persistent:yes

# ------------------------------------------------------------------------------
# 4. MAPEAMENTO DOS HDS DO DESKTOP B550 (Se ligado na rede)
# ------------------------------------------------------------------------------
Write-Host "`n[4/4] Conectando aos HDs do Desktop B550 (R5-5500-5500M)..." -ForegroundColor Yellow
# W: HD 2TB USB 1-de2 (Projetos / Fotos)
net use W: "\\R5-5500-5500M\2TB-2026-7200_900gb-USB_1-de2-W" /persistent:yes
# X: SSD 447GB Trabalho Fotos
net use X: "\\R5-5500-5500M\X_ssd_447_workFOTOS_usb" /persistent:yes
# Y: HD 2TB USB 2-de2 (Backup)
net use Y: "\\R5-5500-5500M\2TB-2026-7200-USB_800gb_2-de2-Q" /persistent:yes
# Z: Apoio Sistema B550
net use Z: "\\R5-5500-5500M\5500-D-107gb-sys" /persistent:yes

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " STATUS ATUAL DAS UNIDADES MAPEADAS: " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
net use

Write-Host "`n[CONCLUIDO] Todos os HDs e compartilhamentos foram configurados com sucesso!" -ForegroundColor Green
