# -*- coding: utf-8 -*-
"""Ilustrasi adegan: menyusun SVG dari latar dan objek yang tertulis di korpus.
"""

from __future__ import annotations

import base64
import html
from functools import lru_cache

from modul.korpus import CERITA


# =============================================================================
# ILUSTRASI ADEGAN (SVG)
# Susunan gambar tiap adegan ada di korpus (kolom "gambar"): satu latar dan daftar objek.
#   {"emoji": "🐊", "x": 470, "y": 400, "ukuran": 120}   emoji sistem bertepi putih (stiker)
#   {"gambar": "kancil", "x": 230, "y": 248, ...}        gambar buatan sendiri di bawah ini
# Kancil digambar sendiri karena tidak ada emojinya.
# =============================================================================


def _stiker(emoji: str, x: int, y: int, ukuran: int = 90, miring: int = 0, cermin: bool = False, hijau: bool = False) -> str:
    skala = "scale(-1,1)" if cermin else ""
    kelas = "stk stk-hijau" if hijau else "stk"
    return (
        f'<g transform="translate({x},{y}) rotate({miring}) {skala}">'
        f'<text class="{kelas}" font-size="{ukuran}" text-anchor="middle" dominant-baseline="central">{emoji}</text></g>'
    )


def _kancil(x: int, y: int, skala: float = 1.0, cermin: bool = False) -> str:
    """Kancil gambar sendiri. Titik (x, y) adalah tengah badan."""
    balik = -1 if cermin else 1
    return (
        f'<g class="stk" transform="translate({x},{y}) scale({balik * skala},{skala})">'
        # kaki belakang dan depan
        '<path d="M-44 18 L-52 74 L-41 74 L-30 24 Z" fill="#8A5526"/>'
        '<path d="M-22 22 L-24 74 L-13 74 L-8 24 Z" fill="#A9692F"/>'
        '<path d="M22 22 L20 74 L31 74 L36 22 Z" fill="#8A5526"/>'
        '<path d="M40 18 L44 74 L55 74 L54 16 Z" fill="#A9692F"/>'
        # badan, perut, ekor
        '<ellipse cx="0" cy="0" rx="66" ry="36" fill="#C07F3E"/>'
        '<path d="M-48 20 Q0 46 48 20 Q0 30 -48 20 Z" fill="#F4DDB5"/>'
        '<ellipse cx="-68" cy="-14" rx="11" ry="9" fill="#F4DDB5"/>'
        # leher dan kepala
        '<path d="M34 -22 Q56 -58 70 -62 L92 -38 Q72 -14 58 12 Z" fill="#C07F3E"/>'
        '<ellipse cx="86" cy="-60" rx="30" ry="22" fill="#C07F3E"/>'
        '<ellipse cx="108" cy="-54" rx="13" ry="10" fill="#F4DDB5"/>'
        '<circle cx="118" cy="-57" r="5" fill="#2A1548"/>'
        # telinga
        '<ellipse cx="66" cy="-88" rx="9" ry="20" fill="#A9692F" transform="rotate(-20 66 -88)"/>'
        '<ellipse cx="84" cy="-92" rx="9" ry="20" fill="#C07F3E" transform="rotate(8 84 -92)"/>'
        '<ellipse cx="84" cy="-90" rx="4" ry="12" fill="#F4C2A8" transform="rotate(8 84 -90)"/>'
        # mata dan senyum
        '<circle cx="90" cy="-66" r="7" fill="#fff"/><circle cx="92" cy="-66" r="4" fill="#2A1548"/>'
        '<path d="M100 -46 Q108 -40 116 -46" fill="none" stroke="#2A1548" stroke-width="2.5" stroke-linecap="round"/>'
        "</g>"
    )


def _rambutan(x: int, y: int, r: int = 13) -> str:
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#E5273F" stroke="#FF8FA0" stroke-width="5" stroke-dasharray="2 4"/>'


def _batu(x: int, y: int, skala: float = 1.0) -> str:
    return (
        f'<g class="stk" transform="translate({x},{y}) scale({skala})">'
        '<path d="M-90 60 L-70 -18 L-28 -62 L34 -54 L78 -8 L92 60 Z" fill="#7C7F93"/>'
        '<path d="M-28 -62 L-12 -6 L-70 -18 Z M34 -54 L-12 -6 L78 -8 Z" fill="#9A9DB0"/>'
        "</g>"
    )


def _pohon(x: int, y: int, skala: float = 1.0, warna: str = "#178A4C") -> str:
    return (
        f'<g transform="translate({x},{y}) scale({skala})">'
        '<rect x="-12" y="0" width="24" height="90" rx="6" fill="#7A4B22"/>'
        f'<circle cx="0" cy="-40" r="62" fill="{warna}"/><circle cx="-50" cy="-8" r="42" fill="{warna}"/>'
        f'<circle cx="50" cy="-8" r="42" fill="{warna}"/></g>'
    )


PENGGAMBAR = {"kancil": _kancil, "rambutan": _rambutan, "batu": _batu, "pohon": _pohon}


def _bukit(warna1: str, warna2: str) -> str:
    return (
        f'<path d="M0 300 Q180 170 380 270 T760 240 T960 280 V480 H0 Z" fill="{warna1}"/>'
        f'<path d="M0 350 Q240 250 480 330 T960 320 V480 H0 Z" fill="{warna2}"/>'
    )


def _laut(warna: str = "#1496D8") -> str:
    return (
        f'<path d="M0 300 Q120 280 240 300 T480 300 T720 300 T960 300 V480 H0 Z" fill="{warna}"/>'
        '<path d="M40 350 q30 -14 60 0 t60 0 M380 400 q30 -14 60 0 t60 0 M700 346 q30 -14 60 0 t60 0" '
        'fill="none" stroke="#C9F2FF" stroke-width="6" stroke-linecap="round"/>'
    )


