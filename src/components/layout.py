import streamlit as st


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1320px;
        }

        h1, h2, h3 {
            letter-spacing: 0;
        }

        h1 {
            font-size: 2.35rem;
            line-height: 1.12;
            margin-bottom: 0.25rem;
        }

        h2, h3 {
            margin-top: 1.25rem;
        }

        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.18);
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 8px;
            padding: 0.85rem 0.95rem;
            background: linear-gradient(180deg, rgba(128, 128, 128, 0.08), rgba(128, 128, 128, 0.035));
            min-height: 92px;
        }

        div[data-testid="stInfo"], div[data-testid="stWarning"], div[data-testid="stError"] {
            border-radius: 8px;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 8px;
        }

        .legis-hero {
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 8px;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
            background: rgba(128, 128, 128, 0.045);
        }

        .legis-eyebrow {
            color: #5EA1FF;
            font-weight: 700;
            font-size: 0.85rem;
            margin-bottom: 0.35rem;
        }

        .legis-subtitle {
            max-width: 920px;
            color: rgba(250, 250, 250, 0.82);
            font-size: 1.02rem;
            line-height: 1.55;
            margin: 0;
        }

        .legis-sidebar-title {
            font-size: 1.2rem;
            font-weight: 800;
            margin-bottom: 0.15rem;
        }

        .legis-sidebar-caption {
            color: rgba(250, 250, 250, 0.62);
            font-size: 0.86rem;
            line-height: 1.35;
            margin-bottom: 0.75rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(title: str, text: str) -> None:
    st.subheader(title)
    st.caption(text)
