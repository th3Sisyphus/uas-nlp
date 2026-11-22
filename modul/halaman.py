# -*- coding: utf-8 -*-
"""Halaman aplikasi: menu tema, daftar cerita, cerita (tahap dengar, tanya, hasil), dan tamat.
"""

from __future__ import annotations

import html
import random

import streamlit as st
import streamlit.components.v1 as components

from modul.daftar import potong_halaman, saring
from modul.flashcard import gambar_kartu, pengecoh
from modul.ilustrasi import gambar_adegan
from modul.komponen import judul_balok, kartu_balasan, kartu_banding, kertas, panel_detail_nlp, papan_stiker
from modul.konfigurasi import MAKS_GANGGUAN_SUARA
from modul.korpus import CERITA, FLASHCARD
from modul.narator import narator
from modul.status import (
    adegan_aktif, kartu_aktif, kartu_berikutnya, ke_adegan_berikutnya, ke_beranda, ke_daftar,
    ke_pertanyaan, ke_ucap, lewati_pertanyaan, mulai_cerita, mulai_kartu, proses_kata, proses_teks,
    tangani_rekaman, tangani_rekaman_kartu,
)
from modul.tts import putar_suara

WILAYAH = ("Semua", "Jawa", "Sumatera", "Kalimantan", "Sulawesi", "Bali dan Nusa Tenggara", "Nusantara")
PER_HALAMAN = 6


def ganti_saringan(wilayah: str) -> None:
    st.session_state.update(wilayah=wilayah, nomor_halaman=1)


def pindah_halaman(nomor: int) -> None:
    st.session_state.nomor_halaman = nomor


def kejutkan_aku() -> None:
    mulai_cerita(random.choice(list(CERITA)))


def halaman_beranda() -> None:
    st.html(judul_balok("DONGENG") + '<p class="anak-judul">Mau belajar apa hari ini?</p>')
    tema = [
        ("Cerita Rakyat", f'{len(CERITA)} cerita', "pilih_tema_rakyat", lambda: ke_daftar()),
        ("Hewan", f'{len(FLASHCARD["hewan"]["kartu"])} kartu', "pilih_tema_hewan", lambda: mulai_kartu("hewan")),
        ("Buah", f'{len(FLASHCARD["buah"]["kartu"])} kartu', "pilih_tema_buah", lambda: mulai_kartu("buah")),
    ]
    for wadah, (nama, keterangan, kunci, aksi) in zip(st.columns(3, gap="medium"), tema):
        with wadah:
            kertas(f"<h3>{html.escape(nama)}</h3><p>{html.escape(keterangan)}</p>", "kartu-tema")
            st.button("Pilih", key=kunci, type="primary", width="stretch", on_click=aksi)


def kartu_cerita(kode: str, cerita: dict) -> None:
    with st.container(key=f"kartu_{kode}"):
        kertas(f'{gambar_adegan(kode, 0)}<h3>{html.escape(cerita["judul"])}</h3>'
               f'<p>{html.escape(cerita["asal"])}</p>', "kartu-cerita")
        st.button("Dengarkan", key=f"pilih_{kode}", type="primary", width="stretch",
                  on_click=mulai_cerita, args=(kode,))


def halaman_daftar() -> None:
    s = st.session_state
    st.html(judul_balok("CERITA") + '<p class="anak-judul">Pilih cerita yang mau kamu dengar!</p>')

    kiri, kanan = st.columns([1, 1])
    with kiri:
        st.button("Menu tema", key="tombol_menu", width="stretch", on_click=ke_beranda)
    with kanan:
        st.button("Kejutkan aku!", key="tombol_kejut", type="primary", width="stretch", on_click=kejutkan_aku)

    for wadah, wilayah in zip(st.columns(7, gap="small"), WILAYAH):
        with wadah:
            st.button(wilayah, key=f"saring_{wilayah}", width="stretch", on_click=ganti_saringan, args=(wilayah,))

    semua = saring(list(CERITA.items()), s.wilayah, s.kata_cari)
    if not semua:
        kertas('<p class="bacaan">Belum ada cerita yang cocok. Coba kata lain, ya.</p>')
    isi, total = potong_halaman(semua, s.nomor_halaman, PER_HALAMAN)
    for awal in range(0, len(isi), 3):
        for wadah, (kode, cerita) in zip(st.columns(3, gap="medium"), isi[awal:awal + 3]):
            with wadah:
                kartu_cerita(kode, cerita)

    kiri, tengah, kanan = st.columns([1, 1, 1], vertical_alignment="center")
    with kiri:
        st.button("Sebelumnya", key="tombol_sebelum", width="stretch", disabled=s.nomor_halaman <= 1,
                  on_click=pindah_halaman, args=(s.nomor_halaman - 1,))
    with tengah:
        st.html(f'<p class="kecil" style="text-align:center">Halaman {s.nomor_halaman} dari {total}</p>')
    with kanan:
        st.button("Berikutnya", key="tombol_berikut", width="stretch", disabled=s.nomor_halaman >= total,
                  on_click=pindah_halaman, args=(s.nomor_halaman + 1,))

    with st.expander("Untuk orang tua dan guru"):
        st.text_input("Cari judul cerita", key="kata_cari", on_change=ganti_saringan, args=(s.wilayah,))


