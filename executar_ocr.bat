@echo off
echo Verificando requisitos...

REM Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado!
    echo Por favor, instale o Python 3.12 do site:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante a instalacao, marque a opcao "Add Python to PATH"
    pause
    exit /b 1
)

REM Verifica se o pip está instalado e instala os requisitos
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip nao encontrado!
    echo Erro na instalacao do Python.
    pause
    exit /b 1
)

echo Instalando dependencias...
cd %~dp0
pip install -r requirements.txt

echo.
echo Para processar um comprovante, arraste a imagem para este arquivo batch
echo ou execute:
echo python ocr_windows.py caminho_da_imagem
echo.

if "%~1"=="" (
    echo Nenhuma imagem fornecida.
    echo Arraste uma imagem para este arquivo .bat para processar
    pause
) else (
    python ocr_windows.py "%~1"
    pause
)