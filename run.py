#!/usr/bin/env python
"""
Script para iniciar o servidor Flask de forma simples
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório do backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Verificar configurações
print("=" * 50)
print("Iniciando Backend - Inventory Control System")
print("=" * 50)

# Verificar MongoDB URI
mongodb_uri = os.getenv('MONGODB_URI')
if not mongodb_uri:
    print("[ERRO] MONGODB_URI não configurada no .env")
    print("Configure em: backend/.env")
    sys.exit(1)

print(f"[OK] MongoDB URI configurado: {mongodb_uri}")
print(f"[OK] Ambiente: {os.getenv('FLASK_ENV', 'development')}")

# Importar e executar app
from app import create_app

app = create_app()

print("=" * 50)
print("Servidor iniciando em http://localhost:5000")
print("Pressione CTRL+C para parar")
print("=" * 50)
print()

app.run(host='0.0.0.0', port=5000, debug=True)
