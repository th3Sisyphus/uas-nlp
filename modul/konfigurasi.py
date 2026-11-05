# -*- coding: utf-8 -*-
"""Konfigurasi: lokasi berkas dan semua angka yang bisa disetel.

Angka ambang dan bobot adalah hasil penyetelan pada data pengembangan
(lihat pengujian/uji_sistem.py dan laporan bagian 9).
"""

from __future__ import annotations

from pathlib import Path


FOLDER = Path(__file__).resolve().parent.parent   # folder proyek
FOLDER_CERITA = FOLDER / "korpus" / "cerita"
BERKAS_LEKSIKON = FOLDER / "korpus" / "leksikon.json"
BERKAS_CSS = FOLDER / "aset" / "tampilan.css"

BAHASA_ASR = "id-ID"            # kode bahasa untuk Google Speech Recognition
BAHASA_TTS = "id"               # kode bahasa untuk gTTS
BATAS_WAKTU_TTS = 10            # detik, agar aplikasi tidak menunggu selamanya
BATAS_WAKTU_ASR = 12            # detik

MAKS_PERCOBAAN = 3              # jawaban salah ke-3: kunci dibacakan, cerita lanjut
MAKS_GANGGUAN_SUARA = 3         # setelah ini muncul tombol lewati pertanyaan

# Hasil penyetelan pada data pengembangan (lihat uji_sistem.py dan laporan).
AMBANG_LULUS = 0.75             # skor minimum agar jawaban dianggap benar
BOBOT_KATA = 0.60               # porsi cosine tingkat kata dalam skor gabungan
RASIO_HAMPIR = 0.75             # skor >= ambang x rasio dianggap "hampir benar"
BATAS_EJAAN = 0.80              # kemiripan minimum untuk koreksi ejaan keluaran ASR

# Batas pemeriksaan kualitas audio. Amplitudo memakai skala 0..1.
DURASI_MINIMUM = 0.45           # detik; lebih pendek dianggap terpotong
RMS_MINIMUM = 0.006             # di bawah ini dianggap tidak ada suara
KEYAKINAN_MINIMUM = 0.40        # keyakinan ASR rendah + jawaban salah = minta ulang

WARNA_BERANDA = {"dunia": "#6B3FD4", "aksen": "#FFD23F"}
