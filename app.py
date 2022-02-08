import altair as alt
import inflect
import pandas as pd
import streamlit as st

df_v3 = pd.read_stata("data/CHES2019V3.dta")
df_e = pd.read_stata("data/CHES2019_experts.dta")

p = inflect.engine()


def select_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    container = st.container()
    select_all = st.checkbox(f"Select all {p.plural(column_name)}")
    # TODO: Add option to select from ID and (maybe) full name
    if select_all:
        parties = container.multiselect(
            f"Choose {p.plural(column_name)}",
            sorted(df[column_name].unique()),
            sorted(df[column_name].unique()),
        )
    else:
        parties = container.multiselect(
            f"Choose {p.plural(column_name)}", sorted(df[column_name].unique()), []
        )

    return df.loc[df[column_name].isin(parties)]


df_v3_c = select_column(df_v3, "country")
df_v3_p = select_column(df_v3_c, "party")

if st.checkbox("Show dataframe"):
    st.dataframe(df_v3_p)


stripplot = (
    alt.Chart(df_v3_p)
    .mark_circle()
    .encode(
        x="party:O",
        y="eu_position:Q",
        color="party_id",
    )
)

st.altair_chart(stripplot, use_container_width=True)
