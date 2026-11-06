from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


# Configure the app.
st.set_page_config(
    page_title="Global Road Safety",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# Adjust spacing only.
# Streamlit's theme controls navigation text and background colors.
st.markdown(
    """
    <style>
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
        height: calc(100vh - 115px) !important;
        min-height: 400px;
        border: none;
        background: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Navigation between the two HTML documents.
pages = {
    "Global atlas": "road_safety_atlas.html",
    "Detailed case studies": "road_safety_case_studies.html",
}

selected_page = st.radio(
    "Choose a view",
    options=list(pages),
    horizontal=True,
    label_visibility="collapsed",
)


# Locate and read the selected document.
project_folder = Path(__file__).resolve().parent
html_path = project_folder / pages[selected_page]

if not html_path.is_file():
    st.error(
        f"Cannot find {html_path.name}. "
        "Put it in the same folder as app.py."
    )
    st.stop()

html_content = html_path.read_text(encoding="utf-8")


# Make internal links scroll within the HTML document.
navigation_fix = """
<script>
document.addEventListener("click", function(event) {
    if (!(event.target instanceof Element)) return;

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
        navigation_fix + "\n</body>",
        1,
    )
else:
    html_content += navigation_fix


# Display the selected document.
components.html(
    html_content,
    height=1000,
    scrolling=True,
)