import os
import shutil

repo_dir = r"C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\sedam-solar-vistoria-outorga"

targets = [
    r"G:\Meu Drive\IDEs_Agents_26\SEDAM\-DAK_VertexAI_CRM_ERP-rede-sedam\07_GITHUB_PAGES_E_APPS_SCRIPT",
    r"G:\Meu Drive\IDEs_Agents_26\SEDAM\SOLAR\modelo de ortoga a preencher em campo\publicar_github_pages"
]

files_to_mirror = [
    "CRM_ERP_GLOBAL_SEDAM.html",
    "index.html",
    "APPS_SCRIPT_CRM_ERP_BACKEND.gs",
    "dados/catalogo_2026_2012.js",
    "dados/catalogo_2026_2012.json",
    "dados/dossie_lino_duque.js",
    "dados/dossie_lino_duque.json"
]

for t in targets:
    if os.path.exists(t):
        os.makedirs(os.path.join(t, "dados"), exist_ok=True)
        for f in files_to_mirror:
            src = os.path.join(repo_dir, f)
            dst = os.path.join(t, f)
            if os.path.exists(src):
                shutil.copy2(src, dst)
        print(f"Successfully mirrored files to {t}")
    else:
        print(f"Target directory {t} does not exist!")
