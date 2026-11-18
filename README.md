# Global Road Safety dashboard, full deployment bundle

## Deployment
Unzip at the **root of the GitHub repository** for the existing Streamlit app, preserving `data/` and `.streamlit/`. Overwrite `app.py` and matching HTML files. Set Streamlit Community Cloud's main file to `app.py`. No manual integration script is needed.

## Contents
- `app.py`, `requirements.txt`, `.streamlit/config.toml`
- Seven self-contained HTML dashboard pages (overview, atlas, taskforces, existing documents, bodies and strategies, ideal checklist and country audit case studies)
- `data/` contains complete 85-cell ideal framework, official-source findings, 1,700 audit cells, audit status and correction-review queue.

## Evidence limitations (read before publication)
The **Country Case Studies** tab displays the latest 20-mechanism official-source re-evaluation, with 36 specifically documented matches. It is not a complete 72-cell re-audit of all 20 mechanisms. Seven earlier detailed audits (Croatia, Cyprus, Estonia, France, Japan, Jordan, Latvia) are **not re-created** because their exact previous detailed records were unavailable as an editable local file. The latest original 27-mechanism Case_Studies.html was not available for safe merger; no data is invented to fill that gap. Retain a backup of your GitHub repo version if it includes those detailed reviews. To preserve them precisely, merge against that original file when it is available.

Global HTML directories are the source copies supplied in this session and have not been fully re-audited during this packaging step. Their content is not silently modified to match selected new country findings. The source comparison queue identifies targeted updates needed. Standard header typography and contrast styles were added without modifying embedded country datasets or page scripts. Some older source pages have their own layout elements and can still be visually different from the case audit.

## Source basis
Atlas, taskforces, document directory and bodies/strategies directories were uploaded with this project session. The ideal intervention schema comes from the 85-cell supplied workbook (recorded also in `data/Framework_Source_85_Cells.json`). Country audit evidence and source links come from `Road_Safety_Country_Evidence_Reevaluation_2026` produced November 18, 2026.

Seven previously reviewed countries are listed in the Case Studies tab with their confirmed institution/document attribution links, while their earlier source-level intervention codes remain explicitly unavailable. `data/Prior_Seven_Country_Directory_Evidence.json` contains these 7 directory crosslinks.
