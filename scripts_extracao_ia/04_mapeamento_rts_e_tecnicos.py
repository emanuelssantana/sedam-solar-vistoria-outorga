import os
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')
t0 = time.time()
base = r'\\172.16.6.10\sedam\ERGAS\Alta Floresta'

# Explicit known folders in ERGAS\Alta Floresta where documents and producer folders live (depth 1 only, no recursion into photo directories!)
target_folders = [
    r'',
    r'FRANCISCO',
    r'FRANCISCO\2025',
    r'FRANCISCO\2024',
    r'FRANCISCO\FOTOS 2025-2026',
    r'FRANCISCO\FOTOS OUTORGA',
    r'FRANCISCO\ANTIGOS',
    r'FURTADO',
    r'FURTADO\IMAGENS E RELATÓRIOS 2020',
    r'FURTADO\LICENCIAMENTO AMBIENTAL DE POÇO TUBULAR - RO',
    r'FURTADO\MODELO DE RELATORIO DE OUTORGA',
    r'FURTADO\NOVA',
    r'KATIA',
    r'KATIA\CEMITERIO AFO',
    r'KATIA\DOC. 2026',
    r'KATIA\DOC. 2025',
    r'KATIA\DOC. 2024',
    r'KATIA\DOC. 2023',
    r'MALOTE 2026',
    r'NILCE',
    r'NILCE\DOC. 2023',
    r'NILCE\DOC. 2022',
    r'NILCE\DOC. 2021',
    r'NILCE\DOC. 2020',
    r'NILCE\MALOTE A PARTIR DE 20 MAIO 2025',
    r'SARAH',
    r'VALENTINA',
    r'VALVIQUE',
    r'01 - ADMINISTRATIVO\1-MALOTE 2025',
    r'01 - ADMINISTRATIVO\2-MEMORANDOS 2025',
    r'01 - ADMINISTRATIVO\MALOTE 2026',
    r'01 - ADMINISTRATIVO\MALOTE A PARTIR DE MAIO 2025',
    r'01 - ADMINISTRATIVO\2024',
    r'01 - ADMINISTRATIVO\DOC. 2021',
    r'01 - ADMINISTRATIVO\DOC.2022',
    r'01 - ADMINISTRATIVO\GUAI DE MALOTE 2024',
    r'01 - ADMINISTRATIVO\GUAI MALOTE 2022',
    r'01 - ADMINISTRATIVO\MEMORANDOS 2022',
    r'02 - REQ. PARCELAMENTO AUTOS',
    r'03 - Formulário de denúncia\9 - DENÚNCIAS 2026',
    r'03 - Formulário de denúncia\8 - DENÚNCIAS 2025',
    r'03 - Formulário de denúncia\7 - DENUNCIAS 2024',
    r'03 - Formulário de denúncia\6 - DENÚNCIAS 2023',
    r'03 - Formulário de denúncia\5 - DENÚNCIAS 2022',
    r'03 - Formulário de denúncia\4 - DENÚNCIAS 2021',
    r'03 - Formulário de denúncia\3 - DENÚNCIAS 2020',
    r'03 - Formulário de denúncia\2 - DENÚNCIAS 2019',
    r'03 - Formulário de denúncia\1 - DENÚNCIAS 2018',
    r'04 - OUTROS\CAMILA',
    r'04 - OUTROS\CAMILA\2026',
    r'04 - OUTROS\CAMILA\2025',
    r'04 - OUTROS\CAMILA\2024',
    r'04 - OUTROS\CAMILA\2023',
    r'04 - OUTROS\CAMILA\Antigos',
    r'04 - OUTROS\ISADORA',
    r'04 - OUTROS\KAMILA BINS',
    r'04 - OUTROS\MARCELO',
    r'04 - OUTROS\ROBSON',
    r'04 - OUTROS\ROBSON\VISTORIAS',
    r'04 - OUTROS\ROBSON\DOCUMENTOS ROBSON',
    r'04 - OUTROS\SIRLEIA',
]

all_docs = []
all_dirs = []

for tf in target_folders:
    p = os.path.join(base, tf) if tf else base
    if not os.path.exists(p):
        continue
    try:
        for e in os.scandir(p):
            name = e.name
            nl = name.lower()
            if nl in ('thumbs.db', 'desktop.ini') or name.startswith('~$') or nl.endswith('.tmp') or nl.endswith('_files'):
                continue
            rel = os.path.join(tf, name) if tf else name
            if e.is_dir(follow_symlinks=False):
                all_dirs.append({
                    'folder_group': tf or 'ROOT',
                    'rel_path': rel,
                    'path': e.path,
                    'name': name
                })
            elif e.is_file(follow_symlinks=False):
                ext = os.path.splitext(nl)[1]
                st = e.stat(follow_symlinks=False)
                all_docs.append({
                    'folder_group': tf or 'ROOT',
                    'rel_path': rel,
                    'path': e.path,
                    'name': name,
                    'ext': ext,
                    'size': st.st_size,
                    'mtime': st.st_mtime
                })
    except Exception as ex:
        print(f"Err {tf}: {ex}", flush=True)

print(f"Finished in {time.time()-t0:.2f}s! Found {len(all_dirs)} dirs and {len(all_docs)} files across {len(target_folders)} target folders.", flush=True)

by_ext = {}
for d in all_docs:
    by_ext[d['ext']] = by_ext.get(d['ext'], 0) + 1
print("Files by ext:", json.dumps(by_ext, indent=2), flush=True)

out_file = r'C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\ergas_all_technician_docs.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump({'dirs': all_dirs, 'docs': all_docs}, f, ensure_ascii=False, indent=2)
print("Saved to", out_file, flush=True)
