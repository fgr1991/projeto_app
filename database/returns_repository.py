from __future__ import annotations

import pandas as pd


class ReturnsRepository:
    """
    Responsabilidade:
        - Ler a tabela returns
        - Retornar DataFrame estruturado
        - ZERO regra de negócio
        - ZERO regra de ML
    """

    def __init__(self, connection):
        """
        connection: instância da classe Connection
        com método get_connection()
        """
        self.connection = connection

    # ============================================================
    # 1️⃣ Buscar todos os retornos
    # ============================================================

    def get_all_returns(self) -> pd.DataFrame:
        """
        Retorna:
            ticker | ano_inicio | ano_fim | retorno
        """

        query = """
            SELECT
                t.ticker AS ticker,
                r.ano_inicio AS ano_inicio,
                r.ano_fim AS ano_fim,
                r.retorno AS retorno
            FROM returns r
            JOIN dim_tickers t ON t.id = r.ticker_id
            ORDER BY t.ticker, r.ano_inicio
        """

        df = pd.read_sql(
            query,
            self.connection.get_connection()
        )

        return df

    # ============================================================
    # 2️⃣ Buscar por intervalo de ano_inicio
    # ============================================================

    def get_returns_by_start_year_range(
        self,
        start_year: int,
        end_year: int
    ) -> pd.DataFrame:
        """
        Filtra por ano_inicio (ano t).
        Útil para backtests controlados.
        """

        query = """
            SELECT
                t.ticker AS ticker,
                r.ano_inicio AS ano_inicio,
                r.ano_fim AS ano_fim,
                r.retorno AS retorno
            FROM returns r
            JOIN dim_tickers t ON t.id = r.ticker_id
            WHERE r.ano_inicio BETWEEN %s AND %s
            ORDER BY t.ticker, r.ano_inicio
        """

        df = pd.read_sql(
            query,
            self.connection.get_connection(),
            params=(start_year, end_year)
        )

        return df