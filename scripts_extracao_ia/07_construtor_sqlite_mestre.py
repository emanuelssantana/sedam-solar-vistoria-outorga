import os
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')
t0 = time.time()
base = r'\\172.16.6.10\sedam\ERGAS\Alta Floresta'

with open(r'C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\ergas_all_technician_docs.json', 'r', encoding='utf-8') as f:
    d1 = json.load(f)

docs_map = {x['path']: x for x in d1['docs']}
dirs_map = {x['path']: x for x in d1['dirs']}

doc_exts = {'.doc', '.docx', '.pdf', '.xlsx', '.xls', '.odt', '.html', '.htm', '.kml', '.kmz', '.shp', '.gtm', '.qgz', '.csv', '.txt'}
img_exts = {'.jpg', '.jpeg', '.png', '.webp', '.avi', '.mp4'}

# Check inside all non-Guia, non-Backup dirs from d1['dirs'] up to 2 more levels
for dir_entry in list(d1['dirs']):
    dp = dir_entry['path']
    dn = dir_entry['name'].lower()
    if dn.startswith('guia n') or dn == 'backups-usuarios' or dn.endswith('_files'):
        continue
    try:
        img_count = 0
        sample_imgs = []
        for e in os.scandir(dp):
            en = e.name
            enl = en.lower()
            if enl in ('thumbs.db', 'desktop.ini') or en.startswith('~$') or enl.endswith('.tmp') or enl.endswith('_files'):
                continue
            if e.is_file(follow_symlinks=False):
                ext = os.path.splitext(enl)[1]
                if ext in doc_exts and e.path not in docs_map:
                    st = e.stat(follow_symlinks=False)
                    docs_map[e.path] = {
                        'folder_group': dir_entry['rel_path'],
                        'rel_path': os.path.relpath(e.path, base),
                        'path': e.path,
                        'name': en,
                        'ext': ext,
                        'size': st.st_size,
                        'mtime': st.st_mtime
                    }
                elif ext in img_exts:
                    img_count += 1
                    if len(sample_imgs) < 5:
                        sample_imgs.append(en)
            elif e.is_dir(follow_symlinks=False) and not enl.startswith('guia n'):
                # 1 more level
                rel_sub = os.path.relpath(e.path, base)
                dirs_map[e.path] = {
                    'folder_group': dir_entry['rel_path'],
                    'rel_path': rel_sub,
                    'path': e.path,
                    'name': en
                }
                try:
                    sub_imgs = 0
                    for e2 in os.scandir(e.path):
                        en2 = e2.name
                        enl2 = en2.lower()
                        if enl2 in ('thumbs.db', 'desktop.ini') or en2.startswith('~$') or enl2.endswith('.tmp') or enl2.endswith('_files'):
                            continue
                        if e2.is_file(follow_symlinks=False):
                            ext2 = os.path.splitext(enl2)[1]
                            if ext2 in doc_exts and e2.path not in docs_map:
                                st2 = e2.stat(follow_symlinks=False)
                                docs_map[e2.path] = {
                                    'folder_group': rel_sub,
                                    'rel_path': os.path.relpath(e2.path, base),
                                    'path': e2.path,
                                    'name': en2,
                                    'ext': ext2,
                                    'size': st2.st_size,
                                    'mtime': st2.st_mtime
                                }
                            elif ext2 in img_exts:
                                sub_imgs += 1
                    dirs_map[e.path]['img_count'] = sub_imgs
                except Exception:
                    pass
        dir_entry['img_count'] = img_count
        dir_entry['sample_imgs'] = sample_imgs
    except Exception:
        pass

all_docs = list(docs_map.values())
all_dirs = list(dirs_map.values())
print(f"Complete scan in {time.time()-t0:.2f}s: {len(all_dirs)} dirs, {len(all_docs)} docs/files!")

by_ext = {}
for d in all_docs:
    by_ext[d['ext']] = by_ext.get(d['ext'], 0) + 1
print("By ext:", json.dumps(by_ext, indent=2))

out_master = r'C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\ergas_complete_master_index.json'
with open(out_master, 'w', encoding='utf-8') as f:
    json.dump({'dirs': all_dirs, 'docs': all_docs}, f, ensure_ascii=False, indent=2)
print("Saved to", out_master)
