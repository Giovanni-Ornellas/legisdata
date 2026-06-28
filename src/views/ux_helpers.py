import pandas as pd


def build_proposicao_options(df: pd.DataFrame) -> dict[int, str]:
    return {
        int(row.proposicao_id): f"{row.proposicao} · {str(row.ementa)[:110]}"
        for row in df.itertuples()
    }
