# OCR Script - Docker

Este projeto contém um script Python para extrair texto de imagens usando OCR (Optical Character Recognition) com suporte a Docker.

## Características

- Extrai Nome, Valor e Data de comprovantes PIX
- Filtra strings indesejadas como "CHARLES DA CONCEICAO"
- Salva resultados em arquivo CSV
- Suporte completo ao Docker

## Dependências

O script utiliza as seguintes bibliotecas Python:
- OpenCV (cv2)
- NumPy
- Pillow (PIL)
- pytesseract
- Tesseract OCR engine

## Como usar com Docker

### 1. Construir a imagem Docker

```bash
docker build -t ocr-script .
```

### 2. Executar o script

Para processar uma imagem específica:

```bash
docker run -v $(pwd):/app/output ocr-script pix4.jpg
```

Para processar uma imagem e salvar o CSV na pasta atual:

```bash
docker run -v $(pwd):/app/output ocr-script pix4.jpg
```

### 3. Verificar os resultados

O arquivo `ocr_results.csv` será criado no diretório atual com os resultados do processamento.

### 4. Executar de forma interativa

Para entrar no container e executar múltiplos comandos:

```bash
docker run -it -v $(pwd):/app/output ocr-script bash
```

Dentro do container, você pode executar:

```bash
python ocr_script_final.py pix1.jpg
python ocr_script_final.py pix2.jpg
cat ocr_results.csv
```

## Estrutura de arquivos

```
.
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── ocr_script_final.py
├── *.jpg (imagens para processar)
└── ocr_results.csv (arquivo de saída)
```

## Formato do CSV de saída

O arquivo CSV contém as seguintes colunas:
- Nome: Nome extraído da imagem
- Valor: Valor em reais
- Data: Data da transação
- Arquivo_Imagem: Nome do arquivo processado
- Timestamp: Data e hora do processamento

## Troubleshooting

Se encontrar problemas com permissões de arquivo, execute:

```bash
sudo docker run -v $(pwd):/app/output ocr-script pix4.jpg
```

Para debug, você pode executar o container e verificar os logs:

```bash
docker run -it ocr-script bash
```
