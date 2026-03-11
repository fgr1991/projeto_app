import os
import re
import math
import glob
import pandas as pd
import mysql.connector
from mysql.connector import Error

# ============================================================
# CONFIGURAÇÕES
# ============================================================

HOST = "localhost"
PORT = 3306
USER = "root"
PASSWORD = "Oracle1991#"
DATABASE = "finance_db"

DATA_FOLDER = r"G:\projeto_app\data"

# ============================================================
# MAPEAMENTO DAS COLUNAS FUNDAMENTALISTAS
# ============================================================

FUNDAMENTALS_MAPPING = {
    "Ticker": "ticker",
    "Ano": "ano",
    "D.Y": "dy",
    "P/L": "pl",
    "PEG Ratio": "peg_ratio",
    "P/VP": "pvp",
    "EV/EBITDA": "ev_ebitda",
    "EV/EBIT": "ev_ebit",
    "P/EBITDA": "p_ebitda",
    "P/EBIT": "p_ebit",
    "VPA": "vpa",
    "P/Ativo": "p_ativo",
    "LPA": "lpa",
    "P/SR": "psr",
    "P/Cap. Giro": "p_cap_giro",
    "P/Ativo Circ. Liq.": "p_ativo_circ_liq",
    "Dív. líquida/PL": "div_liquida_pl",
    "Dív. líquida/EBITDA": "div_liquida_ebitda",
    "Dív. líquida/EBIT": "div_liquida_ebit",
    "PL/Ativos": "pl_ativos",
    "Passivos/Ativos": "passivos_ativos",
    "Liq. corrente": "liq_corrente",
    "M. Bruta": "m_bruta",
    "M. EBITDA": "m_ebitda",
    "M. EBIT": "m_ebit",
    "M. Líquida": "m_liquida",
    "ROE": "roe",
    "ROA": "roa",
    "ROIC": "roic",
    "Giro ativos": "giro_ativos",
    "CAGR Receitas 5 anos": "cagr_receitas_5y",
    "CAGR Lucros 5 anos": "cagr_lucros_5y",
}

FUNDAMENTALS_DB_COLUMNS = [
    "dy", "pl", "peg_ratio", "pvp", "ev_ebitda", "ev_ebit",
    "p_ebitda", "p_ebit", "vpa", "p_ativo", "lpa", "psr",
    "p_cap_giro", "p_ativo_circ_liq", "div_liquida_pl",
    "div_liquida_ebitda", "div_liquida_ebit", "pl_ativos",
    "passivos_ativos", "liq_corrente", "m_bruta", "m_ebitda",
    "m_ebit", "m_liquida", "roe", "roa", "roic", "giro_ativos",
    "cagr_receitas_5y", "cagr_lucros_5y"
]

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def is_null_like(value):
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True

    text = str(value).strip().lower()
    return text in {"", "-", "--", "nan", "none", "null", "n/a", "na"}

def to_float(value):
    """
    Converte textos como:
    '12,34%' -> 12.34
    '1.234,56' -> 1234.56
    '-' -> None
    """
    if is_null_like(value):
        return None

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if pd.isna(value):
            return None
        return float(value)

    text = str(value).strip()

    # Remove %
    text = text.replace("%", "")

    # Remove espaços
    text = text.replace(" ", "")

    # Converte padrão BR para float
    # 1.234,56 -> 1234.56
    text = text.replace(".", "")
    text = text.replace(",", ".")

    try:
        return float(text)
    except ValueError:
        return None

def to_int(value):
    if is_null_like(value):
        return None
    try:
        return int(float(value))
    except Exception:
        return None

def clean_ticker(value):
    if is_null_like(value):
        return None
    return str(value).strip().upper()

def get_xlsx_files(folder):
    pattern = os.path.join(folder, "*.xlsx")
    return glob.glob(pattern)

