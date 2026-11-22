# -*- coding: utf-8 -*-
"""Narator chibi "Steven": SVG berlapis + CSS untuk menemani cerita.

Satu gambar, enam pose. Pose tidak digambar ulang: tiap pose hanya mengganti isi
grup #mata/#alis/#mulut dan menambah transform pada grup #kepala, #tangan-kiri,
#tangan-kanan, #efek. Proporsi dan wajah selalu sama.

Semua bagian gambar (kepala, rambut, badan, tangan, efek) ditulis di dalam SVG.
Satu-satunya teks HTML di luar SVG adalah gelembung bicara, dan isinya di-escape.

Catatan gaya: ilustrasi.py mengemas SVG sebagai <img> karena st.html menyaring
<svg>. Narator butuh CSS hidup (kedip, napas, mulut), jadi SVG ditulis langsung
sebagai HTML dan animasi ditaruh di <style> di dalam SVG itu sendiri.
"""

from __future__ import annotations

import html
import re

from functools import lru_cache


# =============================================================================
# GAYA
# =============================================================================

# Palet: 5 warna hangat-bercerah, kontras tinggi di latar terang.
_KULIT = "#FFC79E"
_KULIT_TEPI = "#E79A66"
_RAMBUT = "#4A2B16"
_KAIN = "#E84D4D"
_KAIN_TUA = "#B92F3C"
_AKSEN = "#FFC93C"

_TEBAL = 4  # garis tepi tebal dan seragam untuk seluruh tokoh


def _gaya(durasi: float) -> str:
    """CSS animasi. Durasi bicara mengikuti panjang audio (detik).

    Napas 2-3 px dan kedipan selalu aktif; gerak mulut hanya di pose "bicara".
    prefers-reduced-motion mematikan semua gerak selain pergantian pose.
    """
    # Satu siklus buka-tutup mulut per suku kata kira-kira 0,28 detik.
    # shortkut: tanpa durasi audio, pakai 0,28 detik; perbaiki bila keluhan.
    per = max(0.16, durasi / 6) if durasi > 0 else 0.28
    return f"""
.sv {{ --tebal:{_TEBAL}; position:relative; }}
.sv svg {{ display:block; width:100%; height:auto; overflow:visible; }}
.sv .napas {{ transform-origin:100px 250px; animation:napas 4s ease-in-out infinite; }}
.sv .kedip {{ transform-origin:100px 100px; animation:kedip 4.6s infinite; }}
.sv .bicara-mulut {{ animation:mulut {per:.2f}s infinite; }}
.sv .bicara-mulut .m0 {{ animation:b0 {per:.2f}s steps(1) infinite; }}
.sv .bicara-mulut .m1 {{ animation:b1 {per:.2f}s steps(1) infinite; }}
.sv .bicara-mulut .m2 {{ animation:b2 {per:.2f}s steps(1) infinite; }}
.sv .lambai {{ transform-origin:150px 190px; animation:lambai 1s ease-in-out infinite; }}
.sv .lompat {{ animation:lompat 0.9s ease-in-out infinite; }}
.sv .bintang {{ animation:bintang 1.2s ease-in-out infinite; }}
.sv .tanya {{ animation:tanya 1.6s ease-in-out infinite; }}
@keyframes napas {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-3px) }} }}
@keyframes kedip {{ 0%,92%,100% {{ transform:scaleY(1) }} 96% {{ transform:scaleY(.08) }} }}
@keyframes mulut {{ 0%,100% {{ opacity:1 }} }}
@keyframes b0 {{ 0%,32% {{ opacity:1 }} 33%,100% {{ opacity:0 }} }}
@keyframes b1 {{ 0%,32% {{ opacity:0 }} 33%,65% {{ opacity:1 }} 66%,100% {{ opacity:0 }} }}
@keyframes b2 {{ 0%,65% {{ opacity:0 }} 66%,100% {{ opacity:1 }} }}
.gelembung {{ position:relative; background:#fff; border:3px solid #2A1548; border-radius:16px; padding:10px 14px; max-width:340px; }}
.gelembung p {{ margin:0; font-size:20px; line-height:1.3; font-weight:600; color:#2A1548; }}
.sv {{ position:relative; }}
.sv .suara {{ position:absolute; left:50%; bottom:4px; width:60px; transform:translateX(-50%); z-index:2; }}
.sv .suara [data-testid="stAudioInput"], .sv .suara [data-testid="stAudioInputControl"] {{ background:none; border:none; box-shadow:none; padding:0; }}
.sv .suara button {{ width:60px; height:60px; min-height:60px; border-radius:50%; background:#E84D4D; color:#fff; border:3px solid #2A1548; box-shadow:0 3px 0 #B92F3C; }}
.sv .suara button:hover {{ background:#F26363; color:#fff; }}
.sv .suara [data-testid="stAudioInput"] audio, .sv .suara [data-testid="stAudioInput"] label,
.sv .suara [data-testid="stAudioInput"] small {{ display:none; }}
.sv .suara [data-testid="stWidgetLabel"] {{ display:none; }}
.gelembung .ekor {{ position:absolute; left:-22px; top:50%; width:20px; height:20px; transform:translateY(-50%); }}
@keyframes lambai {{ 0%,100% {{ transform:rotate(-14deg) }} 50% {{ transform:rotate(16deg) }} }}
@keyframes lompat {{ 0%,100% {{ transform:translateY(0) }} 45% {{ transform:translateY(-10px) }} }}
@keyframes bintang {{ 0%,100% {{ transform:scale(.85); opacity:.7 }} 50% {{ transform:scale(1.15); opacity:1 }} }}
@keyframes tanya {{ 0%,100% {{ transform:translateY(0) rotate(-6deg) }} 50% {{ transform:translateY(-6px) rotate(6deg) }} }}
@media (prefers-reduced-motion: reduce) {{
  .sv .napas,.sv .kedip,.sv .bicara-mulut .m0,.sv .bicara-mulut .m1,.sv .bicara-mulut .m2,.sv .lambai,.sv .lompat,.sv .bintang,.sv .tanya {{ animation:none; }}
  .sv .kedip .mata-tutup {{ display:none; }}
}}
"""


