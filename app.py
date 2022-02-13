import sqlite3 as sl
from collections import defaultdict

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import codebook_loader, dta_to_table, load_questions


@st.cache
def initialize(db_path: str, codebook_path: str, dta1_path: str, dta2_path: str):
    """Initialize the tables, etc.

    Args:
        db_path (str): sqlite database location
        codebook_path (str): `2019_CHES_codebook.pdf` location
        dta1_path (str): `CHES2019V3.dta` location
        dta2_path (str): `CHES2019_experts.dta` location

    Returns:
        pd.DataFrame: dataframe corresponding to `CHES2019V3.dta`
        pd.DataFrame: dataframe corresponding to `CHES2019_experts.dta`
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

    df_questions = load_questions()

    return df_v3, df_experts, df_questions


def multiselect_content(
    df: pd.DataFrame,
    select_method: str,
    default_phrase: str,
    optional_phrase: list = [],
    default_multiselect_value: dict or defaultdict = defaultdict(list),
    default_select_all: bool = False,
) -> pd.DataFrame:
    """Select part of the dataframe using streamlit multiselector

    Args:
        df (pd.DataFrame): dataframe to select from
        select_method (str): from {"column", "column_match"}. "column" means column
            names will be used for selection, "column_match" means unique value of
            certain column will be used.
        default_phrase (str): default phrase to describe the object
        optional_phrase (list, optional): optional phrases used to descibe an object,
            e.g. `country` can also be descibed as `country_id`. Defaults to [].
        default_multiselect_value (list, optional): what value to show in the multiselector
            when the app started. Defaults to [].
        default_select_all (bool, optional): Select all options by default. Defaults
            to False.

    Returns:
        pd.DataFrame:
    """

    def _multiselector(multiselect_options: list) -> list:
        """Multiselector with select all checkbox

        Args:
            multiselect_options (list): list of options to select from

        Returns:
            list: list of selected options
        """
        if select_all:
            selected_items = container.multiselect(
                f"Choose {selected_phrase}",
                sorted(multiselect_options),
                sorted(multiselect_options),
            )
        else:
            selected_items = container.multiselect(
                f"Choose {selected_phrase}",
                multiselect_options,
                default_multiselect_value[selected_phrase],
            )

        return selected_items

    if optional_phrase:
        selected_phrase = st.select_slider(
            f"Select your prefered phrase to display the {default_phrase}",
            options=[default_phrase, *optional_phrase],
        )
    else:
        selected_phrase = default_phrase

    container = st.container()
    select_all = st.checkbox(f"Select all {selected_phrase}", value=default_select_all)

    if select_method == "column":
        multiselect_options = list(
            set(df.columns.get_level_values(default_phrase)).difference(
                set(["country", "party"])
            )
        )
        selected_items = _multiselector(multiselect_options)

        return df.loc[:, selected_items], selected_phrase, selected_items

    elif select_method == "column_match":
        multiselect_options = sorted(df[selected_phrase].unique())
        selected_items = _multiselector(multiselect_options)

        return (
            df.loc[df[selected_phrase].isin(selected_items)],
            selected_phrase,
            selected_items,
        )

    else:
        raise Exception(
            f"select_method: {select_method} not recognised./n"
            "Please select from ['column', 'column_match']"
        )


@st.cache
def aggregate(
    df: pd.DataFrame, country_phrase: str, party_phrase: str, dropped_columns: list = []
) -> pd.DataFrame:
    """Aggregate dataframe, group by country and party

    Args:
        df (pd.DataFrame): dataframe to aggregate from
        country_phrase (str): chosen phrase to describe country
        party_phrase (str): chosen phrase to describe party
        dropped_columns (list, optional): redundant columns not to aggregate. Defaults to [].

    Returns:
        pd.DataFrame: aggregated dataframe
                        |    question |
        ________________| aggregation |
        country | party |
    """
    if dropped_columns:
        df = df.drop(columns=set(dropped_columns).difference({country_phrase, party_phrase}))
    grouped = df.groupby([country_phrase, party_phrase])
    df_agg = grouped.aggregate(func=[np.nanmean, np.nanmedian, np.std, np.nanvar])
    df_agg.columns.names = ["question", "aggregation"]

    return df_agg


st.set_page_config(
    page_title="CHES2019 Data Analysis",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        "Get help": "https://github.com/Taiquan-Liu/CHES-data-assignment",
        "Report a Bug": "https://github.com/Taiquan-Liu/CHES-data-assignment/issues",
    },
)

with st.sidebar:

    st.image("data/Europe_blank_map.png")
    st.title("2019 Chapel Hill expert survey - Data analysis")

    st.markdown("---")

    db_path = st.text_input("Database path", "data/ches-data.db")
    codebook_path = st.text_input("Codebook path", "data/2019_CHES_codebook.pdf")
    dta1_path = st.text_input("DTA file 1 path", "data/CHES2019V3.dta")
    dta2_path = st.text_input("DTA file 2 path", "data/CHES2019_experts.dta")

    optional_country_selector = ["country_id", "country_fullname"]
    optional_party_selector = ["party_id", "party_name", "party_name_english"]

    df_v3, df_experts, df_questions = initialize(
        db_path, codebook_path, dta1_path, dta2_path
    )

    st.markdown("---")

    plot_option = st.selectbox(
        "How would you like to plot?",
        ("Country Aggregation on each question", "Detailed survey result (Finland)"),
    )

    if plot_option == "Country Aggregation on each question":
        plot_args = {
            "default_multiselect_value_country": defaultdict(list),
            "default_select_all_countries": True,
            "default_select_all_parties": True,
            "default_select_all_questions": False,
            "detail_level": "less",
        }
    elif plot_option == "Detailed survey result (Finland)":
        plot_args = {
            "default_multiselect_value_country": {
                "country": ["fin"],
                "country_id": [14],
                "country_fullname": ["Finland"],
            },
            "default_select_all_countries": False,
            "default_select_all_parties": True,
            "default_select_all_questions": True,
            "detail_level": "more",
        }

    st.markdown("---")

    df_c, country_phrase, selected_countries = multiselect_content(
        df_experts,
        "column_match",
        "country",
        default_multiselect_value=plot_args["default_multiselect_value_country"],
        default_select_all=plot_args["default_select_all_countries"],
        optional_phrase=optional_country_selector,
    )

    st.markdown("---")

    df_p, party_phrase, selected_parties = multiselect_content(
        df_c,
        "column_match",
        "party",
        default_select_all=plot_args["default_select_all_parties"],
        optional_phrase=optional_party_selector,
    )

    df_agg = aggregate(
        df_p,
        country_phrase,
        party_phrase,
        dropped_columns=[
            "country",
            "party",
            *optional_country_selector,
            *optional_party_selector,
        ],
    )

    st.markdown("---")

    df_q, _, selected_questions = multiselect_content(
        df_agg,
        "column",
        "question",
        default_select_all=plot_args["default_select_all_questions"],
    )

    st.markdown("---")

    button = st.button("Plot!")

if button:
    if plot_args["detail_level"] == "less":
        for q in selected_questions:
            df = df_q.loc[:, q].reset_index()
            df_questions_q = df_questions.loc[q]
            scores = [int(m) for m in df_questions_q.loc["scores"].keys()]
            fig = px.box(
                df,
                y="nanmean",
                x=country_phrase,
                range_y = [scores[0], scores[-1]],
                hover_data=[party_phrase],
                title=q,
                color=country_phrase,
                points="all",
            )
            fig.update_xaxes(type="category", automargin=True)
            fig.update_layout(hoverdistance=5)
            st.plotly_chart(fig)
            st.json(df_questions_q.to_json())

    elif plot_args["detail_level"] == "more":
        for q in selected_questions:
            df = df_p.loc[:, [party_phrase, q]]
            df_questions_q = df_questions.loc[q]
            scores = [int(m) for m in df_questions_q.loc["scores"].keys()]
            fig = px.box(
                df,
                y=q,
                x=party_phrase,
                range_y = [scores[0], scores[-1]],
                hover_data=[q],
                title=q,
                color=party_phrase,
                points="all",
            )
            fig.update_xaxes(type="category", automargin=True)
            fig.update_layout(hoverdistance=5)
            st.plotly_chart(fig)
            st.json(df_questions_q.to_json())

else:
    st.json(df_questions.to_json())