def create_database_and_tables():
    conn = None
    cursor = None

    try:
        # conexão sem database para criar o banco
        conn = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD
        )
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
        cursor.execute(f"USE {DATABASE}")

        create_sql = """
        CREATE TABLE IF NOT EXISTS dim_tickers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticker VARCHAR(15) NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS fundamentals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticker_id INT NOT NULL,
            ano INT NOT NULL,
            dy DECIMAL(18,4),
            pl DECIMAL(18,4),
            peg_ratio DECIMAL(18,4),
            pvp DECIMAL(18,4),
            ev_ebitda DECIMAL(18,4),
            ev_ebit DECIMAL(18,4),
            p_ebitda DECIMAL(18,4),
            p_ebit DECIMAL(18,4),
            vpa DECIMAL(18,4),
            p_ativo DECIMAL(18,4),
            lpa DECIMAL(18,4),
            psr DECIMAL(18,4),
            p_cap_giro DECIMAL(18,4),
            p_ativo_circ_liq DECIMAL(18,4),
            div_liquida_pl DECIMAL(18,4),
            div_liquida_ebitda DECIMAL(18,4),
            div_liquida_ebit DECIMAL(18,4),
            pl_ativos DECIMAL(18,4),
            passivos_ativos DECIMAL(18,4),
            liq_corrente DECIMAL(18,4),
            m_bruta DECIMAL(18,4),
            m_ebitda DECIMAL(18,4),
            m_ebit DECIMAL(18,4),
            m_liquida DECIMAL(18,4),
            roe DECIMAL(18,4),
            roa DECIMAL(18,4),
            roic DECIMAL(18,4),
            giro_ativos DECIMAL(18,4),
            cagr_receitas_5y DECIMAL(18,4),
            cagr_lucros_5y DECIMAL(18,4),
            FOREIGN KEY (ticker_id) REFERENCES dim_tickers(id),
            UNIQUE KEY unique_fundamentals (ticker_id, ano)
        );

        CREATE TABLE IF NOT EXISTS prices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticker_id INT NOT NULL,
            ano INT NOT NULL,
            preco_abertura_ano DECIMAL(18,4),
            preco_fechamento DECIMAL(18,4),
            preco_medio DECIMAL(18,4),
            FOREIGN KEY (ticker_id) REFERENCES dim_tickers(id),
            UNIQUE KEY unique_prices (ticker_id, ano)
        );

        CREATE TABLE IF NOT EXISTS returns (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticker_id INT NOT NULL,
            ano_inicio INT NOT NULL,
            ano_fim INT NOT NULL,
            retorno DECIMAL(18,4),
            FOREIGN KEY (ticker_id) REFERENCES dim_tickers(id),
            UNIQUE KEY unique_returns (ticker_id, ano_inicio, ano_fim)
        );
        """

        for statement in create_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)

        conn.commit()
        print(f"Banco '{DATABASE}' e tabelas criados com sucesso.")

    except Error as e:
        print("Erro ao criar banco/tabelas:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

def get_connection():
    return mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )

def get_or_create_ticker_id(cursor, ticker):
    insert_sql = "INSERT IGNORE INTO dim_tickers (ticker) VALUES (%s)"
    select_sql = "SELECT id FROM dim_tickers WHERE ticker = %s"

    cursor.execute(insert_sql, (ticker,))
    cursor.execute(select_sql, (ticker,))
    result = cursor.fetchone()

    if result:
        return result[0]
    return None

def standardize_dataframe(df):
    # Remove espaços extras dos nomes das colunas
    df.columns = [str(col).strip() for col in df.columns]

    # Renomeia apenas as colunas conhecidas de fundamentals
    rename_dict = {col: FUNDAMENTALS_MAPPING[col] for col in df.columns if col in FUNDAMENTALS_MAPPING}
    df = df.rename(columns=rename_dict)

    return df

def insert_fundamentals_row(cursor, ticker_id, row):
    ano = to_int(row.get("ano"))
    if ano is None:
        return

    values = [ticker_id, ano]

    for col in FUNDAMENTALS_DB_COLUMNS:
        values.append(to_float(row.get(col)))

    sql = f"""
    INSERT IGNORE INTO fundamentals (
        ticker_id, ano, {", ".join(FUNDAMENTALS_DB_COLUMNS)}
    )
    VALUES (
        %s, %s, {", ".join(["%s"] * len(FUNDAMENTALS_DB_COLUMNS))}
    )
    """

    cursor.execute(sql, tuple(values))

