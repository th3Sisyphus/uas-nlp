# -*- coding: utf-8 -*-
"""Logika flashcard kata: memilih sesi, menggambar kartu, dan mencocokkan ucapan anak.

Semua fungsi di sini murni (tanpa Streamlit), kecuali gambar_kartu yang memakai
st.cache_data untuk membaca berkas gambar sekali saja.
"""

from __future__ import annotations

import base64
import difflib
import html
import random
from pathlib import Path

import streamlit as st

from modul.konfigurasi import AMBANG_KATA_BENAR, AMBANG_KATA_HAMPIR, FOLDER, JUMLAH_KARTU_SESI
from modul.nlp import normalisasi


# =============================================================================
# SESI DAN GAMBAR
# =============================================================================


def pilih_sesi(kartu: list[dict], jumlah: int = JUMLAH_KARTU_SESI) -> list[dict]:
    """Ambil beberapa kartu pertama (urutan berkas = mudah ke sulit), lalu acak urutannya."""
    sesi = list(kartu[:jumlah])
    random.shuffle(sesi)
    return sesi


@st.cache_data(max_entries=128)
def _data_uri(berkas: str) -> str | None:
    """Isi berkas gambar sebagai data URI. None bila berkasnya tidak ada."""
    jalur = Path(berkas) if Path(berkas).is_absolute() else FOLDER / berkas
    if not jalur.is_file():
        return None
    isi = base64.b64encode(jalur.read_bytes()).decode("ascii")
    jenis = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(
        jalur.suffix.lower(), "image/png")
    return f"data:{jenis};base64,{isi}"


def gambar_kartu(kartu: dict) -> str:
    """HTML gambar kartu: berkas gambar, kalau tidak ada emoji besar, kalau tidak kotak kata."""
    uri = _data_uri(kartu["gambar"]) if kartu.get("gambar") else None
    if uri:
        return f'<img class="gambar-kartu" src="{uri}" alt="{html.escape(kartu["kata"])}">'
    if kartu.get("emoji"):
        return f'<div class="emoji-kartu" aria-hidden="true">{html.escape(kartu["emoji"])}</div>'
    return f'<div class="kotak-kata" aria-hidden="true">{html.escape(kartu["kata"].upper())}</div>'


# =============================================================================
# PENCOCOKAN UCAPAN
# Kata kartu lain ikut dinilai karena kosakata tema ini tertutup: anak hanya bisa
# menyebut salah satu kartu di tema yang sama.
# =============================================================================


def _skor_kartu(ucapan: str, kartu: dict) -> float:
    """Kemiripan satu ucapan yang sudah dinormalisasi dengan satu kartu (0..1)."""
    if not ucapan:
        return 0.0
    variasi = [normalisasi(v) for v in kartu["variasi"]]
    if ucapan in variasi:
        return 1.0
    kata = normalisasi(kartu["kata"])
    # Kata utuh: 1,0 bila seluruh kata kartu disebut, 0,85 bila hanya kata pertamanya
    # ("jeruk" dalam "jeruk bali"). Skor 0,85 tetap di atas ambang hampir, jadi target
    # yang benar tidak jatuh ke "salah" hanya karena ada kartu lain yang lebih spesifik.
    kata_ucapan = set(ucapan.split())
    kata_kartu = kata.split()
    if all(k in kata_ucapan for k in kata_kartu):
        return 1.0 if len(kata_ucapan - set(kata_kartu)) <= 1 else 0.85
    if kata_kartu[0] in kata_ucapan:
        return 0.85
    # Spasi dibuang agar ucapan yang tergabung ("iniapel") tetap terukur.
    return max(difflib.SequenceMatcher(None, ucapan, v).ratio() for v in variasi + [v.replace(" ", "") for v in variasi])


def _disebut_utuh(ucapan: list[str], semua: list[dict], id_kartu: str) -> bool:
    """True bila salah satu ucapan memuat kata kartu itu sebagai kata utuh."""
    kartu = next(k for k in semua if k["id"] == id_kartu)
    kata = normalisasi(kartu["kata"])
    return any(kata in u.split() for u in ucapan)


def _kecocokan_persis(ucapan: list[str], semua: list[dict], id_kartu: str) -> tuple[int, int]:
    """Penentu seri: persis salah satu variasi (1/0), lalu panjang kata kartu."""
    kartu = next(k for k in semua if k["id"] == id_kartu)
    variasi = {normalisasi(v) for v in kartu["variasi"]}
    return (int(any(u in variasi for u in ucapan)), len(normalisasi(kartu["kata"])))


def cocokkan_kata(alternatif: list[str], target: dict, semua: list[dict]) -> dict:
    """Menilai ucapan anak terhadap kartu target di antara semua kartu tema itu.

    Hasil: {"status": benar | hampir | salah, "skor", "terdengar", "terdekat"}.
    Benar hanya bila kartu terdekat adalah target dan skornya mencapai ambang benar.
    Bila ada kartu lain yang persis disebut, kartu itu yang dianggap terdekat,
    supaya "jeruk bali" tidak dinilai sebagai "jeruk".
    """
    ucapan = [normalisasi(a) for a in alternatif if normalisasi(a)]
    skor = {kartu["id"]: max((_skor_kartu(u, kartu) for u in ucapan), default=0.0) for kartu in semua}
    # Urutan penentu: persis salah satu variasi, lalu skor kemiripan, lalu jumlah kata
    # yang disebut utuh, lalu kata terpanjang. Skor di atas kata utuh agar "ini buah
    # naga" tidak kalah dari "beri hitam" yang kebetulan mirip.
    terdekat = max(
        semua, key=lambda k: (
            _kecocokan_persis(ucapan, semua, k["id"])[0],
            skor[k["id"]],
            int(_disebut_utuh(ucapan, semua, k["id"])),
            len(normalisasi(k["kata"])),
        ),
    )["id"] if skor else None
    skor_target = skor.get(target["id"], 0.0)

    if terdekat == target["id"] and skor_target >= AMBANG_KATA_BENAR:
        status = "benar"
    elif terdekat == target["id"] and skor_target >= AMBANG_KATA_HAMPIR:
        status = "hampir"
    else:
        status = "salah"
    return {"status": status, "skor": skor_target, "terdengar": " / ".join(alternatif), "terdekat": terdekat}


def pengecoh(target: dict, semua: list[dict], jumlah: int = 2) -> list[dict]:
    """Kartu lain dari tema yang sama, untuk mode ketuk gambar."""
    lain = [k for k in semua if k["id"] != target["id"]]
    return random.sample(lain, min(jumlah, len(lain)))
