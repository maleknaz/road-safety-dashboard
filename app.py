from pathlib import Path
import json
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Global Road Safety | Evidence Dashboard",page_icon="🌍",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
[data-testid="stHeader"]{display:none!important}
.block-container,[data-testid="stMainBlockContainer"]{max-width:100%!important;padding:4px 12px 22px!important}
.stTabs [data-baseweb="tab-list"]{gap:6px;flex-wrap:wrap;border-bottom:1px solid #dce8ef;padding:4px 4px 9px}
.stTabs [data-baseweb="tab"]{color:#184a69!important;background:#edf6fa!important;border:1px solid #dce8ef!important;border-radius:7px!important;padding:9px 15px!important;font-size:13px;font-weight:750!important;min-height:44px}
.stTabs [data-baseweb="tab"][aria-selected="true"]{color:#fff!important;background:#0c5e86!important;border-color:#0c5e86!important}
.stTabs [data-baseweb="tab"]:hover{border-color:#09a7d5!important}
@media (prefers-color-scheme:dark){.stTabs [data-baseweb="tab"]{color:#eaf4fa!important;background:#244659!important;border-color:#456b81!important}.stTabs [data-baseweb="tab"][aria-selected="true"]{color:#fff!important;background:#0c749c!important}}
</style>""",unsafe_allow_html=True)

PAGES=[
 ("Start here","Dashboard_Overview.html"),
 ("Atlas","road_safety_atlas.html"),
 ("Taskforces","who_has_task_forces.html"),
 ("Existing documents","Existing_road_safety_documents.html"),
 ("Bodies & strategies","Bodies_Their_Road_Safety_Strategies.html"),
 ("Checklists for your task force","Checklists_for_Your_Task_Force.html"),
 ("Case Studies","Case_Studies.html"),
 ("Download data",None),
]

nav=st.tabs([label for label,_ in PAGES])
for tab,(label,filename) in zip(nav,PAGES):
 with tab:
  if filename:
   p=ROOT/filename
   if not p.is_file(): st.error(f"Missing page: {filename}")
   else:
    # Original standalone HTML and script content is rendered unchanged inside the frame.
    components.html(p.read_text(encoding="utf-8"),height=1080,scrolling=True)
  else:
   st.markdown("### Download reviewed-country research data")
   st.write("These structured datasets underpin the 22-mechanism comparison. Seven countries have detailed source-audited 17-domain and 85-cell files. Other case-level totals are documented in the combined summary but should not be mistaken for fully re-audited cell records.")
   files=[ROOT/'data'/'Reviewed_Cases_2026_Summary.csv',ROOT/'data'/'Reviewed_Cases_2026_Data.json']
   files += sorted((ROOT/'data').glob('*_2026_*Audit.csv'))
   for p in files:
    if not p.is_file(): continue
    st.download_button(label=p.name,data=p.read_bytes(),file_name=p.name,mime='application/json' if p.suffix=='.json' else 'text/csv',key='d_'+p.name,use_container_width=True)
   st.markdown("**How to interpret the research:** F is documented formal representation; P indicates a partner link or a partial task match; A is a specifically documented planned task; N/A means unverified; X indicates an undefined ideal cell. None of these labels independently measures delivered road safety outcomes.")
