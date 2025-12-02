#!/bin/bash
# Script de Setup para Backend Flask com MongoDB - Linux/Mac

echo ""
echo "======================================"
echo "Setup - Backend Inventory Control"
echo "======================================"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 não está instalado"
    echo "Instale com: sudo apt-get install python3 python3-pip"
    exit 1
fi

echo "[OK] Python 3 encontrado"

# Verificar MongoDB
echo ""
echo "Verificando MongoDB..."
echo "[INFO] Certifique-se de que MongoDB está rodando localmente ou configure a URL no .env"

# Criar ambiente virtual
echo ""
echo "[STEP 1] Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "[STEP 2] Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "[STEP 3] Instalando dependências..."
pip install -r requirements.txt

# Copiar .env.example para .env se não existir
if [ ! -f .env ]; then
    echo "[STEP 4] Criando arquivo .env..."
    cp .env.example .env
    echo "[OK] Arquivo .env criado. Por favor, configure as variáveis de ambiente."
else
    echo "[OK] Arquivo .env já existe"
fi

echo ""
echo "======================================"
echo "Setup concluído com sucesso!"
echo "======================================"
echo ""
echo "Para iniciar o servidor, execute:"
echo "  python app.py"
echo ""
echo "O servidor rodará em http://localhost:5000"
echo ""
