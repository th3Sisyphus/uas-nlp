# -*- coding: utf-8 -*-
"""Halaman pratinjau komponen mikrofon: tiga kartu status sejajar.

    streamlit run pengujian/pratinjau_mikrofon.py

Tombol LEWATI di sini hanya bagian pratinjau. Di aplikasi, tombol itu tetap
tombol Streamlit biasa di luar komponen.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modul.mikrofon import tampilkan_mikrofon  # noqa: E402

KARTU = (
    ("1. SIAP", "siap", True, False),
    ("2. MENDENGARKAN", "mendengarkan", False, True),
    ("3. TUNGGU NARATOR", "nonaktif", True, False),
)

GAYA = """
<style>
.stApp { background: #0E5C4A; }
.block-container { padding-top: 2.5rem; max-width: 1100px; }
.pratinjau-baris { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.pratinjau-kartu {
  display: flex; flex-direction: column; align-items: center; gap: 16px;
  padding: 18px 16px 22px; background: #fff; border: 4px solid #2B2250;
  border-radius: 28px; box-shadow: 8px 8px 0 #2B2250;
  font-family: 'Nunito', 'Baloo 2', Verdana, sans-serif; color: #2B2250;
}
.pratinjau-header {
  font-size: 15px; font-weight: 800; letter-spacing: 0.16em;
  text-transform: uppercase; color: #2B2250; margin: 0;
}
.pratinjau-lewati {
  min-width: 176px; min-height: 64px; padding: 0 22px;
  font-family: inherit; font-size: 20px; font-weight: 800; letter-spacing: 0.06em;
  text-transform: uppercase; color: #2B2250; background: #fff;
  border: 4px solid #2B2250; border-radius: 18px; box-shadow: 5px 5px 0 #2B2250;
  cursor: pointer; transition: transform 200ms ease-out, box-shadow 200ms ease-out;
}
.pratinjau-lewati:active { transform: translate(3px, 3px); box-shadow: 2px 2px 0 #2B2250; }
.pratinjau-lewati[disabled] { color: #8B86A3; border-color: #8B86A3; box-shadow: 5px 5px 0 #8B86A3; cursor: not-allowed; }
.pratinjau-kosong { height: 64px; }
@media (max-width: 760px) { .pratinjau-baris { grid-template-columns: 1fr; } }
@media (prefers-reduced-motion: reduce) {
  .pratinjau-lewati { transition-duration: 1ms; }
}
</style>
"""


def kartu(nomor: int, header: str, status: str, ada_lewati: bool, lewati_aktif: bool) -> None:
    with st.container(border=False):
        st.markdown(f'<p class="pratinjau-header">{header}</p>', unsafe_allow_html=True)
        tampilkan_mikrofon(status, kunci=f"mikrofon_pratinjau_{nomor}")
        if ada_lewati:
            nonaktif = "" if lewati_aktif else " disabled"
            st.markdown(f'<button class="pratinjau-lewati" type="button"{nonaktif}>Lewati</button>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="pratinjau-kosong"></div>', unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="Pratinjau Mikrofon", page_icon="🎤", layout="wide")
    st.markdown(GAYA, unsafe_allow_html=True)
    st.markdown('<p class="pratinjau-header">Pratinjau komponen mikrofon</p>', unsafe_allow_html=True)

    kolom = st.columns(3, gap="small")
    for wadah, (nomor, (header, status, ada_lewati, lewati_aktif)) in zip(kolom, enumerate(KARTU, start=1)):
        with wadah:
            kartu(nomor, header, status, ada_lewati, lewati_aktif)


if __name__ == "__main__":
    main()
