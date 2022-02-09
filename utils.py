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

            return df.rename(
                columns={"Country": "Country Abbreviation", "Country.1": "Country"}
            ).drop(index=0)

        cache_file_path = self.cache_path / cache_name

        if self.use_cache and cache_file_path.exists():

            return pd.read_pickle(cache_file_path)

        else:
            df_left = load_partial_contries(self, area=[153, 82, 403, 300])
            df_right = load_partial_contries(self, area=[153, 320, 403, 529])
            df = pd.concat([df_left, df_right], ignore_index=True)
            df.to_pickle(cache_file_path)

            return df

    def load_parties():

        return

    def load_questions():

        return
