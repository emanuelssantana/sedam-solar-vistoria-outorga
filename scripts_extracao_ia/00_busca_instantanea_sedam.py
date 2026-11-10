# -*- coding: utf-8 -*-
"""
00_busca_instantanea_sedam.py
Buscador Instantaneo SEDAM (Sem precisar varrer o HD fisico 172.16.6.10)
Tempo de resposta: < 0.1 segundo
Consulta: Catalogo Consolidado Local + SQLite Mestre
Uso:
  python 00_busca_instantanea_sedam.py "Lino Duque"
  python 00_busca_instantanea_sedam.py "cafe"
  python 00_busca_instantanea_sedam.py "1801/00667"
"""
import sys
import os
import json
import sqlite3

# Suporte utf-8
sys.stdout.reconfigure(encoding='utf-8')

termo = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else ""

if not termo:
    print("=" * 70)
    print("  BUSCADOR INSTANTANEO SEDAM (OFFLINE / CACHE ULTRA-RAPIDO)")
    print("=" * 70)
    print("Uso: python 00_busca_instantanea_sedam.py <termo_de_busca>")
    print("Exemplos:")
    print("  python 00_busca_instantanea_sedam.py 'Lino'")
    print("  python 00_busca_instantanea_sedam.py 'cafe'")
    print("  python 00_busca_instantanea_sedam.py 'piscicultura'")
    print("  python 00_busca_instantanea_sedam.py '1801/00667'")
    print("  python 00_busca_instantanea_sedam.py '340.439'")
    sys.exit(0)

print(f"\n🔍 Buscando por: '{termo}' nos indices mestres locais...")

# 1. Caminhos prioritarios dos indices
caminhos_catalogo = [
    r"G:\Meu Drive\IDEs_Agents_26\SEDAM\-DAK_VertexAI_CRM_ERP-rede-sedam\06_BASE_SEPARADA_POR_ANO_2026_A_2012\CATALOGO_RT_E_PRODUTORES_UNIFICADO\PRODUTORES_CONSOLIDADOS_2026_A_2012_COMPLETO.json",
    r"G:\Meu Drive\IDEs_Agents_26\SEDAM\-DAK_VertexAI_CRM_ERP-rede-sedam\07_GITHUB_PAGES_E_APPS_SCRIPT\dados\catalogo_2026_2012.json",
    os.path.join(os.path.dirname(__file__), "..", "dados", "catalogo_2026_2012.json")
]

caminhos_sqlite = [
    r"G:\Meu Drive\IDEs_Agents_26\SEDAM\SEDAM-REDE_GERAL\CACHE_CONSULTA_AGENTES\INDICE_MESTRE_PRODUTORES_E_PROCESSOS.sqlite",
    r"G:\Meu Drive\IDEs_Agents_26\SEDAM\-DAK_VertexAI_CRM_ERP-rede-sedam\BASES_INDEXADAS_GERAIS\SEDAM_ERGAS_8TB\INDICE_MESTRE_PRODUTORES_E_PROCESSOS.sqlite"
]

encontrados_catalogo = []
termo_lower = termo.lower()

# Busca no Catalogo JSON
for cp in caminhos_catalogo:
    if os.path.exists(cp):
        try:
            with open(cp, "r", encoding="utf-8") as f:
                data = json.load(f)
                prods = data.get("produtores_catalogo", [])
                for p in prods:
                    hay = f"{p.get('nome_produtor_ou_empresa','')} {p.get('cpf_cnpj','')} {p.get('municipio','')} {' '.join(p.get('processos',[]))} {' '.join(p.get('atividades',[]))} {' '.join(p.get('tecnicos',[]))}".lower()
                    if termo_lower in hay:
                        encontrados_catalogo.append(p)
            break
        except Exception as e:
            pass

print(f"\n📊 Resultados no Catalogo Consolidado: {len(encontrados_catalogo)} produtor(es)/empresa(s)")
print("=" * 70)

for idx, p in enumerate(encontrados_catalogo[:10], start=1):
    print(f"[{idx}] {p.get('nome_produtor_ou_empresa', 'SEM NOME')} (ID: {p.get('id_catalogo', '-')})")
    print(f"    • CPF/CNPJ: {p.get('cpf_cnpj', '-')} | Tipo: {p.get('tipo_pessoa', '-')}")
    print(f"    • Municipio: {p.get('municipio', '-')} | Anos Ativos: {', '.join(p.get('anos_ativos', []))}")
    print(f"    • Atividades: {', '.join(p.get('atividades', ['Consultar']))}")
    print(f"    • Tecnicos (RT): {', '.join(p.get('tecnicos', ['Nenhum']))}")
    print(f"    • Processos ({p.get('qtd_processos_unicos', 0)}): {', '.join(p.get('processos', [])[:5])}")
    print(f"    • Laudos Word: {len(p.get('vistorias_e_laudos', []))} arquivos | Fotos: {len(p.get('pastas_fotos', []))} pastas")
    print(f"    • Gasto Consultoria Est.: R$ {p.get('gasto_estimado_consultoria_brl', 0):,.2f}")
    print("-" * 70)

if len(encontrados_catalogo) > 10:
    print(f"... e mais {len(encontrados_catalogo) - 10} registros. Refine o termo para filtrar.")

# Busca no SQLite (Processos e Malotes)
encontrados_sqlite = []
for sp in caminhos_sqlite:
    if os.path.exists(sp):
        try:
            conn = sqlite3.connect(sp)
            cur = conn.cursor()
            q = f"SELECT ano, processo, data, requerente_assunto, setor, via FROM produtores_processos WHERE requerente_assunto LIKE ? OR processo LIKE ? LIMIT 10"
            cur.execute(q, (f"%{termo}%", f"%{termo}%"))
            encontrados_sqlite = cur.fetchall()
            conn.close()
            break
        except Exception as e:
            pass

if encontrados_sqlite:
    print(f"\n📁 Ocorrencias no Livro de Malotes / Protocolos ({len(encontrados_sqlite)} amostras):")
    for r in encontrados_sqlite:
        print(f"  • [{r[0]}] Proc: {r[1]} ({r[2]}) - {r[3]} [Setor: {r[4]} | Via: {r[5]}]")

print("\n💡 Dica: Para acessar o arquivo fisico no servidor 172.16.6.10, use a letra M:\\ ou K:\\ diretamente pelo caminho do laudo, sem necessidade de varrer pastas inteiras.")
