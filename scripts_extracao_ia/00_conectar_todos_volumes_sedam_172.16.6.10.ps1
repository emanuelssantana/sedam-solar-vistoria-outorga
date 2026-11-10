# ==============================================================================
# SCRIPT 00: CONEXÃO PRIORITÁRIA TOTAL AO SERVIDOR SEDAM (172.16.6.10)
# Mapeia TODOS os 9 compartilhamentos disponíveis no storage central da SEDAM
# Executar no A320MH (e em qualquer máquina Windows da rede)
# ==============================================================================

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " CONECTANDO A TODOS OS COMPARTILHAMENTOS DO SERVIDOR SEDAM (172.16.6.10)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Teste de Acessibilidade de Rede (Porta 445 SMB)
Write-Host "`n[1/3] Testando conectividade com 172.16.6.10..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName "172.16.6.10" -Count 1 -Quiet -ErrorAction SilentlyContinue
if ($ping) {
    Write-Host "  [OK] Servidor 172.16.6.10 respondeu ao ping!" -ForegroundColor Green
} else {
    Write-Host "  [AVISO] Servidor 172.16.6.10 nao respondeu ao ping ICMP. Testando porta SMB 445..." -ForegroundColor Yellow
    $tcp = Test-NetConnection -ComputerName "172.16.6.10" -Port 445 -WarningAction SilentlyContinue
    if ($tcp.TcpTestSucceeded) {
        Write-Host "  [OK] Porta 445 SMB aberta em 172.16.6.10!" -ForegroundColor Green
    } else {
        Write-Host "  [ALERTA] Porta 445 nao alcancada. Verifique se o Tailscale esta conectado com --accept-routes." -ForegroundColor Red
    }
}

# 2. Injetar Credenciais Oficiais no Windows Credential Manager
Write-Host "`n[2/3] Injetando credenciais homologadas SEDAM\22255613972..." -ForegroundColor Yellow
cmdkey /add:172.16.6.10 /user:SEDAM\22255613972 /pass:AnaePenina@2024
cmdkey /add:sedam /user:SEDAM\22255613972 /pass:AnaePenina@2024
Write-Host "  [OK] Credenciais salvas no cofre do Windows." -ForegroundColor Green

# 3. Mapear Todos os Compartilhamentos Disponíveis
Write-Host "`n[3/3] Mapeando compartilhamentos do servidor..." -ForegroundColor Yellow

$shares = @(
    @{ Letra = "M:"; UNC = "\\172.16.6.10\SEDAM";           Desc = "Volume Principal (ERGAS, ASCOM, GOVCLIMA)" },
    @{ Letra = "K:"; UNC = "\\172.16.6.10\ZONEAMENTO";      Desc = "Zoneamento Socioeconomico e Ecologico (ZSEE-RO / Shapefiles)" },
    @{ Letra = "S:"; UNC = "\\172.16.6.10\TREINAMENTO SEI"; Desc = "Capacitacao e Manuais do Sistema SEI-RO" },
    @{ Letra = "L:"; UNC = "\\172.16.6.10\lemaf";           Desc = "Laboratorio de Modelagem Florestal / CAR / SIGA" },
    @{ Letra = "B:"; UNC = "\\172.16.6.10\BACKUPS";         Desc = "Backups e Dumps de Bases" },
    @{ Letra = "I:"; UNC = "\\172.16.6.10\MIDIAS";          Desc = "Midias, Videos Institucionais e Drone" },
    @{ Letra = "O:"; UNC = "\\172.16.6.10\OFFICE";          Desc = "Modelos Oficiais de Documentos e Manuais" },
    @{ Letra = "T:"; UNC = "\\172.16.6.10\SUPORTE";         Desc = "Arquivos de Apoio e TI" },
    @{ Letra = "J:"; UNC = "\\172.16.6.10\LOGS";            Desc = "Logs de Operacoes e Servidores" }
)

foreach ($s in $shares) {
    $l = $s.Letra
    $u = $s.UNC
    $d = $s.Desc
    Write-Host "`nConectando $l ➔ $u ($d)..." -ForegroundColor White
    
    # Se a letra ja estiver em uso, remove antes
    $existing = Get-PSDrive -Name $l.Replace(":", "") -ErrorAction SilentlyContinue
    if ($existing) {
        net use $l /delete /yes 2>$null | Out-Null
    }
    
    $res = net use $l "$u" /user:SEDAM\22255613972 AnaePenina@2024 /persistent:yes 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [SUCESSO] $l conectado a $u" -ForegroundColor Green
    } else {
        # Tenta sem credencial explicita (reaproveitando sessao ativa)
        $res2 = net use $l "$u" /persistent:yes 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [SUCESSO] $l conectado via sessao ativa a $u" -ForegroundColor Green
        } else {
            Write-Host "  [AVISO] $l ($u): $res" -ForegroundColor Yellow
        }
    }
}

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host " STATUS FINAL DAS UNIDADES MAPEADAS: " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
net use

Write-Host "`n[CONCLUIDO] Todos os compartilhamentos do 172.16.6.10 foram processados!" -ForegroundColor Green
