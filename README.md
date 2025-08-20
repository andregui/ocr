# OCR Script para Comprovantes PIX

Este projeto contém um script Python para extrair informações de comprovantes PIX usando OCR (Optical Character Recognition) com suporte a Docker.

## Características

- Extrai automaticamente:
  - Nome do pagador/beneficiário
  - Valor da transação
  - Data da transação
- Filtra strings indesejadas como "FULANO DE TAL"
- Salva resultados em arquivo CSV com timestamp
- Imagem Docker otimizada (~1.12GB)
- Suporte a português via Tesseract OCR

## Dependências

O projeto utiliza:
- Python 3.12
- OpenCV (cv2)
- NumPy
- Pillow (PIL)
- pytesseract
- Tesseract OCR engine com suporte a português

Todas as dependências são gerenciadas automaticamente via Docker.

## Como usar

### 1. Construir a imagem Docker

```bash
docker build -t ocr .
```

### 2. Processar uma imagem

Para processar um comprovante PIX:

```bash
docker run -v $(pwd):/app ocr pix/imagem.jpg
```

Onde:
- `$(pwd):/app`: monta o diretório atual no container
- `imagem.jpg`: caminho para a imagem a ser processada (relativo ao diretório atual)

### 3. Verificar resultados

O script gera um arquivo `ocr_results.csv` no diretório atual com os resultados. Para visualizar:

```bash
cat ocr_results.csv
```

## Estrutura do Projeto

```
.
├── Dockerfile          # Configuração do container Docker
├── requirements.txt    # Dependências Python
├── ocr.py             # Script principal de OCR
├── pix/               # Diretório com imagens de exemplo
│   ├── pix.jpg
│   ├── pix2.jpg
│   └── ...
└── ocr_results.csv    # Arquivo de saída com resultados
```

## Formato do CSV

O arquivo de saída contém as seguintes colunas:
- `Nome`: Nome extraído da imagem
- `Valor`: Valor da transação (formato R$ XX,XX)
- `Data`: Data da transação (formato DD/MM/AAAA)
- `Arquivo_Imagem`: Nome do arquivo processado
- `Timestamp`: Data e hora do processamento (formato YYYY-MM-DD HH:MM:SS)

## Troubleshooting

### Problemas de permissão

Se encontrar problemas com permissões de arquivo:

```bash
sudo chown -R $USER:$USER ocr_results.csv
```

### Ajuda do script

Para ver as opções disponíveis:

```bash
docker run ocr --help
```

### Debug

Para entrar no container em modo interativo:

```bash
docker run -it --entrypoint bash ocr
```

## Notas de Segurança

- A imagem Docker usa uma base Python slim para minimizar a superfície de ataque
- O container executa sem privilégios elevados
- Os arquivos são montados somente leitura quando possível
- Todas as dependências são instaladas de fontes oficiais
