import pandas as pd
import numpy as np


class ModelService:

    def __init__(self, model_class):
        """
        model_class: classe do modelo (ex: RandomForestModel)
        """
        self.model_class = model_class
        self.model = None

    # ==========================================
    # Criação do modelo
    # ==========================================
    def create_model(self, **model_params):
        self.model = self.model_class(**model_params)

    # ==========================================
    # Split temporal (SEM look-ahead bias)
    # ==========================================
    def temporal_split(
        self,
        df: pd.DataFrame,
        train_year: int,
        test_year: int,
        feature_cols: list,
        target_col: str,
    ):
        """
        Treina com dados de train_year
        Testa com dados de test_year
        """

        df_train = df[df["ano"] == train_year]
        df_test = df[df["ano"] == test_year]

        X_train = df_train[feature_cols]
        y_train = df_train[target_col]

        X_test = df_test[feature_cols]
        y_test = df_test[target_col]

        tickers_test = df_test["ticker"].values

        return X_train, y_train, X_test, y_test, tickers_test

    # ==========================================
    # Treino + Predição
    # ==========================================
    def train_and_predict(
        self,
        df: pd.DataFrame,
        train_year: int,
        test_year: int,
        feature_cols: list,
        target_col: str,
        model_params: dict,
    ):
        """
        Pipeline completo:
        - cria modelo
        - separa temporalmente
        - treina
        - prediz
        - retorna ranking
        """

        # 1️⃣ Criar modelo
        self.create_model(**model_params)

        # 2️⃣ Split temporal
        X_train, y_train, X_test, y_test, tickers = self.temporal_split(
            df,
            train_year,
            test_year,
            feature_cols,
            target_col,
        )

        # 3️⃣ Treinar
        self.model.train(X_train, y_train)

        # 4️⃣ Predizer
        predictions = self.model.predict(X_test)

        # 5️⃣ Criar DataFrame resultado
        results = pd.DataFrame({
            "ticker": tickers,
            "real_return": y_test.values,
            "predicted_return": predictions
        })

        # 6️⃣ Ranking
        results = results.sort_values(
            by="predicted_return",
            ascending=False
        ).reset_index(drop=True)

        return results

    # ==========================================
    # Feature Importance
    # ==========================================
    def get_feature_importance(self):
        if self.model is None:
            raise RuntimeError("Modelo não criado.")
        return self.model.get_feature_importance()

    # ==========================================
    # Retornar modelo treinado
    # ==========================================
    def get_model(self):
        return self.model