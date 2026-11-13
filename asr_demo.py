# -*- coding: utf-8 -*-
"""
asr_demo.py -- Prototipe Automated Speech Recognition (ASR), Minggu 1.

Merekam suara dari mikrofon, mengenalinya sebagai bahasa Indonesia (id-ID)
dengan Google Speech Recognition (pustaka SpeechRecognition), lalu mencetak
teks hasilnya. Belum ada pencocokan jawaban; itu tugas minggu berikutnya.

Cara menjalankan (dari folder proyek):
    python asr_demo.py
    python asr_demo.py --durasi 6      # batas waktu merekam dalam detik
    python asr_demo.py --berkas jawab.wav   # uji tanpa mikrofon, dari berkas WAV
    python asr_demo.py --ambang 300    # mulai merekam saat suara melewati ambang

Atur mikrofon di Windows: Settings > System > Sound > Input.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BAHASA_ASR = "id-ID"        # kode bahasa Indonesia untuk Google Speech Recognition
DURASI_MAKS = 8             # detik, batas waktu menunggu ucapan
AMBANG_AWAL = 300           # tingkat energi suara agar rekaman dimulai (bawaan pustaka)
PENYESUAIAN_AWAL = 1.0      # detik, untuk mengukur kebisingan ruangan


def transkripsi(pengenal, sumber) -> str:
    """Mengubah isi sumber audio menjadi teks. Gagal = pesan jelas, bukan traceback."""
    try:
        print("[asr] Mendengarkan... (bicara sekarang)")
        rekaman = pengenal.listen(sumber, timeout=DURASI_MAKS, phrase_time_limit=DURASI_MAKS)
    except Exception as galat:
        # Termasuk sr.WaitTimeoutError: tidak ada suara sampai batas waktu.
        print(f"[info] Tidak ada suara yang masuk ({type(galat).__name__}).")
        return ""

    # Pesan status singkat: ini yang akan anak lihat di aplikasi nanti.
    print("[asr] Suara tertangkap, sedang mengenali...")
    try:
        teks = pengenal.recognize_google(rekaman, language=BAHASA_ASR, show_all=True)
    except ImportError:
        print("[gagal] Alat pengenal suara belum lengkap. Pasang paket 'flac' di komputer ini.")
        return ""
    except Exception as galat:
        nama = type(galat).__name__
        if nama in ("UnknownValueError",):
            print("[info] Suara terdengar, tetapi belum bisa dimengerti. Coba bicara lebih jelas.")
        elif nama in ("RequestError", "ConnectionError", "TimeoutError"):
            print("[gagal] Gagal menghubungi layanan pengenal suara. Periksa sambungan internet.")
        else:
            print(f"[gagal] Pengenalan suara gagal: {galat}")
        return ""

    # show_all=True: hasil berupa dict {"alternative": [{"transcript", "confidence"}, ...]}.
    if isinstance(teks, dict):
        alternatif = teks.get("alternative") or []
        if not alternatif:
            print("[info] Suara terdengar, tetapi belum bisa dimengerti. Coba bicara lebih jelas.")
            return ""
        hasil = alternatif[0]
        isi = hasil.get("transcript", "")
        keyakinan = hasil.get("confidence")
        if keyakinan is not None:
            print(f"[asr] Keyakinan: {float(keyakinan) * 100:.0f}%")
        if len(alternatif) > 1:
            lain = [a.get("transcript") for a in alternatif[1:] if a.get("transcript")]
            if lain:
                print(f"[asr] Kemungkinan lain: {' | '.join(lain)}")
        return isi
    return str(teks or "")


def rekam_dari_mikrofon(durasi: int, ambang: int, penyetelan: float) -> str:
    """Merekam dari mikrofon lalu mengembalikan teksnya. "" berarti tidak ada hasil."""
    try:
        import speech_recognition as sr
    except ImportError:
        print("[gagal] Pustaka SpeechRecognition belum terpasang.")
        print("        Jalankan: pip install SpeechRecognition PyAudio")
        return ""

    pengenal = sr.Recognizer()
    try:
        mikrofon = sr.Microphone()
    except (AttributeError, OSError) as galat:
        # AttributeError: PyAudio belum terpasang. OSError: tidak ada perangkat mikrofon.
        print(f"[gagal] Mikrofon tidak tersedia ({galat}).")
        print("        Pasang PyAudio (pip install pyaudio) atau sambungkan mikrofon, lalu coba lagi.")
        return ""

    with mikrofon as sumber:
        # Ukur kebisingan ruangan sebentar agar ambang suara lebih pas dengan tempat demo.
        print(f"[asr] Mengukur kebisingan ruangan ({penyetelan:.1f} detik)...")
        try:
            pengenal.adjust_for_ambient_noise(sumber, duration=penyetelan)
        except Exception:
            pass   # tidak fatal: tetap lanjut dengan ambang bawaan
        pengenal.energy_threshold = ambang
        return transkripsi(pengenal, sumber)


def rekam_dari_berkas(jalur: Path, ambang: int) -> str:
    """Menguji alur ASR tanpa mikrofon, memakai berkas WAV yang sudah ada."""
    try:
        import speech_recognition as sr
    except ImportError:
        print("[gagal] Pustaka SpeechRecognition belum terpasang. Jalankan: pip install SpeechRecognition")
        return ""
    if not jalur.exists():
        print(f"[gagal] Berkas tidak ditemukan: {jalur}")
        return ""
    pengenal = sr.Recognizer()
    pengenal.energy_threshold = ambang
    try:
        with sr.AudioFile(str(jalur)) as sumber:
            return transkripsi(pengenal, sumber)
    except Exception as galat:
        print(f"[gagal] Berkas suara tidak bisa dibuka ({galat}). Pastikan formatnya WAV.")
        return ""


def main() -> int:
    """Titik masuk: rekam, kenali, cetak teks, lalu keluar dengan rapi."""
    parser = argparse.ArgumentParser(description="Prototipe ASR bahasa Indonesia dari mikrofon.")
    parser.add_argument("--durasi", type=int, default=DURASI_MAKS, help="batas waktu merekam, detik")
    parser.add_argument("--ambang", type=int, default=AMBANG_AWAL, help="ambang suara agar rekaman dimulai")
    parser.add_argument("--penyetelan", type=float, default=PENYESUAIAN_AWAL,
                        help="lama mengukur kebisingan ruangan, detik")
    parser.add_argument("--berkas", type=Path, default=None, help="uji memakai berkas WAV, tanpa mikrofon")
    argumen = parser.parse_args()

    durasi = max(2, argumen.durasi)
    if argumen.berkas:
        teks = rekam_dari_berkas(argumen.berkas, argumen.ambang)
    else:
        teks = rekam_dari_mikrofon(durasi, argumen.ambang, max(0.0, argumen.penyetelan))

    if not teks.strip():
        print("[selesai] Belum ada teks yang bisa dicetak. Program ditutup dengan rapi.")
        return 0

    print("\n" + "=" * 48)
    print(f"Hasil ASR: {teks.strip()}")
    print("=" * 48)
    print("(Teks di atas belum dibandingkan dengan kunci jawaban; itu dikerjakan minggu berikutnya.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())