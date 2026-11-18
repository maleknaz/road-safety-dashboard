# Global Road Safety Atlas, consolidated November 2026.
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import csv, json, io

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
st.set_page_config(page_title="Global Road Safety | Governance Atlas",page_icon="🚦",layout="wide",initial_sidebar_state="collapsed")
st.markdown('''<style>
:root {color-scheme:light}
html,body{margin:0!important}
header[data-testid="stHeader"]{height:0!important;visibility:hidden!important}
#MainMenu,footer[data-testid="stFooter"],div[data-testid="stDecoration"]{display:none!important}
section.main>div.block-container,[data-testid="stMainBlockContainer"]{max-width:none!important;padding:0 0 25px!important;margin:0!important}
[data-testid="stAppViewContainer"]{background:#f3f8fb!important}
[data-testid="stTabs"]{margin:0!important}
/* High contrast for BOTH old and new Streamlit tab markup; never inherit white-on-white theme */
[data-testid="stTabs"] :is([data-baseweb="tab-list"],[role="tablist"]){display:flex!important;gap:6px!important;background:#0e2b48!important;padding:11px 16px!important;flex-wrap:wrap!important;border-bottom:3px solid #09a7d5!important;min-height:64px!important}
[data-testid="stTabs"] :is(button[data-baseweb="tab"],button[role="tab"],[role="tablist"]>[role="tab"]){box-sizing:border-box!important;min-height:42px!important;font-family:"Segoe UI",Arial,sans-serif!important;font-size:13px!important;line-height:1.25!important;font-weight:750!important;border-radius:6px!important;padding:10px 14px!important;white-space:normal!important;background-color:#23516f!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;border:1px solid #7cabc4!important;opacity:1!important;box-shadow:none!important;text-shadow:none!important}
[data-testid="stTabs"] :is(button[data-baseweb="tab"],button[role="tab"]) :is(p,span,div,strong){color:#fff!important;-webkit-text-fill-color:#fff!important;font-size:13px!important;opacity:1!important}
[data-testid="stTabs"] :is(button[data-baseweb="tab"],button[role="tab"]):is([aria-selected="true"],[data-selected="true"]){background:#fff!important;color:#0e2b48!important;-webkit-text-fill-color:#0e2b48!important;border:2px solid #09a7d5!important}
[data-testid="stTabs"] :is(button[data-baseweb="tab"],button[role="tab"]):is([aria-selected="true"],[data-selected="true"]) :is(p,span,div,strong){color:#0e2b48!important;-webkit-text-fill-color:#0e2b48!important}
[data-testid="stTabs"] :is(button[data-baseweb="tab"],button[role="tab"]):hover:not([aria-selected="true"]){background:#30769a!important}
[data-testid="stTabs"] :is(button[data-baseweb="tab"],button[role="tab"]):focus-visible{outline:3px solid #f0c766!important;outline-offset:1px!important}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:#09a7d5!important}
[data-testid="stTabs"] [role="tabpanel"]{padding:0!important}
div[data-testid="stVerticalBlock"]{gap:0}
iframe{border:0!important}
</style>''',unsafe_allow_html=True)

def page(filename,height=1550):
    path=ROOT/filename
    if not path.exists():
        st.error(f"Missing required dashboard page: {filename}")
        return
    components.html(path.read_text(encoding="utf-8"),height=height,scrolling=True)

tabs=st.tabs(["Start here","Atlas","Taskforces","Existing documents","Bodies & strategies","Checklists for your taskforce","Country case studies","Download data"])
with tabs[0]:page('Dashboard_Overview.html',1050)
with tabs[1]:page('road_safety_atlas.html',1550)
with tabs[2]:page('who_has_task_forces.html',1550)
with tabs[3]:page('Existing_road_safety_documents.html',1550)
with tabs[4]:page('Bodies_Their_Road_Safety_Strategies.html',1550)
with tabs[5]:page('Checklists_for_Your_Task_Force.html',1700)
with tabs[6]:page('Case_Studies.html',1800)
with tabs[7]:
    st.markdown('''<div style="padding:30px 32px 10px;background:#10334b;color:white"><h1 style="margin:0;color:white">Download the evidence</h1><p style="color:#d4e8f5">The 195-country data, 27-mechanism comparative mapping and quality-control records are available separately. Provisional and reviewed assignments are labelled explicitly.</p></div>''',unsafe_allow_html=True)
    files=[("Country Master (195)","Country_Master_195.csv"),("Global entity directory (290)","Global_Taskforce_Directory_290.csv"),("Attributed institutional documents","Global_Bodies_and_Attributed_Documents.csv"),("Global document catalogue","Global_Document_Catalogue.csv"),("27-case evidence register","Country_Mechanism_Review_Status.csv"),("17-domain membership matrix","Institutional_17_Domains_27_Mechanisms.csv"),("85-cell mapping (including 13 X)","Interventions_85_Cells_27_Mechanisms.csv"),("Ideal 85-cell framework","Ideal_Framework_85_Cells.csv"),("Outstanding evidence review queue","Evidence_Review_Queue.csv")]
    left,right=st.columns(2,gap="large")
    for i,(label,name) in enumerate(files):
        col=left if i%2==0 else right
        with col:
            st.download_button(label, (DATA/name).read_bytes(),file_name=name,mime='text/csv',key=name,use_container_width=True)
    st.markdown('''<div style="padding:12px 30px;color:#3b5970"><b>Review protocol:</b> F = formal representation, P = documented functional involvement, N/A = insufficient evidence. Action-level A and P are documented planned matches, not demonstrated delivery. The 13 X cells are undefined in the ideal framework. Existing earlier summary metrics are not recalculated using provisional example matches.</div>''',unsafe_allow_html=True)
