sudo apt update
sudo apt install python3 -y
sudo apt install python3-pip -y
sudo apt-get install python3-distutils -y
sudo apt install tesseract-ocr -y
sudo apt install python3-venv -y
if [ ! -d ".venv" ]; then
    mkdir .venv
fi
python3 -m venv .venv
source .venv/bin/activate
#pip install -r requirements.txt 