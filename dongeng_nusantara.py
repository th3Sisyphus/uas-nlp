# -*- coding: utf-8 -*-
"""
PANGGUNG DONGENG NUSANTARA
Tugas Pemrograman Akhir NLPTA (IT6073), Tugas A:
Kuis interaktif belajar bahasa Indonesia berbasis suara untuk anak usia dini.

Cara menjalankan:
    pip install -r requirements.txt
    streamlit run dongeng_nusantara.py

Berkas ini hanya titik masuk aplikasi. Semua logika ada di folder modul/:
    modul/konfigurasi.py   lokasi berkas, ambang, dan batas waktu
    modul/korpus.py        memuat korpus/cerita/*.json dan korpus/leksikon.json
    modul/nlp.py           praproses, TF-IDF, cosine similarity
    modul/tts.py           gTTS dengan cadangan pyttsx3
    modul/asr.py           pemeriksaan rekaman, Google Speech Recognition, gangguan suara
    modul/kuis.py          pujian, petunjuk bertingkat, kunci jawaban
    modul/ilustrasi.py     gambar adegan (SVG)
    modul/status.py        status permainan di st.session_state
    modul/komponen.py      CSS, kartu, papan stiker, panel guru
    modul/halaman.py       halaman beranda, cerita, dan tamat

Alur singkat:
    pilih cerita -> TTS membacakan adegan -> TTS membacakan pertanyaan
    -> anak menjawab lewat mikrofon -> ASR mentranskripsi
    -> NLP menilai (TF-IDF + cosine) -> TTS memberi umpan balik -> adegan berikutnya
"""

import streamlit as st

from modul.halaman import (
    halaman_beranda, halaman_cerita, halaman_daftar, halaman_kartu, halaman_selesai_kartu, halaman_tamat,
)
from modul.komponen import pasang_css, pengaturan_guru
from modul.konfigurasi import WARNA_BERANDA, WARNA_TEMA
from modul.korpus import CERITA
from modul.status import siapkan_state

HALAMAN = {
    "beranda": halaman_beranda, "daftar": halaman_daftar, "cerita": halaman_cerita, "tamat": halaman_tamat,
    "kartu": halaman_kartu, "selesai_kartu": halaman_selesai_kartu,
}


def warna_aktif() -> dict:
    """Warna dunia mengikuti cerita yang dibuka, tema kartu, atau beranda."""
    s = st.session_state
    if s.kode:
        return CERITA[s.kode]["warna"]
    if s.halaman in ("kartu", "selesai_kartu") and s.tema_kartu:
        return WARNA_TEMA[s.tema_kartu]
    return WARNA_BERANDA


def main() -> None:
    st.set_page_config(page_title="Panggung Dongeng Nusantara", page_icon="🦌", layout="centered")
    siapkan_state()
    pasang_css(warna_aktif())

    # Pengaturan guru ada di sidebar (bisa dilipat). Dijalankan lebih dulu supaya
    # nilainya sudah terbaca saat st.rerun() dipanggil dari halaman.
    pengaturan_guru()
    HALAMAN[st.session_state.halaman]()


if __name__ == "__main__":
    main()