# Menyeragamkan tampilan perekam jadi satu tombol bulat. Ditempel sekali per render;
# mencari data-testid yang stabil, bukan class acak Streamlit.
_SKRIP_MIKROFON = """<script>
(() => {
  const induk = window.parent;
  if (induk.__bulatMikrofon) return;
  induk.__bulatMikrofon = 1;
  const pasang = () => {
  if (induk.__gayaMikrofon) return;
  induk.__gayaMikrofon = 1;
  const gaya = induk.document.createElement("style");
  gaya.textContent = `
    [data-testid="stWidgetLabel"] { display: none !important; }
    [data-testid="stAudioInput"] { background: none !important; border: none !important;
      box-shadow: none !important; padding: 0 !important; width: auto !important; }
    [data-testid="stAudioInputWaveSurfer"] { display: none !important; }
    [data-testid="stAudioInputActionButton"] {
      width: 60px !important; height: 60px !important; border-radius: 50% !important;
      background: #E84D4D !important; color: #fff !important; border: 3px solid #2A1548 !important;
      box-shadow: 0 3px 0 #B92F3C !important; }
    [data-testid="stAudioInputActionButton"]:hover { background: #F26363 !important; }
  `;
  induk.document.head.appendChild(gaya);
  };
  pasang();
  induk.document.addEventListener("DOMContentLoaded", pasang);
})();
</script>"""


def _mikrofon(kunci: str) -> None:
    """Tombol mikrofon bulat untuk merekam jawaban.

    shortkut: st.audio_input 1.50 tidak punya bentuk tombol ikon dan memakai class acak,
    jadi tampilannya diubah lewat satu <style> yang disuntik ke halaman induk dari iframe
    components.html (st.html menyaring <script>). Perilaku ASR tetap milik widget.
    Upgrade: komponen audio kustom bila data-testid berubah.
    """
    with st.container(key=f"suara_{kunci}", horizontal_alignment="center"):
        st.audio_input("Rekam jawabanmu", key=f"mic_{kunci}", label_visibility="collapsed")
    components.html(_SKRIP_MIKROFON, height=0)


def narator_cerita(keadaan: str, teks: str = "", durasi_bicara: float = 0.0) -> None:
    """Narator + tombol mikrofon di bawah tokoh (dipakai di cerita dan flashcard).

    st.html menyaring <svg> (lihat ilustrasi.py), jadi SVG narator dikirim lewat
    st.markdown yang mempertahankan HTML mentah.
    """
    st.markdown(narator(keadaan, teks, durasi_bicara), unsafe_allow_html=True)
    _mikrofon(f"{st.session_state.kode}_{st.session_state.indeks}_{st.session_state.nonce_mic}")


def tahap_dengar(cerita: dict, adegan: dict) -> None:
    narator_cerita("bicara", adegan["narasi"], 2.4)
    kertas(f'<p class="bacaan">{html.escape(adegan["narasi"])}</p>')
    putar_suara(adegan["narasi"])
    st.button("Aku siap menjawab", key="tombol_siap", type="primary", width="stretch", on_click=ke_pertanyaan)


def tahap_tanya(cerita: dict, adegan: dict) -> None:
    s = st.session_state
    balasan = s.balasan

    if balasan:
        pose = {"benar": "benar", "hampir": "menyemangati"}.get(balasan["jenis"], "bingung")
        narator_cerita(pose, balasan["pesan"], 2.0)
        kartu_balasan(balasan)
        if balasan["jenis"] != "ulang":
            kartu_banding(balasan, adegan, tampilkan_kunci=False)
        panel_detail_nlp(balasan)
        putar_suara(balasan["pesan"])
    else:
        narator_cerita("mendengar", adegan["tanya"], 2.0)
        kertas(f'<p class="tanya">{html.escape(adegan["tanya"])}</p>')
        putar_suara(adegan["tanya"])

    _mikrofon(f"{s.kode}_{s.indeks}_{s.nonce_mic}")
    rekaman = s.get(f"mic_{s.kode}_{s.indeks}_{s.nonce_mic}")
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
        st.button("Ganti cerita", key="tombol_ganti", width="stretch", on_click=ke_daftar)

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
        st.button("Pilih cerita lain", key="tombol_lain", width="stretch", on_click=ke_daftar)

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


