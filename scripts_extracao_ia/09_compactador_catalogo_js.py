import os
import json

repo_dir = r"C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\sedam-solar-vistoria-outorga"
json_path = os.path.join(repo_dir, "dados/catalogo_2026_2012.json")
js_path = os.path.join(repo_dir, "dados/catalogo_2026_2012.js")

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Compact JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

# Compact JS
with open(js_path, "w", encoding="utf-8") as f:
    f.write("window.AGROPRIME_CATALOGO_2026_2012=" + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ";")

print("Compacted JSON:", os.path.getsize(json_path), "bytes")
print("Compacted JS:  ", os.path.getsize(js_path), "bytes")
