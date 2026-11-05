# -*- coding: utf-8 -*-
"""Modul ASR: pemeriksaan rekaman, transkripsi Google Speech Recognition, dan penanganan gangguan suara.
"""

from __future__ import annotations

import io
import wave

import numpy as np

# SpeechRecognition dimuat dengan try-except agar aplikasi tetap terbuka (mode ketik guru)
# walaupun pustakanya belum terpasang.
try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover
    sr = None

from modul.konfigurasi import BAHASA_ASR, BATAS_WAKTU_ASR, DURASI_MINIMUM, RMS_MINIMUM


# =============================================================================
# MODUL ASR DAN PENANGANAN KESALAHAN SUARA
# =============================================================================


# Pesan yang dibacakan TTS untuk tiap jenis gangguan.
PESAN_GANGGUAN = {
    "kosong": "Hmm, belum ada suara yang masuk. Yuk, dekatkan mikrofon, lalu bicara lebih keras!",
    "terpotong": "Suaramu terpotong. Yuk, ucapkan sampai selesai, baru tekan tombol berhenti!",
    "tidak_jelas": "Maaf, suaramu belum terdengar jelas, yuk coba ucapkan lagi!",
    "kurang_yakin": "Maaf, aku belum yakin mendengarnya. Yuk, ucapkan lagi pelan-pelan!",
    "internet": "Maaf, sambungan internetnya sedang terganggu. Minta tolong orang dewasa memeriksanya, ya!",
    "rusak": "Rekamannya tidak bisa dibuka. Yuk, kita rekam sekali lagi!",
    "pustaka": "Alat pengenal suara belum lengkap di komputer ini. Minta tolong orang dewasa memeriksanya, ya!",
}

# Lebar sampel WAV (byte) -> (tipe numpy, titik nol, skala) untuk mengubah ke rentang -1..1.
FORMAT_PCM = {1: (np.uint8, 128, 128), 2: (np.int16, 0, 2**15), 4: (np.int32, 0, 2**31)}


def gangguan(kategori: str) -> dict:
    """Hasil untuk rekaman yang belum bisa dinilai. Kategorinya memilih pesan di PESAN_GANGGUAN.

    Semua fungsi suara mengembalikan dict dengan kunci "gangguan": None berarti rekaman
    aman diproses. Gangguan tidak pernah mengurangi kesempatan anak.
    """
    return {"gangguan": kategori}


def periksa_audio(data_wav: bytes) -> dict:
    """Memeriksa rekaman sebelum dikirim ke ASR.

    Tujuannya memberi pesan yang tepat, karena ASR hanya bisa berkata "tidak dimengerti":
        - berkas kosong atau rusak    -> rusak
        - durasi terlalu pendek       -> terpotong
        - energi RMS sangat kecil     -> kosong
    Rekaman yang berhenti saat suara masih keras ditandai ujung_terpotong.
    Tanda ini baru dipakai jika jawabannya salah, jadi jawaban benar tetap diterima.
    Hasil: {"gangguan", "durasi", "rms", "ujung_terpotong"}.
    """
    try:
        with wave.open(io.BytesIO(data_wav), "rb") as wav:
            kanal, lebar, laju = wav.getnchannels(), wav.getsampwidth(), wav.getframerate()
            bingkai = wav.getnframes()
            mentah = wav.readframes(bingkai)
    except (wave.Error, EOFError, ValueError):
        return gangguan("rusak")

    if bingkai == 0 or laju == 0:
        return gangguan("terpotong")
    if lebar not in FORMAT_PCM:  # format lain: biarkan ASR yang menilai
        return {"gangguan": None, "durasi": bingkai / laju, "rms": 1.0, "ujung_terpotong": False}
    tipe, nol, skala = FORMAT_PCM[lebar]
    sinyal = (np.frombuffer(mentah, dtype=tipe).astype(np.float64) - nol) / skala

    if kanal > 1:
        sinyal = sinyal.reshape(-1, kanal).mean(axis=1)
    durasi = len(sinyal) / laju
    if durasi < DURASI_MINIMUM:
        return gangguan("terpotong")

    rms = float(np.sqrt(np.mean(sinyal**2)))
    if rms < RMS_MINIMUM:
        return gangguan("kosong")

    # Bandingkan energi 150 ms terakhir dengan energi seluruh rekaman.
    rms_ekor = float(np.sqrt(np.mean(sinyal[-int(0.15 * laju):] ** 2)))
    return {"gangguan": None, "durasi": durasi, "rms": rms, "ujung_terpotong": rms_ekor >= 0.9 * rms}


def transkripsi(data_wav: bytes) -> dict:
    """Mengubah rekaman WAV menjadi teks. Semua kegagalan menjadi kategori gangguan.

    Rekaman datang dari st.audio_input, jadi mikrofon di peramban pengguna yang dipakai
    dan PyAudio tidak diperlukan. SpeechRecognition memproses berkas lewat sr.AudioFile.
    Hasil: {"gangguan", "alternatif" (n-best), "keyakinan", "ujung_terpotong"}.
    """
    if sr is None:
        return gangguan("pustaka")
    info = periksa_audio(data_wav)
    if info["gangguan"]:
        return info

    pengenal = sr.Recognizer()
    pengenal.operation_timeout = BATAS_WAKTU_ASR
    try:
        with sr.AudioFile(io.BytesIO(data_wav)) as sumber:
            rekaman = pengenal.record(sumber)
        # show_all=True meminta seluruh hipotesis (n-best) beserta keyakinannya.
        jawaban_api = pengenal.recognize_google(rekaman, language=BAHASA_ASR, show_all=True)
    except sr.UnknownValueError:
        # Suara ada, tetapi tidak bisa dimengerti oleh ASR.
        return gangguan("tidak_jelas")
    except (sr.RequestError, ConnectionError, TimeoutError):
        # Tidak ada internet, kunci API ditolak, layanan gangguan, atau waktu habis.
        return gangguan("internet")
    except OSError:
        # Misalnya pengubah FLAC bawaan pustaka tidak tersedia di sistem ini.
        return gangguan("pustaka")
    except (ValueError, EOFError, wave.Error):
        # Format berkas tidak bisa dibaca oleh sr.AudioFile, biasanya rekaman terpotong.
        return gangguan("terpotong")

    # Beberapa versi pustaka mengembalikan [] jika tidak ada hasil, bukan melempar error.
    alternatif, keyakinan = [], None
    if isinstance(jawaban_api, str):
        alternatif = [jawaban_api]
    elif isinstance(jawaban_api, dict) and jawaban_api.get("alternative"):
        daftar = jawaban_api["alternative"]
        alternatif = [a["transcript"] for a in daftar if a.get("transcript")]
        keyakinan = daftar[0].get("confidence")
    if not alternatif:
        return gangguan("tidak_jelas")
    return {"gangguan": None, "alternatif": alternatif, "keyakinan": keyakinan,
            "ujung_terpotong": info["ujung_terpotong"]}
