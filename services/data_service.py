# services/data_service.py

from __future__ import annotations
import pandas as pd

from preprocessing.data_preprocessor import DataPreprocessor


class DataService:

    def __init__(
        self,
        fundamentals_repository,
        returns_repository,
        preprocessor: DataPreprocessor,
    ):
        self.fund_repo = fundamentals_repository
        self.returns_repo = returns_repository
        self.preprocessor = preprocessor

    # ============================================================
    # 1️⃣ Carregar fundamentals
    # ============================================================

    def load_fundamentals(self) -> pd.DataFrame:
        """
        Retorna:
            ticker | ano | indicadores...
        """
        df = self.fund_repo.get_all()
        return df

    # ============================================================
    # 2️⃣ Carregar returns
    # ============================================================

    def load_returns(self) -> pd.DataFrame:
        """
        Retorna:
            ticker | ano_inicio | ano_fim | retorno
        """
        df = self.returns_repo.get_all_returns()
        return df

    # ============================================================
    # 3️⃣ Merge fundamentals + returns
    # ============================================================

    def merge_fundamentals_with_returns(self) -> pd.DataFrame:
        """
        Faz o merge correto:
            fundamentals.ano  == returns.ano_inicio

        Resultado:
            ticker | ano | indicadores | retorno
        """

        fundamentals = self.load_fundamentals()
        returns = self.load_returns()

        df = fundamentals.merge(
            returns,
            left_on=["ticker", "ano"],
            right_on=["ticker", "ano_inicio"],
            how="inner"
        )

        # Remove colunas redundantes
        df = df.drop(columns=["ano_inicio", "ano_fim"])

        return df

    # ============================================================
    # 4️⃣ Separar treino e teste temporal
    # ============================================================

    def train_test_split_by_year(
        self,
        df: pd.DataFrame,
        train_year: int
    ):
        """
        Treina:
            fundamentals ano = y
            target retorno y→y+1

        Testa:
            fundamentals ano = y+1
            target retorno (y+1)→(y+2)
        """

        df_train = df[df["ano"] == train_year].copy()
        df_test = df[df["ano"] == train_year + 1].copy()

        return df_train, df_test

    # ============================================================
    # 5️⃣ Pipeline completo para modelo
    # ============================================================

    def prepare_dataset(
        self,
        train_year: int,
        imputation_method: str = "median_by_year",
    ):
        """
        Pipeline:
            - Merge fundamentals + returns
            - Preprocessamento (apenas features)
            - Split temporal
            - Retorna X_train, y_train, X_test, y_test
        """

        # 1️⃣ Merge
        df = self.merge_fundamentals_with_returns()

        # 2️⃣ Preprocessamento
        if imputation_method == "median_by_year":
            df = self.preprocessor.impute_median_by_year(df)

        elif imputation_method == "rank":
            df = self.preprocessor.rank_by_year_and_neutral_impute(df)

        elif imputation_method == "winsorize":
            df = self.preprocessor.winsorize_then_impute_median_by_year(df)

        else:
            raise ValueError("Método de imputação inválido")

        # 3️⃣ Split temporal
        df_train, df_test = self.train_test_split_by_year(df, train_year)

        # 4️⃣ Seleção de features
        feature_cols = [
            col for col in df.columns
            if col not in ["ticker", "ano", "retorno"]
        ]

        X_train = df_train[feature_cols]
        y_train = df_train["retorno"]

        X_test = df_test[feature_cols]
        y_test = df_test["retorno"]

        return X_train, y_train, X_test, y_test