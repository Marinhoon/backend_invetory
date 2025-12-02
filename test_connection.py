import sys
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


def test_mongodb_connection():
    """Testa a conexão com o MongoDB"""

    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/inventory_control')

    print(f"Testando conexão com: {mongo_uri[:50]}...")

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

        # Testar a conexão
        client.admin.command('ping')

        # Obter nome do banco
        db = client.get_database()
        db_name = db.name

        print(f"✓ Conectado ao MongoDB com sucesso!")
        print(f"✓ Banco de dados: {db_name}")

        # Listar collections
        collections = db.list_collection_names()
        print(f"✓ Collections: {collections if collections else 'Nenhuma (banco vazio)'}")

        return True

    except Exception as e:
        print(f"✗ Erro ao conectar ao MongoDB:")
        print(f"  {str(e)}")
        print("\nDicas:")
        print("1. Certifique-se de que MONGODB_URI está correto no .env")
        print("2. Verifique se o MongoDB está rodando")
        print("3. Se usar MongoDB Atlas, adicione seu IP à whitelist")
        return False


if __name__ == '__main__':
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)
