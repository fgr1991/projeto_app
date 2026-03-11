import pandas as pd
import mysql.connector

# ============================================================
# CONEXÃO
# ============================================================

conexao = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="Oracle1991#",
    database="finance_db"
)

print("Conectado ao banco.")

# ============================================================
# DIM TICKERS
# ============================================================

tickers_df = pd.read_sql("""
SELECT *
FROM dim_tickers
""", conexao)

# ============================================================
# FUNDAMENTALS COM TICKER
# ============================================================

fundamentals_df = pd.read_sql("""
SELECT
    t.ticker,
    f.*
FROM fundamentals f
JOIN dim_tickers t
    ON f.ticker_id = t.id
""", conexao)

# ============================================================
# PRICES COM TICKER
# ============================================================

prices_df = pd.read_sql("""
SELECT
    t.ticker,
    p.*
FROM prices p
JOIN dim_tickers t
    ON p.ticker_id = t.id
""", conexao)

# ============================================================
# RETURNS COM TICKER
# ============================================================

returns_df = pd.read_sql("""
SELECT
    t.ticker,
    r.*
FROM returns r
JOIN dim_tickers t
    ON r.ticker_id = t.id
""", conexao)

# ============================================================
# FECHAR CONEXÃO
# ============================================================

conexao.close()

print("Banco carregado em DataFrames.")