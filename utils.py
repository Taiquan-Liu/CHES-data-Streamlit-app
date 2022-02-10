from pathlib import Path

import pandas as pd
import tabula


class codebook_loader:
    """Load data from the code book.

    :param codebook_path: folder for codebook, default "data/2019_CHES_codebook.pdf"
    :param cache_path: folder to store cache files, default "cache/"
    :param use_cache: if True, load data from cache_path; if False, always
                      load data from codebook_path and save to cache_path
    """

    def __init__(
        self,
        codebook_path: str = "data/2019_CHES_codebook.pdf",
        cache_path: str = "cache/",
        use_cache: bool = True,
    ):
        self.codebook_path = Path(codebook_path).absolute()
        self.cache_path = Path(cache_path).absolute()
        self.use_cache = use_cache

        if not self.cache_path.exists():
            self.cache_path.mkdir()

    def load_contries(self, cache_name: str = "countries.pkl") -> pd.DataFrame:
        """Load table of countries from codebook page 2"""

        def load_partial_contries(self, area: list[int]) -> pd.DataFrame:
            """The contry table in the codebook has left and right part, so we
            need to load them seperately. We also need to clean the part where
            tabula misunderstands the table.

            :param area: [top, left, bottom, right]
            """
            tables = tabula.read_pdf(self.codebook_path, area=area, pages=2)
            df = tables[0]

            # Rename the columns to be the same as in the dta/csv files
            df = df.rename(
                columns={"Country": "country", "Country.1": "Country Fullname"}
            ).drop(index=0)

            # make country ids lower cases, same as in the dta/csv files
            df["country"] = df["country"].str.lower()

            return df

        cache_file_path = self.cache_path / cache_name

        if self.use_cache and cache_file_path.exists():

            return pd.read_pickle(cache_file_path)

        else:
            df_left = load_partial_contries(self, area=[153, 82, 403, 300])
            df_right = load_partial_contries(self, area=[153, 320, 403, 529])
            df = pd.concat([df_left, df_right], ignore_index=True)
            df.to_pickle(cache_file_path)

            return df

    def load_parties(self, cache_name: str = "parties.pkl") -> pd.DataFrame:
        """Load table of parties from codebook page 3-11"""

        cache_file_path = self.cache_path / cache_name

        if self.use_cache and cache_file_path.exists():

            return pd.read_pickle(cache_file_path)

        else:

            tables = tabula.read_pdf(
                "data/2019_CHES_codebook.pdf", area=[80, 40, 520, 800], pages="3-11"
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
            df1 = df.loc[first_rows].fillna("")
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

            # Rename the columns to be the same as in the dta/csv files
            df = df.rename(
                columns={
                    "Country": "country",
                    "Party ID": "party_id",
                    "Party Abbrev": "party",
                }
            ).drop(index=0)

            # make country ids lower cases, same as in the dta/csv files
            df["country"] = df["country"].str.lower()

            df = df.reset_index(drop=True)
            df.to_pickle(cache_file_path)

            return df


    def load_questions():

        return
