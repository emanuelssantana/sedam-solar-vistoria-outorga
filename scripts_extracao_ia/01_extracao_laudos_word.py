import os
import sys
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

sys.stdout.reconfigure(encoding='utf-8')
t0 = time.time()

with open(r'C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\ergas_complete_master_index.json', 'r', encoding='utf-8') as f:
    master = json.load(f)

docs = master['docs']

def parse_docx(path):
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs = []
    tables = []
    with zipfile.ZipFile(path) as z:
        xml_bytes = z.read('word/document.xml')
        root = ET.fromstring(xml_bytes)
        for p in root.findall('.//w:body/w:p', ns):
            texts = [t.text for t in p.findall('.//w:t', ns) if t.text]
            line = ''.join(texts).strip()
            if line:
                paragraphs.append(line)
        for tbl in root.findall('.//w:body/w:tbl', ns):
            t_rows = []
            for tr in tbl.findall('.//w:tr', ns):
                row_cells = []
                for tc in tr.findall('.//w:tc', ns):
                    c_texts = [t.text for t in tc.findall('.//w:t', ns) if t.text]
                    row_cells.append(' '.join(''.join(c_texts).split()))
                if any(row_cells):
                    t_rows.append(row_cells)
            if t_rows:
                tables.append(t_rows)
    return paragraphs, tables

def parse_doc_fast(path, size, is_2025_2026=False):
    with open(path, 'rb') as f:
        if is_2025_2026 or size <= 600000:
            data = f.read()
        else:
            head = f.read(393216)
            f.seek(max(393216, size - 131072))
            tail = f.read(131072)
            data = head + b'\n' + tail
    chunks = []
    try:
        u16 = data.decode('utf-16le', errors='ignore')
        for m in re.finditer(r'[\w\s\.,;:\-\(\)/ºª°\'\"%\+\$\n\r@#&!\?]{25,}', u16):
            s = m.group(0).strip()
            alpha = sum(c.isalpha() for c in s)
            if alpha > len(s) * 0.4:
                chunks.append(s)
    except Exception:
        pass
    try:
        lat = data.decode('latin-1', errors='ignore')
        for m in re.finditer(r'[A-Za-zÀ-ÿ0-9\s\.,;:\-\(\)/ºª°\'\"%\+\$\n\r]{30,}', lat):
            s = m.group(0).strip()
            if any(k in s.upper() for k in ('SEDAM', 'OUTORGA', 'VISTORIA', 'PROCESSO', 'INTERESSADO', 'CPF', 'CNPJ', 'COORDENADA', 'CONCLUS', 'RELAT', 'ALTA FLORESTA', 'SANTA LUZIA', 'ALTO ALEGRE')):
                chunks.append(s)
    except Exception:
        pass
    lines = []
    seen = set()
    for c in chunks:
        for ln in c.splitlines():
            ln_clean = ' '.join(ln.split())
            if len(ln_clean) >= 4 and ln_clean not in seen:
                if not any(bad in ln_clean for bad in ('Normal.dotm', 'Microsoft Office Word', 'Times New Roman', 'Calibri', 'Root Entry', 'WordDocument')):
                    seen.add(ln_clean)
                    lines.append(ln_clean)
    return lines, []

def infer_year(rel_path, filename, full_text=''):
    for y in ('2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012'):
        if y in rel_path or y in filename:
            return y
    for y in ('2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018'):
        if y in full_text[:3000]:
            return y
    return 'ANTERIORES'