# =============================================================================
# BAGIAN TOKOH (digambar sekali, dipakai semua pose)
# =============================================================================

def _rambut() -> str:
    return (
        '<g id="rambut">'
        f'<path d="M54 78 Q50 30 100 26 Q150 30 146 78 Q138 52 100 48 Q62 52 54 78 Z" fill="{_RAMBUT}" '
        f'stroke="#2A1548" stroke-width="{_TEBAL}" stroke-linejoin="round"/>'
        # poni kiri-kanan, geometris
        f'<path d="M58 74 Q70 58 88 56 L84 74 Z M142 74 Q130 58 112 56 L116 74 Z" fill="{_RAMBUT}"/>'
        '</g>'
    )


def _badan() -> str:
    # Batik parang sederhana: garis miring bergelombang. Geometris saja, tanpa gambar luar.
    motif = "".join(
        f'<path d="M{x} 152 q8 -10 16 0 q8 10 16 0" fill="none" stroke="{_KAIN_TUA}" stroke-width="4" stroke-linecap="round"/>'
        for x in range(60, 128, 20)
    )
    return (
        '<g id="badan">'
        # leher
        f'<rect x="90" y="128" width="20" height="16" rx="6" fill="{_KULIT_TEPI}"/>'
        # baju (kebaya netral gender)
        f'<path d="M64 152 Q100 140 136 152 L146 226 Q100 238 54 226 Z" fill="{_KAIN}" '
        f'stroke="#2A1548" stroke-width="{_TEBAL}" stroke-linejoin="round"/>'
        f'{motif}'
        # sabuk
        f'<rect x="56" y="208" width="88" height="12" rx="5" fill="{_AKSEN}" stroke="#2A1548" stroke-width="{_TEBAL}"/>'
        # celana
        f'<path d="M58 220 Q100 232 142 220 L138 250 L106 250 L100 232 L94 250 L62 250 Z" fill="{_KAIN_TUA}" '
        f'stroke="#2A1548" stroke-width="{_TEBAL}" stroke-linejoin="round"/>'
        # kaki
        f'<rect x="72" y="246" width="14" height="10" rx="4" fill="{_KULIT}" stroke="#2A1548" stroke-width="3"/>'
        f'<rect x="114" y="246" width="14" height="10" rx="4" fill="{_KULIT}" stroke="#2A1548" stroke-width="3"/>'
        '</g>'
    )


def _kepala(mata: str = "normal", alis: str = "normal", mulut: str = "senyum") -> str:
    """Kepala besar (proporsi 1:1,3 dengan badan). Wajah diganti lewat parameter."""
    return (
        '<g id="kepala">'
        f'<ellipse cx="100" cy="96" rx="52" ry="54" fill="{_KULIT}" stroke="#2A1548" stroke-width="{_TEBAL}"/>'
        # telinga
        f'<ellipse cx="48" cy="100" rx="7" ry="10" fill="{_KULIT_TEPI}" stroke="#2A1548" stroke-width="3"/>'
        f'<ellipse cx="152" cy="100" rx="7" ry="10" fill="{_KULIT_TEPI}" stroke="#2A1548" stroke-width="3"/>'
        f'<g class="kedip">{_mata(mata)}</g>'
        f'{_alis(alis)}'
        # bola pipi
        f'<circle cx="72" cy="116" r="9" fill="#FF9E8A" opacity=".55"/>'
        f'<circle cx="128" cy="116" r="9" fill="#FF9E8A" opacity=".55"/>'
        f'{_mulut(mulut)}'
        '</g>'
    )


