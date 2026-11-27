# syntax=docker/dockerfile:1

# Panggung Dongeng Nusantara - Tugas Pemrograman Akhir NLP
# Dibangun di atas python:3.12-slim. espeak-ng ditambahkan untuk cadangan
# TTS luring pyttsx3 (dipakai hanya jika edge-tts dan gTTS gagal).

FROM python:3.12-slim

LABEL maintainer="Kelompok NLP - UKDW" \
      description="Kuis interaktif belajar bahasa Indonesia berbasis suara (TTS + ASR)"

# Pustaka sistem:
# - espeak-ng: suara cadangan luring untuk pyttsx3 (hanya menulis ke .wav
#   di server, tidak memutar lewat perangkat suara, jadi tidak perlu
#   pustaka ALSA seperti libasound2/libasound2t64)
# - ffmpeg: dipakai gTTS/pydub untuk konversi audio
# - curl: untuk HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
        espeak-ng \
        ffmpeg \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Salin requirements dulu agar layer cache pip terpakai ulang
# selama requirements.txt tidak berubah (build ulang lebih cepat).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh proyek. .dockerignore membuang berkas yang tidak perlu
# (git, __pycache__, docs/cerita-rakyat/sumber, dsb).
COPY . .

# Jalankan sebagai pengguna non-root
RUN useradd --create-home --uid 1000 app \
    && chown -R app:app /app
USER app

# Streamlit tidak butuh PyAudio di sini: mikrofon direkam di peramban
# pengguna (lihat aset/mikrofon/), bukan di server.
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "dongeng_nusantara.py"]
