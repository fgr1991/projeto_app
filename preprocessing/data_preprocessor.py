from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Optional, Sequence


class DataPreprocessor:

    def __init__(
        self,
        year_col: str = "ano",
        ticker_col: str = "ticker",
    ):
        self.year_col = year_col
        self.ticker_col = ticker_col

    # ============================================================
    # 🔒 MÉTODO INTERNO PARA PROTEGER COLUNAS ESTRUTURAIS
    # ============================================================

    def _get_numeric_feature_columns(self, df: pd.DataFrame):
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        exclude = {self.year_col, self.ticker_col}
        return [col for col in numeric_cols if col not in exclude]

    # ============================================================
    # -------------------- 1️⃣ IMPUTAÇÕES BÁSICAS ----------------
    # ============================================================

    def fillna_zero(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        numeric_cols = self._get_numeric_feature_columns(df)
        df[numeric_cols] = df[numeric_cols].fillna(0)
        return df

    def fillna_constant(self, df: pd.DataFrame, value: float) -> pd.DataFrame:
        df = df.copy()
        numeric_cols = self._get_numeric_feature_columns(df)
        df[numeric_cols] = df[numeric_cols].fillna(value)
        return df

    def fillna_mean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        numeric_cols = self._get_numeric_feature_columns(df)
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        return df

    def fillna_median(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        numeric_cols = self._get_numeric_feature_columns(df)
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        return df

    def fillna_mode(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        numeric_cols = self._get_numeric_feature_columns(df)
        mode_vals = df[numeric_cols].mode().iloc[0]
        df[numeric_cols] = df[numeric_cols].fillna(mode_vals)
        return df


    # ============================================================
    # -------------------- 2️⃣ TEMPORAIS SIMPLES -----------------
    # ============================================================

    def forward_fill_by_ticker(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values([self.ticker_col, self.year_col]).copy()
        numeric_cols = self._get_numeric_feature_columns(df)
        df[numeric_cols] = df.groupby(self.ticker_col)[numeric_cols].ffill()
        return df

    def backward_fill_by_ticker(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values([self.ticker_col, self.year_col]).copy()
        numeric_cols = self._get_numeric_feature_columns(df)
        df[numeric_cols] = df.groupby(self.ticker_col)[numeric_cols].bfill()
        return df

    def linear_interpolate_by_ticker(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values([self.ticker_col, self.year_col]).copy()
        numeric_cols = self._get_numeric_feature_columns(df)

        df[numeric_cols] = df.groupby(self.ticker_col)[numeric_cols].transform(
            lambda x: x.interpolate(method="linear")
        )

        return df


    # ============================================================
    # -------------------- 3️⃣ CROSS-SECTIONAL -------------------
    # ============================================================

    def impute_median_by_year(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        numeric_cols = self._get_numeric_feature_columns(df)

        df[numeric_cols] = df.groupby(self.year_col)[numeric_cols].transform(
            lambda x: x.fillna(x.median())
        )
        return df


    # ============================================================
    # -------------------- 4️⃣ ROBUSTIFICAÇÃO --------------------
    # ============================================================

    def winsorize_then_impute_median_by_year(
        self,
        df: pd.DataFrame,
        lower_q: float = 0.01,
        upper_q: float = 0.99,
    ) -> pd.DataFrame:

        df = df.copy()
        numeric_cols = self._get_numeric_feature_columns(df)

        def process(group):
            lower = group[numeric_cols].quantile(lower_q)
            upper = group[numeric_cols].quantile(upper_q)

            group[numeric_cols] = group[numeric_cols].clip(lower, upper, axis=1)
            group[numeric_cols] = group[numeric_cols].fillna(
                group[numeric_cols].median()
            )
            return group

        df = df.groupby(self.year_col, group_keys=False).apply(process)
        return df


    # ============================================================
    # -------------------- 5️⃣ RANK NEUTRO -----------------------
    # ============================================================

    def rank_by_year_and_neutral_impute(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        numeric_cols = self._get_numeric_feature_columns(df)

        def rank_group(group):
            ranked = group[numeric_cols].rank(pct=True)
            group[numeric_cols] = ranked.fillna(0.5)
            return group

        df = df.groupby(self.year_col, group_keys=False).apply(rank_group)
        return df


    # ============================================================
    # -------------------- 6️⃣ MACHINE LEARNING ------------------
    # ============================================================

    def knn_impute_by_year(self, df: pd.DataFrame, k: int = 5) -> pd.DataFrame:
        from sklearn.impute import KNNImputer

        df = df.copy()
        numeric_cols = self._get_numeric_feature_columns(df)

        def process(group):
            imputer = KNNImputer(n_neighbors=k)
            group[numeric_cols] = imputer.fit_transform(group[numeric_cols])
            return group

        df = df.groupby(self.year_col, group_keys=False).apply(process)
        return df


    def mice_impute_by_year(
        self,
        df: pd.DataFrame,
        max_iter: int = 15,
        random_state: int = 42,
    ) -> pd.DataFrame:

        from sklearn.experimental import enable_iterative_imputer
        from sklearn.impute import IterativeImputer

        df = df.copy()
        numeric_cols = self._get_numeric_feature_columns(df)

        def process(group):
            imputer = IterativeImputer(
                max_iter=max_iter,
                random_state=random_state
            )
            group[numeric_cols] = imputer.fit_transform(group[numeric_cols])
            return group

        df = df.groupby(self.year_col, group_keys=False).apply(process)
        return df