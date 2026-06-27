import streamlit as st


def render_help_box(title: str, text: str) -> None:
    st.info(f"**{title}**\n\n{text}")


def render_query_explanation(explanation: dict[str, str]) -> None:
    with st.expander("Como interpretar esta seção?"):
        st.markdown(f"**O que esta consulta mostra?** {explanation['mostra']}")
        st.markdown(f"**Por que isso é útil?** {explanation['utilidade']}")
        st.markdown(f"**Como interpretar?** {explanation['interpretacao']}")