# Latar adegan. Warna langit dan tanah mengikuti suasana cerita.
LATAR = {
    "sungai": '<rect width="960" height="480" fill="#9BE8FF"/><circle cx="820" cy="90" r="52" fill="#FFD84D"/>'
    + _bukit("#6FDB7E", "#35BE69") + _pohon(90, 190, 1.1)
    + '<path d="M0 330 Q240 300 480 330 T960 325 V480 H0 Z" fill="#2CB5E8"/>'
    '<path d="M60 380 q30 -14 60 0 t60 0 M420 420 q30 -14 60 0 t60 0 M720 372 q30 -14 60 0 t60 0" '
    'fill="none" stroke="#BDEFFF" stroke-width="6" stroke-linecap="round"/>',
    "senja": '<rect width="960" height="480" fill="#FFB347"/><rect y="0" width="960" height="150" fill="#FF7E5F"/>'
    '<circle cx="770" cy="170" r="74" fill="#FFE14D"/>' + _bukit("#E0559C", "#8E3FB5"),
    "ladang": '<rect width="960" height="480" fill="#FFE27A"/><circle cx="130" cy="100" r="58" fill="#FF9D2E"/>'
    + _bukit("#A8DC4B", "#5FBF3D")
    + '<path d="M0 430 H960 M0 396 H960" stroke="#3E9B2C" stroke-width="7" stroke-dasharray="26 18"/>',
    "bambu": '<rect width="960" height="480" fill="#FFCC66"/>'
    + "".join(
        f'<rect x="{x}" y="60" width="26" height="420" rx="8" fill="{w}"/>'
        for x, w in [(60, "#27A85A"), (160, "#3CC36F"), (690, "#27A85A"), (780, "#3CC36F"), (880, "#27A85A")]
    )
    + '<rect y="410" width="960" height="70" fill="#8E3FB5"/>',
    "lumpur": '<rect width="960" height="480" fill="#FF9E5E"/><circle cx="180" cy="110" r="56" fill="#FFE14D"/>'
    '<path d="M0 290 Q240 260 480 290 T960 290 V380 H0 Z" fill="#1496D8"/>'
    '<path d="M0 370 Q240 340 480 370 T960 370 V480 H0 Z" fill="#7A3E1D"/>'
    '<circle cx="660" cy="404" r="16" fill="#A85E2E"/><circle cx="720" cy="430" r="10" fill="#A85E2E"/>',
    "pantai": '<rect width="960" height="480" fill="#8FE3FF"/><circle cx="150" cy="96" r="54" fill="#FFD84D"/>'
    + _laut() + '<path d="M0 400 Q300 330 620 400 T960 380 V480 H0 Z" fill="#FFE3A3"/>',
    "dermaga": '<rect width="960" height="480" fill="#FFC6A8"/><circle cx="800" cy="110" r="60" fill="#FFF2A8"/>'
    + _laut("#1E7BD6") + '<path d="M0 410 Q300 360 620 420 T960 410 V480 H0 Z" fill="#FFD98A"/>',
    "badai": '<rect width="960" height="480" fill="#3B3F73"/>'
    '<path d="M0 70 Q90 20 200 60 T420 56 T640 60 T960 46 V0 H0 Z" fill="#23264F"/>'
    '<path d="M540 56 L500 180 L556 170 L512 290" fill="none" stroke="#FFE14D" stroke-width="12" stroke-linejoin="round"/>'
    + _laut("#14508F"),
    "polos": '<rect width="960" height="480" fill="#FFE27A"/>' + _bukit("#FFB347", "#FF7E5F"),
}


def _objek(objek: dict) -> str:
    """Satu objek gambar dari korpus: kunci "gambar" memilih penggambar, selain itu stiker emoji."""
    argumen = {k: v for k, v in objek.items() if k != "gambar"}
    return PENGGAMBAR[objek["gambar"]](**argumen) if "gambar" in objek else _stiker(**argumen)


# Efek stiker: tepi putih mengikuti bentuk gambar. Gaya ini harus berada di dalam SVG,
# karena SVG yang dimuat lewat <img> tidak bisa membaca CSS halaman.
_TEPI_PUTIH = "drop-shadow(3px 0 0 #fff) drop-shadow(-3px 0 0 #fff) drop-shadow(0 3px 0 #fff) drop-shadow(0 -3px 0 #fff)"
GAYA_SVG = (
    f"<style>.stk {{ filter: {_TEPI_PUTIH} drop-shadow(0 4px 2px rgba(42,21,72,.35)); }}"
    f".stk-hijau {{ filter: hue-rotate(130deg) saturate(1.3) {_TEPI_PUTIH}; }}</style>"
)


@lru_cache(maxsize=64)
def gambar_adegan(kode: str, indeks: int) -> str:
    """Menyusun SVG satu adegan dari latar dan objek di korpus.

    st.html menyaring HTML dengan DOMPurify dan membuang elemen <svg>, jadi SVG
    dikemas sebagai gambar data URI (<img>), yang lolos penyaringan.
    """
    gambar = CERITA[kode]["adegan"][indeks]["gambar"]
    isi = LATAR.get(gambar["latar"], LATAR["polos"]) + "".join(_objek(o) for o in gambar["objek"])
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="480" viewBox="0 0 960 480">{GAYA_SVG}{isi}</svg>'
    label = html.escape(f"Gambar adegan {indeks + 1} cerita {CERITA[kode]['judul']}")
    return f'<img class="adegan" alt="{label}" src="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}">'
