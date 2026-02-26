import pandas as pd


class FundamentalsRepository:
    def __init__(self, connection):
        self.connection = connection

    def get_all(self) -> pd.DataFrame:
        query = """
        SELECT f.*, t.ticker
        FROM fundamentals f
        JOIN dim_tickers t ON f.ticker_id = t.id
        """

        cursor = self.connection.cursor(dictionary=True)

        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return pd.DataFrame(results)

        finally:
            cursor.close()