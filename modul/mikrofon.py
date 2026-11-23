# -*- coding: utf-8 -*-
"""Komponen mikrofon anak: satu tombol besar dengan empat status.

Kontrak antarmuka (dipakai bersama modul lain, jangan diubah tanpa lapor):
    DOM     akar .mik[data-status], tombol #mik-tombol, label #mik-label,
            lima batang .mik-bar, progres #mik-progres > i
    Status  siap | mendengarkan | memproses | nonaktif
    Data    {"status", "tunda_detik", "idle_detik", "hening_detik", "maks_detik"}
    Kejadian ke Python: rekaman, hening, izin_ditolak

Perekaman suara belum ada di tahap ini; yang dipasang baru tampilan dan status.
"""

from __future__ import annotations

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
    """Mendaftarkan komponen sekali per proses; Streamlit menolak nama ganda."""
    if "mikrofon_anak" not in st.session_state.get("_komponen_mikrofon", {}):
        st.session_state.setdefault("_komponen_mikrofon", {})["mikrofon_anak"] = component(
            "mikrofon_anak",
            html=_aset("mikrofon.html"),
            css=_aset("mikrofon.css"),
            js=_aset("mikrofon.js"),
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
