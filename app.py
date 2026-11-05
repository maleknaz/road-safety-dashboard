from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Global Road Safety Atlas",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

html_path = Path(__file__).parent / "road_safety_atlas.html"

if not html_path.is_file():
    st.error(
        "Cannot find road_safety_atlas.html. "
        "Put it in the same folder as app.py."
    )
    st.stop()

components.html(
    html_path.read_text(encoding="utf-8"),
    height=1100,
    scrolling=True,
)