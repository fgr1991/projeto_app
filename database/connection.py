import mysql.connector
from mysql.connector import Error


class DatabaseConnection:
    def __init__(
        self,
        host: str = "localhost",
        user: str = "root",
        password: str = "senha",
        database: str = "finance_db",
        port: int = 3306,
    ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
            )

            if self.connection.is_connected():
                print("Conexão com MySQL estabelecida.")
                return self.connection

        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            raise

    def get_connection(self):
        if self.connection is None or not self.connection.is_connected():
            return self.connect()
        return self.connection

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexão com MySQL encerrada.")