def extract_metadata_from_text(full_text, filename, rel_path):
    cpfs = list(dict.fromkeys(re.findall(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', full_text)))
    cnpjs = list(dict.fromkeys(re.findall(r'\b\d{2}\.?\d{3}\.?\d{3}/\d{4}-?\d{2}\b', full_text)))
    phones = list(dict.fromkeys(re.findall(r'(?:\(?\d{2}\)?\s*)?(?:9\s*)?\d{4}[-\s]\d{4}', full_text)))
    proc_sei = list(dict.fromkeys(re.findall(r'\b\d{4}\.\d{5,6}/\d{4}-\d{2}\b', full_text)))
    proc_siga = list(dict.fromkeys(re.findall(r'\b(?:1801|1610|1800)\d{6}\b|\b1801/\d{4,5}/\d{4}\b', full_text)))
    creas = list(dict.fromkeys(re.findall(r'CREA[:\s/-]*[0-9A-Za-z\./-]+', full_text, re.I)))
    arts = list(dict.fromkeys(re.findall(r'ART[:\sNºnº-]*[0-9A-Za-z\./-]+', full_text, re.I)))
    cars = list(dict.fromkeys(re.findall(r'RO-\d{7}-[0-9A-Fa-f]{32}', full_text)))
    dms_coords = list(dict.fromkeys(re.findall(r"\d{1,2}\s*[°º]\s*\d{1,2}\s*['’′]\s*\d{1,2}(?:[\.,]\d+)?\s*[\"”″]?\s*[NSnsLOloWw]?", full_text)))
    areas = list(dict.fromkeys(re.findall(r'\b\d+(?:[\.,]\d+)?\s*(?:ha|hectares|alqueires)\b', full_text, re.I)))
    valores = list(dict.fromkeys(re.findall(r'(?:R\$\s*\d+(?:[\.\d]+)*,\d{2}|\d+(?:,\d+)?\s*UPF(?:/RO)?)', full_text, re.I)))
    year = infer_year(rel_path, filename, full_text)

    mun = 'AFO'
    up_all = (rel_path + ' ' + full_text[:2000]).upper()
    if 'SANTA LUZIA' in up_all or ' SLO' in up_all:
        mun = 'SLO'
    elif 'ALTO ALEGRE' in up_all or ' AAP' in up_all:
        mun = 'AAP'
    elif 'NOVA BRASIL' in up_all or ' NBO' in up_all:
        mun = 'NBO'
    elif 'ROLIM DE MOURA' in up_all:
        mun = 'RM'
    elif 'COSTA MARQUES' in up_all:
        mun = 'CM'

    interessado = ''
    empreendimento = ''
    rt_info = ''
    localizacao = ''
    for line in full_text.splitlines()[:80]:
        lu = line.upper()
        if not interessado and any(k in lu for k in ('INTERESSADO:', 'REQUERENTE:', 'PROPRIETÁRIO:', 'PROPRIETARIO:', 'AUTUADO:', 'EM NOME DE:')):
            interessado = line.strip()[:180]
        if not empreendimento and any(k in lu for k in ('EMPREENDIMENTO:', 'DENOMINAÇÃO:', 'PROPRIEDADE:', 'IMÓVEL:')):
            empreendimento = line.strip()[:180]
        if not rt_info and any(k in lu for k in ('RESPONSÁVEL TÉCNICO', 'RESPONSAVEL TECNICO', 'ENGENHEIRO', 'CREA')):
            rt_info = line.strip()[:180]
        if not localizacao and any(k in lu for k in ('ENDEREÇO:', 'LOCALIZAÇÃO:', 'LINHA ', 'GLEBA ')):
            localizacao = line.strip()[:180]

    return {
        'ano_referencia': year,
        'municipio': mun,
        'interessado_extraido': interessado,
        'empreendimento_extraido': empreendimento,
        'rt_extraido': rt_info,
        'localizacao_extraida': localizacao,
        'cpfs': cpfs[:10],
        'cnpjs': cnpjs[:10],
        'telefones': phones[:10],
        'processos_sei': proc_sei[:15],
        'processos_siga': proc_siga[:15],
        'creas': creas[:10],
        'arts': arts[:10],
        'cars': cars[:5],
        'coordenadas_dms': dms_coords[:30],
        'areas_mencionadas': areas[:15],
        'valores_taxas': valores[:10]
    }

def worker(doc_item):
    p = doc_item['path']
    ext = doc_item['ext']
    yr = doc_item['prelim_year']
    is_recent = yr in ('2026', '2025', '2024')
    try:
        if ext == '.docx':
            paras, tbls = parse_docx(p)
        else:
            paras, tbls = parse_doc_fast(p, doc_item['size'], yr in ('2026', '2025'))
        full_txt = '\n'.join(paras) + '\n' + '\n'.join([' | '.join(r) for t in tbls for r in t])
        meta = extract_metadata_from_text(full_txt, doc_item['name'], doc_item['rel_path'])
        return {
            'rel_path': doc_item['rel_path'],
            'path': p,
            'name': doc_item['name'],
            'ext': ext,
            'size': doc_item['size'],
            'mtime': doc_item['mtime'],
            'metadata': meta,
            'paragraphs_count': len(paras),
            'tables_count': len(tbls),
            'paragraphs': paras if is_recent else paras[:100],
            'tables': tbls if is_recent else tbls[:10]
        }
    except Exception as e:
        return {
            'rel_path': doc_item['rel_path'],
            'path': p,
            'name': doc_item['name'],
            'ext': ext,
            'size': doc_item['size'],
            'metadata': {'ano_referencia': yr},
            'error': str(e)
        }

phase1_docs = []
phase2_docs = []
for d in docs:
    if d['ext'] not in ('.docx', '.doc'):
        continue
    nl = d['name'].lower()
    if any(skip in nl for skip in ('cloreto de magn', 'para casais', '10 ditados', 'nova ortografia', 'granulitos')):
        continue
    yr = infer_year(d['rel_path'], d['name'])
    d['prelim_year'] = yr
    if yr in ('2026', '2025', '2024', '2023') or not d['rel_path'].startswith('FURTADO\\IMAGENS E RELATÓRIOS 2020'):
        phase1_docs.append(d)
    else:
        phase2_docs.append(d)

print(f"Phase 1 (2026->2023 + active technician folders): {len(phase1_docs)} docs...", flush=True)
res1 = []
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = [ex.submit(worker, d) for d in phase1_docs]
    for fut in as_completed(futs):
        res1.append(fut.result())

print(f"Phase 1 done in {time.time()-t0:.2f}s ({len(res1)} docs)!", flush=True)
out_p1 = r'C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\ergas_extracted_2026_2025_2024_and_controls.json'
with open(out_p1, 'w', encoding='utf-8') as f:
    json.dump(res1, f, ensure_ascii=False, indent=2)

print(f"Phase 2 (Historical archive 2012-2020 in Furtado): {len(phase2_docs)} docs...", flush=True)
res2 = []
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = [ex.submit(worker, d) for d in phase2_docs]
    for fut in as_completed(futs):
        res2.append(fut.result())

all_res = res1 + res2
print(f"All {len(all_res)} docs extracted in {time.time()-t0:.2f}s!", flush=True)
out_all = r'C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\ergas_extracted_all_docs_content.json'
with open(out_all, 'w', encoding='utf-8') as f:
    json.dump(all_res, f, ensure_ascii=False, indent=2)
print("Saved all to", out_all, flush=True)
