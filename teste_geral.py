from database.connection import DatabaseConnection
from database.fundamentals_repository import FundamentalsRepository


# 🔹 Conexão
db = DatabaseConnection(
    host="localhost",
    user="root",
    password="Oracle1991#",
    database="finance_db",
    port=3306
)

connection = db.get_connection()

# 🔹 Repository
repo = FundamentalsRepository(connection)

# 🔹 Buscar TODOS os anos
df = repo.get_all()

print("DataFrame completo carregado!")
print("Shape:", df.shape)

df.info()

db.close()