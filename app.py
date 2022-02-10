import sqlite3 as sl

import altair as alt
import pandas as pd
import streamlit as st

from utils import codebook_loader, dta_to_table


@st.cache
def initialize(db_path, codebook_path, dta1_path, dta2_path):
    """Save to the SQL database and join tables. This will run initially and then only run if
    input arguments are changed.
    """
    # Save the tables
    con = sl.connect(db_path)
    cl = codebook_loader(con, codebook_path=codebook_path, skip_write_if_exist=False)
    cl.save_parties(if_exists="replace", table_name="PARTIES")
    cl.save_countries(if_exists="replace", table_name="COUNTRIES")
    dta_to_table(
        con, dta1_path, table_name="V3", skip_write_if_exist=False, if_exists="replace"
    )
    dta_to_table(
        con,
        dta2_path,
        table_name="EXPERTS",
        skip_write_if_exist=False,
        if_exists="replace",
    )

    # Join the tables to have more filtering info
    pd.read_sql(
        """
        SELECT p.*, c.country_id, c.country_fullname
        FROM PARTIES p
        LEFT JOIN COUNTRIES c ON p.country = c.country
        """,
        con,
        index_col="index",
    ).to_sql("LOOKUP", con, if_exists="replace")

    df_v3 = pd.read_sql(
        """
        SELECT v.*, l.party_name, l.party_name_english, l.country_id, l.country_fullname
        FROM V3 v
        LEFT JOIN LOOKUP l on v.party_id = l.party_id
    """,
        con,
        index_col="index",
    )

    df_experts = pd.read_sql(
        """
        SELECT e.*, l.country, l.party_name, l.party_name_english, l.country_id, l.country_fullname
        FROM EXPERTS e
        LEFT JOIN LOOKUP l on e.party_id = l.party_id
    """,
        con,
        index_col="index",
    )

    return df_v3, df_experts


def select_column(
    df: pd.DataFrame,
    default_column: str,
    optional_selector: list = [],
) -> pd.DataFrame:

    selected_colomn = st.select_slider(
        f"Select your prefered way to display the {default_column}",
        options=[default_column, *optional_selector],
    )

    container = st.container()
    select_all = st.checkbox(f"Select all {selected_colomn}")

    if select_all:
        selected = container.multiselect(
            f"Choose {selected_colomn}",
            sorted(df[selected_colomn].unique()),
            sorted(df[selected_colomn].unique()),
        )
    else:
        selected = container.multiselect(
            f"Choose {selected_colomn}", sorted(df[selected_colomn].unique()), []
        )

    return df.loc[df[selected_colomn].isin(selected)]


db_path = st.text_input("Database path", "data/ches-data.db")
codebook_path = st.text_input("Codebook path", "data/2019_CHES_codebook.pdf")
dta1_path = st.text_input("DTA file 1 path", "data/CHES2019V3.dta")
dta2_path = st.text_input("DTA file 2 path", "data/CHES2019_experts.dta")

df_v3, df_experts = initialize(db_path, codebook_path, dta1_path, dta2_path)

df_v3_c = select_column(
    df_v3, "country", optional_selector=["country_id", "country_fullname"]
)
df_v3_p = select_column(
    df_v3_c, "party", optional_selector=["party_id", "party_name", "party_name_english"]
)

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
