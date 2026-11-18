from pathlib import Path
import json
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Road Safety | Reviewed Countries", page_icon="🌍", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
[data-testid="stHeader"]{display:none}
.block-container,[data-testid="stMainBlockContainer"]{max-width:100%!important;padding:12px 22px 40px!important}
.stTabs [data-baseweb="tab-list"]{gap:5px;flex-wrap:wrap;border-bottom:1px solid #cbdde7}
.stTabs [data-baseweb="tab"]{font-weight:650;color:#24506d!important;background:#edf5f8!important;padding:8px 13px;border-radius:7px 7px 0 0}
.stTabs [data-baseweb="tab"][aria-selected="true"]{color:#005b80!important;background:#dceef5!important;border-bottom:3px solid #079bb5}
[data-testid="stMetricValue"]{color:inherit}
@media(prefers-color-scheme:dark){.stTabs [data-baseweb="tab"]{color:#eaf3fa!important;background:#254759!important}.stTabs [data-baseweb="tab"][aria-selected="true"]{color:white!important;background:#17617e!important}}
</style>""", unsafe_allow_html=True)

stats = json.loads((ROOT / "Reviewed_Cases_2026_Data.json").read_text(encoding="utf-8"))["stats"]
st.title("Road safety governance | Reviewed countries")
st.caption("Evidence-qualified comparison of the mechanisms reviewed through Latvia (November 2026). Not a global audit; published policy responsibilities are not evidence of completed implementation.")
a,b,c,d=st.columns(4)
a.metric("Countries",stats["country_count"])
b.metric("Coordinating mechanisms",stats["case_count"])
c.metric("Documented domain links",f'{stats["domain_numerator"]}/{stats["domain_denominator"]}')
d.metric("Exact planned-action matches",stats["exact"])

PAGES = [
 ("Practice vs Checklist", "Practice_vs_Checklist_Reviewed_2026.html"),
 ("Reviewed Case Assessments", "Reviewed_Case_Assessments_2026.html"),
 ("Correction Log", "Reviewed_Case_Change_Log_2026.html"),
 ("Bodies & Their Strategies", "Bodies_Their_Road_Safety_Strategies_Reviewed_2026.html"),
 ("Download data", None),
]
tabs=st.tabs([name for name,_ in PAGES])
for tab,(name,filename) in zip(tabs,PAGES):
 with tab:
  if filename:
   path=ROOT/filename
   if not path.is_file():
    st.error(f"Missing deployment file: {filename}")
   else:
    components.html(path.read_text(encoding="utf-8"),height=1050,scrolling=True)
  else:
   st.markdown("**Download the underlying reviewed-case data and evidence audits.**")
   downloads=["Reviewed_Cases_2026_Summary.csv","Reviewed_Cases_2026_Change_Log.csv","Reviewed_Cases_2026_Data.json"]
   downloads += sorted(p.name for p in ROOT.glob("*_2026_*.csv") if p.name not in downloads)
   for file in dict.fromkeys(downloads):
    p=ROOT/file
    if p.is_file():
     st.download_button(file, data=p.read_bytes(),file_name=file,mime="application/json" if file.endswith(".json") else "text/csv",key="download_"+file,use_container_width=True)
   st.info("Detailed source-reviewed intervention audits are available for Croatia, Cyprus, Estonia, France, Japan, Jordan and Latvia. For other reviewed mechanisms the earlier evidence-qualified summaries are retained; a fully recoded cell-level audit is not claimed.")
   st.markdown("**How to interpret the codes:** F = formal membership or statutory link; P = relevant documented functional partner; A = exact documented planned responsibility; N/A = not verified; X = undefined ideal cell. The 72 scored interventions exclude 13 undefined cells per mechanism.")
