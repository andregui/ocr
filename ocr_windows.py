#!/usr/bin/env python3
"""
Script para extrair texto de imagens usando OCR e filtrar palavras indesejadas.
Versão adaptada para Windows.
"""

import os
import sys
import pytesseract
from ocr import main as ocr_main

# Configura o caminho do Tesseract (ajuste conforme seu caminho de instalação)
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def check_requirements():
    """Verifica se todos os requisitos estão instalados"""
    try:
        import cv2
        import numpy
        from PIL import Image
    except ImportError as e:
        print(f"Erro: Biblioteca {e.name} não encontrada.")
        print("\nPor favor, instale as dependências necessárias usando:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    # Verifica se o Tesseract está instalado
    if not os.path.exists(tesseract_path):
        print("Erro: Tesseract não encontrado no caminho padrão.")
        print("\nPor favor:")
        print("1. Instale o Tesseract-OCR do site:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print("\n2. Verifique se o caminho de instalação está correto:")
        print(f"   {tesseract_path}")
        print("\n3. Ou atualize a variável tesseract_path neste script com o caminho correto")
        sys.exit(1)

def main():
    """Função principal adaptada para Windows"""
    # Configura o caminho do Tesseract
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    # Verifica os requisitos
    check_requirements()
    
    # Executa o OCR
    ocr_main()

if __name__ == "__main__":
    main()