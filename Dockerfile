# Use uma imagem base oficial do Python
FROM python:3.11-slim

# Definir o diretório de trabalho no container
WORKDIR /app

# Instalar dependências do sistema necessárias para OpenCV, Tesseract e processamento de imagem
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Copiar o arquivo de requirements primeiro (para aproveitar o cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o script Python e as imagens para o container
COPY ocr_script_final.py .
COPY *.jpg ./

# Criar diretório para arquivos de saída
RUN mkdir -p /app/output

# Configurar variável de ambiente para o Tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# Definir o comando padrão
# O usuário pode passar o nome da imagem como argumento
ENTRYPOINT ["python", "ocr_script_final.py"]

# Comando padrão (pode ser sobrescrito)
CMD ["--help"]
