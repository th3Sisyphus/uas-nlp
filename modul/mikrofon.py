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


@lru_cache(maxsize=1)
def _aset(nama: str) -> str:
    return (FOLDER_MIKROFON / nama).read_text(encoding="utf-8")


def _mikrofon_anak():
    """Mendaftarkan komponen sekali per proses; Streamlit menolak nama ganda.

    Komponen menerima satu berkas JS, jadi dua berkas digabung: fungsi murni dari
    mikrofon-inti.js lalu badan mikrofon.js. Berkas aset relatif tidak bisa diimpor
    sebagai modul ES dari JS komponen, karena itu import dan "export default" dibuang
    dengan replace. Badan berkas kedua menjadi ekspresi fungsi bernama.
    """
    if "mikrofon_anak" not in st.session_state.get("_komponen_mikrofon", {}):
        inti = _aset("mikrofon-inti.js")
        utama = _aset("mikrofon.js")
        utama = utama.replace(
            'import { rms, encodeWav, turunkanLaju, keBase64 } from "./mikrofon-inti.js";', ""
        ).replace("export default function (component) {", "function (component) {")
        kepala, badan = utama.split("function (component) {", 1)
        inti = re.sub(r"^export\s+", "", inti, flags=re.MULTILINE)
        js = f"export default function () {{\nlet komponenMikrofon; {inti} {kepala} komponenMikrofon = (function (component) {{{badan});\nreturn komponenMikrofon;\n}}"
        st.session_state.setdefault("_komponen_mikrofon", {})["mikrofon_anak"] = component(
            "mikrofon_anak",
            html=_aset("mikrofon.html"),
            css=_aset("mikrofon.css"),
            js=js,
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
        height=320,
        width="content",
        on_status_terpasang_change=lambda: None,
    )
