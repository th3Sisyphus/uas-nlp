# -*- coding: utf-8 -*-
"""Halaman uji narator: keenam pose berdampingan dengan label.

Jalankan: streamlit run uji_narator.py
"""

import streamlit as st

from modul.narator import _NAMA_POSE, narator

st.set_page_config(page_title="Uji narator", layout="wide")
st.markdown("## Uji narator Steven")

CONTOH = {
    "melambai": "Halo! Aku Steven.",
    "bicara": "Dahulu kala, hiduplah seekor kancil.",
    "mendengar": "Aku dengarkan ya.",
    "benar": "Hebat, jawabanmu benar!",
    "menyemangati": "Hampir benar, coba lagi!",
    "bingung": "Suaranya belum terdengar.",
}

for baris in range(0, len(_NAMA_POSE), 3):
    for kolom, pose in zip(st.columns(3), _NAMA_POSE[baris:baris + 3]):
        with kolom:
            st.caption(pose)
            st.markdown(narator(pose, CONTOH[pose], 1.5), unsafe_allow_html=True)

with st.expander("Pemeriksaan cepat"):
    h = narator("benar", "<b>x</b>", 1.5)
    st.write("Escape teks:", "&lt;b&gt;" in h)
    st.write("Nilai tak dikenal jatuh ke melambai:", narator("ngawur", "") == narator("melambai", ""))
