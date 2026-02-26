#!/usr/bin/env python3
"""Processa todos os arquivos de um diretório:
- se for imagem (jpg,jpeg,png,gif) chama `ocr_fast.py`
- se for pdf chama `pdf_fast.py`

Uso:
  python batch_process.py --dir C:\caminho\para\pasta [--recursive] [--timeout 30]
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path


IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif'}


def call_script(script_path, file_path, timeout):
    cmd = [sys.executable, str(script_path), str(file_path)]
    try:
        print(f"Chamando: {' '.join(cmd)}")
        subprocess.run(cmd, check=False, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"Timeout ao processar {file_path} (>{timeout}s)")
    except Exception as e:
        print(f"Erro ao chamar {script_path} para {file_path}: {e}")


def process_directory(directory, recursive, timeout):
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        print(f"Diretório não encontrado: {directory}")
        return

    script_dir = Path(__file__).parent
    ocr_script = script_dir / 'ocr_fast.py'
    pdf_script = script_dir / 'pdf_fast.py'

    if recursive:
        files = directory.rglob('*')
    else:
        files = directory.iterdir()

    for p in files:
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext in IMAGE_EXTS:
            call_script(ocr_script, p, timeout)
        elif ext == '.pdf':
            call_script(pdf_script, p, timeout)
        else:
            print(f"Ignorado (tipo não suportado): {p}")


def main():
    ap = argparse.ArgumentParser(description='Processa imagens e PDFs em lote')
    ap.add_argument('--dir', '-d', default='.', help='Diretório a varrer')
    ap.add_argument('--recursive', '-r', action='store_true', help='Varrer subpastas')
    ap.add_argument('--timeout', '-t', type=int, default=30, help='Timeout (s) por arquivo')
    args = ap.parse_args()

    process_directory(args.dir, args.recursive, args.timeout)


if __name__ == '__main__':
    main()
