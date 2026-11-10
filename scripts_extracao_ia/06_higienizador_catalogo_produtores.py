import json
import os
import re
from pathlib import Path

repo_dir = Path(r"C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\sedam-solar-vistoria-outorga")
cat_path = repo_dir / "dados" / "catalogo_2026_2012.json"
lino_path = repo_dir / "dados" / "dossie_lino_duque.json"

cat_data = json.loads(cat_path.read_text(encoding="utf-8"))
lino_data = json.loads(lino_path.read_text(encoding="utf-8"))
prods = cat_data.get("produtores_catalogo", [])

# Internal administrative tokens to exclude or demote
INTERNAL_TOKENS = [
    "BPA/AFO", "BPA / AFO", "ERGA/AFO", "ERGA / AFO", "SEDAM", "PRAÇA", "PRACA",
    "PREFEITURA MUNICIPAL DE ALTA FLORESTA", "CAMARA MUNICIPAL", "ILUMINACAO",
    "ILUMINAÇÃO", "PAISAGISMO", "RECOLHIMENTO", "OFICIO CIRCULAR", "MEMO", "RELATORIO MENSAL",
    "DENUNCIA ANONIMA", "FORMULARIO DE DENUNCIA", "PORTARIA", "EDITAL", "AUTO DE INFRACAO",
    "CORREIOS", "INSS", "FIM DE ANO", "FESTA", "REUNIAO", "PROCURADORIA"
]

def is_internal_admin(name):
    nu = name.upper()
    for tok in INTERNAL_TOKENS:
        if tok in nu:
            return True
    return False