# ---------------------------------------------------------------------------
# Bagian yang berganti per pose
# ---------------------------------------------------------------------------

def _mata(bentuk: str, kelas: str = "") -> str:
    """Mata: normal (besar), gembira (melengkung), besar (kagum/mendengar)."""
    k = f' class="{kelas}"' if kelas else ""
    if bentuk == "gembira":
        return (
            f'<g id="mata"{k}>'
            '<path d="M76 100 q8 -10 16 0 M108 100 q8 -10 16 0" fill="none" '
            'stroke="#2A1548" stroke-width="4" stroke-linecap="round"/>'
            '</g>'
        )
    r = 11 if bentuk == "besar" else 9
    return (
        f'<g id="mata"{k}>'
        f'<circle cx="84" cy="98" r="{r}" fill="#fff" stroke="#2A1548" stroke-width="3"/>'
        f'<circle cx="116" cy="98" r="{r}" fill="#fff" stroke="#2A1548" stroke-width="3"/>'
        f'<circle cx="85" cy="99" r="{max(4, r - 4)}" fill="#2A1548"/>'
        f'<circle cx="117" cy="99" r="{max(4, r - 4)}" fill="#2A1548"/>'
        '<circle cx="82" cy="95" r="2" fill="#fff"/><circle cx="114" cy="95" r="2" fill="#fff"/>'
        '</g>'
    )


def _alis(bentuk: str) -> str:
    """Alis: normal, naik (menyemangati), tanya (satu terangkat)."""
    if bentuk == "naik":
        d = "M74 82 q10 -8 20 -3 M106 79 q10 -5 20 3"
    elif bentuk == "tanya":
        d = "M74 84 q10 -2 20 0 M106 80 q10 -8 20 -4"
    else:
        d = "M74 84 q10 -4 20 -1 M106 83 q10 -3 20 1"
    return f'<g id="alis"><path d="{d}" fill="none" stroke="#2A1548" stroke-width="4" stroke-linecap="round"/></g>'


def _mulut(bentuk: str) -> str:
    """Mulut: senyum, lebar, tutup, rileks, bergelombang, dan mulut bicara (3 bentuk)."""
    if bentuk == "bicara":
        # Tiga bentuk ditumpuk; CSS menyalakan satu per langkah (steps).
        return (
            '<g id="mulut" class="bicara-mulut">'
            '<path class="m0" d="M90 121 q10 4 20 0" fill="none" stroke="#2A1548" stroke-width="4" stroke-linecap="round"/>'
            f'<ellipse class="m1" cx="100" cy="124" rx="7" ry="5" fill="{_KAIN_TUA}" stroke="#2A1548" stroke-width="3"/>'
            f'<ellipse class="m2" cx="100" cy="125" rx="10" ry="8" fill="{_KAIN_TUA}" stroke="#2A1548" stroke-width="3"/>'
            '</g>'
        )
    if bentuk == "lebar":
        d = f'M82 118 q18 22 36 0 q-18 8 -36 0 Z'
        return (f'<g id="mulut"><path d="{d}" fill="{_KAIN_TUA}" stroke="#2A1548" '
                'stroke-width="3" stroke-linejoin="round"/></g>')
    if bentuk == "tutup":
        d = "M90 122 q10 5 20 0"
    elif bentuk == "rileks":
        d = "M88 121 q12 6 24 0"
    elif bentuk == "gelombang":
        d = "M86 122 q7 -6 14 0 q7 6 14 0"
    else:
        d = "M88 119 q12 10 24 0"
    return f'<g id="mulut"><path d="{d}" fill="none" stroke="#2A1548" stroke-width="4" stroke-linecap="round"/></g>'


def _tangan(sisi: str, transform: str = "", kelas: str = "") -> str:
    """Lengan + telapak. Sisi kiri = di kiri layar. Transform menempel di siku."""
    if sisi == "kiri":
        d = f"M62 162 L44 196"
        cx, cy, sudut = 44, 200, -12
        gid = "tangan-kiri"
    else:
        d = "M138 162 L156 196"
        cx, cy, sudut = 156, 200, 12
        gid = "tangan-kanan"
    return (
        f'<g id="{gid}" class="{kelas}" transform="{transform}">'
        f'<path d="{d}" fill="none" stroke="{_KULIT}" stroke-width="12" stroke-linecap="round"/>'
        f'<circle cx="{cx}" cy="{cy}" r="10" fill="{_KULIT}" stroke="#2A1548" stroke-width="3"/>'
        '</g>'
    )


