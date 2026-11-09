from pathlib import Path
import re

import streamlit as st
import streamlit.components.v1 as components


# Configure the app.
st.set_page_config(
    page_title="Global Road Safety",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Style the top navigation to match the four HTML pages.
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

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #dce8ef;
    }

    .stTabs [data-baseweb="tab"] {
        color: #52677a;
        font-weight: 700;
        padding: 10px 18px;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #066b9c;
        border-bottom-color: #09a7d5;
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

# Each tab prefers the latest two-tone design, if present.
# Original filenames remain supported for existing deployments.
pages = [
    (
        "Atlas",
        ("road_safety_atlas_two_tone.html", "road_safety_atlas.html"),
    ),
    (
        "Task forces around the Globe",
        ("who has task forces_V1.html", "who has task forces.html"),
    ),
    (
        "Largest Initiatives",
        (
            "road_safety_case_studies_two_tone.html",
            "road_safety_case_studies.html",
        ),
    ),
    (
        "Policies, Strategies, and Plans Around the Globe",
        ("Existing docs.html",),
    ),
]

project_folder = Path(__file__).resolve().parent

# Make in-page anchor links scroll within the HTML document.
navigation_fix = """
<script>
document.addEventListener("click", function(event) {
    if (!(event.target instanceof Element)) return;

    const link = event.target.closest("a[href^='#']");
    if (!link) return;

    const href = link.getAttribute("href");
    if (!href || href === "#") return;

    let targetId;
    try {
        targetId = decodeURIComponent(href.slice(1));
    } catch {
        return;
    }

    const target = document.getElementById(targetId);
    if (target) {
        event.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
});
</script>
"""

# Tabs are displayed in the same order as the pages list above.
tabs = st.tabs([label for label, _ in pages])

for tab, (label, candidate_filenames) in zip(tabs, pages):
    with tab:
        html_path = next(
            (
                project_folder / filename
                for filename in candidate_filenames
                if (project_folder / filename).is_file()
            ),
            None,
        )

        if html_path is None:
            st.error(
                f"Cannot find the HTML for the {label} tab. "
                f"Place one of these files beside app.py: "
                + ", ".join(candidate_filenames)
            )
            continue

        html_content = html_path.read_text(encoding="utf-8")

        # Inject the navigation helper without modifying the stored HTML file.
        if re.search(r"</body\s*>", html_content, flags=re.IGNORECASE):
            html_content = re.sub(
                r"</body\s*>",
                lambda match: navigation_fix + "\n" + match.group(0),
                html_content,
                count=1,
                flags=re.IGNORECASE,
            )
        else:
            html_content += navigation_fix

        components.html(html_content, height=1000, scrolling=True)
