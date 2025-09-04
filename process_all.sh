#!/bin/bash

echo "Iniciando processamento OCR para todas as imagens na pasta pix..."

# Verifica se a pasta pix existe
if [ ! -d "pix" ]; then
    echo "Erro: A pasta 'pix' não foi encontrada!"
    exit 1
fi

# Conta quantos arquivos de imagem existem
image_count=$(find pix -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | wc -l)

if [ $image_count -eq 0 ]; then
    echo "Nenhuma imagem encontrada na pasta 'pix'!"
    exit 1
fi

echo "Encontradas $image_count imagens para processar."
echo

# Processa cada imagem na pasta pix
count=1
find pix -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | while read image; do
    echo "[$count/$image_count] Processando: $image"
    python ocr.py "$image"
    echo "----------------------------------------"
    ((count++))
done

echo
echo "Processamento concluído! Verifique o arquivo ocr_results.csv para os resultados."