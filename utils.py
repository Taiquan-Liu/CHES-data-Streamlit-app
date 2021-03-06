import sqlite3 as sl
from pathlib import Path

import pandas as pd
import tabula


class codebook_loader:
    """Load data from the code book.

    Args:
        sql_con (sl.Connection): SQL connection to a database
        codebook_path (str, optional): folder for codebook, default
            "data/2019_CHES_codebook.pdf"
        skip_write_if_exist (bool, optional): default True = skip write if table
            exists in the db

    """

    def __init__(
        self,
        sql_con: sl.Connection,
        codebook_path: str = "data/2019_CHES_codebook.pdf",
        skip_write_if_exist: bool = True,
    ):
        self.sql_con = sql_con
        self.codebook_path = Path(codebook_path).absolute()
        self.skip_write_if_exist = skip_write_if_exist

    def save_countries(self, table_name: str = "COUNTRIES", if_exists: str = "fail"):
        """Load countries from codebook page 2 and save to table "countries" in
        SQL database.

        Args:
            table_name (str, optional): table name to store to SQL database
            if_exists (str, optional): How to behave if the table already exists,
                only have effect when skip_write_if_exist is False, choose from
                {"fail", "replace", "append"}, default "fail"
        """

        def load_partial_contries(self, area: list[int]) -> pd.DataFrame:
            """The contry table in the codebook has left and right part, so we
            need to load them seperately. We also need to clean the part where
            tabula misunderstands the table.

            Args:
                area (list): [top, left, bottom, right]

            Returns:
                pd.Dataframe:
            """
            tables = tabula.read_pdf(self.codebook_path, area=area, pages=2)
            df = tables[0]

            # Rename the columns to be the same as in the dta/csv files
            df = df.rename(
                columns={
                    "Country": "country",
                    "Country ID": "country_id",
                    "Country.1": "country_fullname",
                }
            ).drop(index=0)

            # make country ids lower cases, same as in the dta/csv files
            df["country"] = df["country"].str.lower()

            return df

        if pd.io.sql.has_table(table_name, self.sql_con) and self.skip_write_if_exist:
            pass
        else:
            df_left = load_partial_contries(self, area=[153, 82, 403, 300])
            df_right = load_partial_contries(self, area=[153, 320, 403, 529])
            df = pd.concat([df_left, df_right], ignore_index=True)

            df.to_sql(table_name, self.sql_con, if_exists=if_exists)

    def save_parties(self, table_name: str = "PARTIES", if_exists: str = "fail"):
        """Load parties from codebook page 3-11 and save to table "parties" in
        SQL database.

        Args:
            table_name (str, optional): table name to store to SQL database
            if_exists (str, optional): How to behave if the table already exists,
                only have effect when skip_write_if_exist is False, choose from
                {"fail", "replace", "append"}, default "fail"
        """

        if pd.io.sql.has_table(table_name, self.sql_con) and self.skip_write_if_exist:
            pass
        else:
            tables = tabula.read_pdf(
                "data/2019_CHES_codebook.pdf", area=[80, 40, 525, 800], pages="3-11"
            )
            df = pd.concat(tables, ignore_index=True)

            # Drop the "Continued on next page" read as a row
            df = df.drop(
                df.loc[
                    (df["Party Name (English)"] == "Continued on next page")
                    | (df["Unnamed: 0"] == "Continued on next page")
                ].index
            )

            # Drop the last useless column caused by having to read too much to right
            df = df.drop(columns={"Unnamed: 0"})

            # Fix parties with too long names which go to the second rows
            second_rows = (
                df.loc[
                    df["Country"].isna()
                    & df["Party ID"].isna()
                    & df["Party Abbrev"].isna()
                ]
            ).index
            first_rows = [i - 1 for i in second_rows]
            df1 = df.loc[first_rows]
            df2 = df.loc[second_rows].fillna("")
            df2.index = first_rows
            df1["Party Name"] = df1["Party Name"] + df2["Party Name"]
            df1["Party Name (English)"] = (
                df1["Party Name (English)"] + df2["Party Name (English)"]
            )
            df.loc[first_rows] = df1
            df = df.drop(second_rows)

            # Forward fill all the NaNs in the country column
            df["Country"] = df["Country"].ffill()

            # make country ids lower cases, same as in the dta/csv files
            df["Country"] = df["Country"].str.lower()

            # Change abbr for Hungary from hung to hun, same as COUNTRIES
            df["Country"] = df["Country"].str.replace("hung", "hun")

            # Fill Remaining NaNs
            df = df.fillna("")

            # Rename the columns to be the same as in the dta/csv files
            df = df.rename(
                columns={
                    "Country": "country",
                    "Party ID": "party_id",
                    "Party Abbrev": "party",
                    "Party Name": "party_name",
                    "Party Name (English)": "party_name_english",
                }
            )

            df = df.reset_index(drop=True)

            df.to_sql(table_name, self.sql_con, if_exists=if_exists)

    def save_questions():
        # TODO: Automate extrating questions from codebook
        return


def dta_to_table(
    sql_con: sl.Connection,
    dta_path: str,
    table_name: str,
    skip_write_if_exist: bool = True,
    if_exists: str = "fail",
):
    """Load csv data as SQL database table.

    Args:
        sql_con (s1.Connection): SQL connection to a database
        dta_path (str): dta file path to load
        table_name (str): SQL table name to save
        skip_write_if_exist (bool, optional): default True = skip write if table
            exists in the db
        if_exists (str, optional): How to behave if the table already exists, only
            have effect when skip_write_if_exist is False, choose from
            {"fail", "replace", "append"}, default "fail"
    """

    if pd.io.sql.has_table(table_name, sql_con) and skip_write_if_exist:
        pass
    else:
        df = pd.read_stata(dta_path)

        # Cleaning up the data and unify column name
        if "CHES2019_experts" in dta_path:
            df = df.drop(
                columns={
                    "id",  # related to questionnaire
                    "party",  # related to questionnaire
                    "cname",  # duplicating country_name
                    "dob",  # date of birth cannot be drawn to the same plot
                    "lrecon_self",  # Supposely self-evaluate question?
                    "lrecon_sd",  # Will recalculate during aggregation
                    "galtan_self",  # Supposely self-evaluate question?
                    "galtan_sd",  # Will recalculate during aggregation
                    "eu_position_sd",  # Supposely self-evaluate question?
                    "party_a_econ",  # don't know what this is
                    "party_b_econ",  # don't know what this is
                    "party_c_econ",  # don't know what this is
                    "gender",  # don't know what this is
                }
            )
            df = df.rename(
                columns={
                    "party_name": "party",
                    "immigra_salience": "immigrate_salience",
                    "position": "eu_position",
                }
            )

            # Change Party ID of Fratelli d???Italia to 844, same as other tables
            df["party_id"] = df["party_id"].replace(to_replace=843, value=844)

            # Change Party ID of ChristenUnie to 1016, same as other tables
            df["party_id"] = df["party_id"].replace(to_replace=1009, value=1016)

        df.to_sql(table_name, sql_con, if_exists=if_exists)


def load_questions(json_path: str = "data/questions.json") -> pd.DataFrame:
    """Load json with question metadata to a dataframe, also does necessary cleanup.

    Args:
        json_path (str): path for `questions.json`

    Returns:
        pd.DataFrame
        __________| description | catagory | scores |
        questions |
    """
    df_q = pd.read_json(json_path).T
    df_q.index = df_q.index.str.lower()
    return df_q
