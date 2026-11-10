import os
import shutil

repo_dir = r"C:\Users\Usuario\.gemini\antigravity\brain\e37401e3-17fb-431d-bca7-5612ec183a18\scratch\sedam-solar-vistoria-outorga"
p = os.path.join(repo_dir, "index.html")

with open(p, "r", encoding="utf-8") as f:
    c = f.read()

target = '<div class="secao-titulo">No escritório</div>'
addition = '''<div class="secao-titulo">No escritório</div>

    <a class="menu-item" href="CRM_ERP_GLOBAL_SEDAM.html" style="border: 2px solid #10b981; background: #f0fdf4;">
      <div class="menu-icone" style="background:#059669">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
      </div>
      <div class="menu-texto">
        <b style="color:#065f46">CRM/ERP Global &amp; Piloto #01 Lino Duque</b>
        <span>Catálogo 2026–2012 (2.377 produtores), Dossiê 100%, RTs, DAK BigQuery e Vertex AI</span>
      </div>
    </a>'''

if target in c and "CRM_ERP_GLOBAL_SEDAM.html" not in c:
    c = c.replace(target, addition, 1)
    with open(p, "w", encoding="utf-8") as f:
        f.write(c)
    print("Updated index.html successfully")
else:
    print("Target not found or already added")

# Also mirror files to G:\Meu Drive\IDEs_Agents_26\SEDAM\-DAK_VertexAI_CRM_ERP-rede-sedam\07_GITHUB_PAGES_E_APPS_SCRIPT
mirror_dir = r"G:\Meu Drive\IDEs_Agents_26\SEDAM\-DAK_VertexAI_CRM_ERP-rede-sedam\07_GITHUB_PAGES_E_APPS_SCRIPT"
os.makedirs(mirror_dir, exist_ok=True)
for fname in ["index.html", "CRM_ERP_GLOBAL_SEDAM.html"]:
    src = os.path.join(repo_dir, fname)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(mirror_dir, fname))

# Also mirror to G:\Meu Drive\IDEs_Agents_26\SEDAM\SOLAR\modelo de ortoga a preencher em campo\publicar_github_pages
solar_mirror = r"G:\Meu Drive\IDEs_Agents_26\SEDAM\SOLAR\modelo de ortoga a preencher em campo\publicar_github_pages"
if os.path.exists(solar_mirror):
    for fname in ["index.html", "CRM_ERP_GLOBAL_SEDAM.html"]:
        src = os.path.join(repo_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(solar_mirror, fname))
print("Mirrored updated HTMLs to Google Drive locations!")
