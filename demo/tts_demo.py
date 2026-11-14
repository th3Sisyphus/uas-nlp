# -*- coding: utf-8 -*-
"""
tts_demo.py -- Prototipe Text-to-Speech (TTS), Minggu 1.

Membaca segmen cerita dari korpus/cerita/*.json, lalu menyuarakannya dalam bahasa
Indonesia. Korpus ini sama dengan korpus yang dibaca aplikasi (dongeng_nusantara.py
lewat modul/korpus.py), jadi tidak ada dua sumber yang bisa tidak sinkron. Tiap
adegan dianggap satu segmen.

Mesin utama adalah edge-tts (Microsoft Edge, butuh internet) dengan suara saraf
id-ID-GadisNeural atau id-ID-ArdiNeural. Cadangan otomatis: gTTS, lalu pyttsx3
(luring, memakai suara yang terpasang di komputer).

Hasil suara disimpan di folder suara/ sebagai berkas MP3 bernama hash dari
teks + mesin + suara + rate + pitch. Nama yang sama tidak disintesis ulang.

Cara menjalankan (dari folder proyek):
    python demo/tts_demo.py
    python demo/tts_demo.py --cerita malin --segmen 2 --suara id-ID-ArdiNeural
    python demo/tts_demo.py --rate -10% --pitch +5Hz
    python demo/tts_demo.py --mesin gtts
    python demo/tts_demo.py --bandingkan        # tiga mesin, kalimat yang sama
    python demo/tts_demo.py --semua             # pra-render seluruh korpus
    python demo/tts_demo.py --daftar            # tampilkan id cerita dan segmen

Hasil suara diputar dengan pemutar bawaan sistem (pakai --tanpa-putar untuk
mematikannya).
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


FOLDER = Path(__file__).resolve().parent.parent   # demo/ ada di dalam folder proyek
FOLDER_KORPUS = FOLDER / "korpus" / "cerita"
FOLDER_SUARA = FOLDER / "suara"

BAHASA_TTS = "id"                        # kode bahasa Indonesia untuk gTTS
SUARA_EDGE = "id-ID-GadisNeural"         # suara utama edge-tts
SUARA_EDGE_CADANGAN = "id-ID-ArdiNeural" # suara pria edge-tts, dipakai jika suara utama tidak ada
RATE_AWAL = 0             # persen, edge-tts: --rate -10 berarti 10% lebih lambat
PITCH_AWAL = 0            # Hz, edge-tts: --pitch 5 berarti nada naik 5 Hz
LAJU_PYTTSX3 = 150        # kata per menit untuk pyttsx3 (bawaan mesin sekitar 200)
LAJU_TERCEPAT = 300       # batas atas agar laju pyttsx3 tetap masuk akal
MESIN = ["edge", "gtts", "pyttsx3"]

# Pola nilai edge-tts: tanda wajib di depan supaya hasilnya tidak ambigu.
POLA_RATE = re.compile(r"^[+-]\d{1,3}%$")
POLA_PITCH = re.compile(r"^[+-]\d{1,3}Hz$")

# Kalimat uji untuk --bandingkan: pertanyaan, seruan, dan kalimat panjang.
TEKS_BANDING = "Hai, teman-teman! Hari ini kita akan membaca cerita Si Kancil dan Buaya."

# Kalimat umpan balik dari aplikasi, ikut di-pra-render oleh --semua.
TEKS_UMPAN_BALIK = "Wah, suaranya kurang terdengar, coba bilang sekali lagi yuk!"


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


def jalur_cache(teks: str, mesin: str, suara: str, rate: str, pitch: str) -> Path:
    """Nama berkas dari hash isi: teks + mesin + suara + rate + pitch."""
    bahan = "\x1f".join([teks, mesin, suara, rate, pitch])
    sidik = hashlib.sha1(bahan.encode("utf-8")).hexdigest()[:16]
    return FOLDER_SUARA / f"{mesin}_{sidik}.mp3"


def laju_pyttsx3(rate: str) -> int:
    """Menerjemahkan rate edge-tts ("-10%") menjadi kata per menit pyttsx3."""
    persen = int(rate.rstrip("%"))
    return max(50, min(round(LAJU_PYTTSX3 * (100 + persen) / 100), LAJU_TERCEPAT))


def simpan_edge(teks: str, suara: str, rate: str, pitch: str, tujuan: Path) -> None:
    """Menyimpan MP3 dengan edge-tts; mengganti suara yang tidak tersedia."""
    import edge_tts

    def tulis(pilihan: str) -> None:
        # Communicate dibuat di dalam korutin: konstruktornya bisa menyentuh jaringan.
        async def jalan() -> None:
            await edge_tts.Communicate(teks, pilihan, rate=rate, pitch=pitch).save(str(tujuan))

        asyncio.run(jalan())

    galat: Exception | None = None
    for pilihan in (suara, SUARA_EDGE, SUARA_EDGE_CADANGAN):
        try:
            tulis(pilihan)
            if tujuan.exists() and tujuan.stat().st_size > 0:
                return
            galat = RuntimeError("edge-tts tidak menghasilkan berkas suara")
        except Exception as salah:   # internet putus, layanan menolak, suara salah
            galat = salah
        print(f"[info] Suara {pilihan} gagal, mencoba suara lain.")
        tujuan.unlink(missing_ok=True)
    raise galat or RuntimeError("suara edge-tts tidak tersedia")


def simpan_gtts(teks: str, tujuan: Path) -> None:
    """Menyimpan MP3 dengan gTTS (rate dan pitch tidak didukung gTTS)."""
    from gtts import gTTS   # diimpor di dalam fungsi agar galat ImportError mudah ditangani

    # gTTS tidak mendukung rate/pitch; slow tetap False karena kecepatan diatur edge-tts.
    gTTS(text=teks, lang=BAHASA_TTS, slow=False, lang_check=False, timeout=15).save(str(tujuan))
    if tujuan.stat().st_size == 0:
        raise RuntimeError("gTTS tidak menghasilkan berkas suara")


def simpan_pyttsx3(teks: str, tujuan: Path, laju: int) -> None:
    """Menyimpan WAV dengan pyttsx3 (luring), lalu diubah ke MP3; tanpa ffmpeg tetap WAV."""
    import pyttsx3

    mesin = pyttsx3.init()
    suara_id = pilih_suara_indonesia(mesin)
    if suara_id:
        mesin.setProperty("voice", suara_id)
    else:
        print("[info] Suara bahasa Indonesia belum terpasang; memakai suara bawaan sistem.")
    mesin.setProperty("rate", laju)

    sementara = tujuan.with_suffix(".wav")
    mesin.save_to_file(teks, str(sementara))
    mesin.runAndWait()
    mesin.stop()
    if not sementara.exists() or sementara.stat().st_size == 0:
        raise RuntimeError("pyttsx3 tidak menghasilkan berkas suara.")
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(sementara),
                        str(tujuan)], check=True, timeout=60,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        tujuan = sementara.replace(tujuan.with_suffix(".wav"))
        print("[info] ffmpeg tidak ada; suara pyttsx3 disimpan sebagai WAV.")
    else:
        sementara.unlink(missing_ok=True)


def urutan_mesin(pilihan: str) -> list[str]:
    """Urutan percobaan mesin: auto = edge, gtts, pyttsx3; lainnya mesin itu dulu."""
    if pilihan == "auto":
        return MESIN
    return [pilihan] + [m for m in MESIN if m != pilihan]


def buat_suara(teks: str, pilihan: dict) -> tuple[Path, str]:
    """Menyintesis teks dengan urutan mesin (utama lalu cadangan).

    Mengembalikan (berkas, mesin yang berhasil) atau melempar RuntimeError berisi
    daftar kegagalan. Berkas yang sudah ada di cache dipakai ulang.
    """
    daftar_galat: list[str] = []
    for mesin in urutan_mesin(pilihan["mesin"]):
        suara = pilihan["suara"] if mesin == "edge" else mesin
        tujuan = jalur_cache(teks, mesin, suara, pilihan["rate"], pilihan["pitch"])
        if tujuan.exists():
            print(f"[cache] {mesin}: {tujuan.name} sudah ada, dipakai ulang.")
            return tujuan, mesin
        try:
            FOLDER_SUARA.mkdir(exist_ok=True)
            if mesin == "edge":
                simpan_edge(teks, pilihan["suara"], pilihan["rate"], pilihan["pitch"], tujuan)
            elif mesin == "gtts":
                simpan_gtts(teks, tujuan)
            else:
                simpan_pyttsx3(teks, tujuan, laju_pyttsx3(pilihan["rate"]))
            if not tujuan.exists():
                tujuan = tujuan.with_suffix(".wav")   # pyttsx3 tanpa ffmpeg
        except ImportError as galat:
            daftar_galat.append(f"{mesin}: pustaka belum terpasang ({galat})")
        except Exception as galat:   # internet putus, layanan menolak, driver suara, dll.
            daftar_galat.append(f"{mesin}: {galat}")
        else:
            return tujuan, mesin

    raise RuntimeError("; ".join(daftar_galat))


def bandingkan(rate: str, pitch: str, tanpa_putar: bool) -> int:
    """Membacakan kalimat contoh yang sama dengan ketiga mesin, berurutan."""
    print(f"Kalimat: {TEKS_BANDING}")
    berhasil = 0
    for mesin in MESIN:
        pilihan = {"mesin": mesin, "suara": SUARA_EDGE, "rate": rate, "pitch": pitch}
        try:
            berkas, _ = buat_suara(TEKS_BANDING, pilihan)
        except RuntimeError as galat:
            print(f"[gagal] {mesin} tidak menghasilkan suara ({galat}).")
            continue
        berhasil += 1
        print(f"[{mesin}] {berkas.name} ({berkas.stat().st_size // 1024} KB)")
        if not tanpa_putar:
            putar(berkas)
    return 0 if berhasil else 1


def render_semua(rate: str, pitch: str, mesin: str, suara: str) -> int:
    """Pra-render semua segmen cerita, pertanyaan, dan kalimat umpan balik."""
    pilihan = {"mesin": mesin, "suara": suara, "rate": rate, "pitch": pitch}
    tugas: list[tuple[str, str]] = []
    for cerita in muat_cerita():
        for nomor, segmen in enumerate(cerita["segmen"], start=1):
            tugas.append((f"{cerita['id']} segmen {nomor}", segmen.get("narasi", "")))
            tugas.append((f"{cerita['id']} tanya {nomor}", segmen.get("tanya", "")))
    tugas.append(("umpan balik", TEKS_UMPAN_BALIK))

    gagal = 0
    for label, teks in tugas:
        teks = teks.strip()
        if not teks:
            continue
        try:
            berkas, dipakai = buat_suara(teks, pilihan)
        except RuntimeError as galat:
            gagal += 1
            print(f"[gagal] {label}: {galat}")
            continue
        print(f"[ok] {label:<20} {dipakai:<8} {berkas.name}")
    print(f"[selesai] {len(tugas) - gagal} dari {len(tugas)} teks ada di {FOLDER_SUARA}.")
    return 0 if gagal == 0 else 1


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
    """Titik masuk: baca argumen, lalu pilih mode (biasa, --bandingkan, --semua)."""
    parser = argparse.ArgumentParser(description="Prototipe TTS bahasa Indonesia dari korpus cerita.")
    parser.add_argument("--cerita", default="kancil", help="id cerita, lihat --daftar")
    parser.add_argument("--segmen", type=int, default=1, help="nomor segmen (adegan), mulai dari 1")
    parser.add_argument("--mesin", choices=["auto", "edge", "gtts", "pyttsx3"], default="auto",
                        help="mesin utama; gagal maka pindah ke cadangan")
    parser.add_argument("--suara", default=SUARA_EDGE,
                        help=f"suara edge-tts (bawaan {SUARA_EDGE}; alternatif {SUARA_EDGE_CADANGAN})")
    parser.add_argument("--rate", type=int, default=RATE_AWAL,
                        help=f"kecepatan edge-tts, persen, contoh -10 (bawaan {RATE_AWAL})")
    parser.add_argument("--pitch", type=int, default=PITCH_AWAL,
                        help=f"tinggi nada edge-tts, Hz, contoh 5 (bawaan {PITCH_AWAL})")
    parser.add_argument("--bandingkan", action="store_true",
                        help="bacakan kalimat contoh dengan ketiga mesin berurutan")
    parser.add_argument("--semua", action="store_true",
                        help="pra-render semua segmen, pertanyaan, dan umpan balik")
    parser.add_argument("--tanpa-putar", action="store_true", help="hanya simpan berkas, tidak diputar")
    parser.add_argument("--daftar", action="store_true", help="tampilkan id cerita dan jumlah segmen")
    argumen = parser.parse_args()

    # Edge-tts minta tanda di depan; nilai bulat dari CLI dirapikan di sini.
    rate, pitch = f"{argumen.rate:+d}%", f"{argumen.pitch:+d}Hz"
    if not POLA_RATE.match(rate) or not POLA_PITCH.match(pitch):
        print("[gagal] Nilai --rate atau --pitch di luar batas (maksimal tiga angka).")
        return 2

    try:
        daftar = muat_cerita()
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as galat:
        print(f"[gagal] Korpus tidak bisa dibaca: {galat}")
        return 1

    if argumen.daftar:
        for c in daftar:
            print(f"{c['id']:<10} {c['judul']} ({len(c['segmen'])} segmen, berkas {c['berkas']})")
        return 0

    if argumen.bandingkan:
        return bandingkan(rate, pitch, argumen.tanpa_putar)
    if argumen.semua:
        return render_semua(rate, pitch, argumen.mesin, argumen.suara)

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
    print(f"Mesin  : {argumen.mesin}, suara {argumen.suara}, rate {rate}, pitch {pitch}")

    pilihan = {"mesin": argumen.mesin, "suara": argumen.suara, "rate": rate, "pitch": pitch}
    try:
        berkas, mesin_dipakai = buat_suara(teks, pilihan)
    except RuntimeError as galat:
        print("[gagal] Tidak ada mesin TTS yang berhasil.")
        for pesan in str(galat).split("; "):
            print(f"        - {pesan}")
        print("        Periksa internet (edge-tts, gTTS) atau suara yang terpasang (pyttsx3).")
        return 1

    print(f"[sukses] {mesin_dipakai} menyimpan {berkas}")
    if not argumen.tanpa_putar:
        putar(berkas)
    return 0


if __name__ == "__main__":
    sys.exit(main())