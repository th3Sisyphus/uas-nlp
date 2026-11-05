# -*- coding: utf-8 -*-
"""Logika kuis: mengubah skor NLP menjadi pujian, petunjuk bertingkat, atau kunci jawaban.
"""

from __future__ import annotations

from modul.asr import PESAN_GANGGUAN
from modul.konfigurasi import KEYAKINAN_MINIMUM, MAKS_PERCOBAAN


# =============================================================================
# LOGIKA KUIS
# =============================================================================

PUJIAN = [
    "Wah, pintar sekali!",
    "Hebat, jawabanmu benar!",
    "Betul sekali, kamu menyimak dengan baik!",
    "Keren, kamu ingat ceritanya!",
    "Bagus sekali!",
]


def keputusan(jenis: str, pesan: str, lanjut: bool, hitung_percobaan: bool) -> dict:
    """Tindakan berikutnya setelah satu jawaban dinilai.

    jenis            : benar | hampir | salah | kunci | ulang
    pesan            : kalimat yang tampil dan dibacakan TTS
    lanjut           : True berarti pertanyaan selesai dan boleh ke adegan berikutnya
    hitung_percobaan : False berarti tidak mengurangi kesempatan anak
    """
    return {"jenis": jenis, "pesan": pesan, "lanjut": lanjut, "hitung_percobaan": hitung_percobaan}


def putuskan(
    hasil: dict,
    adegan: dict,
    percobaan_sebelumnya: int,
    nomor_adegan: int = 0,
    keyakinan: float | None = None,
    ujung_terpotong: bool = False,
) -> dict:
    """Mengubah skor NLP menjadi umpan balik. Fungsi murni sehingga mudah diuji."""
    if hasil["lulus"]:
        pujian = PUJIAN[nomor_adegan % len(PUJIAN)]
        return keputusan("benar", f"{pujian} Jawabannya memang {adegan['utama']}.", True, False)

    # Jawaban salah yang mungkin akibat gangguan ASR tidak dihitung sebagai kesalahan anak.
    if ujung_terpotong and not hasil["hampir"]:
        return keputusan("ulang", PESAN_GANGGUAN["terpotong"], False, False)
    if keyakinan is not None and keyakinan < KEYAKINAN_MINIMUM and not hasil["hampir"]:
        return keputusan("ulang", PESAN_GANGGUAN["kurang_yakin"], False, False)

    percobaan = percobaan_sebelumnya + 1
    if percobaan >= MAKS_PERCOBAAN:
        pesan = (f"Tidak apa-apa, kamu sudah berusaha. Jawabannya adalah {adegan['utama']}. "
                 "Yuk, kita lanjutkan ceritanya!")
        return keputusan("kunci", pesan, True, True)
    # Petunjuk bertingkat: mula-mula makna, lalu huruf awal untuk mengenalkan keaksaraan.
    petunjuk = adegan["petunjuk"]
    if percobaan > 1:
        petunjuk += f" Jawabannya dimulai dengan huruf {adegan['utama'][0].upper()}."
    jenis, awalan = ("hampir", "Hampir benar!") if hasil["hampir"] else ("salah", "Belum tepat, tidak apa-apa.")
    return keputusan(jenis, f"{awalan} {petunjuk} Coba lagi, ya!", False, True)
