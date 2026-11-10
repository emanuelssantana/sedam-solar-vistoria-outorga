import json
import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

SCRATCH = Path(r"C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch")
IDX = json.loads((SCRATCH / "ergas_complete_master_index.json").read_text(encoding="utf-8"))

# 1. Convert Lino Duque's newly found 2026 & 2023 photos to WebP (both in local folder and GitHub repo assets)
webp_dir = Path(r"G:\Meu Drive\IDEs_Agents_26\SEDAM\-DAK_VertexAI_CRM_ERP-rede-sedam\02_PILOTO_PRODUTOR_01_COMPLETO\midia_webp")
webp_dir.mkdir(parents=True, exist_ok=True)

gh_webp_dir = SCRATCH / "sedam-solar-vistoria-outorga" / "midia_webp"
gh_webp_dir.mkdir(parents=True, exist_ok=True)

# Copy existing WebPs to gh_webp_dir too
for existing_webp in webp_dir.glob("*.webp"):
    dst_gh = gh_webp_dir / existing_webp.name
    if not dst_gh.exists():
        dst_gh.write_bytes(existing_webp.read_bytes())

lino_new_photos = [
    (r"M:\ERGAS\Alta Floresta\FRANCISCO\FOTOS 2025-2026\VISTORIA LINO DUQUE AFO 03.02.2026\TimePhoto_20260203_103737.jpg", "2026_02_03_TimePhoto_103737_Lino_Duque_Outorga_Piscicultura.webp"),
    (r"M:\ERGAS\Alta Floresta\FRANCISCO\FOTOS 2025-2026\VISTORIA LINO DUQUE AFO 03.02.2026\TimePhoto_20260203_105514.jpg", "2026_02_03_TimePhoto_105514_Lino_Duque_Tanques_Carimbada.webp"),
    (r"M:\ERGAS\Alta Floresta\FRANCISCO\FOTOS 2025-2026\VISTORIA LINO DUQUE AFO 03.02.2026\DSC01105.JPG", "2026_02_03_DSC01105_Vistoria_Lino_Duque.webp"),
    (r"M:\ERGAS\Alta Floresta\FRANCISCO\FOTOS 2025-2026\PONTO DE CAPTAÇÃO D' ÁGUA E DIVISA LINO DUQUE AFO 24.02.2026\DSC01439.JPG", "2026_02_24_DSC01439_Captacao_Divisa_Cafe_Lino_Duque.webp"),
    (r"M:\ERGAS\Alta Floresta\FRANCISCO\FOTOS 2025-2026\PONTO DE CAPTAÇÃO D' ÁGUA E DIVISA LINO DUQUE AFO 24.02.2026\DSC01450.JPG", "2026_02_24_DSC01450_Captacao_Divisa_Cafe_Lino_Duque.webp"),
    (r"M:\ERGAS\Alta Floresta\FRANCISCO\ANTIGOS\REPRESA LINO DUQUE AFO 05.04.2023\DSC03981.JPG", "2023_04_05_DSC03981_Represa_Barragem_Lino_Duque.webp"),
]

converted = []
for src, dst_name in lino_new_photos:
    if os.path.exists(src):
        try:
            img = Image.open(src)
            img.thumbnail((1280, 1280))
            dst = webp_dir / dst_name
            img.save(dst, "WEBP", quality=78)
            img.save(gh_webp_dir / dst_name, "WEBP", quality=78)
            converted.append(dst_name)
        except Exception as e:
            print(f"WebP err {src}: {e}")
print(f"Converted {len(converted)} new 2026/2023 photos to WebP: {converted}")

# 2. Extract all .xlsx files from M:\ERGAS\Alta Floresta
def read_xlsx_fast(full_path):
    rows_out = []
    try:
        with zipfile.ZipFile(full_path) as z:
            shared = []
            if "xl/sharedStrings.xml" in z.namelist():
                tree = ET.fromstring(z.read("xl/sharedStrings.xml"))
                for si in tree.iter():
                    if si.tag.endswith("}si"):
                        texts = [t.text for t in si.iter() if t.tag.endswith("}t") and t.text]
                        shared.append("".join(texts))
            sheet_files = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
            for sf in sorted(sheet_files):
                stree = ET.fromstring(z.read(sf))
                for row in stree.iter():
                    if row.tag.endswith("}row"):
                        vals = []
                        for c in row:
                            if c.tag.endswith("}c"):
                                ctype = c.attrib.get("t", "")
                                v_text = ""
                                for sub in c.iter():
                                    if sub.tag.endswith("}v") and sub.text:
                                        v_text = sub.text
                                    elif sub.tag.endswith("}t") and sub.text:
                                        v_text += sub.text
                                if ctype == "s" and v_text.isdigit():
                                    idx = int(v_text)
                                    if 0 <= idx < len(shared):
                                        v_text = shared[idx]
                                if v_text.strip():
                                    vals.append(v_text.strip())
                        if vals:
                            rows_out.append(" | ".join(vals))
    except Exception as e:
        rows_out.append(f"[ERR: {e}]")
    return rows_out

xlsx_docs = [d for d in IDX["docs"] if d["ext"].lower() == ".xlsx"]
xlsx_extracted = []
for d in xlsx_docs:
    rel = d["rel_path"]
    full = os.path.join(r"M:\ERGAS\Alta Floresta", rel)
    rows = read_xlsx_fast(full)
    xlsx_extracted.append({
        "rel_path": rel,
        "mtime": d["mtime"],
        "row_count": len(rows),
        "rows": rows[:500]
    })

(SCRATCH / "ergas_all_xlsx_extracted.json").write_text(
    json.dumps(xlsx_extracted, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"Extracted {len(xlsx_extracted)} .xlsx spreadsheets!")
