@echo off
REM Script de Setup para Backend Flask com MongoDB - Windows

echo.
echo ======================================
echo Setup - Backend Inventory Control
echo ======================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não está instalado ou não está no PATH
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado

REM Verificar se MongoDB está rodando (opcional)
echo.
echo Verificando MongoDB...
echo [INFO] Certifique-se de que MongoDB está rodando localmente ou configure a URL no .env

REM Criar ambiente virtual
echo.
echo [STEP 1] Criando ambiente virtual...
python -m venv venv

REM Ativar ambiente virtual
echo [STEP 2] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependências
echo [STEP 3] Instalando dependências...
pip install -r requirements.txt

REM Copiar .env.example para .env se não existir
if not exist .env (
    echo [STEP 4] Criando arquivo .env...
    copy .env.example .env
    echo [OK] Arquivo .env criado. Por favor, configure as variáveis de ambiente.
) else (
    echo [OK] Arquivo .env já existe
)

echo.
echo ======================================
echo Setup concluído com sucesso!
echo ======================================
echo.
echo Para iniciar o servidor, execute:
echo   python app.py
echo.
echo O servidor rodará em http://localhost:5000
echo.
pause
