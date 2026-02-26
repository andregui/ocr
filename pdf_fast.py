#!/usr/bin/env python3
"""Extrai nome, valor e data de PDFs com texto pesquisável (sem OCR).

Uso: python pdf_fast.py <arquivo.pdf>
"""
import re
import os
import sys
from datetime import datetime
import csv

try:
    from PyPDF2 import PdfReader
except Exception:
    print('Erro: PyPDF2 não encontrado. Instale com: pip install PyPDF2')
    sys.exit(1)


def extract_name_from_filename(pdf_path):
    filename = os.path.basename(pdf_path)
    name_without_ext = os.path.splitext(filename)[0]
    if '-' in name_without_ext:
        name = name_without_ext.rsplit('-', 1)[-1].strip()
        return name if name else name_without_ext.strip()
    return name_without_ext.strip()


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    texts = []
    for page in reader.pages:
        try:
            t = page.extract_text()
        except Exception:
            t = ''
        if t:
            texts.append(t)
    return '\n'.join(texts)


def normalize_currency_text(text):
    # Normaliza variações comuns que o OCR confundia (RS, R5) — aqui por segurança
    text = re.sub(r'R[\s]*[Ss5]\s*(?=\d)', 'R$ ', text)
    text = re.sub(r'R\s*\$\s*', 'R$ ', text)
    return text


def extract_value_and_date(text):
    result = {}
    txt = normalize_currency_text(text)

    # Extrair valor (formato brasileiro)
    m = re.search(r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', txt)
    if m:
        val = m.group(1)
        if '.' in val and len(val.split('.')[-1]) == 2:
            val = val.replace('.', ',')
        elif ',' not in val:
            val = val + ',00'
        result['Valor'] = f"R$ {val}"

    # Extrair data dd/mm/yyyy
    dm = re.search(r'(\d{2})/(\d{2})/(\d{4})', text)
    if dm:
        day = dm.group(1).zfill(2)
        month = dm.group(2).zfill(2)
        year = dm.group(3)
        result['Data'] = f"{day}/{month}/{year}"

    return result


def save_to_csv(result, pdf_path, csv_filename="ocr_results_pdf.csv"):
    file_exists = os.path.exists(csv_filename)
    row = {
        'Nome': result.get('Nome', ''),
        'Valor': result.get('Valor', ''),
        'Data': result.get('Data', ''),
        'Arquivo': os.path.basename(pdf_path),
        'Arquivo_Caminho': os.path.abspath(pdf_path),
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(csv_filename, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['Nome', 'Valor', 'Data', 'Arquivo', 'Arquivo_Caminho', 'Timestamp']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def main():
    if len(sys.argv) != 2:
        print('Uso: python pdf_fast.py <arquivo.pdf>')
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Erro: arquivo '{pdf_path}' não encontrado")
        sys.exit(1)

    print(f"Processando: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        print('Nenhum texto extraível do PDF.')
        sys.exit(1)

    print('\nTrecho do texto extraído:')
    print('-' * 50)
    print(text[:1000] + ('...' if len(text) > 1000 else ''))
    print('-' * 50)

    result = {}
    result['Nome'] = extract_name_from_filename(pdf_path)
    result.update(extract_value_and_date(text))

    if 'Nome' in result:
        print(f"Nome: {result['Nome']}")
    if 'Valor' in result:
        print(f"Valor: {result['Valor']}")
    if 'Data' in result:
        print(f"Data: {result['Data']}")

    save_to_csv(result, pdf_path)
    print('Resultados salvos em ocr_results_pdf.csv')


if __name__ == '__main__':
    main()
