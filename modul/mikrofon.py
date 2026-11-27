# -*- coding: utf-8 -*-
"""Komponen mikrofon anak: satu tombol besar dengan empat status.

Kontrak antarmuka (dipakai bersama modul lain, jangan diubah tanpa lapor):
    DOM     akar .mik[data-status], tombol #mik-tombol, label #mik-label,
            lima batang .mik-bar, progres #mik-progres > i
    Status  siap | mendengarkan | memproses | nonaktif
    Data    {"status", "tunda_detik", "idle_detik", "hening_detik", "maks_detik"}
    Kejadian ke Python: rekaman, hening, izin_ditolak

Perekaman berjalan di peramban: AudioWorklet menangkap PCM, diturunkan ke 16 kHz mono
16 bit, dikemas WAV, lalu dikirim sebagai kejadian "rekaman". Status "memproses" dipasang
komponen sampai Python mengirim status baru.
"""

from __future__ import annotations

import base64
import re
from functools import lru_cache

import streamlit as st
from streamlit.components.v2 import component

from modul.konfigurasi import FOLDER

FOLDER_MIKROFON = FOLDER / "aset" / "mikrofon"

STATUS_SAH = ("siap", "mendengarkan", "memproses", "nonaktif")

# Batas waktu bawaan komponen. Angka ini ikut dikirim ke JS pada setiap render.
IDLE_DETIK = 10.0
HENING_DETIK = 1.6
MAKS_DETIK = 10.0

# Tinggi tetap komponen: 176px tombol + label + batang/progres (muncul saat aktif).
# Isi dibatasi overflow:hidden di mikrofon.css supaya tidak muncul scrollbar.
TINGGI = 320


@lru_cache(maxsize=1)
def _aset(nama: str) -> str:
    return (FOLDER_MIKROFON / nama).read_text(encoding="utf-8")


def _mikrofon_anak():
    if "mikrofon_anak" not in st.session_state.get("_komponen_mikrofon", {}):
        inti = _aset("mikrofon-inti.js")
        utama = _aset("mikrofon.js")
        # inti berisi const/function tingkat-modul. Taruh di atas fungsi utama (tanpa
        # "export"), lalu buang baris import-nya. "export default function (component)"
        # pada mikrofon.js DIBIARKAN APA ADANYA -- itu satu-satunya fungsi yang dipanggil
        # Streamlit dengan argumen component. JANGAN dibungkus fungsi luar tanpa
        # parameter lagi (bug sebelumnya: fungsi asli tidak pernah terpanggil).
        inti = re.sub(r"^export\s+", "", inti, flags=re.MULTILINE)
        utama = utama.replace(
            'import { rms, encodeWav, turunkanLaju, keBase64 } from "./mikrofon-inti.js";\n', ""
        )
        js = f"{inti}\n{utama}"
        st.session_state.setdefault("_komponen_mikrofon", {})["mikrofon_anak"] = component(
            "mikrofon_anak", html=_aset("mikrofon.html"), css=_aset("mikrofon.css"), js=js,
        )
    return st.session_state["_komponen_mikrofon"]["mikrofon_anak"]


def tampilkan_mikrofon(status: str = "siap", kunci: str = "mikrofon") -> None:
    """Menampilkan satu tombol mikrofon pada status tertentu (dipakai halaman pratinjau)."""
    if status not in STATUS_SAH:
        raise ValueError(f"status tidak dikenal: {status!r}; pilih salah satu dari {STATUS_SAH}")
    _mikrofon_anak()(
        key=kunci,
        data={
            "status": status,
            "tunda_detik": 0.0,
            "idle_detik": IDLE_DETIK,
            "hening_detik": HENING_DETIK,
            "maks_detik": MAKS_DETIK,
        },
        height=TINGGI,
        width="stretch",
        on_status_terpasang_change=lambda: None,
    )


def perkirakan_durasi(teks: str, pelan: bool = False) -> float:
    """Perkiraan lama narator membacakan teks, dalam detik.

    Mikrofon dibiarkan nonaktif selama kira-kira selama itu supaya suara narator
    tidak ikut terekam.
    """
    kata = len(teks.split())
    return kata / (2.2 if pelan else 2.6)


def perekam(kunci: str, status: str = "siap", tunda_detik: float = 0.0) -> bytes | str | None:
    """Memanggil komponen mikrofon_anak dan menerjemahkan hasilnya.

    Mengembalikan bytes WAV jika ada rekaman, "hening" jika idle/tidak ada suara,
    "izin_ditolak" jika peramban menolak izin mikrofon, atau None jika belum ada apa-apa.
    """
    hasil = _mikrofon_anak()(
        key=kunci,
        data={
            "status": status,
            "tunda_detik": float(tunda_detik),
            "idle_detik": IDLE_DETIK,
            "hening_detik": HENING_DETIK,
            "maks_detik": MAKS_DETIK,
        },
        height=TINGGI,
        width="stretch",
        on_rekaman_change=lambda: None,
        on_hening_change=lambda: None,
        on_izin_ditolak_change=lambda: None,
    )
    if hasil.rekaman and hasil.rekaman.get("wav_base64"):
        return base64.b64decode(hasil.rekaman["wav_base64"])
    if hasil.hening is not None:
        return "hening"
    if hasil.izin_ditolak is not None:
        return "izin_ditolak"
    return None
