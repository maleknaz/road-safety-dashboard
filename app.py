from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Global Road Safety Atlas",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Remove the surrounding Streamlit space and fill the browser window.
st.markdown(
    """
    <style>
    html, body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #F5F9FC;
    }

    [data-testid="stHeader"] {
        display: none;
    }

    .block-container,
    [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    [data-testid="stMain"] {
        overflow: hidden;
    }

    iframe {
        display: block;
        width: 100% !important;
        height: 100vh !important;
        height: 100dvh !important;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

html_path = Path(__file__).parent / "road_safety_atlas.html"

if not html_path.is_file():
    st.error("Put road_safety_atlas.html in the same folder as app.py.")
    st.stop()

atlas_html = html_path.read_text(encoding="utf-8")

# Handle internal links by scrolling, without navigating or reloading.
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
    if (!target) return;

    target.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
});
</script>
"""

if "</body>" in atlas_html:
    atlas_html = atlas_html.replace(
        "</body>",
        navigation_fix + "</body>",
        1,
    )
else:
    atlas_html += navigation_fix

components.html(
    atlas_html,
    height=1000,
    scrolling=True,
)