# -*- coding: utf-8 -*-
"""Komponen pemutar suara narator: satu tombol besar dengan ikon speaker.

Kontrak antarmuka (dipakai bersama modul lain, jangan diubah tanpa lapor):
    DOM     akar .spk[data-status], tombol #spk-tombol, label #spk-label,
            lima batang .spk-bar, progres #spk-progres > i
    Status  siap | memutar | nonaktif
    Data    {"audio_base64", "mime", "autoplay", "status"}
    Kejadian ke Python: selesai

Kejadian "selesai" dikirim sekali setelah audio benar-benar habis. Bila autoplay
diblokir peramban atau data audio kosong, kejadian itu juga dikirim supaya
halaman tidak tertahan menunggu.
"""

from __future__ import annotations

import base64
from functools import lru_cache

import streamlit as st
from streamlit.components.v2 import component

from modul.konfigurasi import FOLDER

FOLDER_SPEAKER = FOLDER / "aset" / "speaker"

STATUS_SAH = ("siap", "memutar", "nonaktif")

# Tinggi tetap komponen: 176px tombol + label + batang/progres (muncul saat aktif).
# Nilai tetap wajib karena komponen di dalam shadow root tidak bisa auto-resize.
# Isi dibatasi overflow:hidden di speaker.css supaya tidak muncul scrollbar.
TINGGI = 320


@lru_cache(maxsize=3)
def _aset(nama: str) -> str:
    return (FOLDER_SPEAKER / nama).read_text(encoding="utf-8")


def _speaker_anak():
    if "speaker_anak" not in st.session_state.get("_komponen_speaker", {}):
        st.session_state.setdefault("_komponen_speaker", {})["speaker_anak"] = component(
            "speaker_anak",
            html=_aset("speaker.html"),
            css=_aset("speaker.css"),
            js=_aset("speaker.js"),
        )
    return st.session_state["_komponen_speaker"]["speaker_anak"]


def tampilkan_speaker(
    data: bytes | None,
    format_audio: str = "audio/mpeg",
    autoplay: bool = True,
    kunci: str = "speaker",
    status: str = "siap",
) -> str:
    """Menampilkan satu tombol pemutar dan mengembalikan status terakhirnya.

    Mengembalikan "selesai" bila audio sudah habis (atau tidak dapat diputar sama
    sekali), selain itu None. data None atau status "nonaktif" menampilkan tombol
    abu-abu tanpa suara dan langsung mengembalikan "selesai".
    """
    if status not in STATUS_SAH:
        raise ValueError(f"status tidak dikenal: {status!r}; pilih salah satu dari {STATUS_SAH}")
    if data is None or status == "nonaktif":
        _speaker_anak()(
            key=kunci,
            data={"audio_base64": None, "mime": format_audio, "autoplay": False, "status": "nonaktif"},
            height=TINGGI,
            width="stretch",
            on_selesai_change=lambda: None,
        )
        return "selesai"
    hasil = _speaker_anak()(
        key=kunci,
        data={
            "audio_base64": base64.b64encode(data).decode("ascii"),
            "mime": format_audio,
            "autoplay": bool(autoplay),
            "status": status,
        },
        height=TINGGI,
        width="stretch",
        on_selesai_change=lambda: None,
    )
    return "selesai" if getattr(hasil, "selesai", None) is not None else None
