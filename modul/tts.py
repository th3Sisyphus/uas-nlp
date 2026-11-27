# -*- coding: utf-8 -*-
"""Modul TTS: teks menjadi suara dengan edge-tts sebagai mesin utama.

Cadangan otomatis tetap sama: gTTS, lalu pyttsx3 (luring).
"""

from __future__ import annotations

import asyncio
import io
import os
import tempfile
from pathlib import Path

import streamlit as st

# gTTS dimuat dengan try-except agar aplikasi tetap terbuka walaupun pustakanya belum terpasang.
try:
    from gtts import gTTS
    from gtts.tts import gTTSError
except ImportError:  # pragma: no cover
    gTTS = None
    gTTSError = Exception

from modul.konfigurasi import BAHASA_TTS, BATAS_WAKTU_TTS, SUARA_TTS
from modul.speaker import tampilkan_speaker


# =============================================================================
# MODUL TTS
# =============================================================================


@st.cache_data(show_spinner=False, max_entries=300)
def _suara_edge(teks: str, pelan: bool, suara: str) -> bytes:
    """Membuat MP3 dengan edge-tts (butuh internet).

    Hasil di-cache agar teks yang sama tidak disintesis ulang. Jika gagal, fungsi
    melempar error sehingga st.cache_data tidak menyimpan kegagalan.
    """
    import edge_tts

    # pelan: 15% lebih lambat, sama seperti atur pelan di gTTS.
    rate = "-15%" if pelan else "+0%"

    async def tulis() -> bytes:
        data = bytearray()
        # Communicate dibuat di dalam korutin: konstruktornya bisa menyentuh jaringan.
        async for potong in edge_tts.Communicate(
                teks, suara, rate=rate, connect_timeout=BATAS_WAKTU_TTS).stream():
            if potong["type"] == "audio":
                data.extend(potong["data"])
        return bytes(data)

    hasil = asyncio.run(tulis())
    if not hasil:
        raise RuntimeError("edge-tts tidak menghasilkan suara")
    return hasil


@st.cache_data(show_spinner=False, max_entries=300)
def _suara_gtts(teks: str, pelan: bool) -> bytes:
    """Membuat MP3 dengan gTTS. Hasil di-cache agar teks yang sama tidak diunduh ulang.

    Jika gagal, fungsi melempar error sehingga st.cache_data tidak menyimpan kegagalan.
    """
    if gTTS is None:
        raise RuntimeError("gTTS belum terpasang")
    # lang_check=False: lewati permintaan web untuk memeriksa daftar bahasa.
    suara = gTTS(text=teks, lang=BAHASA_TTS, slow=pelan, lang_check=False, timeout=BATAS_WAKTU_TTS)
    wadah = io.BytesIO()
    suara.write_to_fp(wadah)
    return wadah.getvalue()


def _suara_pyttsx3(teks: str) -> bytes | None:
    """Cadangan TTS luring. Kualitas bergantung pada suara yang terpasang di komputer."""
    try:
        import pyttsx3
    except ImportError:
        return None
    jalur = ""
    try:
        try:  # Windows: thread Streamlit perlu inisialisasi COM untuk SAPI5.
            import pythoncom

            pythoncom.CoInitialize()
        except ImportError:
            pass
        mesin = pyttsx3.init()
        for suara in mesin.getProperty("voices"):
            if "indones" in f"{suara.id} {suara.name}".lower():
                mesin.setProperty("voice", suara.id)
                break
        mesin.setProperty("rate", 150)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as berkas:
            jalur = berkas.name
        mesin.save_to_file(teks, jalur)
        mesin.runAndWait()
        data = Path(jalur).read_bytes()
        return data or None
    except Exception:  # driver suara tiap sistem operasi berbeda-beda errornya
        return None
    finally:
        if jalur and os.path.exists(jalur):
            os.remove(jalur)


def buat_suara(teks: str, pelan: bool = False) -> tuple[bytes | None, str]:
    """Mengembalikan (data_audio, format). data_audio None jika semua mesin TTS gagal."""
    try:
        return _suara_edge(teks, pelan, SUARA_TTS), "audio/mpeg"
    except Exception:   # internet putus, layanan menolak, pustaka belum terpasang
        pass
    try:
        return _suara_gtts(teks, pelan), "audio/mpeg"
    except (gTTSError, RuntimeError, ValueError, OSError):
        return _suara_pyttsx3(teks), "audio/wav"


def putar_suara(teks: str, autoplay: bool = True, kunci: str = "utama") -> str:
    """Menampilkan tombol pemutar suara untuk teks. Jika TTS gagal, teks tetap tampil di layar.

    kunci membedakan beberapa pemutar pada satu halaman. nonce_suara ikut jadi bagian
    kunci supaya kalimat yang sama diputar ulang sebagai komponen baru.
    Mengembalikan "selesai" bila audio sudah habis atau tidak tersedia, selain itu None.
    """
    data, format_audio = buat_suara(teks, st.session_state.get("atur_pelan", False))
    if data is None:
        st.caption("Suara narator belum tersedia. Periksa internet, lalu minta orang dewasa membacakan.")
        return "selesai"
    nonce = st.session_state.get("nonce_suara", 0)
    return tampilkan_speaker(data, format_audio, autoplay=autoplay, kunci=f"suara_{kunci}_{nonce}")
