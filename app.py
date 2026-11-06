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