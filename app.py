from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Global Road Safety",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Page appearance.
st.markdown(
    """
    <style>
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #F5F9FC;
        color: #193B52;
    }

    [data-testid="stHeader"] {
        display: none;
    }

    .block-container,
    [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        padding: 12px 16px 0 !important;
    }

    iframe {
        display: block;
        width: 100% !important;
        height: calc(100vh - 100px) !important;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Readers select which document to view.
selected_page = st.radio(
    "Choose a view",
    ["Global atlas", "Detailed case studies"],
    horizontal=True,
    label_visibility="collapsed",
)

pages = {
    "Global atlas": "road_safety_atlas.html",
    "Detailed case studies": "road_safety_case_studies.html",
}

html_path = Path(__file__).parent / pages[selected_page]

if not html_path.is_file():
    st.error(f"Missing file: {html_path.name}")
    st.stop()

html_content = html_path.read_text(encoding="utf-8")

# Keep internal navigation inside the displayed document.
navigation_fix = """
<script>
document.addEventListener("click", function(event) {
    const link = event.target.closest("a[href^='#']");
    if (!link) return;

    const href = link.getAttribute("href");
    if (!href || href === "#") return;

    event.preventDefault();

    let targetId;

    try {
        targetId = decodeURIComponent(href.slice(1));
    } catch {
        return;
    }

    const target = document.getElementById(targetId);

    if (target) {
        target.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
});
</script>
"""

if "</body>" in html_content:
    html_content = html_content.replace(
        "</body>",
        navigation_fix + "</body>",
        1,
    )
else:
    html_content += navigation_fix

components.html(
    html_content,
    height=1000,
    scrolling=True,
)