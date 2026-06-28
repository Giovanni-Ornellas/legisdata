import streamlit as st


def select_table_limit(label: str = "Linhas exibidas", default: int = 50, maximum: int = 500) -> int:
    return st.slider(label, min_value=10, max_value=maximum, value=default, step=10)


def select_top_n(label: str = "Quantidade no ranking", default: int = 10, maximum: int = 50) -> int:
    return st.slider(label, min_value=5, max_value=maximum, value=default, step=5)
