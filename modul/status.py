# -*- coding: utf-8 -*-
"""Status permainan di st.session_state: perpindahan tahap, riwayat, dan pemrosesan jawaban.

Fungsi di sini dipanggil lewat on_click tombol, atau setelah rekaman masuk.
"""

from __future__ import annotations

import streamlit as st

from modul.asr import PESAN_GANGGUAN, gangguan, transkripsi
from modul.konfigurasi import AMBANG_LULUS
from modul.korpus import CERITA
from modul.kuis import putuskan
from modul.nlp import hasil_nlp, nilai_alternatif


def siapkan_state() -> None:
    bawaan = {
        "halaman": "beranda",   # beranda | cerita | tamat
        "kode": None,
        "indeks": 0,
        "tahap": "dengar",      # dengar | tanya | hasil
        "percobaan": 0,         # jumlah jawaban salah pada pertanyaan ini
        "gangguan": 0,          # jumlah rekaman gagal berturut-turut
        "nonce_mic": 0,         # berubah agar perekam kembali kosong
        "nonce_suara": 0,       # berubah agar kalimat yang sama diputar lagi
        "balasan": None,        # umpan balik terakhir
        "riwayat": [],          # catatan semua jawaban untuk halaman tamat
        "stiker_baru": None,
        # pengaturan guru
        "atur_ambang": AMBANG_LULUS,
        "atur_detail": False,
        "atur_ketik": False,
        "atur_pelan": False,
    }
    for nama, nilai in bawaan.items():
        st.session_state.setdefault(nama, nilai)


def adegan_aktif() -> dict:
    s = st.session_state
    return CERITA[s.kode]["adegan"][s.indeks]


# ---- Perpindahan tahap (dipanggil lewat on_click) ----------------------------


def mulai_cerita(kode: str) -> None:
    s = st.session_state
    s.kode, s.indeks, s.halaman, s.tahap = kode, 0, "cerita", "dengar"
    s.percobaan, s.gangguan, s.balasan, s.stiker_baru = 0, 0, None, None
    s.riwayat = []
    s.nonce_suara += 1


def ke_beranda() -> None:
    st.session_state.update(halaman="beranda", kode=None, balasan=None)


def ke_pertanyaan() -> None:
    st.session_state.tahap = "tanya"
    st.session_state.nonce_suara += 1


def ke_adegan_berikutnya() -> None:
    s = st.session_state
    s.percobaan, s.gangguan, s.balasan, s.stiker_baru = 0, 0, None, None
    s.nonce_mic += 1
    s.nonce_suara += 1
    if s.indeks + 1 < len(CERITA[s.kode]["adegan"]):
        s.indeks += 1
        s.tahap = "dengar"
    else:
        s.halaman = "tamat"


def lewati_pertanyaan() -> None:
    catat_riwayat("(dilewati)", hasil_nlp(), "dilewati")
    ke_adegan_berikutnya()


def catat_riwayat(dengar: str, hasil: dict, status: str) -> None:
    adegan = adegan_aktif()
    st.session_state.riwayat.append({
        "indeks": st.session_state.indeks, "tanya": adegan["tanya"], "dengar": dengar,
        "kunci": adegan["utama"], "skor": hasil["skor"], "status": status, "stiker": adegan["stiker"],
    })


def tetapkan_gangguan(kategori: str) -> None:
    s = st.session_state
    s.gangguan += 1
    s.nonce_mic += 1
    s.nonce_suara += 1
    s.balasan = {"jenis": "ulang", "pesan": PESAN_GANGGUAN[kategori], "dengar": "", "hasil": None, "kategori": kategori}


def proses_teks(alternatif: list[str], keyakinan: float | None = None, ujung_terpotong: bool = False) -> None:
    """Dipanggil setelah ASR berhasil, atau saat guru mengetik jawaban."""
    s = st.session_state
    adegan = adegan_aktif()
    hasil = nilai_alternatif(alternatif, adegan["tanya"], adegan["kunci"], s.kode, s.atur_ambang)
    dengar = hasil["jawaban"] or alternatif[0]

    putusan = putuskan(hasil, adegan, s.percobaan, s.indeks, keyakinan, ujung_terpotong)
    if putusan["hitung_percobaan"]:
        s.percobaan += 1
    s.gangguan = s.gangguan + 1 if putusan["jenis"] == "ulang" else 0
    s.nonce_mic += 1
    s.nonce_suara += 1
    s.balasan = {"jenis": putusan["jenis"], "pesan": putusan["pesan"], "dengar": dengar, "hasil": hasil}

    if putusan["lanjut"]:
        status = "benar" if putusan["jenis"] == "benar" else "dibantu"
        catat_riwayat(dengar, hasil, status)
        s.stiker_baru = adegan["stiker"] if status == "benar" else None
        s.tahap = "hasil"


def tangani_rekaman(data_wav: bytes) -> None:
    """Pintu masuk semua rekaman. Penanganan kesalahan suara berpusat di sini.

    Suara kosong, terpotong, tidak dimengerti, atau internet putus: TTS menjawab
    dengan ramah dan kesempatan anak tidak berkurang.
    """
    try:
        asr = transkripsi(data_wav)
    except Exception:  # lapisan terakhir: anak tidak boleh melihat traceback
        asr = gangguan("rusak")
    if asr["gangguan"]:
        tetapkan_gangguan(asr["gangguan"])
    else:
        proses_teks(asr["alternatif"], asr["keyakinan"], asr["ujung_terpotong"])
