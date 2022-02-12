import sqlite3 as sl
import tempfile
import sqlite3 as sl
from pathlib import Path

import pandas as pd
import pytest

from utils import codebook_loader, dta_to_table, load_questions

pytestmark = pytest.mark.unit


def test_tables_from_codebook_joinable_by_country():
    """Test when PARTIES left join COUNTRIES on country, there won't be any extra
    entry in PARTIES
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        con = sl.connect(db_path)
        cl = codebook_loader(con)
        cl.save_parties(if_exists="replace", table_name="PARTIES")
        cl.save_countries(if_exists="replace", table_name="COUNTRIES")

        df_c = pd.read_sql("""
            SELECT *
            FROM COUNTRIES
        """, con, index_col="index")
        df_p = pd.read_sql("""
            SELECT *
            FROM PARTIES
        """, con, index_col="index")

    assert set(df_p["country"].unique()).issubset(df_c["country"].unique())


def test_tables_joinable_by_party_id():
    """Test when V3 and EXPERTS left join LOOKUP on party_id (entries should be
    the same as PARTIES), there won't be any extra entry
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        con = sl.connect(db_path)
        cl = codebook_loader(con)
        cl.save_parties(if_exists="replace", table_name="PARTIES")

        dta_to_table(
            con, "data/CHES2019V3.dta", table_name="V3")
        dta_to_table(
            con,
            "data/CHES2019_experts.dta",
            table_name="EXPERTS"
        )

        df_p = pd.read_sql("""
            SELECT *
            FROM PARTIES
        """, con, index_col="index")
        df_v3 = pd.read_sql("""
            SELECT *
            FROM V3
        """, con, index_col="index")
        df_e = pd.read_sql("""
            SELECT *
            FROM EXPERTS
        """, con, index_col="index")

    assert set(df_v3["party_id"].unique()).issubset(df_p["party_id"].unique())
    assert set(df_e["party_id"].unique()).issubset(df_p["party_id"].unique())


def test_questions_json_joinable():
    """Test when joining questions.json to EXPERTS on questions, there won't be
    any extra entries.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        con = sl.connect(db_path)
        cl = codebook_loader(con)

        dta_to_table(con, "data/CHES2019_experts.dta", table_name="EXPERTS")

        df_e = pd.read_sql(
            """
            SELECT *
            FROM EXPERTS
        """,
            con,
            index_col="index",
        )

        df_q = load_questions()

    df_e = df_e.drop(columns=["party_id", "party", "dob"])
    df_s = pd.DataFrame(df_e.stack())
    df_s = df_s.reset_index()
    df_s = df_s.rename(
        columns={"index": "questionnaire", "level_1": "question", 0: "score"}
    )

    assert set(df_s["question"].unique()).issubset(df_q.index.unique())