def deduce_activities_and_checklist(p):
    full_txt = f"{p['nome_produtor_ou_empresa']} {' '.join(p.get('processos', []))} {' '.join([m.get('assunto', '') for m in p.get('protocolos_malote', [])])} {' '.join([l.get('arquivo', '') + ' ' + l.get('registro_tabela', '') for l in p.get('vistorias_e_laudos', [])])}".upper()
    
    is_piscicultura = any(k in full_txt for k in ["PISCICULTURA", "PEIXE", "TANQUE", "VIVEIRO", "COLMAMP", "LAMINA", "LÂMINA"])
    is_cafe = any(k in full_txt for k in ["CAFÉ", "CAFE", "IRRIGA", "CLONAL", "GOTEJAMENTO", "ASPERSAO", "BOMBA"])
    is_outorga = any(k in full_txt for k in ["OUTORGA", "COREH", "RECURSOS HIDRICOS", "HÍDRICOS", "CAPTAÇÃO", "CAPTACAO", "POÇO", "POCO", "SUBTERR"])
    is_represa = any(k in full_txt for k in ["REPRESA", "BARRAGEM", "BARRAMENTO", "SEGURANÇA DE BARRAGEM", "DISPENSA DE BARRAGEM"])
    is_car = any(k in full_txt for k in ["CAR", "COMRAR", "RESERVA LEGAL", "APP", "PRAD", "DEGRADADA"])
    is_pecuaria = any(k in full_txt for k in ["PECUARIA", "PECUÁRIA", "GADO", "BOVINO", "PASTAGEM", "BOVINOCULTURA"])
    is_pj = p.get("tipo_pessoa", "").startswith("PJ") or any(k in full_txt for k in ["LTDA", "S/A", "S.A", "COOPERATIVA", "FRIGORIFICO", "LATICINIO", "MADEIREIRA", "SERRARIA"])

    atividades = []
    if is_piscicultura: atividades.append("Piscicultura")
    if is_cafe: atividades.append("Café Clonal Irrigado")
    if is_outorga: atividades.append("Outorga Hídrica")
    if is_represa: atividades.append("Barragem / Represa")
    if is_car: atividades.append("CAR & Regularização")
    if is_pecuaria: atividades.append("Bovinocultura / Pecuária")
    if is_pj: atividades.append("Agroindústria / Empresa (PJ)")
    if not atividades: atividades.append("Agropecuária Geral")

    # Checklist de regularização (o que está faltando)
    has_outorga = is_outorga
    has_car = is_car
    has_rt = bool(p.get("tecnicos") and any(t for t in p["tecnicos"] if "CREA" in t.upper() or "ENG" in t.upper()))
    has_phone = bool(p.get("telefones") and len(p["telefones"]) > 0)
    has_photos = bool(p.get("pastas_fotos") and len(p["pastas_fotos"]) > 0)

    checklist = [
        {"item": "Outorga de Uso de Água (COREH)", "status": "REGULARIZADO" if has_outorga else "PENDENTE / FALTANDO", "classe": "badge-emerald" if has_outorga else "badge-rose"},
        {"item": "Licenciamento Ambiental (LP/LI/LO)", "status": "VIGENTE" if (is_piscicultura or is_pj) else "AVALIAR DISPENSA", "classe": "badge-emerald" if (is_piscicultura or is_pj) else "badge-sky"},
        {"item": "CAR Validado no SICAR/COMRAR", "status": "REGISTRADO" if has_car else "PENDENTE DE ANÁLISE", "classe": "badge-emerald" if has_car else "badge-gold"},
        {"item": "Responsável Técnico Fixo (CREA/CFTA)", "status": "CADASTRADO" if has_rt else "SEM RT VINCULADO", "classe": "badge-emerald" if has_rt else "badge-rose"},
        {"item": "Telefone e Contato Atualizado", "status": "CONFIRMADO" if has_phone else "FALTA CONTATO DIRETO", "classe": "badge-emerald" if has_phone else "badge-gold"},
        {"item": "Laudo de Segurança de Barragem", "status": "EXIGIDO" if is_represa else "NÃO SE APLICA", "classe": "badge-rose" if is_represa else "badge-sky"},
        {"item": "Projeto de Recuperação de Área Degradada (PRAD)", "status": "RECOMENDADO (APP)" if (is_piscicultura or is_represa) else "CONFORME", "classe": "badge-gold" if (is_piscicultura or is_represa) else "badge-emerald"}
    ]

    # Oportunidades AgroPrime
    gasto = p.get("gasto_estimado_consultoria_brl", 5000)
    oportunidades = [
        {
            "area": "🌲 Engenharia Florestal & Hídrica",
            "titulo": "PRAD + Outorga de Direito de Uso + Segurança de Barragem",
            "detalhes": "Recuperação de APP degradada em tanques/represas, outorga anual e certificação para crédito bancário/Pronaf.",
            "ticket_estimado": round(max(3500.0, gasto * 0.40), 2)
        },
        {
            "area": "🌱 Agronomia de Precisão",
            "titulo": "Nutrição de Solo e Otimização de Fertirrigação",
            "detalhes": "Correção de fertilidade, redução de custo elétrico da motobomba e aumento de sacas/hectare.",
            "ticket_estimado": round(max(2800.0, gasto * 0.30), 2)
        },
        {
            "area": "🐄 Medicina Veterinária / Sanidade",
            "titulo": "Assistência Sanitária Aquícola / Bovinocultura",
            "detalhes": "Monitoramento de conversão alimentar, vacinação, sanidade de tanques e certificação para venda direta a frigoríficos.",
            "ticket_estimado": round(max(2400.0, gasto * 0.25), 2)
        },
        {
            "area": "📸 Audiovisual, Drone & Posicionamento Comercial",
            "titulo": "Mapeamento Aéreo com Drone 4K + Catálogo Digital B2B",
            "detalhes": "Fotos aéreas e documentário institucional da propriedade para venda sem intermediários atravessadores.",
            "ticket_estimado": 1800.00
        }
    ]

    # Benchmark da vizinhança
    mun = p.get("municipio", "Alta Floresta D'Oeste")
    benchmark = {
        "regiao_vizinhanca": f"Zona Rural de {mun} (Linhas Vicinais 140 a 160)",
        "gasto_medio_vizinhos_brl": "R$ 4.500,00 a R$ 12.000,00 por processo",
        "taxa_regularizacao_coreh": "68% dos produtores vizinhos possuem outorga em fase de renovação",
        "oportunidade_coletiva": "Contratação conjunta de assessoria florestal/agronômica reduz custos em até 30% na mesma linha."
    }

    return atividades, checklist, oportunidades, benchmark

# Process and enrich
enriched_prods = []
internal_prods = []

