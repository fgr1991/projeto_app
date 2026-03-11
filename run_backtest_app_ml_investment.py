from database.connection import DatabaseConnection
from database.fundamentals_repository import FundamentalsRepository
from database.returns_repository import ReturnsRepository
from services.model_service import ModelService
from models.randomForest import RandomForestModel
from backtest.backtester import Backtester


def main():

    db = DatabaseConnection(
        host="localhost",
        user="root",
        password="Oracle1991#",
        database="finance_db",
        port=3306
    )

    conn = db.get_connection()

    fundamentals_repo = FundamentalsRepository(conn)
    returns_repo = ReturnsRepository(db)

    df_fund = fundamentals_repo.get_all()
    df_ret = returns_repo.get_all_returns()

    variaveis_explicativas = [
        'dy', 'pl', 'peg_ratio', 'pvp', 'ev_ebitda', 'ev_ebit',
        'p_ebitda', 'p_ebit', 'vpa', 'p_ativo', 'lpa', 'psr',
        'p_cap_giro', 'p_ativo_circ_liq', 'div_liquida_pl',
        'div_liquida_ebitda', 'div_liquida_ebit', 'pl_ativos',
        'passivos_ativos', 'liq_corrente', 'm_bruta', 'm_ebitda',
        'm_ebit', 'm_liquida', 'roe', 'roa', 'roic',
        'giro_ativos', 'cagr_receitas_5y', 'cagr_lucros_5y'
    ]

    model_service = ModelService(RandomForestModel)
    backtester = Backtester(model_service)

    results = backtester.run_tcc_style_with_real_return(
        df_fundamentals=df_fund,
        df_returns=df_ret,
        variaveis_explicativas=variaveis_explicativas,
        start_year=2016,
        end_year=2023
    )

    print(results)

    db.close()


if __name__ == "__main__":
    main()