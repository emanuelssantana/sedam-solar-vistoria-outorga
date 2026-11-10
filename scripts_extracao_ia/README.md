# 🛠️ Ferramentas e Scripts de Mineração, Extração e IA SEDAM (2012–2026)

Este diretório contém os scripts desenvolvidos e homologados para extração, higienização, estruturação e publicação dos dados da SEDAM e do CRM/ERP Global, projetados para interoperabilidade entre os agentes **Dell G3** e **A320MH**.

---

## 📋 Índice dos Scripts e Utilidades

| Arquivo | Função / Propósito | Saída / Destino |
| :--- | :--- | :--- |
| `01_extracao_laudos_word.py` | Mineração em lote dos 1.475 laudos Word (`.doc`/`.docx`) com regex forense de tabelas, motobombas, vazões e coordenadas. | Metadados e textos integrais indexados. |
| `02_extracao_malotes_protocolos.py` | Leitura das 584 planilhas de malote e protocolos (2012–2026), vinculando números SIGA/SEI e CPFs. | Tabela cronológica e histórico de processos. |
| `03_varredura_anual_ergas.py` | Varredura recursiva de pastas anuais em `M:\ERGAS\Alta Floresta` mapeando documentos e fotos. | Índice de pastas e contagem de mídias. |
| `04_mapeamento_rts_e_tecnicos.py` | Extração de Responsáveis Técnicos (engenheiros, agrônomos, biólogos, veterinários) e cálculo de % com RT fixo. | Base consolidada de técnicos e prestadores. |
| `05_conversor_fotos_webp.py` | Conversão ultrarrápida de fotos JPG/PNG de campo para `.webp` (redução de ~90% de tamanho para mobile). | Imagens otimizadas em `midia_webp/`. |
| `06_higienizador_catalogo_produtores.py` | Normalização de CPFs/CNPJs, remoção de pastas administrativas (BPA, ERGA) e cálculo de oportunidades AgroPrime. | `catalogo_2026_2012.json`. |
| `07_construtor_sqlite_mestre.py` | Geração do banco SQLite mestre relacional com FTS (Full-Text Search) de todos os produtores e vistorias. | `INDICE_MESTRE_PRODUTORES_E_PROCESSOS.sqlite`. |
| `08_gerador_crm_html_daylight.py` | Gerador do HTML responsivo com modo dia de alto contraste, busca universal hero e cartões retráteis. | `CRM_ERP_GLOBAL_SEDAM.html`. |
| `09_compactador_catalogo_js.py` | Compactador do catálogo de dados em bundle JS otimizado para celulares e Starlink móvel (1,85 MB). | `dados/catalogo_2026_2012.js`. |
| `10_sincronizador_drive_mirror.py` | Espelhamento automático de todos os arquivos estáticos para as pastas correspondentes do Google Drive. | `07_GITHUB_PAGES_E_APPS_SCRIPT` no Drive. |
| `11_atualizador_index_html.py` | Adiciona card de navegação para o CRM/ERP Global dentro do aplicativo mobile `index.html`. | `index.html`. |
| `12_testador_conectividade_tailscale.py` | Testador de conectividade mesh Tailscale (IPv4, ping entre máquinas) e verificação de acesso ao `M:\`. | Diagnóstico imediato no terminal. |

---

## 🔒 Regras de Execução

1. **ZERO WRITES EM `M:\`:** Nunca gravar, alterar ou renomear nada na rede corporativa `172.16.6.10\sedam` (`M:\`). Toda saída deve ser gravada no Google Drive (`G:\`) ou no repositório local Git.
2. **Sincronização Git:** Sempre rode `git pull origin main` antes de iniciar processamentos novos.
