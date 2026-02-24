#!/usr/bin/env python3
"""
Script OCR simplificado para testes rápidos - usa a nova lógica
"""

import re
import os
import sys
import pytesseract
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import csv
from datetime import datetime

tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tesseract_path

def extract_text_simple(image_path):
    """Extrai texto com pré-processamento leve (pode demorar ~10s).

    Estratégia:
    - tenta pré-processamento com OpenCV (grayscale, upscale, CLAHE,
      bilateral filter, adaptive threshold, pequeno fechamento)
    - chama Tesseract com PSM 6
    - em caso de erro volta ao método simples com Pillow
    """
    try:
        # Carrega imagem com OpenCV suportando caminhos com espaços/UTF-8
        arr = np.fromfile(image_path, dtype=np.uint8)
        img_cv = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img_cv is None:
            raise ValueError('Não foi possível abrir a imagem com OpenCV')

        # Escala e converte para grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape[:2]
        gray = cv2.resize(gray, (w*2, h*2), interpolation=cv2.INTER_CUBIC)

        # Redução de ruído preservando contornos
        gray = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

        # Melhora contraste local
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)

        # Binarização adaptativa (ajustável) - robusto a iluminação
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 15, 9)

        # Pequeno fechamento para conectar traços finos do cifrão
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel, iterations=1)

        # Converter para PIL para passar ao pytesseract
        pil_img = Image.fromarray(gray)

        # Config: PSM 6 (assume bloco de texto) — não usar whitelist muito restritiva
        config = '--psm 6'
        text = pytesseract.image_to_string(pil_img, lang='por', config=config)
        return text
    except Exception:
        # Fallback simples (rápido)
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            width, height = image.size
            image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
            return pytesseract.image_to_string(image, lang='por')
        except Exception as e:
            print(f"Erro ao extrair texto: {e}")
            return ""

def extract_name_from_filename(image_path):
    """
    Extrai o nome do arquivo, pegando as palavras após o último '-'.
    """
    filename = os.path.basename(image_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    if '-' in name_without_ext:
        name = name_without_ext.rsplit('-', 1)[-1]
        name = name.strip()
        return name if name else ""
    
    return name_without_ext.strip()

def extract_name_from_origem_section(text):
    """Extrai nome da seção de Origem de forma robusta"""
    # Padrão muito flexível para aceitar erros de OCR
    origem_match = re.search(
        r'[^\n]*?\s+Origem(.+?)(?=\s*Instituição)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    
    if not origem_match:
        return None
    
    section = origem_match.group(1)
    
    # Extrair todas as linhas não vazias
    lines = [line.strip() for line in section.split('\n') if line.strip()]
    
    # Palavras-chave para filtrar
    keywords = ['Nome', 'CPF', 'Agência', 'Conta', 'Tipo', 'PAGAMENTOS', 'IP']
    
    # Processar linhas
    processed_lines = []
    for line in lines:
        if line.lower().startswith('nome '):
            line = line[5:].strip()
        
        if not any(line.lower() == kw.lower() for kw in keywords) and line:
            processed_lines.append(line)
    
    if processed_lines:
        name = ' '.join(processed_lines)
        name = re.sub(r'\s+', ' ', name).strip()
        name = re.sub(r'[^A-Za-zÀ-ÿ\s]', '', name).strip()
        
        # Verifica filtros
        if (not re.search(r'IGREJA BATISTA EM CAVALEIROS|INSTITUI|CPF|PIX|BANCO|TRANSFERENCIA|ITAU|UNIBANCO|CORA|SCF|PAGAMENTOS', name, re.IGNORECASE) 
            and len(name) > 5 and len(name.split()) >= 2):
            return name
    
    return None

def extract_name_value_and_date(text, image_path):
    """Extrai nome (do arquivo), valor e data"""
    result = {}
    
    # Extrai nome do arquivo
    name = extract_name_from_filename(image_path)
    if name:
        result['Nome'] = name
    
    # Normaliza possíveis confusões do OCR antes de extrair (RS, R5, R S)
    text_norm = text
    # Substitui casos como 'RS 180', 'R5 180', 'R S180' por 'R$ 180'
    text_norm = re.sub(r'R[\s]*[Ss5]\s*(?=\d)', 'R$ ', text_norm)
    text_norm = re.sub(r'R\s*\$\s*', 'R$ ', text_norm)

    # Extrair valor a partir do texto normalizado
    value_match = re.search(r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', text_norm)
    if value_match:
        value = value_match.group(1)
        if '.' in value and len(value.split('.')[-1]) == 2:
            value = value.replace('.', ',')
        elif ',' not in value:
            value = value + ',00'
        result['Valor'] = f"R$ {value}"
    
    # Extrair data
    date_match = re.search(r'(\d{2})/(\d{2})/(\d{4})', text)
    if date_match:
        day = date_match.group(1).zfill(2)
        month = date_match.group(2).zfill(2)
        year = date_match.group(3)
        result['Data'] = f"{day}/{month}/{year}"
    
    return result

def save_to_csv(result, image_path, csv_filename="ocr_results.csv"):
    """Salva os resultados no CSV"""
    file_exists = os.path.exists(csv_filename)
    
    row_data = {
        'Nome': result.get('Nome', ''),
        'Valor': result.get('Valor', ''),
        'Data': result.get('Data', ''),
        'Arquivo_Imagem': os.path.basename(image_path),
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Nome', 'Valor', 'Data', 'Arquivo_Imagem', 'Timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(row_data)
    
    print(f"Dados salvos no arquivo CSV")

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("Uso: python script.py <imagem>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Erro: Arquivo '{image_path}' não encontrado.")
        sys.exit(1)
    
    print(f"Processando imagem: {image_path}")
    
    # Extrai texto
    text = extract_text_simple(image_path)
    
    if not text.strip():
        print("Erro: Não foi possível extrair texto da imagem.")
        sys.exit(1)
    
    print("\nTexto extraído:")
    print("-" * 50)
    print(text[:300] + "..." if len(text) > 300 else text)
    print("-" * 50)
    
    # Extrai dados (passa image_path)
    result = extract_name_value_and_date(text, image_path)
    
    if result:
        if 'Nome' in result:
            print(f"Nome: {result['Nome']}")
        if 'Valor' in result:
            print(f"Valor: {result['Valor']}")
        if 'Data' in result:
            print(f"Data: {result['Data']}")
        
        save_to_csv(result, image_path)
    else:
        print("Não foi possível extrair dados da imagem.")
        save_to_csv({}, image_path)

if __name__ == "__main__":
    main()
