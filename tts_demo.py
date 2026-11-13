# -*- coding: utf-8 -*-
"""
tts_demo.py -- Prototipe Text-to-Speech (TTS), Minggu 1.

Membaca satu segmen cerita dari korpus/cerita/*.json, lalu menyuarakannya dalam
bahasa Indonesia. Korpus ini sama dengan korpus yang dibaca aplikasi
(dongeng_nusantara.py lewat modul/korpus.py), jadi tidak ada dua sumber yang bisa
tidak sinkron. Tiap adegan dianggap satu segmen.

Mesin utama adalah gTTS (butuh internet); jika gTTS gagal, program mencoba
pyttsx3 (luring, memakai suara yang terpasang di komputer).

Cara menjalankan (dari folder proyek):
    python tts_demo.py
    python tts_demo.py --cerita malin --segmen 2
    python tts_demo.py --pelan                 # gTTS: kecepatan bicara lambat
    python tts_demo.py --laju 130 --mesin pyttsx3   # atur kecepatan pyttsx3
    python tts_demo.py --daftar                # tampilkan id cerita dan segmen

Hasil suara disimpan di folder suara/, lalu diputar dengan pemutar bawaan sistem.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


FOLDER = Path(__file__).resolve().parent
FOLDER_KORPUS = FOLDER / "korpus" / "cerita"
FOLDER_SUARA = FOLDER / "suara"

BAHASA_TTS = "id"        # kode bahasa Indonesia untuk gTTS
LAJU_AWAL = 150          # kata per menit untuk pyttsx3 (bawaan mesin sekitar 200)
LAJU_TERCEPAT = 300      # batas atas agar nilai --laju tetap masuk akal


def muat_cerita(folder: Path = FOLDER_KORPUS) -> list[dict]:
    """Membaca semua korpus/cerita/*.json, urut nama berkas.

    Kode cerita diambil dari nama berkas: "01_kancil.json" menjadi "kancil",
    sama seperti modul/korpus.py agar id yang dipakai sama di kedua tempat.
    """
    if not folder.exists():
        raise FileNotFoundError(f"Folder korpus tidak ditemukan: {folder}")
    daftar = []
    for berkas in sorted(folder.glob("*.json")):
        data = json.loads(berkas.read_text(encoding="utf-8"))
        daftar.append({
            "id": re.sub(r"^\d+_", "", berkas.stem),
            "judul": data.get("judul", berkas.stem),
            "segmen": data.get("adegan", []),
            "berkas": berkas.name,
        })
    if not daftar:
        raise ValueError(f"Tidak ada berkas cerita di {folder}")
    return daftar


def ambil_segmen(daftar: list[dict], id_cerita: str, nomor: int) -> tuple[dict, dict]:
    """Mengambil satu cerita dan satu segmennya. Nomor segmen dimulai dari 1."""
    cerita = next((c for c in daftar if c.get("id") == id_cerita), None)
    if cerita is None:
        pilihan = ", ".join(c.get("id", "?") for c in daftar)
        raise ValueError(f"Cerita '{id_cerita}' tidak ada. Pilihan: {pilihan}")
    segmen = cerita.get("segmen", [])
    if not 1 <= nomor <= len(segmen):
        raise ValueError(f"Cerita '{id_cerita}' punya {len(segmen)} segmen; nomor {nomor} tidak ada.")
    return cerita, segmen[nomor - 1]


def pilih_suara_indonesia(mesin) -> str | None:
    """Memilih suara berbahasa Indonesia yang terpasang, jika ada."""
    for suara in mesin.getProperty("voices"):
        info = f"{suara.id} {suara.name} {getattr(suara, 'languages', '')}".lower()
        if "indones" in info or "id_id" in info or "id-id" in info:
            return suara.id
    return None


def simpan_mp3(teks: str, pelan: bool, nama: str) -> Path:
    """Menyimpan suara gTTS ke folder suara/ dan mengembalikan jalurnya."""
    from gtts import gTTS   # diimpor di dalam fungsi agar galat ImportError mudah ditangani

    FOLDER_SUARA.mkdir(exist_ok=True)
    tujuan = FOLDER_SUARA / f"{nama}.mp3"
    # slow=True membuat gTTS membacakan kalimat lebih lambat (kecepatan bicara).
    gTTS(text=teks, lang=BAHASA_TTS, slow=pelan, lang_check=False, timeout=15).save(str(tujuan))
    return tujuan


def ucapkan_pyttsx3(teks: str, laju: int, nama: str) -> Path:
    """Menyuarakan teks dengan pyttsx3 (luring) dan menyimpannya sebagai WAV."""
    import pyttsx3

    mesin = pyttsx3.init()
    suara_id = pilih_suara_indonesia(mesin)
    if suara_id:
        mesin.setProperty("voice", suara_id)
    else:
        print("[info] Suara bahasa Indonesia belum terpasang; memakai suara bawaan sistem.")
    mesin.setProperty("rate", laju)

    FOLDER_SUARA.mkdir(exist_ok=True)
    tujuan = FOLDER_SUARA / f"{nama}.wav"
    mesin.save_to_file(teks, str(tujuan))
    mesin.runAndWait()
    mesin.stop()
    if not tujuan.exists() or tujuan.stat().st_size == 0:
        raise RuntimeError("pyttsx3 tidak menghasilkan berkas suara.")
    return tujuan


def putar(berkas: Path) -> None:
    """Memutar berkas suara dengan pemutar bawaan sistem operasi."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(berkas)                       # Windows
        elif sys.platform == "darwin":
            os.system(f'open "{berkas}"')              # macOS
        else:
            os.system(f'xdg-open "{berkas}" >/dev/null 2>&1')  # Linux
    except OSError as galat:
        print(f"[info] Tidak bisa memutar otomatis ({galat}). Berkas bisa dibuka manual:")
        print(f"       {berkas}")


def main() -> int:
    """Titik masuk: baca argumen, ambil segmen, lalu suarakan."""
    parser = argparse.ArgumentParser(description="Prototipe TTS bahasa Indonesia dari korpus cerita.")
    parser.add_argument("--cerita", default="kancil", help="id cerita, lihat --daftar")
    parser.add_argument("--segmen", type=int, default=1, help="nomor segmen (adegan), mulai dari 1")
    parser.add_argument("--pelan", action="store_true", help="gTTS membacakan lebih lambat")
    parser.add_argument("--laju", type=int, default=LAJU_AWAL,
                        help=f"kecepatan bicara pyttsx3, kata per menit (bawaan {LAJU_AWAL})")
    parser.add_argument("--mesin", choices=["gtts", "pyttsx3"], default="gtts",
                        help="mesin TTS yang dipakai lebih dulu")
    parser.add_argument("--tanpa-putar", action="store_true", help="hanya simpan berkas, tidak diputar")
    parser.add_argument("--daftar", action="store_true", help="tampilkan id cerita dan jumlah segmen")
    argumen = parser.parse_args()

    try:
        daftar = muat_cerita()
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as galat:
        print(f"[gagal] Korpus tidak bisa dibaca: {galat}")
        return 1

    if argumen.daftar:
        for c in daftar:
            print(f"{c['id']:<10} {c['judul']} ({len(c['segmen'])} segmen, berkas {c['berkas']})")
        return 0

    laju = max(50, min(argumen.laju, LAJU_TERCEPAT))
    nama = f"{argumen.cerita}_segmen{argumen.segmen}_{'pelan' if argumen.pelan else 'normal'}"

    try:
        cerita, segmen = ambil_segmen(daftar, argumen.cerita, argumen.segmen)
    except ValueError as galat:
        print(f"[gagal] Korpus tidak bisa dibaca: {galat}")
        return 1

    teks = segmen.get("narasi", "").strip()
    if not teks:
        print("[gagal] Segmen yang dipilih tidak punya teks narasi.")
        return 1

    print(f"Cerita : {cerita.get('judul')} (segmen {argumen.segmen})")
    print(f"Teks   : {teks}")
    print(f"Mesin  : {argumen.mesin}")

    if argumen.mesin == "gtts":
        mesin_urutan = ["gtts", "pyttsx3"]
    else:
        mesin_urutan = ["pyttsx3", "gtts"]

    galat_mesin: list[str] = []
    for mesin in mesin_urutan:
        try:
            if mesin == "gtts":
                berkas = simpan_mp3(teks, argumen.pelan, nama)
            else:
                berkas = ucapkan_pyttsx3(teks, laju, nama)
        except ImportError as galat:
            galat_mesin.append(f"{mesin}: pustaka belum terpasang ({galat})")
        except Exception as galat:   # gTTSError, koneksi, driver suara, dll.
            galat_mesin.append(f"{mesin}: {galat}")
        else:
            print(f"[sukses] Suara disimpan: {berkas}")
            if not argumen.tanpa_putar:
                putar(berkas)
            return 0

    print("[gagal] Tidak ada mesin TTS yang berhasil.")
    for pesan in galat_mesin:
        print(f"        - {pesan}")
    print("        Periksa internet (gTTS) atau suara yang terpasang di komputer (pyttsx3).")
    return 1


if __name__ == "__main__":
    sys.exit(main())