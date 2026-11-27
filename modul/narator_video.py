# -*- coding: utf-8 -*-
"""Narator video: klip MP4 berlatar hijau, latarnya dibuang di peramban.

Kontrak antarmuka (dipakai bersama modul lain, jangan diubah tanpa lapor):
    DOM     akar .nar-vid, satu <canvas>
    Data    {"src", "ulang"}

Berkas video disajikan Streamlit dari folder static/ (enableStaticServing di
.streamlit/config.toml). Salin ulang aset/narator/*.mp4 ke static/ bila video
diperbarui.
"""

from __future__ import annotations

from functools import lru_cache

import streamlit as st
from streamlit.components.v2 import component

from modul.konfigurasi import FOLDER

FOLDER_NARATOR = FOLDER / "aset" / "narator"

# Pose narator ke berkas video. Nama pose sama dengan pose SVG lama supaya
# pemanggil di halaman.py tidak perlu berubah.
VIDEO = {
    "melambai": "salam_rev.mp4",
    "bicara": "berbicara_rev.mp4",
    "mendengar": "mendengar.mp4",
    "benar": "benar.mp4",
    "menyemangati": "semangat_rev.mp4",
    "bingung": "bingung_rev1.mp4",
}

# Pose yang diputar berulang; sisanya cukup sekali lalu berhenti di bingkai akhir.
ULANG = {"bicara", "mendengar"}

# Rasio video 1280x720. Tinggi kotak dihitung dari lebar agar canvas tidak gepeng.
RASIO = 720 / 1280
TINGGI_MAKS = 200


@lru_cache(maxsize=3)
def _aset(nama: str) -> str:
    return (FOLDER_NARATOR / nama).read_text(encoding="utf-8")


def _narator_video():
    if "narator_video" not in st.session_state.get("_komponen_narator", {}):
        st.session_state.setdefault("_komponen_narator", {})["narator_video"] = component(
            "narator_video",
            html=_aset("narator-video.html"),
            css=_aset("narator-video.css"),
            js=_aset("narator-video.js"),
        )
    return st.session_state["_komponen_narator"]["narator_video"]


def tampilkan_narator(pose: str, lebar: int = 160) -> None:
    """Menampilkan video narator untuk pose tertentu.

    pose tidak dikenal jatuh ke "melambai", sama seperti narator SVG sebelumnya.
    """
    nama = VIDEO.get(pose, VIDEO["melambai"])
    _narator_video()(
        key=f"narator_{pose}",
        data={"src": f"/app/static/{nama}", "ulang": pose in ULANG},
        width=lebar,
        height=int(lebar * RASIO),
    )