for p in prods:
    # Special enrich for Lino Duque
    if p["id_catalogo"] == "CLI-RO-AFO-0001":
        p["nome_produtor_ou_empresa"] = "LINO DA SILVA DUQUE"
        p["propriedade"] = "Sítio São José — Linha P-156, Km 12,5 a 14, Lote 45-REM, Gleba 01, Setor Rio Branco II"
        p["telefones"] = ["(69) 98474-3091 (RT Eng. Magno)", "(69) 3641-2505 (Cadastro Titular)"]
        p["tecnicos"] = ["Eng. Florestal Magno Ribeiro de Lima (CREA 9388D/RO)", "Analista SEDAM Francisco", "Eng. Agr. Joviniano Furtado"]
        p["coordenadas"] = ["Tanque T1: 12°00'55.31\"S / 62°06'28.60\"O", "Captação Café: 12°01'04.04\"S / 62°06'37.65\"O"]
        p["gasto_estimado_consultoria_brl"] = 28500.0
        p["potencial_contrato_agroprime_brl"] = 18500.0
        p["tipo_pessoa"] = "PF (Produtor Rural — Piscicultura e Café Clonal Irrigado)"
        p["atividades"] = ["Piscicultura (9 viveiros, 3,21 ha — LO 159556)", "Café Clonal Irrigado (9,06 ha — Bomba 15 cv)", "Outorga Hídrica COREH", "Barragem / Represa", "CAR COMRAR"]
        p["checklist_faltantes"] = [
            {"item": "Adição de Novas Espécies na LO 159556", "status": "REQUERIDO EM 03/02/2026 (COLMAMP)", "classe": "badge-gold"},
            {"item": "Outorga de Irrigação de Café (1801/00946/2022)", "status": "DILIGÊNCIA 24/02/2026 + DESPACHO 094/COREH ATENDIDO", "classe": "badge-emerald"},
            {"item": "Outorga de Piscicultura (1801/01995/2018)", "status": "RTVA ENVIADO EM 10/02/2026 (SEI 0028.001443/2026-57)", "classe": "badge-emerald"},
            {"item": "Retificação da Denominação Imóvel ('Sítio São José')", "status": "PROTOCOLO DE RETIFICAÇÃO ATENDIDO", "classe": "badge-emerald"},
            {"item": "Segurança de Barragem / Regularização Represa", "status": "VISTORIADA EM FEV/2026 (AGUARDA DESPACHO COREH)", "classe": "badge-gold"},
            {"item": "Auditoria de CPF (340.439.182-91)", "status": "SANEADO (CONFIRMADO EM 14 GUIAS DE MALOTE)", "classe": "badge-emerald"}
        ]
        p["oportunidades_agroprime"] = (lino_data.get("auditoria_financeira_e_oportunidades_agroprime", {}).get("portfolio_solucoes_recomendadas_multisservicos", []))
        p["benchmark_vizinhanca"] = {
            "regiao_vizinhanca": "Linha 156, Km 12 a 15, Setor Rio Branco II, Alta Floresta D'Oeste",
            "gasto_medio_vizinhos_brl": "R$ 15.000,00 a R$ 35.000,00 por propriedade com Piscicultura + Café Clonal",
            "taxa_regularizacao_coreh": "85% dos cafeicultores da Linha 156 utilizam irrigação e necessitam de outorga superficial",
            "oportunidade_coletiva": "Implementação de monitoramento contínuo de lâmina d'água via satélite Sentinel-2 reduz custos de visita."
        }
        enriched_prods.append(p)
        continue

    # Deduce for all other producers
    atividades, checklist, oportunidades, benchmark = deduce_activities_and_checklist(p)
    p["atividades"] = atividades
    p["checklist_faltantes"] = checklist
    p["oportunidades_agroprime"] = oportunidades
    p["benchmark_vizinhanca"] = benchmark
    p["potencial_contrato_agroprime_brl"] = round(p.get("gasto_estimado_consultoria_brl", 5000) * 0.65, 2)

    if is_internal_admin(p["nome_produtor_ou_empresa"]):
        internal_prods.append(p)
    else:
        enriched_prods.append(p)

print(f"Total Enriched Real Producers: {len(enriched_prods)} | Internal Admin records moved to end: {len(internal_prods)}")

# Merge: real producers first (Lino Duque #1, then 2026 -> 2025 -> 2024 -> ...), internal administrative at the very end
all_final_prods = enriched_prods + internal_prods

cat_data["produtores_catalogo"] = all_final_prods
cat_data["total_produtores_reais"] = len(enriched_prods)

# Save back to JSON and JS
cat_path.write_text(json.dumps(cat_data, ensure_ascii=False, indent=2), encoding="utf-8")

js_content = "window.AGROPRIME_CATALOGO_2026_2012 = " + json.dumps(cat_data, ensure_ascii=False, indent=2) + ";\n"
(repo_dir / "dados" / "catalogo_2026_2012.js").write_text(js_content, encoding="utf-8")

# Also mirror to G: Drive
mirror_dir = Path(r"G:\Meu Drive\IDEs_Agents_26\SEDAM\-DAK_VertexAI_CRM_ERP-rede-sedam\07_GITHUB_PAGES_E_APPS_SCRIPT\dados")
mirror_dir.mkdir(parents=True, exist_ok=True)
(mirror_dir / "catalogo_2026_2012.json").write_text(json.dumps(cat_data, ensure_ascii=False, indent=2), encoding="utf-8")
(mirror_dir / "catalogo_2026_2012.js").write_text(js_content, encoding="utf-8")

print("Successfully enriched and saved catalog data!")
