import streamlit as st


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }

        h1, h2, h3 {
            letter-spacing: 0;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
            background: rgba(128, 128, 128, 0.06);
        }

        div[data-testid="stInfo"], div[data-testid="stWarning"], div[data-testid="stError"] {
            border-radius: 8px;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(title: str, text: str) -> None:
    st.subheader(title)
    st.caption(text)
