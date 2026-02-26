from sklearn.ensemble import RandomForestRegressor
from sklearn.utils.validation import check_is_fitted
import joblib


class RandomForestModel:
    """
    Encapsulamento do RandomForestRegressor.
    Não depende de BaseModel.
    """

    def __init__(self, **kwargs):
        """
        Recebe hiperparâmetros dinamicamente via kwargs.
        """

        kwargs.setdefault("random_state", 42)
        kwargs.setdefault("n_jobs", -1)

        self.model = RandomForestRegressor(**kwargs)

    # ===============================
    # Treinamento
    # ===============================
    def train(self, X, y):
        self.model.fit(X, y)

    # ===============================
    # Predição
    # ===============================
    def predict(self, X):
        check_is_fitted(self.model)
        return self.model.predict(X)

    # ===============================
    # Feature importance
    # ===============================
    def get_feature_importance(self):
        check_is_fitted(self.model)
        return self.model.feature_importances_

    # ===============================
    # Parâmetros do modelo
    # ===============================
    def get_params(self):
        return self.model.get_params()

    # ===============================
    # Persistência
    # ===============================
    def save(self, path):
        joblib.dump(self.model, path)

    def load(self, path):
        self.model = joblib.load(path)