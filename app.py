"""Global Road Safety dashboard, consolidated static HTML and research datasets."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="Global Road Safety Atlas",page_icon="🚦",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
header[data-testid="stHeader"]{height:0!important;visibility:hidden!important}
#MainMenu,footer[data-testid="stFooter"],[data-testid="stDecoration"]{display:none!important}
[data-testid="stMainBlockContainer"],section.main>div.block-container{max-width:none!important;padding:0!important}
[data-testid="stAppViewContainer"]{background:#f3f8fb!important}
[data-testid="stTabs"] [role="tablist"]{background:#0e2b48!important;padding:12px!important;gap:6px!important;flex-wrap:wrap!important;border-bottom:3px solid #09a7d5!important}
[data-testid="stTabs"] [role="tab"]{background:#21516f!important;color:#fff!important;-webkit-text-fill-color:#fff!important;border:1px solid #85aec3!important;border-radius:6px!important;padding:10px 14px!important;min-height:42px!important;font-size:13px!important;font-weight:750!important;opacity:1!important;white-space:normal!important}
[data-testid="stTabs"] [role="tab"] *{color:#fff!important;-webkit-text-fill-color:#fff!important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:#fff!important;color:#0e2b48!important;-webkit-text-fill-color:#0e2b48!important;border:2px solid #09a7d5!important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] *{color:#0e2b48!important;-webkit-text-fill-color:#0e2b48!important}
[data-testid="stTabs"] [role="tab"]:focus-visible{outline:3px solid #f0c766!important}
[data-testid="stTabs"] [role="tabpanel"]{padding:0!important}
iframe{border:0!important}
</style>""",unsafe_allow_html=True)

def show(filename,height=1550):
    path=ROOT/filename
    if not path.is_file():st.error(f"Missing: {filename}");return
    components.html(path.read_text(encoding="utf-8"),height=height,scrolling=True)

# The checklist is the final tab. Research datasets are not exposed for download.
labels=[
    "Start here",
    "Atlas",
    "Taskforces",
    "Existing documents",
    "Bodies & strategies",
    "Country case studies",
    "Checklists for your taskforce",
]
files=[
    "Dashboard_Overview.html",
    "road_safety_atlas.html",
    "who_has_task_forces.html",
    "Existing_road_safety_documents.html",
    "Bodies_Their_Road_Safety_Strategies.html",
    "Case_Studies.html",
    "Checklists_for_Your_Task_Force.html",
]

tabs=st.tabs(labels)
for label, filename, tab in zip(labels, files, tabs):
    with tab:
        show(filename, 1500 if filename in ("Dashboard_Overview.html", "Checklists_for_Your_Task_Force.html") else 2000)
