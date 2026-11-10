import os
import sys
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

sys.stdout.reconfigure(encoding='utf-8')
t0 = time.time()

with open(r'C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\ergas_complete_master_index.json', 'r', encoding='utf-8') as f:
    master = json.load(f)

docs = master['docs']

class MaloteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_td = False
        self.in_tr = False
        self.rows = []
        self.curr_row = []
        self.curr_cell = []
        self.all_text = []
    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.in_tr = True
            self.curr_row = []
        elif tag in ('td', 'th'):
            self.in_td = True
            self.curr_cell = []
    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.in_td:
            self.in_td = False
            self.curr_row.append(' '.join(''.join(self.curr_cell).split()))
        elif tag == 'tr' and self.in_tr:
            self.in_tr = False
            if any(self.curr_row):
                self.rows.append(self.curr_row)
    def handle_data(self, data):
        s = data.strip()
        if s:
            self.all_text.append(s)
        if self.in_td:
            self.curr_cell.append(data)

html_docs = [d for d in docs if d['ext'] in ('.html', '.htm')]
# Deduplicate by filename (e.g. Guia Nº 0016312025.html copied in NILCE and 01-ADMIN)
unique_html = {}
for d in html_docs:
    clean_name = d['name'].replace(' - Copia', '').strip()
    if clean_name not in unique_html:
        unique_html[clean_name] = d

print(f"Parsing {len(unique_html)} unique Malote HTML guides (from {len(html_docs)} total HTML files)...", flush=True)

def parse_one_malote(d):
    try:
        with open(d['path'], 'r', encoding='utf-8', errors='ignore') as f:
            txt = f.read()
        mp = MaloteParser()
        mp.feed(txt)
        header = ' '.join(mp.all_text[:30])
        m_num = re.search(r'Nº\s*(\d+)', header) or re.search(r'(\d{8,12})', d['name'])
        guia_num = m_num.group(1) if m_num else d['name']
        m_dt = re.search(r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}(?::\d{2})?)', header)
        guia_dt = m_dt.group(1) if m_dt else ''
        year = guia_num[-4:] if len(guia_num) >= 4 and guia_num[-4:].isdigit() else 'OUTROS'

        items = []
        for r in mp.rows:
            if len(r) >= 5 and r[0] != 'Número Protocolo' and not r[0].startswith('Origem:'):
                # Typical row: [protocolo, tipo, documento/processo, assunto, interessado_cpf, destino_extra, data_hora, obs]
                prot = r[0]
                if not re.search(r'\d', prot):
                    continue
                tipo = r[1] if len(r) > 1 else ''
                proc_doc = r[2] if len(r) > 2 else ''
                assunto = r[3] if len(r) > 3 else ''
                interessado_raw = r[4] if len(r) > 4 else ''
                dt_prot = r[6] if len(r) > 6 else (r[5] if len(r) > 5 else guia_dt)

                cpfs = re.findall(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', interessado_raw + ' ' + assunto)
                cnpjs = re.findall(r'\b\d{2}\.?\d{3}\.?\d{3}/\d{4}-?\d{2}\b', interessado_raw + ' ' + assunto)
                # Clean name
                nome_limpo = re.sub(r'(?:,?\s*(?:CPF|CNPJ)\s*[:Nºnº-]*\s*[\d\./-]+).*', '', interessado_raw, flags=re.I).strip(' ,.-')

                items.append({
                    'guia_numero': guia_num,
                    'guia_data': guia_dt,
                    'ano': year,
                    'arquivo_origem': d['rel_path'],
                    'protocolo': prot,
                    'tipo_documento': tipo,
                    'processo_ou_doc': proc_doc,
                    'assunto': assunto,
                    'interessado_bruto': interessado_raw,
                    'nome_interessado': nome_limpo,
                    'cpf': cpfs[0] if cpfs else '',
                    'cnpj': cnpjs[0] if cnpjs else '',
                    'data_hora': dt_prot
                })
        return items
    except Exception as e:
        return []

all_malote_items = []
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = [ex.submit(parse_one_malote, d) for d in unique_html.values()]
    for fut in as_completed(futs):
        all_malote_items.extend(fut.result())

print(f"Extracted {len(all_malote_items)} protocol items from Malote HTML guides in {time.time()-t0:.2f}s!", flush=True)

by_yr = {}
with_cpf = 0
with_cnpj = 0
for it in all_malote_items:
    y = it['ano']
    by_yr[y] = by_yr.get(y, 0) + 1
    if it['cpf']:
        with_cpf += 1
    if it['cnpj']:
        with_cnpj += 1

print("Malote items by year:", json.dumps(by_yr, indent=2), flush=True)
print(f"Items with explicit CPF: {with_cpf}, with explicit CNPJ: {with_cnpj}", flush=True)

out_malotes = r'C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\ergas_all_malotes_extracted.json'
with open(out_malotes, 'w', encoding='utf-8') as f:
    json.dump(all_malote_items, f, ensure_ascii=False, indent=2)
print("Saved to", out_malotes, flush=True)
