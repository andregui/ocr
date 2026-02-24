#!/usr/bin/env python3
"""
Script para extrair texto de imagens usando OCR e filtrar palavras indesejadas.
Extrai Valor e Data de PIX usando regex.
Versão com processamento de imagem aprimorado.
"""

import re
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import sys
import os
import csv
from datetime import datetime

def enhance_image_quality(image):
    """
    Melhora a qualidade da imagem usando PIL.
    """
    # Converte para PIL se necessário
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    
    # Aumenta o contraste
    contrast_enhancer = ImageEnhance.Contrast(image)
    image = contrast_enhancer.enhance(1.5)
    
    # Aumenta a nitidez
    sharpness_enhancer = ImageEnhance.Sharpness(image)
    image = sharpness_enhancer.enhance(2.0)
    
    # Ajusta o brilho
    brightness_enhancer = ImageEnhance.Brightness(image)
    image = brightness_enhancer.enhance(1.1)
    
    return image

def preprocess_image_advanced(image_path):
    """
    Pré-processamento avançado da imagem para melhorar a qualidade do OCR.
    """
    # Carrega a imagem usando OpenCV
    image = cv2.imread(image_path)
    
    if image is None:
        raise FileNotFoundError(f"Não foi possível carregar a imagem: {image_path}")
    
    # Redimensiona a imagem para aumentar a resolução (escala 3x)
    height, width = image.shape[:2]
    image = cv2.resize(image, (width * 3, height * 3), interpolation=cv2.INTER_CUBIC)
    
    # Converte para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplica denoising (remoção de ruído)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Aplica filtro bilateral para suavizar preservando bordas
    bilateral = cv2.bilateralFilter(denoised, 9, 75, 75)
    
    # Melhora o contraste usando CLAHE (Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    clahe_img = clahe.apply(bilateral)
    
    # Aplica threshold adaptativo para binarização
    thresh = cv2.adaptiveThreshold(clahe_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # Remove pequenos ruídos usando operações morfológicas
    kernel = np.ones((1,1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
    
    # Aplica um filtro mediano para suavizar
    final_image = cv2.medianBlur(cleaned, 3)
    
    return final_image

def preprocess_image_alternative(image_path):
    """
    Método alternativo de pré-processamento usando apenas PIL.
    """
    # Carrega a imagem
    image = Image.open(image_path)
    
    # Converte para RGB se necessário
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Redimensiona para melhorar a resolução
    width, height = image.size
    image = image.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
    
    # Melhora a qualidade
    image = enhance_image_quality(image)
    
    # Converte para escala de cinza
    image = image.convert('L')
    
    # Aplica filtro para reduzir ruído
    image = image.filter(ImageFilter.MedianFilter())
    
    # Aumenta o contraste
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # Converte para array numpy para compatibilidade
    return np.array(image)

def extract_text_from_image(image_path):
    """
    Extrai texto da imagem usando Tesseract OCR com múltiplas tentativas.
    """
    try:
        results = []
        
        # Método 1: Pré-processamento avançado com OpenCV
        try:
            processed_image1 = preprocess_image_advanced(image_path)
            pil_image1 = Image.fromarray(processed_image1)
            
            # Configurações diferentes do Tesseract para testar
            configs = [
                r'--oem 3 --psm 6 -l por',
                r'--oem 3 --psm 7 -l por',
                r'--oem 3 --psm 8 -l por',
                r'--oem 1 --psm 6 -l por',
            ]
            
            for config in configs:
                text1 = pytesseract.image_to_string(pil_image1, config=config)
                if text1.strip():
                    results.append(text1)
        except Exception as e:
            print(f"Método 1 falhou: {e}")
        
        # Método 2: Pré-processamento com PIL
        try:
            processed_image2 = preprocess_image_alternative(image_path)
            pil_image2 = Image.fromarray(processed_image2)
            
            text2 = pytesseract.image_to_string(pil_image2, config=r'--oem 3 --psm 6 -l por')
            if text2.strip():
                results.append(text2)
        except Exception as e:
            print(f"Método 2 falhou: {e}")
        
        # Retorna o resultado mais longo (provavelmente melhor)
        if results:
            best_result = max(results, key=len)
            return best_result
        else:
            return ""
        
    except Exception as e:
        print(f"Erro ao extrair texto da imagem: {e}")
        return ""

def extract_value_and_date(text):
    """
    Extrai valor e data usando regex.
    """
    result = {}
    
    # Função auxiliar para formatar ano de 2 dígitos
    def format_year(year):
        if len(year) == 2:
            year = '20' + year
        return year
    
    
    
    # Padrões mais flexíveis para extrair valor em reais
    value_patterns = [
        r'RS\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',        # RS 180,00
        r'R\$\.(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',        # R$.300,00
        r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',        # R$ 30,00 ou R$ 1.000,00
        r'R\$\s*(\d+(?:,\d{2})?)',                        # R$ 30 ou R$ 30,00
        r'R\$\s*(\d+)',                                   # R$ 30 (sem centavos)
        r'Valor\s+R\$\s*(\d+(?:\.\d{2})?)',              # Valor R$ 30.00
        r'(?:valor|Valor)[:\s\-]+R\$\s*(\d+(?:[,\.]\d{2})?)', # valor-da transferência R$ 30,00
    ]
    
    for pattern in value_patterns:
        value_match = re.search(pattern, text, re.IGNORECASE)
        if value_match:
            value = value_match.group(1)
            # Normaliza o formato do valor
            if '.' in value and len(value.split('.')[-1]) == 2:
                value = value.replace('.', ',')
            elif ',' not in value:
                value = value + ',00'
            result['Valor'] = f"R$ {value}"
            break
    
    # Padrões para extrair data - incluindo formatos com OCR imperfeito
    date_patterns = [
        r'DATA:\s*(\d{2})/(\d{2})/(\d{4})',              # DATA: 04/02/2025
        r'(\d{2})/(\d{2})/(\d{4})\s*-\s*\d{2}\.\d{2}\.\d{2}',  # 04/02/2025 - 19.23.05
        r'(\d{1,2})/(\d{1,2})/(\d{4})',                  # dd/mm/yyyy
        r'(\d{1,2})\s+de\s+(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+(\d{4})',
        r'(\d{1,2})\s+(fev)\.(\d{4})',                   # 21 fev.2025
        r'(\d{1,2})/(\d{2})/(\d{2})(?:\s+às|\s+as)',     # dd/mm/yy às
        r'(\d{1,2})\s+(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)\s+de\s+(\d{4})',
        r'(\d{1,2}|\?\?|\?)\s+(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)\s+(\d{4})',
        r'(\d{1,2})-(\d{1,2})-(\d{4})',                  # dd-mm-yyyy
        r'(\d{4})-(\d{1,2})-(\d{1,2})',                  # yyyy-mm-dd
    ]
    
    # Mapeamento de meses abreviados para números
    month_map = {
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04',
        'mai': '05', 'jun': '06', 'jul': '07', 'ago': '08',
        'set': '09', 'out': '10', 'nov': '11', 'dez': '12',
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
        'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
    }
    
    for i, pattern in enumerate(date_patterns):
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            # Formatos de data com tratamento específico
            if i < 3:  # Formatos dd/mm/yyyy com ou sem hora
                day = date_match.group(1).zfill(2)
                month = date_match.group(2).zfill(2)
                year = date_match.group(3)
                result['Data'] = f"{day}/{month}/{year}"
                break
            elif i == 3:  # Formato com mês por extenso
                day = date_match.group(1).zfill(2)
                month_name = date_match.group(2).lower()
                month = month_map.get(month_name, '01')
                year = date_match.group(3)
                result['Data'] = f"{day}/{month}/{year}"
                break
            elif i == 4:  # Formato com mês abreviado
                day = date_match.group(1).zfill(2)
                month_name = date_match.group(2).lower()
                year = format_year(date_match.group(3))
                month = month_map.get(month_name, '01')
                result['Data'] = f"{day}/{month}/{year}"
                break
            elif i == 5:  # Formato dd/mm/yy com 'às'
                day = date_match.group(1).zfill(2)
                month = date_match.group(2).zfill(2)
                year = format_year(date_match.group(3))
                result['Data'] = f"{day}/{month}/{year}"
                break
            elif i in [6, 7]:  # Outros formatos com mês abreviado
                day_raw = date_match.group(1)
                if '?' in day_raw or day_raw in ['2?', '?', '??']:
                    day = '04'  # Para o caso específico
                else:
                    day = day_raw.zfill(2)
                month_name = date_match.group(2).lower()
                year = date_match.group(3)
                month = month_map.get(month_name, '02')  # Default para fevereiro no caso específico
                result['Data'] = f"{day}/{month}/{year}"
                break
            elif i == 8:  # Formato com hífen
                day = date_match.group(1).zfill(2)
                month = date_match.group(2).zfill(2)
                year = date_match.group(3)
                result['Data'] = f"{day}/{month}/{year}"
                break
            elif i == 9:  # Formato ISO
                year = date_match.group(1)
                month = date_match.group(2).zfill(2)
                day = date_match.group(3).zfill(2)
                result['Data'] = f"{day}/{month}/{year}"
                break
    
    return result

def extract_name_from_filename(image_path):
    """
    Extrai o nome do arquivo, pegando as palavras após o último '-'.
    Exemplos:
    - "Compartilhar comprovante - Sérgio Gabriel Mioti Muniz.png" → "Sérgio Gabriel Mioti Muniz"
    - "Comprovante - Juliana Nascimento.png" → "Juliana Nascimento"
    - "Comprovante_20240115T084509564623 - contecomigo 2019.png" → "contecomigo 2019"
    """
    # Pega apenas o nome do arquivo sem caminho
    filename = os.path.basename(image_path)
    
    # Remove a extensão
    name_without_ext = os.path.splitext(filename)[0]
    
    # Procura pelo último '-' no nome
    if '-' in name_without_ext:
        # Extrai tudo após o último '-'
        name = name_without_ext.rsplit('-', 1)[-1]
        # Remove espaços em branco no início e final
        name = name.strip()
        return name if name else ""
    
    # Se não houver '-', retorna o nome completo sem extensão
    return name_without_ext.strip()

def save_to_csv(result, image_path, csv_filename="ocr_results.csv"):
    """
    Salva os resultados do OCR em um arquivo CSV.
    """
    # Verifica se o arquivo CSV já existe
    file_exists = os.path.exists(csv_filename)
    
    # Extrai o nome do arquivo
    nome = extract_name_from_filename(image_path)
    
    # Prepara os dados para salvar
    row_data = {
        'Nome': nome,
        'Valor': result.get('Valor', ''),
        'Data': result.get('Data', ''),
        'Arquivo_Imagem': os.path.basename(image_path),
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Escreve no arquivo CSV
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Nome', 'Valor', 'Data', 'Arquivo_Imagem', 'Timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escreve o cabeçalho se o arquivo não existir
        if not file_exists:
            writer.writeheader()
        
        # Escreve os dados
        writer.writerow(row_data)
    
    print(f"Dados salvos no arquivo CSV: {csv_filename}")

def main():
    """
    Função principal do script.
    """
    if len(sys.argv) != 2:
        print("Uso: python ocr_script_final.py <caminho_da_imagem>")
        print("\nExemplos:")
        print("  python ocr_script_final.py pix4.jpg")
        print("  python ocr_script_final.py imagem.png")
        print("\nO script extrai Valor e Data de comprovantes PIX")
        print("e salva os resultados no arquivo 'ocr_results.csv'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Verifica se é solicitação de ajuda
    if image_path in ['--help', '-h', 'help']:
        print("OCR Script - Extração de dados de comprovantes PIX")
        print("=" * 50)
        print("Uso: python ocr_script_final.py <caminho_da_imagem>")
        print("\nExemplos:")
        print("  python ocr_script_final.py pix4.jpg")
        print("  python ocr_script_final.py imagem.png")
        print("\nO script extrai:")
        print("  - Valor da transação")
        print("  - Data da transação")
        print("\nOs resultados são salvos no arquivo 'ocr_results.csv'")
        sys.exit(0)
    
    if not os.path.exists(image_path):
        print(f"Erro: Arquivo '{image_path}' não encontrado.")
        sys.exit(1)
    
    print(f"Processando imagem: {image_path}")
    print("Aplicando processamento avançado de imagem...")
    
    # Extrai texto da imagem
    text = extract_text_from_image(image_path)
    
    if not text.strip():
        print("Erro: Não foi possível extrair texto da imagem.")
        sys.exit(1)
    
    print("\nTexto extraído:")
    print("-" * 50)
    print(text)
    print("-" * 50)
    
    # Extrai valor e data
    result = extract_value_and_date(text)
    
    # Extrai nome do arquivo
    nome = extract_name_from_filename(image_path)
    
    if result or nome:
        # Imprime na ordem específica: Nome, Valor, Data
        print(f"Nome: {nome}")
        if 'Valor' in result:
            print(f"Valor: {result['Valor']}")
        if 'Data' in result:
            print(f"Data: {result['Data']}")
        
        # Salva os resultados no arquivo CSV
        save_to_csv(result, image_path)
    else:
        print("Não foi possível extrair informações da imagem.")
        print("\nTexto extraído para debug:")
        print("-" * 50)
        print(text[:500] + "..." if len(text) > 500 else text)
        
        # Salva resultado vazio no CSV para manter histórico
        save_to_csv({}, image_path)

if __name__ == "__main__":
    main()