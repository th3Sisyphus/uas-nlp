# -*- coding: utf-8 -*-
"""Status permainan di st.session_state: perpindahan tahap, riwayat, dan pemrosesan jawaban.

Fungsi di sini dipanggil lewat on_click tombol, atau setelah rekaman masuk.
"""

from __future__ import annotations

import streamlit as st

from modul.asr import PESAN_GANGGUAN, gangguan, transkripsi
from modul.flashcard import cocokkan_kata, pilih_sesi
from modul.konfigurasi import AMBANG_LULUS, MAKS_PERCOBAAN
from modul.korpus import CERITA, FLASHCARD
from modul.kuis import PUJIAN, putuskan
from modul.nlp import hasil_nlp, nilai_alternatif


def siapkan_state() -> None:
    bawaan = {
        "halaman": "beranda",   # beranda | daftar | cerita | tamat
        "tema": "rakyat",       # tema yang dipilih di beranda
        "wilayah": "Semua",     # saringan asal di daftar cerita
        "nomor_halaman": 1,     # halaman daftar cerita yang sedang tampil
        "kata_cari": "",        # pencarian judul untuk orang tua dan guru
        "kode": None,
        "indeks": 0,
        "tahap": "dengar",      # dengar | tanya | hasil
        "tema_kartu": None,     # hewan | buah
        "sesi_kartu": [],       # kartu yang dipakai sesi ini, sudah diacak
        "no_kartu": 0,          # posisi di sesi_kartu
        "tahap_kartu": "kenal", # kenal | ucap | hasil
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


def ke_daftar() -> None:
    st.session_state.update(halaman="daftar", kode=None, balasan=None)


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


# ---- Flashcard kata (tema hewan dan buah) ------------------------------------


def kartu_aktif() -> dict:
    s = st.session_state
    return s.sesi_kartu[s.no_kartu]


def mulai_kartu(tema: str) -> None:
    s = st.session_state
    s.tema_kartu, s.sesi_kartu, s.no_kartu, s.tahap_kartu = tema, pilih_sesi(FLASHCARD[tema]["kartu"]), 0, "kenal"
    s.halaman, s.kode = "kartu", None
    s.percobaan, s.gangguan, s.balasan = 0, 0, None
    s.nonce_suara += 1


def ke_ucap() -> None:
    st.session_state.tahap_kartu = "ucap"
    st.session_state.nonce_suara += 1


def kartu_berikutnya() -> None:
    s = st.session_state
    s.percobaan, s.gangguan, s.balasan = 0, 0, None
    s.nonce_mic += 1
    s.nonce_suara += 1
    if s.no_kartu + 1 < len(s.sesi_kartu):
        s.no_kartu += 1
        s.tahap_kartu = "kenal"
    else:
        s.halaman = "selesai_kartu"


def proses_kata(alternatif: list[str]) -> None:
    """Menilai ucapan anak untuk kartu aktif, lalu menyiapkan umpan balik bertingkat."""
    s = st.session_state
    kartu = kartu_aktif()
    hasil = cocokkan_kata(alternatif, kartu, s.sesi_kartu)
    s.nonce_mic += 1
    s.nonce_suara += 1
    s.gangguan = 0
    pesan, jenis = "", hasil["status"]

    if hasil["status"] == "benar":
        pesan = f"{PUJIAN[s.no_kartu % len(PUJIAN)]} Ini memang {kartu['kata']}."
    else:
        s.percobaan += 1
        if s.percobaan >= MAKS_PERCOBAAN:
            jenis = "kunci"
            pesan = f"Tidak apa-apa. Ini {kartu['kata']}. Yuk, kita lihat kartu berikutnya!"
        elif s.percobaan > 1:
            pesan = f"Belum tepat. {kartu['petunjuk']} Ini {kartu['kata']}. Ayo sekali lagi!"
        else:
            pesan = f"Belum tepat. Ayo bilang sekali lagi: {kartu['kata']}!"

    s.balasan = {"jenis": jenis, "pesan": pesan, "dengar": hasil["terdengar"], "hasil": hasil}
    if jenis in ("benar", "kunci"):
        s.tahap_kartu = "hasil"
    else:
        s.tahap_kartu = "ucap"
    # Rerun dipaksa agar tombol "Kartu berikutnya" dan kolom ketik baru muncul seketika.
    st.rerun()


def tangani_rekaman_kartu(data_wav: bytes) -> None:
    """Pintu masuk rekaman flashcard. Gangguan suara tidak mengurangi percobaan.

    Setelah MAKS_GANGGUAN_SUARA gangguan berturut-turut, halaman menampilkan mode
    ketuk gambar supaya anak tetap bisa menyelesaikan kartu tanpa mikrofon.
    """
    try:
        asr = transkripsi(data_wav)
    except Exception:  # lapisan terakhir: anak tidak boleh melihat traceback
        asr = gangguan("rusak")
    if asr["gangguan"]:
        s = st.session_state
        s.gangguan += 1
        s.nonce_mic += 1
        s.nonce_suara += 1
        s.balasan = {"jenis": "ulang", "pesan": PESAN_GANGGUAN[asr["gangguan"]], "dengar": "", "hasil": None}
    else:
        proses_kata(asr["alternatif"])
