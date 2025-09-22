FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ffmpeg installieren
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY . .


# Whisper-Modell vorab laden (base)
RUN python -c "import whisper; whisper.load_model('base')"

CMD ["python", "main.py"]
