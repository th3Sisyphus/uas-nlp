# -*- coding: utf-8 -*-
"""Memuat korpus dongeng (korpus/cerita/*.json) dan leksikon (korpus/leksikon.json).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from modul.konfigurasi import BERKAS_LEKSIKON, FOLDER_CERITA


# =============================================================================
# MEMUAT KORPUS
# Korpus mini berisi penceritaan ulang singkat cerita rakyat Indonesia. Kalimatnya
# sengaja pendek agar mudah diikuti anak usia 4 sampai 6 tahun. Tiap adegan punya satu
# pertanyaan recall atau wh- (metode CROWD). Isinya ada di folder korpus/.
# =============================================================================

KOLOM_CERITA = ("judul", "asal", "ajaran", "warna", "adegan")
KOLOM_ADEGAN = ("narasi", "tanya", "kunci", "utama", "petunjuk", "stiker", "gambar")


def muat_cerita(folder: Path = FOLDER_CERITA) -> dict[str, dict]:
    """Membaca semua dongeng dari korpus/cerita/*.json, urut menurut nama berkas.

    Nama berkas "01_kancil.json" memberi kode cerita "kancil". Kolom yang hilang
    langsung dilaporkan, agar salah ketik di korpus tidak baru ketahuan saat demo.
    """
    cerita = {}
    for berkas in sorted(folder.glob("*.json")):
        data = json.loads(berkas.read_text(encoding="utf-8"))
        kurang = [k for k in KOLOM_CERITA if k not in data]
        for nomor, adegan in enumerate(data.get("adegan", []), 1):
            kurang += [f"adegan {nomor}: {k}" for k in KOLOM_ADEGAN if k not in adegan]
            if adegan.get("utama") not in adegan.get("kunci", []):
                kurang.append(f"adegan {nomor}: 'utama' harus ada di daftar 'kunci'")
        if kurang:
            raise ValueError(f"Korpus {berkas.name} belum lengkap: {'; '.join(kurang)}")
        cerita[re.sub(r"^\d+_", "", berkas.stem)] = data
    if not cerita:
        raise FileNotFoundError(f"Tidak ada berkas cerita di {folder}")
    return cerita


CERITA = muat_cerita()
LEKSIKON = json.loads(BERKAS_LEKSIKON.read_text(encoding="utf-8"))
