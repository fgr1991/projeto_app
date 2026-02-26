import pandas as pd
import numpy as np


class Backtester:

    def __init__(
        self,
        model_service,
        year_col: str = "ano",
        ticker_col: str = "ticker",
        target_col: str = "target"
    ):
        """
        model_service : instância de ModelService
        year_col      : nome da coluna de ano
        ticker_col    : nome da coluna ticker
        target_col    : coluna do retorno futuro (y+1)
        """

        self.model_service = model_service
        self.year_col = year_col
        self.ticker_col = ticker_col
        self.target_col = target_col

    # ============================================================
    # 🔹 MÉTODO PRINCIPAL DE WALK-FORWARD BACKTEST
    # ============================================================

    def run_walk_forward(
        self,
        df: pd.DataFrame,
        start_year: int,
        end_year: int,
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        Executa backtest anual:
        Treina ano y
        Prediz ano y+1
        Calcula retorno realizado em y+2
        """

        results = []

        for year in range(start_year, end_year):

            train_df = df[df[self.year_col] == year].copy()
            test_df = df[df[self.year_col] == year + 1].copy()

            if train_df.empty or test_df.empty:
                continue

            X_train = train_df.drop(
                columns=[self.year_col, self.ticker_col, self.target_col],
                errors="ignore"
            )

            y_train = train_df[self.target_col]

            X_test = test_df.drop(
                columns=[self.year_col, self.ticker_col, self.target_col],
                errors="ignore"
            )

            # ==========================
            # 1️⃣ Treino
            # ==========================

            self.model_service.train(X_train, y_train)

            # ==========================
            # 2️⃣ Predição
            # ==========================

            predictions = self.model_service.predict(X_test)

            test_df["prediction"] = predictions

            # ==========================
            # 3️⃣ Ranking
            # ==========================

            selected = (
                test_df
                .sort_values("prediction", ascending=False)
                .head(top_n)
            )

            # ==========================
            # 4️⃣ Retorno realizado
            # ==========================

            realized_return = selected[self.target_col].mean()

            results.append({
                "train_year": year,
                "test_year": year + 1,
                "portfolio_return": realized_return
            })

        return pd.DataFrame(results)

    # ============================================================
    # 🔹 MÉTRICAS BÁSICAS
    # ============================================================

    def compute_cumulative_return(self, results_df: pd.DataFrame) -> float:
        """
        Retorno acumulado composto
        """

        returns = results_df["portfolio_return"].values
        cumulative = np.prod(1 + returns) - 1
        return cumulative

    def compute_sharpe(self, results_df: pd.DataFrame, risk_free: float = 0.0) -> float:
        """
        Sharpe anual simples
        """

        excess = results_df["portfolio_return"] - risk_free
        return excess.mean() / excess.std()