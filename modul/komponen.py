# -*- coding: utf-8 -*-
"""Komponen tampilan: CSS, judul balok, kartu umpan balik, papan stiker, dan panel guru.

Konsep tampilan (aset/tampilan.css): buku stiker cerita. Tiap cerita punya warna dunianya
sendiri, latar memakai motif batik kawung, dan semua elemen tampak seperti stiker.
"""

from __future__ import annotations

import html
from functools import lru_cache

import streamlit as st

from modul.konfigurasi import BERKAS_CSS
from modul.korpus import CERITA


@lru_cache(maxsize=1)
def _css_dasar() -> str:
    return BERKAS_CSS.read_text(encoding="utf-8")


def pasang_css(warna: dict) -> None:
    """Memasang CSS dasar, warna dunia cerita aktif, dan warna tombol tiap kartu cerita."""
    kartu = "".join(f".st-key-kartu_{k} {{ --aksen:{c['warna']['kartu']}; }}\n" for k, c in CERITA.items())
    st.markdown(
        f"<style>{_css_dasar()}\n:root {{ --dunia:{warna['dunia']}; --aksen:{warna['aksen']}; }}\n{kartu}</style>",
        unsafe_allow_html=True,
    )


def judul_balok(teks: str) -> str:
    huruf = "".join(f'<span class="balok" aria-hidden="true">{html.escape(h)}</span>' for h in teks)
    return f'<div class="balok-judul" role="heading" aria-level="1" aria-label="{html.escape(teks)}">{huruf}</div>'


def kertas(isi: str, kelas: str = "") -> None:
    st.html(f'<div class="kertas {kelas}">{isi}</div>')


def papan_stiker() -> None:
    s = st.session_state
    jumlah = len(CERITA[s.kode]["adegan"])
    didapat = {r["indeks"]: r["stiker"] for r in s.riwayat if r["status"] == "benar"}
    slot = []
    for i in range(jumlah):
        if i in didapat:
            baru = " baru" if didapat[i] == s.stiker_baru else ""
            slot.append(f'<span class="slot dapat{baru}">{didapat[i]}</span>')
        else:
            aktif = " aktif" if i == s.indeks else ""
            slot.append(f'<span class="slot{aktif}">{i + 1}</span>')
    st.html(f'<div class="papan" aria-label="Adegan {s.indeks + 1} dari {jumlah}">{"".join(slot)}</div>')


def kartu_balasan(balasan: dict) -> None:
    ikon = {"benar": "🌟", "hampir": "💪", "salah": "🤔", "kunci": "💡", "ulang": "🎤"}[balasan["jenis"]]
    kertas(f'<span class="ikon" aria-hidden="true">{ikon}</span><p>{html.escape(balasan["pesan"])}</p>',
           f'balas {balasan["jenis"]}')


def kartu_banding(balasan: dict, adegan: dict, tampilkan_kunci: bool) -> None:
    """Umpan balik utama: jawaban anak dibandingkan dengan jawaban sebenarnya dari sistem."""
    if not balasan.get("dengar"):
        return
    isi = f'<div class="sisi"><p class="judul-sisi">Yang kamu ucapkan</p><p class="isi-sisi">{html.escape(balasan["dengar"])}</p></div>'
    meter = ""
    if tampilkan_kunci:
        isi += f'<div class="sisi"><p class="judul-sisi">Jawaban dari cerita</p><p class="isi-sisi">{html.escape(adegan["utama"])}</p></div>'
        hasil = balasan.get("hasil")
        if hasil is not None:
            persen = round(hasil["skor"] * 100)
            batas = round(st.session_state.atur_ambang * 100)
            meter = (
                f'<div class="meter" role="img" aria-label="Kecocokan {persen} persen">'
                f'<div class="isi" style="width:{persen}%"></div><div class="batas" style="left:{batas}%"></div></div>'
                f'<p class="kecil">Kecocokan {persen}% (batas lulus {batas}%)</p>'
            )
    kertas(f'<div class="banding">{isi}</div>{meter}')


def panel_detail_nlp(balasan: dict) -> None:
    """Panel guru: memperlihatkan isi modul NLP untuk demo dan pemeriksaan."""
    hasil = balasan.get("hasil")
    if hasil is None or not st.session_state.atur_detail:
        return
    kertas(
        '<p class="kecil"><b>Detail NLP</b></p>'
        f'<p class="kecil">Token bersih: {html.escape(", ".join(hasil["token"]) or "(kosong)")}</p>'
        f'<p class="kecil">Kunci terdekat: {html.escape(hasil["kunci_terdekat"] or "(tidak ada)")}</p>'
        f'<p class="kecil">Cosine kata {hasil["cos_kata"]:.3f}, cosine huruf {hasil["cos_huruf"]:.3f}, skor {hasil["skor"]:.3f}</p>'
    )


def pengaturan_guru() -> None:
    with st.expander("Untuk guru dan orang tua"):
        st.slider("Batas lulus kecocokan", 0.30, 0.90, step=0.05, key="atur_ambang")
        st.toggle("Tampilkan detail NLP", key="atur_detail")
        st.toggle("Ketik jawaban tanpa mikrofon", key="atur_ketik")
        st.toggle("Suara narator lebih pelan", key="atur_pelan")
        st.caption(
            "Rekaman suara dikirim ke layanan Google untuk ditranskripsi dan tidak disimpan oleh aplikasi ini. "
            "Internet diperlukan untuk suara narator dan pengenalan suara."
        )