def extract_price_columns(columns):
    """
    Retorna colunas como:
    price_2016, price_2017, price_2018
    """
    price_cols = []
    for col in columns:
        match = re.fullmatch(r"price_(\d{4})", str(col).strip())
        if match:
            price_cols.append((col, int(match.group(1))))
    return price_cols

def extract_return_columns(columns):
    """
    Retorna colunas como:
    return_2016_2017, return_2017_2018
    """
    return_cols = []
    for col in columns:
        match = re.fullmatch(r"return_(\d{4})_(\d{4})", str(col).strip())
        if match:
            return_cols.append((col, int(match.group(1)), int(match.group(2))))
    return return_cols

def insert_prices_from_row(cursor, ticker_id, row):
    """
    Para cada coluna price_YYYY:
      insere em prices:
        ano = YYYY
        preco_fechamento = valor
    Como o arquivo não traz claramente abertura/médio para cada ano,
    vamos armazenar:
        preco_abertura_ano = NULL
        preco_fechamento   = price_YYYY
        preco_medio        = NULL
    """
    price_cols = extract_price_columns(row.index)

    for col_name, year in price_cols:
        price_value = to_float(row.get(col_name))
        if price_value is None:
            continue

        sql = """
        INSERT IGNORE INTO prices (
            ticker_id, ano, preco_abertura_ano, preco_fechamento, preco_medio
        )
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (ticker_id, year, None, price_value, None))

def insert_returns_from_row(cursor, ticker_id, row):
    """
    Para cada coluna return_YYYY_YYYY:
      insere em returns:
        ano_inicio = primeiro ano
        ano_fim    = segundo ano
        retorno    = valor
    """
    return_cols = extract_return_columns(row.index)

    for col_name, year_start, year_end in return_cols:
        return_value = to_float(row.get(col_name))
        if return_value is None:
            continue

        sql = """
        INSERT IGNORE INTO returns (
            ticker_id, ano_inicio, ano_fim, retorno
        )
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (ticker_id, year_start, year_end, return_value))

def process_file(file_path, cursor):
    print(f"\nProcessando arquivo: {os.path.basename(file_path)}")

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
        return

    if df.empty:
        print("Arquivo vazio. Pulando.")
        return

    df = standardize_dataframe(df)

    if "ticker" not in df.columns:
        print("Coluna 'Ticker' não encontrada. Pulando arquivo.")
        return

    total_rows = 0

    for _, row in df.iterrows():
        ticker = clean_ticker(row.get("ticker"))
        if not ticker:
            continue

        ticker_id = get_or_create_ticker_id(cursor, ticker)
        if ticker_id is None:
            print(f"Não foi possível obter ticker_id para {ticker}.")
            continue

        # 1) fundamentals do ano y
        if "ano" in df.columns:
            insert_fundamentals_row(cursor, ticker_id, row)

        # 2) prices de y, y+1, y+2
        insert_prices_from_row(cursor, ticker_id, row)

        # 3) returns de y->y+1, y+1->y+2
        insert_returns_from_row(cursor, ticker_id, row)

        total_rows += 1

    print(f"Linhas processadas: {total_rows}")

def main():
    # 1) cria banco e tabelas
    create_database_and_tables()

    # 2) lista arquivos
    files = get_xlsx_files(DATA_FOLDER)

    if not files:
        print(f"Nenhum arquivo .xlsx encontrado em: {DATA_FOLDER}")
        return

    print(f"Arquivos encontrados: {len(files)}")

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for file_path in files:
            process_file(file_path, cursor)
            conn.commit()

        print("\nImportação finalizada com sucesso.")

    except Error as e:
        if conn:
            conn.rollback()
        print("Erro durante a importação:", e)

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    main()