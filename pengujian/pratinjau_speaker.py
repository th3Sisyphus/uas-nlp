# -*- coding: utf-8 -*-
"""Halaman pratinjau komponen pemutar suara: tiga kartu status sejajar.

    streamlit run pengujian/pratinjau_speaker.py

Suara contoh dibuat langsung dengan TTS. Jika internet tidak tersedia, kartu
memakai suara kosong dan tombol tetap tampil pada status masing-masing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modul.speaker import tampilkan_speaker  # noqa: E402
from modul.tts import buat_suara  # noqa: E402

KARTU = (
    ("1. SIAP", "siap", True),
    ("2. MEMUTAR", "memutar", True),
    ("3. TANPA SUARA", "nonaktif", False),
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
@media (max-width: 760px) { .pratinjau-baris { grid-template-columns: 1fr; } }
</style>
"""


@st.cache_data(show_spinner=False)
def _contoh() -> tuple[bytes, str] | tuple[None, str]:
    data, format_audio = buat_suara("Halo, aku Kiko. Ayo dengarkan ceritanya!")
    return data, format_audio


def kartu(nomor: int, header: str, status: str, ada_suara: bool) -> None:
    data, format_audio = _contoh() if ada_suara else (None, "audio/mpeg")
    with st.container(border=False):
        st.markdown(f'<p class="pratinjau-header">{header}</p>', unsafe_allow_html=True)
        tampilkan_speaker(data, format_audio, autoplay=False,
                          kunci=f"speaker_pratinjau_{nomor}", status=status)


def main() -> None:
    st.set_page_config(page_title="Pratinjau Pemutar Suara", page_icon="🔊", layout="wide")
    st.markdown(GAYA, unsafe_allow_html=True)
    st.markdown('<p class="pratinjau-header">Pratinjau komponen pemutar suara</p>', unsafe_allow_html=True)

    kolom = st.columns(3, gap="small")
    for wadah, (nomor, (header, status, ada_suara)) in zip(kolom, enumerate(KARTU, start=1)):
        with wadah:
            kartu(nomor, header, status, ada_suara)


if __name__ == "__main__":
    main()
