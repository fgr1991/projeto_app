import pandas as pd
from typing import Dict, Any

from services.model_service import ModelService
from backtest.backtester import Backtester


class BacktestService:

    def __init__(self, model_service: ModelService):
        self.model_service = model_service
        self.backtester = Backtester()

    # ============================================================
    # 1️⃣ Executar backtest walk-forward (1 ano)
    # ============================================================

    def run_single_period_backtest(
        self,
        df: pd.DataFrame,
        train_year: int,
        test_year: int,
        feature_columns: list,
        target_column: str,
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        Treina no ano train_year
        Testa no ano test_year
        Retorna métricas e carteira simulada
        """

        # --------------------------
        # Split temporal
        # --------------------------

        train_df = df[df["ano"] == train_year]
        test_df = df[df["ano"] == test_year]

        X_train = train_df[feature_columns]
        y_train = train_df[target_column]

        X_test = test_df[feature_columns]
        y_test = test_df[target_column]

        # --------------------------
        # Treinar modelo
        # --------------------------

        self.model_service.train(X_train, y_train)

        # --------------------------
        # Prever retornos
        # --------------------------

        predictions = self.model_service.predict(X_test)

        test_df = test_df.copy()
        test_df["predicted_return"] = predictions

        # --------------------------
        # Rankear ações
        # --------------------------

        ranked_df = test_df.sort_values(
            by="predicted_return",
            ascending=False
        )

        portfolio_df = ranked_df.head(top_n)

        # --------------------------
        # Executar backtest
        # --------------------------

        results = self.backtester.run(portfolio_df)

        return {
            "train_year": train_year,
            "test_year": test_year,
            "portfolio": portfolio_df,
            "metrics": results
        }