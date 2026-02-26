import pandas as pd
from preprocessing.data_preprocessor import DataPreprocessor


class DataService:

    def __init__(self, repository, preprocessor: DataPreprocessor):
        self.repository = repository
        self.preprocessor = preprocessor

    # ============================================================
    # 1️⃣ Carregar dados brutos
    # ============================================================

    def load_data(self) -> pd.DataFrame:
        """
        Busca dados completos do repository.
        """
        df = self.repository.get_all_fundamentals()
        return df

    # ============================================================
    # 2️⃣ Criar target (retorno t+1)
    # ============================================================

    def create_target(self, df: pd.DataFrame, return_column: str = "retorno") -> pd.DataFrame:
        """
        Cria coluna target deslocando retorno em -1 por ticker.
        """

        df = df.sort_values(["ticker", "ano"]).copy()

        df["target"] = (
            df.groupby("ticker")[return_column]
            .shift(-1)
        )

        return df

    # ============================================================
    # 3️⃣ Separar treino e teste temporal
    # ============================================================

    def train_test_split_by_year(
        self,
        df: pd.DataFrame,
        train_year: int
    ):
        """
        Treina em ano = train_year
        Testa em ano = train_year + 1
        """

        df_train = df[df["ano"] == train_year].copy()
        df_test = df[df["ano"] == train_year + 1].copy()

        return df_train, df_test

    # ============================================================
    # 4️⃣ Preparar dados finais para modelo
    # ============================================================

    def prepare_dataset(
        self,
        train_year: int,
        return_column: str = "retorno"
    ):
        """
        Pipeline completo:
        - Carrega dados
        - Cria target
        - Aplica preprocessamento
        - Separa treino e teste
        - Retorna X_train, y_train, X_test, y_test
        """

        df = self.load_data()

        df = self.create_target(df, return_column)

        # remove última linha de cada ticker (pois target será NaN)
        df = df.dropna(subset=["target"])

        # aplica preprocessamento (apenas features)
        df = self.preprocessor.impute_median_by_year(df)

        df_train, df_test = self.train_test_split_by_year(df, train_year)

        feature_cols = [
            col for col in df.columns
            if col not in ["ticker", "ano", "target"]
        ]

        X_train = df_train[feature_cols]
        y_train = df_train["target"]

        X_test = df_test[feature_cols]
        y_test = df_test["target"]

        return X_train, y_train, X_test, y_test