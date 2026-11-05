# -*- coding: utf-8 -*-
"""Halaman aplikasi: beranda, cerita (tahap dengar, tanya, hasil), dan tamat.
"""

from __future__ import annotations

import html

import streamlit as st

from modul.ilustrasi import gambar_adegan
from modul.komponen import judul_balok, kartu_balasan, kartu_banding, kertas, panel_detail_nlp, papan_stiker
from modul.konfigurasi import MAKS_GANGGUAN_SUARA
from modul.korpus import CERITA
from modul.status import (
    adegan_aktif, ke_adegan_berikutnya, ke_beranda, ke_pertanyaan, lewati_pertanyaan,
    mulai_cerita, proses_teks, tangani_rekaman,
)
from modul.tts import putar_suara


def halaman_beranda() -> None:
    st.html(judul_balok("DONGENG") + '<p class="anak-judul">Dengarkan ceritanya, lalu jawab dengan suaramu!</p>')
    daftar = list(CERITA.items())
    for awal in range(0, len(daftar), 3):  # tiga kartu per baris, berapa pun jumlah cerita
        for wadah, (kode, cerita) in zip(st.columns(3, gap="medium"), daftar[awal: awal + 3]):
            with wadah, st.container(key=f"kartu_{kode}"):
                kertas(f'{gambar_adegan(kode, 0)}<h3>{html.escape(cerita["judul"])}</h3>'
                       f'<p>{html.escape(cerita["asal"])}</p>', "kartu-cerita")
                st.button("Dengarkan", key=f"pilih_{kode}", type="primary", width="stretch",
                          on_click=mulai_cerita, args=(kode,))


def tahap_dengar(cerita: dict, adegan: dict) -> None:
    kertas(f'<p class="bacaan">{html.escape(adegan["narasi"])}</p>')
    putar_suara(adegan["narasi"])
    st.button("Aku siap menjawab", key="tombol_siap", type="primary", width="stretch", on_click=ke_pertanyaan)


def tahap_tanya(cerita: dict, adegan: dict) -> None:
    s = st.session_state
    balasan = s.balasan

    if balasan:
        kartu_balasan(balasan)
        if balasan["jenis"] != "ulang":
            kartu_banding(balasan, adegan, tampilkan_kunci=False)
        panel_detail_nlp(balasan)
        putar_suara(balasan["pesan"])
    else:
        kertas(f'<p class="tanya">{html.escape(adegan["tanya"])}</p>')
        putar_suara(adegan["tanya"])

    rekaman = st.audio_input(
        "Tekan mikrofon, ucapkan jawabanmu, lalu tekan berhenti",
        key=f"mic_{s.kode}_{s.indeks}_{s.nonce_mic}",
    )
    if rekaman is not None:
        with st.spinner("Sebentar, aku dengarkan dulu..."):
            tangani_rekaman(rekaman.getvalue())
        st.rerun()

    if s.atur_ketik:
        teks = st.text_input("Jawaban anak", key=f"ketik_{s.kode}_{s.indeks}_{s.nonce_mic}")
        if st.button("Kirim jawaban", key="tombol_kirim") and teks.strip():
            proses_teks([teks.strip()])
            st.rerun()

    if balasan and balasan["jenis"] != "ulang":
        with st.expander("Dengar pertanyaannya lagi"):
            st.html(f'<p class="kecil">{html.escape(adegan["tanya"])}</p>')
            putar_suara(adegan["tanya"], autoplay=False)

    if s.gangguan >= MAKS_GANGGUAN_SUARA:
        st.button("Lewati pertanyaan ini", key="tombol_lewati", width="stretch", on_click=lewati_pertanyaan)


def tahap_hasil(cerita: dict, adegan: dict) -> None:
    s = st.session_state
    kartu_balasan(s.balasan)
    kartu_banding(s.balasan, adegan, tampilkan_kunci=True)
    panel_detail_nlp(s.balasan)
    putar_suara(s.balasan["pesan"])
    akhir = s.indeks + 1 >= len(cerita["adegan"])
    st.button("Lihat stikerku" if akhir else "Lanjut cerita", key="tombol_lanjut", type="primary",
              width="stretch", on_click=ke_adegan_berikutnya)


def halaman_cerita() -> None:
    s = st.session_state
    kiri, kanan = st.columns([4, 1], vertical_alignment="center")
    with kiri:
        papan_stiker()
    with kanan:
        st.button("Ganti cerita", key="tombol_ganti", width="stretch", on_click=ke_beranda)

    st.html(gambar_adegan(s.kode, s.indeks))
    tahap = {"dengar": tahap_dengar, "tanya": tahap_tanya, "hasil": tahap_hasil}[s.tahap]
    tahap(CERITA[s.kode], adegan_aktif())


def halaman_tamat() -> None:
    s = st.session_state
    cerita = CERITA[s.kode]
    didapat = {r["indeks"] for r in s.riwayat if r["status"] == "benar"}
    pesan = (f"Hebat, ceritanya sudah tamat! Kamu mendapat {len(didapat)} stiker dari "
             f"{len(cerita['adegan'])}. {cerita['ajaran']}")

    st.html(judul_balok("TAMAT"))
    stiker = "".join(
        f'<span>{a["stiker"]}</span>' if i in didapat else f'<span class="kosong">{a["stiker"]}</span>'
        for i, a in enumerate(cerita["adegan"])
    )
    kertas(f'<p class="bacaan" style="max-width:none;text-align:center">{html.escape(pesan)}</p>')
    kertas(f'<div class="buku-stiker">{stiker}</div>')
    putar_suara(pesan)

    kiri, kanan = st.columns(2)
    with kiri:
        st.button("Ulangi cerita", key="tombol_ulang", type="primary", width="stretch", on_click=mulai_cerita, args=(s.kode,))
    with kanan:
        st.button("Pilih cerita lain", key="tombol_lain", width="stretch", on_click=ke_beranda)

    baris = "".join(
        f'<tr><td>{html.escape(r["tanya"])}</td><td>{html.escape(r["dengar"])}</td>'
        f'<td>{html.escape(r["kunci"])}</td><td>{r["skor"] * 100:.0f}%</td><td>{html.escape(r["status"])}</td></tr>'
        for r in s.riwayat
    )
    kertas(
        '<p class="kecil"><b>Catatan untuk guru</b></p><table class="tabel-hasil">'
        "<tr><th>Pertanyaan</th><th>Jawaban anak</th><th>Jawaban sistem</th><th>Skor</th><th>Status</th></tr>"
        f"{baris}</table>"
    )