# ---- Flashcard kata: tema hewan dan buah -------------------------------------


def tahap_kenal(kartu: dict) -> None:
    narator_cerita("melambai", f"Halo! Ini {kartu['kata']}.", 2.0)
    kertas(f'<div class="kartu-kata">{gambar_kartu(kartu)}'
           f'<p class="kata-besar">{html.escape(kartu["kata"])}</p></div>')
    putar_suara(kartu["kalimat"])
    st.button("Aku mau bilang!", key="tombol_mau_bilang", type="primary", width="stretch", on_click=ke_ucap)


def ketuk_gambar(kartu: dict, semua: list[dict]) -> None:
    """Mode cadangan setelah mikrofon gagal beberapa kali: anak mengetuk gambar yang benar."""
    st.html('<p class="anak-judul">Ketuk gambar yang benar!</p>')
    pilihan = [kartu] + pengecoh(kartu, semua)
    random.shuffle(pilihan)
    for wadah, kandidat in zip(st.columns(3, gap="medium"), pilihan):
        with wadah:
            kertas(f'<div class="kartu-kata">{gambar_kartu(kandidat)}</div>')
            st.button("Ini!", key=f"ketuk_{kandidat['id']}", width="stretch", on_click=proses_kata,
                      args=([kandidat["kata"]],))


def tahap_ucap(kartu: dict, semua: list[dict]) -> None:
    s = st.session_state
    if s.balasan:
        pose = {"benar": "benar", "hampir": "menyemangati"}.get(s.balasan["jenis"], "bingung")
        narator_cerita(pose, s.balasan["pesan"], 2.0)
        kartu_balasan(s.balasan)
        putar_suara(s.balasan["pesan"])
    else:
        narator_cerita("mendengar", f"Ayo bilang, {kartu['kata']}!", 2.0)
        st.html(f'<p class="tanya" style="text-align:center">Ayo bilang, {html.escape(kartu["kata"])}!</p>')
        putar_suara(f"Ayo bilang, {kartu['kata']}!")

    if s.gangguan >= MAKS_GANGGUAN_SUARA:
        ketuk_gambar(kartu, semua)
        return

    _mikrofon(f"kartu_{s.no_kartu}_{s.nonce_mic}")
    rekaman = s.get(f"mic_kartu_{s.no_kartu}_{s.nonce_mic}")
    if rekaman is not None:
        with st.spinner("Sebentar, aku dengarkan dulu..."):
            tangani_rekaman_kartu(rekaman.getvalue())
        st.rerun()

    if s.atur_ketik:
        teks = st.text_input("Jawaban anak", key=f"ketik_kartu_{s.no_kartu}_{s.nonce_mic}")
        if st.button("Kirim jawaban", key="tombol_kirim_kartu") and teks.strip():
            proses_kata([teks.strip()])
            st.rerun()

    st.button("Dengar lagi", key="tombol_dengar_lagi", width="stretch", on_click=ke_ucap)


def tahap_hasil_kartu(kartu: dict) -> None:
    s = st.session_state
    kartu_balasan(s.balasan)
    putar_suara(s.balasan["pesan"])
    st.button("Kartu berikutnya", key="tombol_kartu_lanjut", type="primary", width="stretch",
              on_click=kartu_berikutnya)


def halaman_kartu() -> None:
    s = st.session_state
    kartu = kartu_aktif()
    kiri, kanan = st.columns([4, 1], vertical_alignment="center")
    with kiri:
        st.html(f'<p class="anak-judul" style="text-align:left">Kartu {s.no_kartu + 1} '
                f'dari {len(s.sesi_kartu)}</p>')
    with kanan:
        st.button("Selesai", key="tombol_selesai_kartu", width="stretch", on_click=ke_beranda)

    if s.tahap_kartu == "kenal":
        tahap_kenal(kartu)
    elif s.tahap_kartu == "ucap":
        tahap_ucap(kartu, s.sesi_kartu)
    else:
        tahap_hasil_kartu(kartu)


def halaman_selesai_kartu() -> None:
    s = st.session_state
    jumlah = len(s.sesi_kartu)
    pesan = f"Hebat! Kamu sudah menyelesaikan {jumlah} kartu. Yuk, pilih yang lain!"

    st.html(judul_balok("SELESAI"))
    kertas(f'<p class="bacaan" style="max-width:none;text-align:center">{html.escape(pesan)}</p>')
    putar_suara(pesan)
    st.button("Kembali ke beranda", key="tombol_kembali_beranda", type="primary", width="stretch",
              on_click=ke_beranda)