def _efek(kepala_miring: float = 0.0, tanya: bool = False, bintang: bool = False) -> str:
    """Efek kecil: tanda tanya atau bintang di sekitar kepala."""
    isi = ""
    if tanya:
        isi += (
            '<g class="tanya">'
            '<text x="160" y="52" font-size="30" font-weight="700" fill="#E84D4D" '
            'stroke="#2A1548" stroke-width="1">?</text></g>'
        )
    if bintang:
        for x, y, r in ((36, 44, 9), (164, 56, 7), (150, 26, 6)):
            isi += (
                f'<path class="bintang" transform="translate({x},{y})" '
                f'd="M0 -{r} L{r * 0.3:.1f} -{r * 0.3:.1f} L{r} 0 L{r * 0.3:.1f} {r * 0.3:.1f} '
                f'L0 {r} L{-r * 0.3:.1f} {r * 0.3:.1f} L{-r} 0 L{-r * 0.3:.1f} {-r * 0.3:.1f} Z" '
                f'fill="{_AKSEN}" stroke="#2A1548" stroke-width="2"/>'
            )
    return f'<g id="efek">{isi}</g>'


# =============================================================================
# POSE
# =============================================================================

# Tiap pose: mata, alis, mulut, efek, rotasi kepala, rotasi tangan kanan, animasi tangan kanan, animasi badan.
# Pose baru cukup satu baris di tabel ini; semua bagian gambar dipakai ulang.
_POSE = {
    "melambai":     ("normal", "normal", "senyum",    {}, 0,  -95, "lambai", ""),
    "bicara":       ("normal", "normal", "bicara",    {}, 0,    0, "",       ""),
    "mendengar":    ("besar",  "normal", "tutup",     {}, -7, -52, "",       ""),
    "benar":        ("gembira","normal", "lebar",     {"bintang": True}, 0, -40, "", "lompat"),
    "menyemangati": ("normal", "naik",   "senyum",    {}, 0,  -70, "",       ""),
    "bingung":      ("normal", "tanya",  "gelombang", {"tanya": True}, 8, -20, "", ""),
}

_NAMA_POSE = tuple(_POSE)


def _svg(pose: str) -> str:
    mata, alis, mulut, efek, miring, putar_kanan, anim_tangan, anim_badan = _POSE[pose]

    kelas_badan = anim_badan
    return (
        '<svg viewBox="0 0 200 260" role="img" aria-label="Steven">'
        f'<g class="napas"><g class="{kelas_badan}">'
        f'{_tangan("kiri")}'
        f'{_badan()}'
        f'{_tangan("kanan", f"rotate({putar_kanan} 156 196)", anim_tangan)}'
        f'<g id="kepala" transform="rotate({miring} 100 150)">'
        f'{_kepala(mata, alis, mulut)}{_rambut()}'
        f'{_efek(efek.get("tanya", False), efek.get("bintang", False))}'
        '</g>'
        '</g></g>'
        '</svg>'
    )


# =============================================================================
# ANTARMUKA
# =============================================================================

def _gelembung(teks: str) -> str:
    """Gelembung bicara di kanan karakter, ekor menunjuk ke tokoh. Teks di-escape."""
    if not teks.strip():
        return ""
    return (
        '<div class="gelembung" role="note">'
        f'<p>{html.escape(teks.strip())}</p>'
        '<svg class="ekor" viewBox="0 0 24 24" aria-hidden="true">'
        '<path d="M22 3 L2 12 L22 21 Z" fill="#fff" stroke="#2A1548" stroke-width="3" stroke-linejoin="round"/></svg>'
        '</div>'
    )


@lru_cache(maxsize=128)
def narator(keadaan: str, teks: str = "", durasi_bicara: float = 0.0) -> str:
    """HTML narator chibi siap pakai di st.markdown(unsafe_allow_html=True) atau components.html.

    keadaan: salah satu dari _NAMA_POSE; nilai lain jatuh ke "melambai".
    durasi_bicara: panjang audio (detik) untuk menyesuaikan kecepatan mulut.
    """
    pose = keadaan if keadaan in _POSE else "melambai"
    # shortkut: <style> ikut terkirim tiap panggilan (Streamlit membuang duplikat). Pindah ke
    # komponen.pasang_css bila HTML makin besar.
    return (
        f'<style>{_gaya(float(durasi_bicara or 0))}</style>'
        '<div class="sv" style="display:flex;align-items:center;gap:12px;max-width:520px">'
        '<div style="flex:0 0 auto;width:160px">'
        f'{_svg(pose)}'
        '</div>'
        f'{_gelembung(teks)}'
        '</div>'
    )