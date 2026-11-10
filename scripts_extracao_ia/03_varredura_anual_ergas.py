import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

base = r'\\172.16.6.10\sedam\ERGAS\Alta Floresta'

# 1. Check FRANCISCO\ANTIGOS\REPRESA LINO DUQUE AFO 05.04.2023 and all files in FRANCISCO\ANTIGOS
antigos_dir = os.path.join(base, r'FRANCISCO\ANTIGOS')
print("=== All files in FRANCISCO\\ANTIGOS ===")
if os.path.exists(antigos_dir):
    for e in sorted(os.scandir(antigos_dir), key=lambda x: x.name):
        if e.is_file():
            print(" [F]", e.name, e.stat().st_size)
        elif 'LINO' in e.name.upper() or 'DUQUE' in e.name.upper():
            print(" [D-MATCH]", e.name)
            for sub in os.scandir(e.path):
                print("    ->", sub.name, sub.stat().st_size if sub.is_file() else 'DIR')

# 2. Check 04 - OUTROS\CAMILA subdirectories
camila_dir = os.path.join(base, r'04 - OUTROS\CAMILA')
print("\n=== 04 - OUTROS\\CAMILA subdirectories ===")
if os.path.exists(camila_dir):
    for e in sorted(os.scandir(camila_dir), key=lambda x: x.name):
        if e.is_dir():
            print(f" [CAMILA\\{e.name}]")
            for sub in sorted(os.scandir(e.path), key=lambda x: x.name):
                print(f"    {'[D]' if sub.is_dir() else '[F]'} {sub.name}")

# 3. Walk all of M:\ERGAS\Alta Floresta (excluding temp files and Thumbs.db) to count and index all files!
all_files = []
all_dirs = []
for root, dirs, files in os.walk(base):
    for d in dirs:
        full_d = os.path.join(root, d)
        all_dirs.append(full_d)
    for f in files:
        if f.lower() in ('thumbs.db', 'desktop.ini') or f.startswith('~$') or f.endswith('.tmp'):
            continue
        full_f = os.path.join(root, f)
        try:
            st = os.stat(full_f)
            all_files.append({
                'path': full_f,
                'rel_path': os.path.relpath(full_f, base),
                'name': f,
                'ext': os.path.splitext(f)[1].lower(),
                'size': st.st_size,
                'mtime': st.st_mtime
            })
        except Exception:
            pass

print(f"\nTotal dirs in ERGAS\\Alta Floresta: {len(all_dirs)}")
print(f"Total valid files in ERGAS\\Alta Floresta: {len(all_files)}")

by_ext = {}
for item in all_files:
    ext = item['ext']
    by_ext[ext] = by_ext.get(ext, 0) + 1
print("Files by extension:", json.dumps(by_ext, indent=2))

# Search for Lino or Duque in any file or dir path
lino_matches = [x for x in all_files if 'lino' in x['rel_path'].lower() or 'duque' in x['rel_path'].lower()]
print(f"\nAll file paths matching Lino/Duque ({len(lino_matches)}):")
for m in lino_matches:
    if not m['ext'] in ('.jpg', '.jpeg', '.png'):
        print("  [DOC/OTHER]", m['rel_path'], m['size'])
print(f"  (Plus {len([m for m in lino_matches if m['ext'] in ('.jpg', '.jpeg', '.png')])} image files in Lino folders)")

# Save full ERGAS file index to local scratch
out_index = r'C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\ergas_full_file_index.json'
with open(out_index, 'w', encoding='utf-8') as f:
    json.dump({'dirs': all_dirs, 'files': all_files}, f, ensure_ascii=False, indent=2)
print("Saved full ERGAS file index to", out_index)
